// SPDX-License-Identifier: MIT
#include <QAccessibilityHints>
#include <QApplication>
#include <QFont>
#include <QGuiApplication>
#include <QJsonDocument>
#include <QJsonObject>
#include <QStyle>
#include <QStyleHints>
#include <QTextStream>

int main(int argc, char **argv)
{
    QApplication application(argc, argv);
    const QAccessibilityHints *accessibility =
        QGuiApplication::styleHints()->accessibility();
    if (!accessibility)
        return 1;

    const Qt::ContrastPreference preference = accessibility->contrastPreference();
    QString preferenceName;
    switch (preference) {
    case Qt::ContrastPreference::NoPreference:
        preferenceName = QStringLiteral("NoPreference");
        break;
    case Qt::ContrastPreference::HighContrast:
        preferenceName = QStringLiteral("HighContrast");
        break;
    default:
        return 2;
    }

    if (!application.style()
        || application.style()->objectName().compare(
               QStringLiteral("NoxForge"), Qt::CaseInsensitive)
            != 0) {
        return 3;
    }

    const QJsonObject report{
        {QStringLiteral("contrastPreference"), preferenceName},
        {QStringLiteral("highContrastExposed"),
         preference == Qt::ContrastPreference::HighContrast},
        {QStringLiteral("platform"), QGuiApplication::platformName()},
        {QStringLiteral("style"), application.style()->objectName()},
        {QStringLiteral("systemFont"), application.font().family()},
        {QStringLiteral("tabFocusBehavior"),
         static_cast<int>(QGuiApplication::styleHints()->tabFocusBehavior())},
    };
    QTextStream(stdout)
        << QJsonDocument(report).toJson(QJsonDocument::Compact) << '\n';
    return 0;
}
