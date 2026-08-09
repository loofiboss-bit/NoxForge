# COPR publication boundary

The authenticated COPR owner is `loofitheboss` and the release project is
`loofitheboss/noxforge`. Fedora 44 x86_64 is the supported build target.

Create the project once:

```bash
copr-cli create noxforge \
  --chroot fedora-44-x86_64 \
  --description "NoxForge Forge Identity components for Fedora KDE" \
  --instructions "Enable the repository, install noxforge, then select NoxForge explicitly in System Settings."
```

Submit only the SRPM built from an exact stable, qualified tag. Refuse
development versions:

```bash
version=$(<VERSION)
case "$version" in
  *-*) echo "Refusing development version: $version" >&2; exit 1 ;;
esac
test "$(git describe --tags --exact-match)" = "v${version}"
copr-cli build loofitheboss/noxforge \
  "rpmbuild/SRPMS/noxforge-${version}-1.fc44.src.rpm"
```

After submission, require COPR's authoritative build state to be terminal
`succeeded` and confirm that the binary package is downloadable. Then install
it in the isolated live-test environment, run `rpm -V noxforge` and
`noxforge-doctor`, and confirm that no active KDE or SDDM setting changed.
