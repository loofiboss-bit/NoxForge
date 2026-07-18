// SPDX-License-Identifier: MIT
#include "noxforgestyle.h"

#include <QStylePlugin>

class NoxForgeStylePlugin final : public QStylePlugin
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "org.qt-project.Qt.QStyleFactoryInterface" FILE "noxforgestyleplugin.json")

public:
    QStyle *create(const QString &key) override
    {
        return key.compare(QStringLiteral("NoxForge"), Qt::CaseInsensitive) == 0
            ? new NoxForgeStyle
            : nullptr;
    }
};

#include "noxforgestyleplugin.moc"
