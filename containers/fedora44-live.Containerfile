# SPDX-License-Identifier: MIT
# Disposable Fedora 44 KDE runtime for NoxForge package and live qualification.
FROM registry.fedoraproject.org/fedora:44

RUN dnf -y install \
        dnf5-plugins \
        dolphin \
        firefox \
        kdialog \
        konsole \
        kwin \
        libei \
        libei-devel \
        cmake \
        gcc-c++ \
        ninja-build \
        plasma-systemsettings \
        plasma-workspace \
        python3-pillow \
        qt6-qtbase-devel \
        qt6-qtbase-gui \
        sddm \
        spectacle \
    && dnf clean all

RUN dnf -y install dbus-daemon qt6-qtdeclarative-devel xorg-x11-server-Xvfb \
    && dnf clean all

COPY . /opt/NoxForge
RUN cmake -S /opt/NoxForge -B /tmp/noxforge-live-build -G Ninja \
        -DNOXFORGE_BUILD_LIVE_INPUT=ON \
    && cmake --build /tmp/noxforge-live-build --target noxforge_live_input \
    && install -Dm0755 \
        /tmp/noxforge-live-build/noxforge-live-input \
        /usr/local/bin/noxforge-live-input \
    && rm -rf /tmp/noxforge-live-build
