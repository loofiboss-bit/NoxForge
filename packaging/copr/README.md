# COPR publication boundary

The authenticated COPR owner is `loofitheboss` and the release project is
`loofitheboss/noxforge`. Fedora 44 x86_64 is the supported build target.

Create the project once:

```bash
copr-cli create noxforge \
  --chroot fedora-44-x86_64 \
  --description "NoxForge Industrial Precision theme for Fedora KDE" \
  --instructions "Enable the repository, install noxforge, then select NoxForge explicitly in System Settings."
```

Submit only the SRPM built from the exact qualified `v3.0.0` tag:

```bash
copr-cli build loofitheboss/noxforge \
  rpmbuild/SRPMS/noxforge-3.0.0-1.fc44.src.rpm
```

After the public build succeeds, install it in the isolated live-test
environment, run `rpm -V noxforge` and `noxforge-doctor`, and confirm that no
active KDE or SDDM setting changed.
