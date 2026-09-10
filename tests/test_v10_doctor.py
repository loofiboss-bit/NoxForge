from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.test_doctor import DOCTOR_FUNCTIONS as doctor, ROOT, THEME_ID, stage_complete, write


class DoctorV10Tests(unittest.TestCase):
    def test_single_color_scheme_is_valid_with_unknown_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / 'color-schemes/NoxForgeDark.colors')
            report = doctor['build_report'](root)
            self.assertEqual(report['schemaVersion'], 3)
            self.assertEqual(report['status'], 'ok')
            self.assertEqual(report['edition']['kind'], 'component')
            self.assertEqual(report['missing'], [])
            self.assertIsNone(report['expectedVersion'])
            self.assertEqual(report['components']['color-scheme']['metadataStatus'], 'unknown')
            self.assertNotIn('RPM', report['nextAction'])

    def test_global_theme_requires_only_declared_store_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / f'plasma/look-and-feel/{THEME_ID}/metadata.json', '{}')
            report = doctor['build_report'](root)
            manifest = json.loads((ROOT / 'distribution/kde-store/package-manifest.json').read_text())
            declared = next(item['dependencies'] for item in manifest['components'] if item['key'] == 'global-theme')
            aliases = {'colors': 'color-scheme', 'wallpapers': 'wallpaper'}
            self.assertEqual(report['missing'], sorted(aliases.get(item, item) for item in declared))
            self.assertIn('Store', report['nextAction'])

    def test_incomplete_portable_preserves_edition_and_advice(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / 'noxforge/manifest.json', '{}')
            write(root / 'color-schemes/NoxForgeDark.colors')
            report = doctor['build_report'](root)
            self.assertEqual(report['edition']['kind'], 'portable')
            self.assertEqual(report['status'], 'incomplete')
            self.assertNotIn('qt-style', report['missing'])
            self.assertIn('portable', report['nextAction'])

    def test_identical_and_changed_copies_have_ordered_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            stage_complete(root)
            source = root / f'usr/share/plasma/desktoptheme/{THEME_ID}'
            target = root / f'usr/local/share/plasma/desktoptheme/{THEME_ID}'
            shutil.copytree(source, target)
            report = doctor['build_report'](root)
            component = report['components']['plasma-style']
            self.assertEqual(report['status'], 'ok')
            self.assertEqual(component['duplicateStatus'], 'identical')
            self.assertEqual(component['effectivePath'], str(target / 'metadata.json'))
            self.assertEqual(component['shadowedPaths'], [str(source / 'metadata.json')])
            write(target / 'contents/different.svg', '<svg/>')
            report = doctor['build_report'](root)
            self.assertFalse(report['mixedVersions'])
            self.assertEqual(report['status'], 'incomplete')
            self.assertEqual(report['components']['plasma-style']['duplicateStatus'], 'conflict')
            self.assertTrue(any(issue['code'] == 'duplicate-conflict' for issue in report['issues']))

    def test_staged_report_never_queries_host_or_uses_repository_version(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / f'plasma/desktoptheme/{THEME_ID}/metadata.json', '{"KPlugin":{"Version":"1.2.3"}}')
            with patch('subprocess.run', side_effect=AssertionError('host command')), patch.dict('os.environ', {'XDG_SESSION_TYPE': 'wayland', 'KDE_FULL_SESSION': 'true', 'WAYLAND_DISPLAY': 'wayland-0'}):
                report = doctor['build_report'](root)
            self.assertIsNone(report['expectedVersion'])
            self.assertFalse(report['mixedVersions'])
            self.assertEqual(report['active'], {})
            self.assertEqual(report['session']['type'], 'not-applicable')
            self.assertEqual(report['session']['kernel'], 'not-applicable')

    def test_version_marker_symlink_cannot_escape_stage(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'noxforge').mkdir()
            (root / 'noxforge/VERSION').symlink_to(ROOT / 'VERSION')
            self.assertIsNone(doctor['expected_version'](root))

    def test_active_native_style_without_plugin_requires_action(self):
        components = {name: {'found': name == 'color-scheme', 'provenance': []} for name in doctor['COMPONENTS']}
        with tempfile.TemporaryDirectory() as temp:
            edition = doctor['edition_report']([Path(temp)], components, [], False, {'qtStyle': 'NoxForge'})
        self.assertEqual(edition['kind'], 'mixed')
        self.assertEqual(edition['missingMandatory'], ['native-qt-style'])

    def test_staged_component_symlink_does_not_import_external_metadata(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as outside:
            root = Path(temp)
            external = Path(outside) / 'metadata.json'
            write(external, '{"KPlugin":{"Version":"99.0.0"}}')
            marker = root / f'plasma/desktoptheme/{THEME_ID}/metadata.json'
            marker.parent.mkdir(parents=True)
            marker.symlink_to(external)
            report = doctor['build_report'](root)
            self.assertEqual(report['componentVersions'], [])
            self.assertFalse(report['components']['plasma-style']['found'])
            self.assertEqual(report['components']['plasma-style']['provenance'], [])

    def test_system_marker_requires_missing_native_plugin(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            stage_complete(root)
            write(root / 'usr/share/noxforge/release-manifest.json', '{}')
            (root / 'usr/lib64/qt6/plugins/styles/libnoxforge6.so').unlink()
            report = doctor['build_report'](root)
            self.assertEqual(report['edition']['kind'], 'complete-system')
            self.assertEqual(report['missing'], ['qt-style'])
            self.assertIn('distribution package manager', report['nextAction'])

    def test_xdg_data_dirs_preserve_precedence_and_remove_duplicates(self):
        with patch.dict('os.environ', {'XDG_DATA_HOME': '/custom/user', 'XDG_DATA_DIRS': '/custom/shared:/usr/share:/custom/shared:relative'}):
            self.assertEqual(doctor['data_roots'](Path('/')), [Path('/custom/user'), Path('/custom/shared'), Path('/usr/share')])

    def test_external_plugin_and_edition_markers_do_not_define_stage(self):
        with tempfile.TemporaryDirectory() as temp, tempfile.TemporaryDirectory() as external:
            root = Path(temp)
            target = Path(external) / 'payload'
            write(target, '{}')
            for name in ('usr/lib64/qt6/plugins/styles/libnoxforge6.so',
                         'usr/share/noxforge/manifest.json',
                         'usr/share/noxforge/release-manifest.json',
                         'usr/share/noxforge/.owned-files'):
                link = root / name
                link.parent.mkdir(parents=True, exist_ok=True)
                link.symlink_to(target)
            report = doctor['build_report'](root)
            self.assertFalse(report['components']['qt-style']['found'])
            self.assertEqual(report['edition']['kind'], 'absent')
            self.assertFalse(report['edition']['portableMarker'])

    def test_looping_version_symlink_is_unknown(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            marker = root / 'noxforge/VERSION'
            marker.parent.mkdir()
            marker.symlink_to('VERSION')
            self.assertIsNone(doctor['expected_version'](root))

    def test_mixed_portable_retains_management_capabilities(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(root / 'noxforge/manifest.json', '{}')
            components = {name: {'found': True, 'provenance': []} for name in doctor['COMPONENTS']}
            edition = doctor['edition_report']([root], components, [], True, {})
            self.assertEqual(edition['kind'], 'mixed')
            self.assertTrue({'installer', 'uninstaller', 'doctor'} <= set(edition['capabilities']))

    def test_service_timeouts_are_unknown_and_bounded(self):
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired('systemctl', 2)) as query:
            _, state = doctor['display_manager_state'](Path('/'))
        self.assertEqual(state, 'unknown')
        self.assertEqual(query.call_count, 2)
        self.assertTrue(all(call.kwargs['timeout'] == 2 for call in query.call_args_list))


if __name__ == '__main__':
    unittest.main()
