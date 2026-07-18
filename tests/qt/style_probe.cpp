// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QStyle>
#include <QStyleFactory>
#include <QStyleOptionSlider>
#include <QTextStream>

int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    if (!QStyleFactory::keys().contains(QStringLiteral("NoxForge"), Qt::CaseInsensitive)) return 1;
    QStyle *style = QStyleFactory::create(QStringLiteral("NoxForge"));
    if (!style || QString::fromLatin1(style->metaObject()->className()) != QStringLiteral("NoxForgeStyle")) return 2;
    app.setStyle(style);
    QStyleOptionSlider scroll;
    scroll.rect = QRect(0, 0, 200, 10);
    scroll.orientation = Qt::Horizontal;
    scroll.minimum = 0;
    scroll.maximum = 100;
    scroll.pageStep = 20;
    scroll.sliderPosition = 36;
    scroll.subControls = QStyle::SC_ScrollBarGroove | QStyle::SC_ScrollBarSlider;
    if (!style->subControlRect(QStyle::CC_ScrollBar, &scroll, QStyle::SC_ScrollBarAddLine).isEmpty()) return 3;
    if (style->subControlRect(QStyle::CC_ScrollBar, &scroll, QStyle::SC_ScrollBarGroove).width() < 190) return 4;
    if (style->subControlRect(QStyle::CC_ScrollBar, &scroll, QStyle::SC_ScrollBarSlider).width() < 18) return 5;
    QStyleOptionSlider slider;
    slider.rect = QRect(0, 0, 220, 32);
    slider.orientation = Qt::Horizontal;
    slider.minimum = 0;
    slider.maximum = 100;
    slider.sliderPosition = 50;
    const QRect sliderGroove = style->subControlRect(QStyle::CC_Slider, &slider, QStyle::SC_SliderGroove);
    const QRect sliderHandle = style->subControlRect(QStyle::CC_Slider, &slider, QStyle::SC_SliderHandle);
    if (sliderGroove.isEmpty() || sliderHandle.size() != QSize(18, 18)) return 6;
    QStyleOption lineEdit;
    lineEdit.rect = QRect(0, 0, 200, 36);
    if (style->subElementRect(QStyle::SE_LineEditContents, &lineEdit) != QRect(8, 4, 184, 28)) return 7;
    const QString className = QString::fromLatin1(app.style()->metaObject()->className());
    QTextStream(stdout) << "QStyleFactory key: NoxForge\nLoaded style class: " << className << '\n';
    return className == QStringLiteral("NoxForgeStyle") ? 0 : 8;
}
