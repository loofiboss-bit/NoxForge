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
        plasma-systemsettings \
        plasma-workspace \
        python3-pillow \
        qt6-qtbase-gui \
        sddm \
        spectacle \
    && dnf clean all

RUN dnf -y install dbus-daemon qt6-qtdeclarative-devel xorg-x11-server-Xvfb \
    && dnf clean all
