// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QCommonStyle>
#include <QFrame>
#include <QImage>
#include <QPainter>
#include <QSettings>
#include <QStyle>
#include <QStyleFactory>
#include <QStyleOptionButton>
#include <QStyleOptionComboBox>
#include <QStyleOptionDockWidget>
#include <QStyleOptionFrame>
#include <QStyleOptionHeader>
#include <QStyleOptionProgressBar>
#include <QStyleOptionSlider>
#include <QStyleOptionSpinBox>
#include <QStyleOptionTitleBar>
#include <QStyleOptionToolButton>
#include <QStyleOptionViewItem>
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

qreal measureTopEdgeCoverage(const QImage &rendered, const QColor &fill, int rows)
{
    qreal coverage = 0;
    for (int y = 0; y < rows; ++y) {
        const QColor pixel = rendered.pixelColor(rendered.width() / 2, y);
        coverage += pixel.alphaF() * qBound(0.0,
            (pixel.greenF() - fill.greenF()) / (1.0 - fill.greenF()), 1.0);
    }
    return coverage;
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
                const qreal coverage = measureTopEdgeCoverage(rendered, fill, qCeil(5 * scale));
                if (qAbs(coverage / scale - 2.0) > 0.16) return 36;
            }
        }
        QStyleOption input;
        input.rect = QRect(0, 0, 160, 40);
        input.state = QStyle::State_Enabled | QStyle::State_HasFocus;
        const QImage rendered = renderPrimitive(style, QStyle::PE_PanelLineEdit, input, scale);
        const qreal coverage = measureTopEdgeCoverage(rendered, QColor("#0D1419"), qCeil(4 * scale));
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
    if (className != QStringLiteral("NoxForgeStyle")) return 20;

    // Verify standard palette colors
    const QPalette stdPal = style->standardPalette();
    if (stdPal.color(QPalette::Base).name().toLower() != QStringLiteral("#0d1419")) return 45;
    if (stdPal.color(QPalette::Window).name().toLower() != QStringLiteral("#141e25")) return 46;

    // Verify dynamic obsidian palette switching via environment or option
    qputenv("NOXFORGE_VARIANT", "obsidian");
    QPalette obsPal;
    style->polish(obsPal);
    if (obsPal.color(QPalette::Base).name().toLower() != QStringLiteral("#000000")) return 47;
    if (obsPal.color(QPalette::Window).name().toLower() != QStringLiteral("#0a0f13")) return 48;

    QStyleOption lineEditOpt;
    lineEditOpt.rect = QRect(0, 0, 100, 32);
    lineEditOpt.palette = obsPal;
    const QImage lineEditImg = renderPrimitive(style, QStyle::PE_PanelLineEdit, lineEditOpt);
    if (!containsColor(lineEditImg, QColor(0, 0, 0))) return 49;
    // Verify menu item sizing contract (prevents text clipping in QMenu)
    {
        QStyleOptionMenuItem menuItemOpt;
        menuItemOpt.text = QStringLiteral("Öppna i nytt fönster\tCtrl+N");
        menuItemOpt.maxIconWidth = 16;
        menuItemOpt.fontMetrics = QFontMetrics(app.font());
        const QSize itemSize = style->sizeFromContents(
            QStyle::CT_MenuItem, &menuItemOpt, menuItemOpt.fontMetrics.size(0, menuItemOpt.text));
        const int fontAdv = menuItemOpt.fontMetrics.horizontalAdvance(QStringLiteral("Öppna i nytt fönster"))
                          + menuItemOpt.fontMetrics.horizontalAdvance(QStringLiteral("Ctrl+N"));
        if (itemSize.height() < 30 || itemSize.width() < fontAdv + 40) return 50;

        // Tray / iconless menu item check
        QStyleOptionMenuItem trayOpt;
        trayOpt.text = QStringLiteral("Open Antigravity");
        trayOpt.maxIconWidth = 0;
        trayOpt.fontMetrics = QFontMetrics(app.font());
        const QSize traySize = style->sizeFromContents(
            QStyle::CT_MenuItem, &trayOpt, trayOpt.fontMetrics.size(0, trayOpt.text));
        const int trayAdv = trayOpt.fontMetrics.horizontalAdvance(QStringLiteral("Open Antigravity"));
        if (traySize.height() < 30 || traySize.width() < trayAdv + 24) return 51;
    }
    qunsetenv("NOXFORGE_VARIANT");

    // V21: verify 6 signature accents including crimson (#FF8FA3) and ice (#93C5FD)
    for (const auto &entry : QList<QPair<QByteArray, QString>>{
             {"lime", QStringLiteral("#a3ff47")},
             {"cyan", QStringLiteral("#22d3ee")},
             {"violet", QStringLiteral("#a78bfa")},
             {"amber", QStringLiteral("#fbbf24")},
             {"crimson", QStringLiteral("#ff8fa3")},
             {"ice", QStringLiteral("#93c5fd")},
         }) {
        qputenv("NOXFORGE_ACCENT", entry.first);
        QPalette accentPal;
        style->polish(accentPal);
        if (accentPal.color(QPalette::Accent).name().toLower() != entry.second) return 52;
    }
    qunsetenv("NOXFORGE_ACCENT");

    // V21: verify newly implemented Qt6 primitives, controls, and complex controls
    {
        QStyleOptionSlider dialOpt;
        dialOpt.rect = QRect(0, 0, 64, 64);
        dialOpt.state = QStyle::State_Enabled | QStyle::State_HasFocus;
        dialOpt.minimum = 0;
        dialOpt.maximum = 100;
        dialOpt.sliderPosition = 65;
        dialOpt.subControls = QStyle::SC_DialGroove | QStyle::SC_DialHandle | QStyle::SC_DialTickmarks;
        const QImage dialImg = renderComplex(style, QStyle::CC_Dial, dialOpt);
        if (!containsColor(dialImg, QColor(QStringLiteral("#A3FF47")))) return 53;

        QStyleOptionSlider tickSlider = slider;
        tickSlider.state = QStyle::State_Enabled;
        tickSlider.tickPosition = QSlider::TicksBothSides;
        tickSlider.tickInterval = 25;
        const QImage tickImg = renderComplex(style, QStyle::CC_Slider, tickSlider);
        if (!containsColor(tickImg, QColor(QStringLiteral("#A3FF47")))) return 54;

        QStyleOptionSpinBox spinActive = spin;
        spinActive.direction = Qt::LeftToRight;
        spinActive.state = QStyle::State_Enabled | QStyle::State_MouseOver | QStyle::State_Sunken;
        spinActive.activeSubControls = QStyle::SC_SpinBoxUp;
        spinActive.stepEnabled = QAbstractSpinBox::StepUpEnabled | QAbstractSpinBox::StepDownEnabled;
        const QImage spinImg = renderComplex(style, QStyle::CC_SpinBox, spinActive);
        if (!containsColor(spinImg, QColor(QStringLiteral("#A3FF47")))) return 55;

        QStyleOptionComplex mdiOpt;
        mdiOpt.rect = QRect(0, 0, 72, 24);
        mdiOpt.state = QStyle::State_Enabled | QStyle::State_MouseOver;
        mdiOpt.subControls = QStyle::SC_MdiMinButton | QStyle::SC_MdiNormalButton | QStyle::SC_MdiCloseButton;
        mdiOpt.activeSubControls = QStyle::SC_MdiCloseButton;
        const QImage mdiImg = renderComplex(style, QStyle::CC_MdiControls, mdiOpt);
        if (!containsColor(mdiImg, QColor(QStringLiteral("#FF6B7A")))) return 56;

        QStyleOptionTitleBar tbOpt;
        tbOpt.rect = QRect(0, 0, 240, 28);
        tbOpt.state = QStyle::State_Enabled;
        tbOpt.titleBarState = Qt::WindowActive;
        tbOpt.text = QStringLiteral("NoxForge");
        tbOpt.subControls = QStyle::SC_TitleBarLabel | QStyle::SC_TitleBarMinButton
                          | QStyle::SC_TitleBarMaxButton | QStyle::SC_TitleBarCloseButton;
        const QImage tbImg = renderComplex(style, QStyle::CC_TitleBar, tbOpt);
        if (!containsColor(tbImg, QColor(QStringLiteral("#A3FF47")))) return 57;

        QStyleOptionDockWidget dockOpt;
        dockOpt.rect = QRect(0, 0, 200, 26);
        dockOpt.state = QStyle::State_Enabled;
        dockOpt.title = QStringLiteral("Inspector");
        const QImage dockImg = renderControl(style, QStyle::CE_DockWidgetTitle, dockOpt);
        if (!containsColor(dockImg, QColor(QStringLiteral("#A3FF47")))) return 58;

        QStyleOption rubberOpt;
        rubberOpt.rect = QRect(0, 0, 80, 48);
        rubberOpt.state = QStyle::State_Enabled;
        const QImage rubberImg = renderControl(style, QStyle::CE_RubberBand, rubberOpt);
        if (!containsColor(rubberImg, QColor(QStringLiteral("#A3FF47")))) return 59;

        QStyleOptionFrame frameOpt;
        frameOpt.rect = QRect(0, 0, 120, 4);
        frameOpt.frameShape = QFrame::HLine;
        const QImage frameImg = renderControl(style, QStyle::CE_ShapedFrame, frameOpt);
        if (frameImg.isNull()) return 60;

        QStyleOption gripOpt;
        gripOpt.rect = QRect(0, 0, 18, 18);
        gripOpt.state = QStyle::State_Enabled;
        const QImage gripImg = renderControl(style, QStyle::CE_SizeGrip, gripOpt);
        if (gripImg.isNull()) return 61;

        QStyleOptionViewItem rowOpt;
        rowOpt.rect = QRect(0, 0, 160, 28);
        rowOpt.state = QStyle::State_Enabled | QStyle::State_Selected;
        const QImage rowImg = renderPrimitive(style, QStyle::PE_PanelItemViewRow, rowOpt);
        if (!containsColor(rowImg, QColor(QStringLiteral("#A3FF47")))) return 62;

        QStyleOption tbHandleOpt;
        tbHandleOpt.rect = QRect(0, 0, 12, 28);
        tbHandleOpt.state = QStyle::State_Enabled | QStyle::State_Horizontal;
        if (renderPrimitive(style, QStyle::PE_IndicatorToolBarHandle, tbHandleOpt).isNull()) return 63;
        if (renderPrimitive(style, QStyle::PE_IndicatorToolBarSeparator, tbHandleOpt).isNull()) return 64;
        if (renderPrimitive(style, QStyle::PE_PanelScrollAreaCorner, tbHandleOpt).isNull()) return 65;
        if (renderPrimitive(style, QStyle::PE_FrameTabBarBase, tbHandleOpt).isNull()) return 66;

        // V21.0.2: verify dock resize handle has crisp 1px metric & no clipped floating lime dot
        if (style->pixelMetric(QStyle::PM_DockWidgetSeparatorExtent) != 1) return 67;
        if (style->pixelMetric(QStyle::PM_SplitterWidth) != 4) return 68;
        QStyleOption dockSepVert;
        dockSepVert.rect = QRect(0, 0, 6, 120);
        dockSepVert.state = QStyle::State_Enabled | QStyle::State_MouseOver;
        const QImage dockSepVertImg = renderPrimitive(style, QStyle::PE_IndicatorDockWidgetResizeHandle, dockSepVert);
        if (containsColor(dockSepVertImg, QColor(QStringLiteral("#A3FF47")))) return 69;
        if (!containsColor(dockSepVertImg, QColor(QStringLiteral("#4B606A")))) return 70;
        QStyleOption dockSepHoriz;
        dockSepHoriz.rect = QRect(0, 0, 120, 6);
        dockSepHoriz.state = QStyle::State_Enabled | QStyle::State_Horizontal;
        const QImage dockSepHorizImg = renderPrimitive(style, QStyle::PE_IndicatorDockWidgetResizeHandle, dockSepHoriz);
        if (!containsColor(dockSepHorizImg, QColor(QStringLiteral("#2F414B")))) return 71;

        // Audit regressions: dark HighlightedText (NoxForgeDark.colors / KDE AccentColor) must never
        // be painted onto dark #223429 selection fills.
        auto relLum = [](const QColor &c) -> qreal {
            auto lin = [](qreal v) -> qreal {
                return v <= 0.04045 ? v / 12.92 : std::pow((v + 0.055) / 1.055, 2.4);
            };
            return 0.2126 * lin(c.redF()) + 0.7152 * lin(c.greenF()) + 0.0722 * lin(c.blueF());
        };
        auto wcagContrast = [&](const QColor &a, const QColor &b) -> qreal {
            const qreal la = relLum(a), lb = relLum(b);
            return (qMax(la, lb) + 0.05) / (qMin(la, lb) + 0.05);
        };
        {
            QPalette kdePal = style->standardPalette();
            kdePal.setColor(QPalette::Highlight, QColor(118, 184, 57));
            kdePal.setColor(QPalette::HighlightedText, QColor(13, 20, 25));

            QStyleOptionViewItem selItem;
            selItem.rect = QRect(0, 0, 180, 32);
            selItem.state = QStyle::State_Enabled | QStyle::State_Active | QStyle::State_Selected;
            selItem.palette = kdePal;
            const QImage selItemImg = renderPrimitive(style, QStyle::PE_PanelItemViewItem, selItem);
            if (wcagContrast(selItemImg.pixelColor(90, 16), QColor(13, 20, 25)) < 7.0) return 72;

            const QImage selRowImg = renderPrimitive(style, QStyle::PE_PanelItemViewRow, selItem);
            if (wcagContrast(selRowImg.pixelColor(90, 16), QColor(13, 20, 25)) < 7.0) return 73;
        }

        // SpinBox & ComboBox width breathing room prevents clipping ("100 %")
        {
            QStyleOptionSpinBox spinSizeOpt;
            const QSize spinSize = style->sizeFromContents(QStyle::CT_SpinBox, &spinSizeOpt, QSize(52, 22));
            if (spinSize.width() < 52 + 40) return 74;

            QStyleOptionComboBox comboSizeOpt;
            const QSize comboSize = style->sizeFromContents(QStyle::CT_ComboBox, &comboSizeOpt, QSize(80, 22));
            if (comboSize.width() < 80 + 44) return 75;
        }

        // Checkable button (State_On) must render distinct accent indicator (e.g. Display Orientation buttons)
        {
            QStyleOptionButton uncheckedBtn;
            uncheckedBtn.rect = QRect(0, 0, 80, 36);
            uncheckedBtn.state = QStyle::State_Enabled | QStyle::State_Raised | QStyle::State_Off;
            QStyleOptionButton checkedBtn = uncheckedBtn;
            checkedBtn.state = QStyle::State_Enabled | QStyle::State_On;
            const QImage uncheckedImg = renderPrimitive(style, QStyle::PE_PanelButtonCommand, uncheckedBtn);
            const QImage checkedImg = renderPrimitive(style, QStyle::PE_PanelButtonCommand, checkedBtn);
            if (uncheckedImg == checkedImg || !containsColor(checkedImg, QColor(QStringLiteral("#A3FF47")))) return 76;
        }

        // Frameless inner QLineEdit (lineWidth == 0, inside QSpinBox/QComboBox) must not draw a nested border
        {
            QStyleOptionFrame innerEdit;
            innerEdit.rect = QRect(0, 0, 100, 28);
            innerEdit.state = QStyle::State_Enabled;
            innerEdit.lineWidth = 0;
            const QImage innerImg = renderPrimitive(style, QStyle::PE_PanelLineEdit, innerEdit);
            if (innerImg.pixelColor(50, 0) != innerImg.pixelColor(50, 14)) return 77;
        }

        // QSettings::IniFormat comma-separated AccentColor (QStringList) parsing regression
        {
            QSettings settings(kdeglobals, QSettings::IniFormat);
            settings.setValue(QStringLiteral("General/AccentColor"), QStringLiteral("34,211,238"));
            settings.sync();
            QStyle *freshStyle = QStyleFactory::create(QStringLiteral("NoxForge"));
            if (!freshStyle) return 78;
            QPalette freshPal;
            freshStyle->polish(freshPal);
            const QString resolvedAccent = freshPal.color(QPalette::Accent).name().toLower();
            delete freshStyle;
            if (resolvedAccent != QStringLiteral("#22d3ee")) return 78;
        }
    }

    QTextStream(stdout) << "QStyleFactory key: NoxForge\n"
                        << "Loaded style class: " << className << '\n'
                        << "Geometry, hit testing, RTL, states, motion duration, indicators, busy, high-DPI, dual-palette Obsidian, 6-accent, and V21 full Qt6 control probes passed\n";
    return 0;
}
