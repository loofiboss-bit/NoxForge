// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QStyle>
#include <QStyleFactory>
#include <QTextStream>

int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    if (!QStyleFactory::keys().contains(QStringLiteral("NoxForge"), Qt::CaseInsensitive)) return 1;
    QStyle *style = QStyleFactory::create(QStringLiteral("NoxForge"));
    if (!style || QString::fromLatin1(style->metaObject()->className()) != QStringLiteral("NoxForgeStyle")) return 2;
    app.setStyle(style);
    const QString className = QString::fromLatin1(app.style()->metaObject()->className());
    QTextStream(stdout) << "QStyleFactory key: NoxForge\nLoaded style class: " << className << '\n';
    return className == QStringLiteral("NoxForgeStyle") ? 0 : 3;
}
