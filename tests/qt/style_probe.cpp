// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QCommonStyle>
#include <QImage>
#include <QPainter>
#include <QSettings>
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
#include <QTemporaryDir>
#include <QtMath>

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

QImage renderComplex(QStyle *style, QStyle::ComplexControl control,
                     const QStyleOptionComplex &option)
{
    QImage image(option.rect.size(), QImage::Format_ARGB32_Premultiplied);
    image.fill(Qt::transparent);
    QPainter painter(&image);
    style->drawComplexControl(control, &option, &painter);
    return image;
}

} // namespace

int main(int argc, char **argv)
{
    QTemporaryDir configRoot;
    if (!configRoot.isValid()) return 25;
    qputenv("XDG_CONFIG_HOME", configRoot.path().toUtf8());
    const QString kdeglobals = configRoot.filePath(QStringLiteral("kdeglobals"));
    {
        QSettings settings(kdeglobals, QSettings::IniFormat);
        settings.setValue(QStringLiteral("KDE/AnimationDurationFactor"), 1.0);
        settings.sync();
    }
    QApplication app(argc, argv);
    if (!QStyleFactory::keys().contains(QStringLiteral("NoxForge"), Qt::CaseInsensitive)) return 1;
    QStyle *style = QStyleFactory::create(QStringLiteral("NoxForge"));
    if (!style
        || QString::fromLatin1(style->metaObject()->className()) != QStringLiteral("NoxForgeStyle"))
        return 2;
    app.setStyle(style);
    QCommonStyle common;

    QStyleOptionSlider scroll;
    const int scrollExtent = style->pixelMetric(QStyle::PM_ScrollBarExtent);
    if (scrollExtent < 16) return 28;
    scroll.rect = QRect(0, 0, 200, scrollExtent);
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
    const QImage scrollImage = renderComplex(style, QStyle::CC_ScrollBar, scroll);
    int visibleTrackRows = 0;
    const QColor background(QStringLiteral("#0D1419"));
    for (int y = 0; y < scrollImage.height(); ++y) {
        bool rowDiffers = false;
        for (int x = 0; x < scrollImage.width(); ++x) {
            if (scrollImage.pixelColor(x, y) != background) {
                rowDiffers = true;
                break;
            }
        }
        visibleTrackRows += rowDiffers ? 1 : 0;
    }
    if (visibleTrackRows < 4 || visibleTrackRows > 8) return 29;

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

    // Measure the top focus stroke in device pixels, including antialiasing.
    // Presence alone would miss the old clipped 1.5px and selected 1px strokes.
    for (const qreal scale : {1.0, 1.25, 1.4, 1.5, 1.75, 2.0}) {
        for (const bool selected : {false, true}) {
            QStyleOption item;
            item.rect = QRect(0, 0, 160, 40);
            item.state = QStyle::State_Enabled | QStyle::State_HasFocus;
            if (selected) item.state |= QStyle::State_Selected;
            for (const auto direction : {Qt::LeftToRight, Qt::RightToLeft}) {
                item.direction = direction;
                const QImage rendered = renderPrimitive(style, QStyle::PE_PanelItemViewItem, item, scale);
                if (!containsColor(rendered, QColor("#A3FF47"))) return 35;
                const QColor fill(selected ? "#223429" : "#0D1419");
                qreal coverage = 0;
                for (int y = 0; y < qCeil(5 * scale); ++y) {
                    const QColor pixel = rendered.pixelColor(rendered.width() / 2, y);
                    coverage += pixel.alphaF() * qBound(0.0,
                        (pixel.greenF() - fill.greenF()) / (1.0 - fill.greenF()), 1.0);
                }
                if (qAbs(coverage / scale - 2.0) > 0.16) return 36;
            }
        }
        QStyleOption input;
        input.rect = QRect(0, 0, 160, 40);
        input.state = QStyle::State_Enabled | QStyle::State_HasFocus;
        const QImage rendered = renderPrimitive(style, QStyle::PE_PanelLineEdit, input, scale);
        qreal coverage = 0;
        for (int y = 0; y < qCeil(4 * scale); ++y) {
            const QColor pixel = rendered.pixelColor(rendered.width() / 2, y);
            coverage += pixel.alphaF() * qBound(0.0,
                (pixel.greenF() - QColor("#0D1419").greenF())
                    / (1.0 - QColor("#0D1419").greenF()), 1.0);
        }
        if (qAbs(coverage / scale - 2.0) > 0.16) return 37;
    }
    QStyleOption overlay;
    overlay.rect = QRect(0, 0, 120, 60);
    for (const auto element : {QStyle::PE_PanelMenu, QStyle::PE_PanelTipLabel}) {
        const QImage rendered = renderPrimitive(style, element, overlay);
        if (rendered.pixelColor(60, 30) != QColor("#22323B")) return 38;
    }
    QStyleOptionButton disabledPrimary;
    disabledPrimary.rect = QRect(0, 0, 160, 40);
    disabledPrimary.features = QStyleOptionButton::DefaultButton;
    const QImage disabledSurface = renderPrimitive(style, QStyle::PE_PanelButtonCommand, disabledPrimary);
    if (disabledSurface.pixelColor(80, 20) != QColor("#141E25")) return 39;

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

    if (style->styleHint(QStyle::SH_Widget_Animate)
        != common.styleHint(QStyle::SH_Widget_Animate)) return 19;
    if (style->styleHint(QStyle::SH_UnderlineShortcut)
        != common.styleHint(QStyle::SH_UnderlineShortcut)) return 30;
    if (style->styleHint(QStyle::SH_MenuBar_AltKeyNavigation)
        != common.styleHint(QStyle::SH_MenuBar_AltKeyNavigation)) return 31;
    {
        QSettings settings(kdeglobals, QSettings::IniFormat);
        settings.setValue(QStringLiteral("KDE/SingleClick"), true);
        settings.sync();
    }
    if (style->styleHint(QStyle::SH_ItemView_ActivateItemOnSingleClick) != 1) return 32;
    {
        QSettings settings(kdeglobals, QSettings::IniFormat);
        settings.setValue(QStringLiteral("KDE/SingleClick"), false);
        settings.sync();
    }
    if (style->styleHint(QStyle::SH_ItemView_ActivateItemOnSingleClick) != 0) return 33;
    {
        QSettings settings(kdeglobals, QSettings::IniFormat);
        settings.remove(QStringLiteral("KDE/SingleClick"));
        settings.sync();
    }
    if (style->styleHint(QStyle::SH_ItemView_ActivateItemOnSingleClick)
        != common.styleHint(QStyle::SH_ItemView_ActivateItemOnSingleClick)) return 34;
    const int animationDuration = style->styleHint(QStyle::SH_Widget_Animation_Duration);
    if (animationDuration != 120) return 24;
    {
        QSettings settings(kdeglobals, QSettings::IniFormat);
        settings.setValue(QStringLiteral("KDE/AnimationDurationFactor"), 0.0);
        settings.sync();
    }
    if (style->styleHint(QStyle::SH_Widget_Animation_Duration) != 0) return 26;
    {
        QSettings settings(kdeglobals, QSettings::IniFormat);
        settings.setValue(QStringLiteral("KDE/AnimationDurationFactor"), 2.0);
        settings.sync();
    }
    if (style->styleHint(QStyle::SH_Widget_Animation_Duration) != 240) return 27;

    QStyleOption branchOpt;
    branchOpt.rect = QRect(0, 0, 20, 20);
    branchOpt.state = QStyle::State_Children | QStyle::State_Open | QStyle::State_Enabled;
    const QImage branchImg = renderPrimitive(style, QStyle::PE_IndicatorBranch, branchOpt);
    if (branchImg.isNull()) return 40;

    QStyleOption tabFrameOpt;
    tabFrameOpt.rect = QRect(0, 0, 100, 100);
    const QImage tabFrameImg = renderPrimitive(style, QStyle::PE_FrameTabWidget, tabFrameOpt);
    if (tabFrameImg.isNull()) return 41;

    QStyleOption dockFrameOpt;
    dockFrameOpt.rect = QRect(0, 0, 100, 100);
    const QImage dockFrameImg = renderPrimitive(style, QStyle::PE_FrameDockWidget, dockFrameOpt);
    if (dockFrameImg.isNull()) return 42;

    QStyleOption statusOpt;
    statusOpt.rect = QRect(0, 0, 200, 24);
    const QImage statusImg = renderPrimitive(style, QStyle::PE_PanelStatusBar, statusOpt);
    if (statusImg.isNull()) return 43;

    QStyleOption splitterOpt;
    splitterOpt.rect = QRect(0, 0, 8, 100);
    splitterOpt.state = QStyle::State_Horizontal;
    const QImage splitterImg = renderControl(style, QStyle::CE_Splitter, splitterOpt);
    if (splitterImg.isNull()) return 44;

    const QString className = QString::fromLatin1(app.style()->metaObject()->className());
    QTextStream(stdout) << "QStyleFactory key: NoxForge\n"
                        << "Loaded style class: " << className << '\n'
                        << "Geometry, hit testing, RTL, states, motion duration, indicators, busy, and high-DPI probes passed\n";
    return className == QStringLiteral("NoxForgeStyle") ? 0 : 20;
}
