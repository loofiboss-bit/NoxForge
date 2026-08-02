from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"scripts/{name}.py")
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load scripts/{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


source_build = load_script("build")
check_v7_candidate = load_script("check_v7_candidate")
CONTRACT = json.loads(
    (ROOT / "design/v7-candidate-contract.json").read_text(encoding="utf-8")
)
EVIDENCE = json.loads(
    (ROOT / "docs/evidence/v7/candidate/phase8.json").read_text(encoding="utf-8")
)


def tree_hash(root: Path) -> str:
    digest = hashlib.sha256()
    if not root.exists():
        return digest.hexdigest()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
    return digest.hexdigest()


class V7PhaseEightTests(unittest.TestCase):
    def test_live_manifest_hashes_are_enforced(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-v7-live-hashes-") as name:
            root = Path(name)
            evidence = root / "evidence.txt"
            evidence.write_text("bound evidence\n", encoding="utf-8")
            manifest = {
                "files": {
                    evidence.name: {
                        "sha256": hashlib.sha256(evidence.read_bytes()).hexdigest(),
                        "bytes": evidence.stat().st_size,
                    }
                }
            }
            check_v7_candidate.verify_live_files(manifest, root)
            evidence.write_text("mutated evidence\n", encoding="utf-8")
            with self.assertRaisesRegex(RuntimeError, "hash or size drifted"):
                check_v7_candidate.verify_live_files(manifest, root)

    def test_source_archive_contains_reproducible_live_environment(self) -> None:
        self.assertIn(Path("containers"), source_build.SOURCE_PATHS)
        container = (ROOT / "containers/fedora44-live.Containerfile").read_text(encoding="utf-8")
        for fragment in (
            "libei-devel",
            "NOXFORGE_BUILD_LIVE_INPUT=ON",
            "--target noxforge_live_input",
            "/usr/local/bin/noxforge-live-input",
        ):
            self.assertIn(fragment, container)

    def test_live_runner_executes_complete_checks_for_every_scenario(self) -> None:
        source = (ROOT / "scripts/run_v7_live_matrix.py").read_text(encoding="utf-8")
        single_case = source.split("def single_case", 1)[1].split("def mixed_case", 1)[0]
        mixed_case = source.split("def mixed_case", 1)[1].split("def inner", 1)[0]
        self.assertNotIn("scale not in", single_case)
        self.assertNotIn("scale !=", single_case)
        self.assertIn("single_case(session)", mixed_case)
        for fragment in (
            "keyboard_dialog_activation(session, label)",
            "blur_state_capture(session, label)",
            "tabbox_state_matrix(session, label)",
            "sddm-enter-validation",
            "require_color_presence(",
            "tolerance=32",
            "for _ in range(4):",
            "time.sleep(0.5)",
            "require_color_row_span(",
            "for _ in range(6):",
            "logout-cancel-focus",
        ):
            self.assertIn(fragment, single_case)

    def test_candidate_is_stable_with_every_mandatory_live_case_passed(self) -> None:
        qualification = json.loads(
            (ROOT / "docs/evidence/v7/qualification.json").read_text(encoding="utf-8")
        )
        self.assertEqual(qualification["releaseState"], "release")
        self.assertTrue(qualification["releaseReady"])
        self.assertRegex(qualification["candidate"]["sourceCommit"], r"^[0-9a-f]{40}$")
        live = {case["id"]: case for case in qualification["liveCases"]}
        for case_id in CONTRACT["mandatoryLiveCases"]:
            self.assertEqual(live[case_id]["status"], "passed")
        self.assertTrue(
            any(live[case_id]["priority"] == "P0" for case_id in CONTRACT["mandatoryLiveCases"])
        )

    def test_release_notes_cover_fix_scope_limitations_upgrade_and_rollback(self) -> None:
        notes = (ROOT / "docs/releases/v7.0.0.md").read_text(encoding="utf-8")
        for fragment in (
            "Corrected behavior",
            "Qualification status and limitations",
            "Installation and upgrade",
            "Rollback",
            "100/125/140/150/175/200",
            "100+140/100+200",
        ):
            self.assertIn(fragment, notes)
        self.assertNotIn("UNQUALIFIED", notes)
        self.assertNotIn("not release-ready", notes)

    def test_local_staging_is_bounded_and_non_publishing(self) -> None:
        source = (ROOT / "scripts/prepare_v7_candidate.py").read_text(encoding="utf-8")
        for required in (
            "unqualified-local-development",
            "unsigned-local-development",
            "archiveIsByteReproducible",
            "SHA256SUMS",
            "releaseReady\": False",
        ):
            self.assertIn(required, source)
        for forbidden in ("curl", "wget", "git push", "gh release", "plasma-apply-", "kwriteconfig"):
            self.assertNotIn(forbidden, source)

    def test_user_install_cycle_preserves_kde_configuration(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-v7-user-cycle-") as name:
            home = Path(name)
            data = home / ".local/share"
            config = home / ".config"
            for relative, value in (
                ("kdeglobals", "[Icons]\nTheme=breeze-dark\n"),
                ("kwinrc", "[TabBox]\nLayoutName=org.kde.breeze.desktop\n"),
                ("plasmarc", "[Theme]\nname=breeze-dark\n"),
                ("sddm-sentinel", "Theme=breeze\n"),
            ):
                path = config / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(value, encoding="utf-8")
            before = tree_hash(config)
            environment = os.environ.copy()
            environment.update(
                HOME=str(home),
                XDG_DATA_HOME=str(data),
                XDG_CONFIG_HOME=str(config),
            )
            for _ in range(2):
                subprocess.run(
                    [str(ROOT / "scripts/install.sh"), "--user"],
                    cwd=ROOT,
                    env=environment,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(tree_hash(config), before)
            for _ in range(2):
                subprocess.run(
                    [str(ROOT / "scripts/uninstall.sh"), "--user"],
                    cwd=ROOT,
                    env=environment,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            self.assertEqual(tree_hash(config), before)
            self.assertFalse((data / "icons/NoxForge").exists())

    @unittest.skipUnless(shutil.which("cmake") and shutil.which("ninja"), "CMake/Ninja unavailable")
    def test_system_install_tree_is_repeatable_diagnosable_and_reversible(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-v7-system-cycle-") as name:
            temporary = Path(name)
            build = temporary / "build"
            stage = temporary / "stage"
            sentinel = stage / "etc/kde-preserved.conf"
            sentinel.parent.mkdir(parents=True)
            sentinel.write_text("preserve=true\n", encoding="utf-8")
            subprocess.run(
                [
                    "cmake",
                    "-S",
                    str(ROOT),
                    "-B",
                    str(build),
                    "-G",
                    "Ninja",
                    "-DCMAKE_BUILD_TYPE=Release",
                    "-DCMAKE_INSTALL_PREFIX=/usr",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                ["cmake", "--build", str(build)],
                check=True,
                capture_output=True,
                text=True,
            )
            environment = os.environ.copy()
            environment.update(
                NOXFORGE_BUILD_ROOT=str(build),
                NOXFORGE_SYSTEM_ROOT=str(stage),
            )
            for _ in range(2):
                subprocess.run(
                    [str(ROOT / "scripts/install-system.sh"), "--system"],
                    cwd=ROOT,
                    env=environment,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            doctor = subprocess.run(
                ["python3", "tools/noxforge-doctor", "--root", str(stage), "--json"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(doctor.stdout)
            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["expectedVersion"], "7.0.0")
            self.assertTrue(
                all(item["provenance"] == ["staged-system"] for item in report["components"].values())
            )
            self.assertTrue(sentinel.is_file())
            for _ in range(2):
                subprocess.run(
                    [str(ROOT / "scripts/uninstall-system.sh"), "--system"],
                    cwd=ROOT,
                    env=environment,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            self.assertTrue(sentinel.is_file())
            self.assertFalse(
                any(path.is_file() for path in (stage / "usr/share/icons/NoxForge").rglob("*"))
            )
            self.assertFalse(list(stage.glob("usr/lib*/qt6/plugins/styles/libnoxforge6.so")))

    def test_system_uninstall_rejects_non_noxforge_manifest_entries(self) -> None:
        with tempfile.TemporaryDirectory(prefix="noxforge-v7-uninstall-scope-") as name:
            temporary = Path(name)
            build = temporary / "build"
            stage = temporary / "stage"
            manifest = build / "install_manifest.txt"
            sentinel = stage / "usr/share/unrelated-project/data.txt"
            manifest.parent.mkdir(parents=True)
            sentinel.parent.mkdir(parents=True)
            manifest.write_text("/usr/share/unrelated-project/data.txt\n", encoding="utf-8")
            sentinel.write_text("preserve\n", encoding="utf-8")
            environment = os.environ.copy()
            environment.update(
                NOXFORGE_BUILD_ROOT=str(build),
                NOXFORGE_SYSTEM_ROOT=str(stage),
            )
            result = subprocess.run(
                [str(ROOT / "scripts/uninstall-system.sh"), "--system"],
                cwd=ROOT,
                env=environment,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Refusing non-NoxForge manifest entry", result.stderr)
            self.assertTrue(sentinel.is_file())

    def test_phase_evidence_records_stable_release_qualification(self) -> None:
        self.assertEqual(EVIDENCE["result"], "release-gate-passed")
        self.assertTrue(all(value == "passed" for value in EVIDENCE["localGate"]["categories"].values()))
        self.assertTrue(EVIDENCE["releaseReady"])
        self.assertTrue(EVIDENCE["liveQualification"]["qualifiesLiveSession"])
        self.assertEqual(EVIDENCE["releaseBlockers"], [])


if __name__ == "__main__":
    unittest.main()
