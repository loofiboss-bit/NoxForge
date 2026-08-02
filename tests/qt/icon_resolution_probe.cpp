// SPDX-License-Identifier: MIT
#include <QGuiApplication>
#include <QIcon>
#include <QImage>
#include <QPixmap>
#include <QTextStream>

namespace {

bool hasVisiblePixel(const QImage &image)
{
    for (int y = 0; y < image.height(); ++y)
        for (int x = 0; x < image.width(); ++x)
            if (image.pixelColor(x, y).alpha() > 16)
                return true;
    return false;
}

bool verifyIcon(const QString &name, const QList<int> &sizes)
{
    const QIcon icon = QIcon::fromTheme(name);
    if (icon.isNull()) {
        QTextStream(stderr) << "unresolved icon: " << name << '\n';
        return false;
    }
    for (const int size : sizes) {
        for (const QIcon::Mode mode : {QIcon::Normal, QIcon::Selected}) {
            const QPixmap pixmap = icon.pixmap(QSize(size, size), mode, QIcon::Off);
            const QImage image = pixmap.toImage();
            if (pixmap.isNull() || image.isNull() || !hasVisiblePixel(image)) {
                QTextStream(stderr) << "blank icon: " << name << ' ' << size << ' '
                                    << (mode == QIcon::Selected ? "selected" : "normal") << '\n';
                return false;
            }
            if (pixmap.width() > size || pixmap.height() > size) {
                QTextStream(stderr) << "oversized icon: " << name << ' ' << size << ' '
                                    << pixmap.width() << 'x' << pixmap.height() << '\n';
                return false;
            }
        }
    }
    return true;
}

} // namespace

int main(int argc, char **argv)
{
    QGuiApplication app(argc, argv);
    if (argc != 2) {
        qWarning() << "usage: noxforge_icon_resolution_probe REPOSITORY_ROOT";
        return 2;
    }

    const QString repositoryRoot = QString::fromLocal8Bit(argv[1]);
    QStringList searchPaths = QIcon::themeSearchPaths();
    searchPaths.prepend(repositoryRoot + QStringLiteral("/icons"));
    if (!searchPaths.contains(QStringLiteral("/usr/share/icons")))
        searchPaths.append(QStringLiteral("/usr/share/icons"));
    QIcon::setThemeSearchPaths(searchPaths);
    QIcon::setThemeName(QStringLiteral("NoxForge"));

    const QStringList required {
        QStringLiteral("draw-highlight"),
        QStringLiteral("view-hidden"),
        QStringLiteral("tools-report-bug"),
        QStringLiteral("system-suspend"),
        QStringLiteral("system-reboot"),
        QStringLiteral("system-shutdown"),
        QStringLiteral("system-lock-screen"),
        QStringLiteral("system-log-out"),
    };
    const QList<int> sizes {16, 22, 24, 32, 48};
    for (const QString &name : required)
        if (!verifyIcon(name, sizes))
            return 3;

    const QString fallbackProbe = QStringLiteral("document-print");
    if (!verifyIcon(fallbackProbe, sizes))
        return 4;

    QTextStream(stdout) << "Qt icon resolution passed: " << required.size()
                        << " NoxForge core icons, 1 Breeze fallback, "
                        << sizes.size() * 2 << " render states per icon\n";
    return 0;
}
