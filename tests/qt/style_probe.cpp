// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QCommonStyle>
#include <QImage>
#include <QPainter>
#include <QStyle>
#include <QStyleFactory>
#include <QStyleOptionButton>
#include <QStyleOptionComboBox>
#include <QStyleOptionHeader>
#include <QStyleOptionProgressBar>
#include <QStyleOptionSlider>
#include <QStyleOptionSpinBox>
#include <QStyleOptionToolButton>
#include <QTextStream>

namespace {

bool containsColor(const QImage &image, const QColor &expected)
{
    for (int y = 0; y < image.height(); ++y)
        for (int x = 0; x < image.width(); ++x)
            if (const QColor actual = image.pixelColor(x, y);
                qAbs(actual.red() - expected.red()) <= 6
                && qAbs(actual.green() - expected.green()) <= 6
                && qAbs(actual.blue() - expected.blue()) <= 6
                && actual.alpha() > 200)
                return true;
    return false;
}

QImage renderPrimitive(QStyle *style, QStyle::PrimitiveElement element,
                       const QStyleOption &option, qreal scale = 1.0)
{
    QImage image(QSize(qRound(option.rect.width() * scale),
                       qRound(option.rect.height() * scale)),
                 QImage::Format_ARGB32_Premultiplied);
    image.setDevicePixelRatio(scale);
    image.fill(Qt::transparent);
    QPainter painter(&image);
    style->drawPrimitive(element, &option, &painter);
    return image;
}

QImage renderControl(QStyle *style, QStyle::ControlElement element,
                     const QStyleOption &option)
{
    QImage image(option.rect.size(), QImage::Format_ARGB32_Premultiplied);
    image.fill(Qt::transparent);
    QPainter painter(&image);
    style->drawControl(element, &option, &painter);
    return image;
}

} // namespace

int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    if (!QStyleFactory::keys().contains(QStringLiteral("NoxForge"), Qt::CaseInsensitive)) return 1;
    QStyle *style = QStyleFactory::create(QStringLiteral("NoxForge"));
    if (!style
        || QString::fromLatin1(style->metaObject()->className()) != QStringLiteral("NoxForgeStyle"))
        return 2;
    app.setStyle(style);

    QStyleOptionSlider scroll;
    scroll.rect = QRect(0, 0, 200, 10);
    scroll.orientation = Qt::Horizontal;
    scroll.minimum = 0;
    scroll.maximum = 100;
    scroll.pageStep = 20;
    scroll.sliderPosition = 36;
    scroll.subControls = QStyle::SC_ScrollBarGroove | QStyle::SC_ScrollBarSlider;
    if (!style->subControlRect(QStyle::CC_ScrollBar, &scroll,
                               QStyle::SC_ScrollBarAddLine).isEmpty()) return 3;
    const QRect scrollGroove = style->subControlRect(
        QStyle::CC_ScrollBar, &scroll, QStyle::SC_ScrollBarGroove);
    const QRect scrollThumb = style->subControlRect(
        QStyle::CC_ScrollBar, &scroll, QStyle::SC_ScrollBarSlider);
    if (scrollGroove.width() < 190 || scrollThumb.width() < 18) return 4;
    if (style->hitTestComplexControl(QStyle::CC_ScrollBar, &scroll,
                                     scrollThumb.center()) != QStyle::SC_ScrollBarSlider) return 5;
    const QRect scrollSubPage = style->subControlRect(
        QStyle::CC_ScrollBar, &scroll, QStyle::SC_ScrollBarSubPage);
    const QRect scrollAddPage = style->subControlRect(
        QStyle::CC_ScrollBar, &scroll, QStyle::SC_ScrollBarAddPage);
    if (scrollSubPage.isEmpty() || scrollAddPage.isEmpty()) return 21;
    if (style->hitTestComplexControl(QStyle::CC_ScrollBar, &scroll,
                                     scrollSubPage.center()) != QStyle::SC_ScrollBarSubPage) return 22;
    if (style->hitTestComplexControl(QStyle::CC_ScrollBar, &scroll,
                                     scrollAddPage.center()) != QStyle::SC_ScrollBarAddPage) return 23;

    QStyleOptionSlider slider;
    slider.rect = QRect(0, 0, 220, 32);
    slider.orientation = Qt::Horizontal;
    slider.minimum = 0;
    slider.maximum = 100;
    slider.sliderPosition = 50;
    const QRect sliderGroove = style->subControlRect(
        QStyle::CC_Slider, &slider, QStyle::SC_SliderGroove);
    const QRect sliderHandle = style->subControlRect(
        QStyle::CC_Slider, &slider, QStyle::SC_SliderHandle);
    if (sliderGroove.isEmpty() || sliderHandle.size() != QSize(18, 18)) return 6;
    if (style->hitTestComplexControl(QStyle::CC_Slider, &slider,
                                     sliderHandle.center()) != QStyle::SC_SliderHandle) return 7;

    QStyleOption lineEdit;
    lineEdit.rect = QRect(0, 0, 200, 36);
    if (style->subElementRect(QStyle::SE_LineEditContents, &lineEdit)
        != QRect(8, 4, 184, 28)) return 8;

    QStyleOptionComboBox combo;
    combo.rect = QRect(0, 0, 200, 36);
    combo.direction = Qt::LeftToRight;
    const QRect comboLtr = style->subControlRect(
        QStyle::CC_ComboBox, &combo, QStyle::SC_ComboBoxArrow);
    combo.direction = Qt::RightToLeft;
    const QRect comboRtl = style->subControlRect(
        QStyle::CC_ComboBox, &combo, QStyle::SC_ComboBoxArrow);
    if (comboLtr.width() != 30 || comboLtr.right() != combo.rect.right()
        || comboRtl.left() != combo.rect.left()) return 9;
    if (style->hitTestComplexControl(QStyle::CC_ComboBox, &combo,
                                     comboRtl.center()) != QStyle::SC_ComboBoxArrow) return 10;

    QStyleOptionSpinBox spin;
    spin.rect = QRect(0, 0, 160, 36);
    spin.direction = Qt::RightToLeft;
    const QRect spinUp = style->subControlRect(
        QStyle::CC_SpinBox, &spin, QStyle::SC_SpinBoxUp);
    const QRect spinDown = style->subControlRect(
        QStyle::CC_SpinBox, &spin, QStyle::SC_SpinBoxDown);
    if (spinUp.left() != spin.rect.left() || spinDown.top() != spinUp.bottom() + 1) return 11;
    if (style->hitTestComplexControl(QStyle::CC_SpinBox, &spin,
                                     spinDown.center()) != QStyle::SC_SpinBoxDown) return 12;

    QStyleOptionToolButton tool;
    tool.rect = QRect(0, 0, 140, 36);
    tool.direction = Qt::LeftToRight;
    tool.features = QStyleOptionToolButton::MenuButtonPopup;
    const QRect toolMenu = style->subControlRect(
        QStyle::CC_ToolButton, &tool, QStyle::SC_ToolButtonMenu);
    if (toolMenu.width() != 24 || toolMenu.right() != tool.rect.right()) return 13;
    if (style->hitTestComplexControl(QStyle::CC_ToolButton, &tool,
                                     toolMenu.center()) != QStyle::SC_ToolButtonMenu) return 14;

    QStyleOption mixed;
    mixed.rect = QRect(0, 0, 24, 24);
    mixed.state = QStyle::State_Enabled | QStyle::State_NoChange;
    QStyleOption unchecked = mixed;
    unchecked.state = QStyle::State_Enabled | QStyle::State_Off;
    QStyleOption checked = mixed;
    checked.state = QStyle::State_Enabled | QStyle::State_On;
    const QImage mixedImage = renderPrimitive(style, QStyle::PE_IndicatorCheckBox, mixed);
    if (mixedImage == renderPrimitive(style, QStyle::PE_IndicatorCheckBox, unchecked)
        || mixedImage == renderPrimitive(style, QStyle::PE_IndicatorCheckBox, checked)) return 15;

    QStyleOptionHeader ascending;
    ascending.rect = QRect(0, 0, 24, 24);
    ascending.state = QStyle::State_Enabled;
    ascending.sortIndicator = QStyleOptionHeader::SortUp;
    QStyleOptionHeader descending = ascending;
    descending.sortIndicator = QStyleOptionHeader::SortDown;
    if (renderPrimitive(style, QStyle::PE_IndicatorHeaderArrow, ascending)
        == renderPrimitive(style, QStyle::PE_IndicatorHeaderArrow, descending)) return 16;

    QStyleOption close;
    close.rect = QRect(0, 0, 24, 24);
    close.state = QStyle::State_Enabled | QStyle::State_MouseOver;
    if (!containsColor(renderPrimitive(style, QStyle::PE_IndicatorTabClose, close, 2.0),
                       QColor(QStringLiteral("#E8F0F2")))) return 17;

    QStyleOptionProgressBar busy;
    busy.rect = QRect(0, 0, 180, 24);
    busy.state = QStyle::State_Enabled | QStyle::State_Horizontal;
    busy.minimum = 0;
    busy.maximum = 0;
    if (!containsColor(renderControl(style, QStyle::CE_ProgressBarContents, busy),
                       QColor(QStringLiteral("#22D3EE")))) return 18;

    QCommonStyle common;
    if (style->styleHint(QStyle::SH_Widget_Animate)
        != common.styleHint(QStyle::SH_Widget_Animate)) return 19;

    const QString className = QString::fromLatin1(app.style()->metaObject()->className());
    QTextStream(stdout) << "QStyleFactory key: NoxForge\n"
                        << "Loaded style class: " << className << '\n'
                        << "Geometry, hit testing, RTL, states, indicators, busy, and high-DPI probes passed\n";
    return className == QStringLiteral("NoxForgeStyle") ? 0 : 20;
}
