// SPDX-License-Identifier: MIT
#pragma once

#include "noxforgemotion.h"

#include <QColor>
#include <QCommonStyle>
#include <QDateTime>
#include <QFileSystemWatcher>
#include <QString>

class NoxForgeStyle final : public QCommonStyle
{
    Q_OBJECT

public:
    explicit NoxForgeStyle();
    ~NoxForgeStyle() override;

    QPalette standardPalette() const override;
    void polish(QPalette &palette) override;
    void polish(QWidget *widget) override;
    void unpolish(QWidget *widget) override;
    int pixelMetric(PixelMetric metric, const QStyleOption *option = nullptr,
                    const QWidget *widget = nullptr) const override;
    int styleHint(StyleHint hint, const QStyleOption *option = nullptr,
                  const QWidget *widget = nullptr,
                  QStyleHintReturn *returnData = nullptr) const override;
    QSize sizeFromContents(ContentsType type, const QStyleOption *option,
                           const QSize &contentsSize,
                           const QWidget *widget = nullptr) const override;
    QRect subControlRect(ComplexControl control, const QStyleOptionComplex *option,
                         SubControl subControl,
                         const QWidget *widget = nullptr) const override;
    SubControl hitTestComplexControl(ComplexControl control,
                                     const QStyleOptionComplex *option,
                                     const QPoint &position,
                                     const QWidget *widget = nullptr) const override;
    QRect subElementRect(SubElement element, const QStyleOption *option,
                         const QWidget *widget = nullptr) const override;
    void drawPrimitive(PrimitiveElement element, const QStyleOption *option,
                       QPainter *painter, const QWidget *widget = nullptr) const override;
    void drawControl(ControlElement element, const QStyleOption *option,
                     QPainter *painter, const QWidget *widget = nullptr) const override;
    void drawComplexControl(ComplexControl control, const QStyleOptionComplex *option,
                            QPainter *painter, const QWidget *widget = nullptr) const override;

protected:
    bool eventFilter(QObject *watched, QEvent *event) override;

private:
    void refreshConfigCache() const;
    bool isObsidianConfig() const;
    bool isObsidianMode(const QStyleOption *option = nullptr,
                        const QWidget *widget = nullptr) const;
    QColor activeAccent(const QStyleOption *option = nullptr) const;
    qreal motionValue(const QWidget *widget, NoxForgeMotion::Channel channel,
                      bool target) const;
    qreal motionScale(const QWidget *widget = nullptr) const;

    NoxForgeMotion m_motion;
    mutable QFileSystemWatcher m_configWatcher;
    mutable bool m_configDirty = true;
    mutable QString m_cachedConfigPath;
    mutable QDateTime m_cachedConfigMtime;
    mutable QDateTime m_cachedConfigCtime;
    mutable qint64 m_cachedConfigSize = -1;
    mutable QString m_cachedScheme;
    mutable QColor m_cachedAccent;
};
