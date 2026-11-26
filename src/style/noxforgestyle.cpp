// SPDX-License-Identifier: MIT
#include "noxforgestyle.h"

#include "noxforgepalette.h"

#include <algorithm>
#include <cmath>
#include <QAbstractItemView>
#include <QApplication>
#include <QDateTime>
#include <QDir>
#include <QEvent>
#include <QFileInfo>
#include <QFrame>
#include <QList>
#include <QPainter>
#include <QPainterPath>
#include <QSettings>
#include <QStandardPaths>
#include <QStyleHints>
#include <QStyleOption>
#include <QStyleOptionButton>
#include <QStyleOptionComboBox>
#include <QStyleOptionDockWidget>
#include <QStyleOptionFrame>
#include <QStyleOptionGroupBox>
#include <QStyleOptionHeader>
#include <QStyleOptionMenuItem>
#include <QStyleOptionProgressBar>
#include <QStyleOptionRubberBand>
#include <QStyleOptionSizeGrip>
#include <QStyleOptionSlider>
#include <QStyleOptionSpinBox>
#include <QStyleOptionTab>
#include <QStyleOptionTitleBar>
#include <QStyleOptionToolButton>
#include <QStyleOptionViewItem>
#include <QTabBar>
#include <QWidget>

namespace NP = NoxForgePalette;

namespace {

QColor mixedColor(const QColor &from, const QColor &to, qreal progress)
{
    const qreal bounded = qBound(0.0, progress, 1.0);
    return QColor::fromRgbF(
        from.redF() + (to.redF() - from.redF()) * bounded,
        from.greenF() + (to.greenF() - from.greenF()) * bounded,
        from.blueF() + (to.blueF() - from.blueF()) * bounded,
        from.alphaF() + (to.alphaF() - from.alphaF()) * bounded
    );
}

QColor activeAccentPressed(const QColor &accent)
{
    return NP::accentPressedForAccent(accent);
}

QColor activeSurfaceSelected(const QColor &accent, bool obsidian = false)
{
    return NP::surfaceSelectedForAccent(accent, obsidian);
}

QColor activeAccentSoft(const QColor &accent, bool obsidian = false)
{
    return NP::accentSoftForAccent(accent, obsidian);
}

QPainterPath surfacePath(const QRectF &rect, bool notched, qreal radius = NP::radius)
{
    const qreal left = rect.left();
    const qreal top = rect.top();
    const qreal right = rect.right();
    const qreal bottom = rect.bottom();
    QPainterPath path;
    path.moveTo(left + (notched ? NP::notch : radius), top);
    path.lineTo(right - radius, top);
    path.quadTo(right, top, right, top + radius);
    path.lineTo(right, bottom - radius);
    path.quadTo(right, bottom, right - radius, bottom);
    path.lineTo(left + radius, bottom);
    path.quadTo(left, bottom, left, bottom - radius);
    path.lineTo(left, top + (notched ? NP::notch : radius));
    if (!notched) {
        path.quadTo(left, top, left + radius, top);
    }
    path.closeSubpath();
    return path;
}

bool enabled(const QStyleOption *option)
{
    return option->state.testFlag(QStyle::State_Enabled);
}

QColor stateSurface(const QStyleOption *option, qreal hover, qreal press, bool obsidian = false)
{
    if (!enabled(option)) {
        return NP::surface(obsidian);
    }
    const QColor hovered = mixedColor(NP::surfaceRaised(obsidian), NP::surfaceHover(obsidian), hover);
    return mixedColor(hovered, NP::surfaceSunken(obsidian), press);
}

void paintSurface(QPainter *painter, const QRect &rect, const QColor &fill,
                  const QColor &stroke, int width = NP::borderWidth, bool notched = false)
{
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing);
    painter->setPen(width > 0 ? QPen(stroke, width) : QPen(Qt::NoPen));
    painter->setBrush(fill);
    const qreal inset = width / 2.0;
    painter->drawPath(surfacePath(QRectF(rect).adjusted(inset, inset, -inset, -inset), notched));
    painter->restore();
}

void paintSelectedSurface(QPainter *painter, const QRect &rect, Qt::LayoutDirection direction,
                          bool focused = false, bool obsidian = false, const QColor &accent = NP::accent())
{
    paintSurface(painter, rect, activeSurfaceSelected(accent, obsidian),
                 focused ? accent : NP::borderStrong(),
                 focused ? NP::focusWidth : NP::borderWidth, true);
    painter->save();
    painter->setPen(Qt::NoPen);
    painter->setBrush(accent);
    const int markerX = direction == Qt::RightToLeft
        ? rect.right() - NP::activeMarkerWidth + 1 : rect.left();
    painter->drawRect(markerX, rect.top() + NP::compactRadius,
                      NP::activeMarkerWidth, qMax(1, rect.height() - 2 * NP::compactRadius));
    painter->restore();
}

void paintArrow(QPainter *painter, const QRect &rect, Qt::ArrowType arrow, const QColor &color)
{
    const QPoint center = rect.center();
    QPolygon points;
    if (arrow == Qt::DownArrow) points << QPoint(center.x() - 4, center.y() - 2) << QPoint(center.x(), center.y() + 2) << QPoint(center.x() + 4, center.y() - 2);
    if (arrow == Qt::UpArrow) points << QPoint(center.x() - 4, center.y() + 2) << QPoint(center.x(), center.y() - 2) << QPoint(center.x() + 4, center.y() + 2);
    if (arrow == Qt::LeftArrow) points << QPoint(center.x() + 2, center.y() - 4) << QPoint(center.x() - 2, center.y()) << QPoint(center.x() + 2, center.y() + 4);
    if (arrow == Qt::RightArrow) points << QPoint(center.x() - 2, center.y() - 4) << QPoint(center.x() + 2, center.y()) << QPoint(center.x() - 2, center.y() + 4);
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing);
    painter->setPen(QPen(color, 2, Qt::SolidLine, Qt::SquareCap, Qt::MiterJoin));
    painter->setBrush(Qt::NoBrush);
    painter->drawPolyline(points);
    painter->restore();
}

void paintCloseIndicator(QPainter *painter, const QRect &rect, const QColor &color)
{
    const int extent = qMax(6, qMin(rect.width(), rect.height()) / 3);
    const QPoint center = rect.center();
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing);
    painter->setPen(QPen(color, 2, Qt::SolidLine, Qt::SquareCap, Qt::MiterJoin));
    painter->drawLine(center + QPoint(-extent, -extent), center + QPoint(extent, extent));
    painter->drawLine(center + QPoint(extent, -extent), center + QPoint(-extent, extent));
    painter->restore();
}

template<typename Option>
void drawLabelWithPalette(const QCommonStyle *style, QStyle::ControlElement element,
                          const Option &option, QPainter *painter,
                          const QWidget *widget, QPalette::ColorRole role,
                          bool obsidian)
{
    Option copy = option;
    const QColor text = enabled(&option) ? NP::textPrimary(obsidian) : NP::textDisabled(obsidian);
    copy.palette.setColor(QPalette::Active, role, text);
    copy.palette.setColor(QPalette::Inactive, role, text);
    copy.palette.setColor(QPalette::Disabled, role, NP::textDisabled(obsidian));
    style->QCommonStyle::drawControl(element, &copy, painter, widget);
}

void paintTitleButtonGlyph(QPainter *painter, const QRect &rect,
                           QStyle::SubControl sub, const QColor &color)
{
    const QPoint c = rect.center();
    const int r = qMax(3, qMin(rect.width(), rect.height()) / 4);
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing);
    painter->setPen(QPen(color, 1.5, Qt::SolidLine, Qt::SquareCap, Qt::MiterJoin));
    painter->setBrush(Qt::NoBrush);
    if (sub == QStyle::SC_TitleBarCloseButton || sub == QStyle::SC_MdiCloseButton) {
        painter->drawLine(c + QPoint(-r, -r), c + QPoint(r, r));
        painter->drawLine(c + QPoint(r, -r), c + QPoint(-r, r));
    } else if (sub == QStyle::SC_TitleBarMinButton || sub == QStyle::SC_MdiMinButton) {
        painter->drawLine(c + QPoint(-r, r / 2), c + QPoint(r, r / 2));
    } else if (sub == QStyle::SC_TitleBarMaxButton) {
        painter->drawRect(QRect(c.x() - r, c.y() - r, r * 2, r * 2));
    } else if (sub == QStyle::SC_TitleBarNormalButton || sub == QStyle::SC_MdiNormalButton) {
        painter->drawRect(QRect(c.x() - r, c.y() - r + 2, r * 2 - 2, r * 2 - 2));
        painter->drawLine(c.x() - r + 2, c.y() - r, c.x() + r, c.y() - r);
        painter->drawLine(c.x() + r, c.y() - r, c.x() + r, c.y() + r - 2);
    } else if (sub == QStyle::SC_TitleBarShadeButton) {
        paintArrow(painter, rect, Qt::UpArrow, color);
    } else if (sub == QStyle::SC_TitleBarUnshadeButton) {
        paintArrow(painter, rect, Qt::DownArrow, color);
    }
    painter->restore();
}

} // namespace

NoxForgeStyle::NoxForgeStyle()
    : m_motion(this)
    , m_configWatcher(this)
{
    setObjectName(QStringLiteral("NoxForge"));
    connect(&m_configWatcher, &QFileSystemWatcher::fileChanged, this, [this]() {
        m_configDirty = true;
    });
    connect(&m_configWatcher, &QFileSystemWatcher::directoryChanged, this, [this]() {
        m_configDirty = true;
    });
    if (qApp) {
        qApp->installEventFilter(this);
    }
}

NoxForgeStyle::~NoxForgeStyle()
{
    if (qApp) {
        qApp->removeEventFilter(this);
    }
}

bool NoxForgeStyle::eventFilter(QObject *watched, QEvent *event)
{
    if (watched == qApp && event && event->type() == QEvent::ApplicationPaletteChange) {
        m_configDirty = true;
    }
    return QCommonStyle::eventFilter(watched, event);
}

void NoxForgeStyle::refreshConfigCache() const
{
    const QString path = QStandardPaths::locate(
        QStandardPaths::GenericConfigLocation, QStringLiteral("kdeglobals"));
    const QFileInfo info(path);
    const bool exists = !path.isEmpty() && info.exists();
    const QDateTime mtime = exists ? info.lastModified() : QDateTime();
    const QDateTime ctime = exists ? info.metadataChangeTime() : QDateTime();
    const qint64 sz = exists ? info.size() : -1;

    if (!m_configDirty
        && path == m_cachedConfigPath
        && mtime == m_cachedConfigMtime
        && ctime == m_cachedConfigCtime
        && sz == m_cachedConfigSize) {
        return;
    }

    if (path != m_cachedConfigPath) {
        if (!m_configWatcher.files().isEmpty()) {
            m_configWatcher.removePaths(m_configWatcher.files());
        }
        if (!m_configWatcher.directories().isEmpty()) {
            m_configWatcher.removePaths(m_configWatcher.directories());
        }
        if (exists) {
            m_configWatcher.addPath(path);
            const QString parentDir = info.absolutePath();
            if (!parentDir.isEmpty() && QDir(parentDir).exists()) {
                m_configWatcher.addPath(parentDir);
            }
        }
    } else if (exists && !m_configWatcher.files().contains(path)) {
        m_configWatcher.addPath(path);
    }

    m_cachedConfigPath = path;
    m_cachedConfigMtime = mtime;
    m_cachedConfigCtime = ctime;
    m_cachedConfigSize = sz;
    m_configDirty = false;
    m_cachedScheme.clear();
    m_cachedAccent = QColor();

    if (!exists) {
        return;
    }

    QSettings settings(path, QSettings::IniFormat);
    settings.beginGroup(QStringLiteral("General"));
    m_cachedScheme = settings.value(QStringLiteral("ColorScheme")).toString();
    const QString accentStr = settings.value(QStringLiteral("AccentColor")).toString();
    if (!accentStr.isEmpty()) {
        const auto parts = accentStr.split(QLatin1Char(','));
        if (parts.size() >= 3) {
            bool okR = false, okG = false, okB = false;
            const int r = parts[0].trimmed().toInt(&okR);
            const int g = parts[1].trimmed().toInt(&okG);
            const int b = parts[2].trimmed().toInt(&okB);
            if (okR && okG && okB) {
                m_cachedAccent = QColor(r, g, b);
            }
        }
    }
}

bool NoxForgeStyle::isObsidianConfig() const
{
    const QString env = qEnvironmentVariable("NOXFORGE_VARIANT");
    if (env.compare(QLatin1String("obsidian"), Qt::CaseInsensitive) == 0) {
        return true;
    }
    if (env.compare(QLatin1String("standard"), Qt::CaseInsensitive) == 0
        || env.compare(QLatin1String("graphite"), Qt::CaseInsensitive) == 0) {
        return false;
    }
    refreshConfigCache();
    return m_cachedScheme.contains(QStringLiteral("Obsidian"), Qt::CaseInsensitive);
}

bool NoxForgeStyle::isObsidianMode(const QStyleOption *option, const QWidget *widget) const
{
    if (option) {
        const QColor base = option->palette.color(QPalette::Base);
        if (base.isValid() && base.red() == 0 && base.green() == 0 && base.blue() == 0 && base.alpha() > 0) {
            return true;
        }
    }
    if (widget) {
        const QColor base = widget->palette().color(QPalette::Base);
        if (base.isValid() && base.red() == 0 && base.green() == 0 && base.blue() == 0 && base.alpha() > 0) {
            return true;
        }
    }
    return isObsidianConfig();
}

QColor NoxForgeStyle::activeAccent(const QStyleOption *option) const
{
    const QString env = qEnvironmentVariable("NOXFORGE_ACCENT").trimmed();
    if (!env.isEmpty()) {
        const QColor named = NP::accentByName(env);
        if (named.isValid()) {
            return named;
        }
    }

    refreshConfigCache();
    if (m_cachedAccent.isValid()) {
        return m_cachedAccent;
    }

    if (option && (option->palette.resolveMask() & (QPalette::ResolveMask(1) << QPalette::Accent))) {
        const QColor palAccent = option->palette.color(QPalette::Accent);
        if (palAccent.isValid()) {
            return palAccent;
        }
    }

    return NP::accent();
}

QPalette NoxForgeStyle::standardPalette() const
{
    QPalette palette;
    const_cast<NoxForgeStyle *>(this)->polish(palette);
    return palette;
}

void NoxForgeStyle::polish(QPalette &palette)
{
    const bool obsidian = isObsidianConfig();
    const auto pal = NP::palette(obsidian);
    const QColor accent = activeAccent();
    const QColor surfSel = activeSurfaceSelected(accent, obsidian);
    palette.setColor(QPalette::Window, pal.surface);
    palette.setColor(QPalette::WindowText, pal.textPrimary);
    palette.setColor(QPalette::Base, pal.background);
    palette.setColor(QPalette::AlternateBase, pal.surface);
    palette.setColor(QPalette::Text, pal.textPrimary);
    palette.setColor(QPalette::Button, pal.surfaceRaised);
    palette.setColor(QPalette::ButtonText, pal.textPrimary);
    palette.setColor(QPalette::Light, pal.borderStrong);
    palette.setColor(QPalette::Midlight, pal.border);
    palette.setColor(QPalette::Mid, pal.border);
    palette.setColor(QPalette::Dark, pal.background);
    palette.setColor(QPalette::Shadow, obsidian ? QColor(QStringLiteral("#000000")) : QColor(QStringLiteral("#080B0E")));
    palette.setColor(QPalette::Highlight, surfSel);
    palette.setColor(QPalette::HighlightedText, pal.textPrimary);
    palette.setColor(QPalette::PlaceholderText, pal.textDisabled);
    palette.setColor(QPalette::Link, pal.cyan);
    palette.setColor(QPalette::LinkVisited, pal.violet);
    palette.setColor(QPalette::ToolTipBase, pal.surfaceRaised);
    palette.setColor(QPalette::ToolTipText, pal.textPrimary);
    palette.setColor(QPalette::Accent, accent);
    for (QPalette::ColorRole role : {QPalette::WindowText, QPalette::Text, QPalette::ButtonText}) {
        palette.setColor(QPalette::Disabled, role, pal.textDisabled);
    }
}

void NoxForgeStyle::polish(QWidget *widget)
{
    QCommonStyle::polish(widget);
    m_motion.setDurationScale(motionScale(widget));
    const bool hoverEffects = QApplication::styleHints()
        ? QApplication::styleHints()->useHoverEffects() : true;
    m_motion.polish(widget, hoverEffects);
}

void NoxForgeStyle::unpolish(QWidget *widget)
{
    m_motion.unpolish(widget);
    QCommonStyle::unpolish(widget);
}

qreal NoxForgeStyle::motionScale(const QWidget *widget) const
{
    Q_UNUSED(widget)
    const QString path = QStandardPaths::locate(
        QStandardPaths::GenericConfigLocation, QStringLiteral("kdeglobals"));
    if (path.isEmpty())
        return 1.0;
    QSettings settings(path, QSettings::IniFormat);
    settings.beginGroup(QStringLiteral("KDE"));
    bool valid = false;
    const qreal factor = settings.value(
        QStringLiteral("AnimationDurationFactor"), 1.0).toDouble(&valid);
    return valid ? qBound(0.0, factor, 4.0) : 1.0;
}

qreal NoxForgeStyle::motionValue(
    const QWidget *widget, NoxForgeMotion::Channel channel, bool target) const
{
    return m_motion.value(widget, channel, target);
}

int NoxForgeStyle::pixelMetric(PixelMetric metric, const QStyleOption *option, const QWidget *widget) const
{
    switch (metric) {
    case PM_DefaultFrameWidth: return 1;
    case PM_ButtonMargin: return 8;
    case PM_ButtonDefaultIndicator: return 0;
    case PM_LayoutHorizontalSpacing:
    case PM_LayoutVerticalSpacing: return 8;
    case PM_ScrollBarExtent: return 16;
    case PM_SliderThickness: return 18;
    case PM_SliderLength: return 18;
    case PM_IndicatorWidth:
    case PM_IndicatorHeight:
    case PM_ExclusiveIndicatorWidth:
    case PM_ExclusiveIndicatorHeight: return 16;
    case PM_TabBarTabHSpace: return 20;
    case PM_TabBarTabVSpace: return 10;
    case PM_ToolBarIconSize: return 22;
    case PM_SmallIconSize: return 16;
    case PM_MenuPanelWidth: return 1;
    case PM_MenuHMargin: return 2;
    case PM_MenuVMargin: return 4;
    case PM_MenuButtonIndicator: return 20;
    case PM_SubMenuOverlap: return 0;
    default: return QCommonStyle::pixelMetric(metric, option, widget);
    }
}

int NoxForgeStyle::styleHint(StyleHint hint, const QStyleOption *option,
                             const QWidget *widget, QStyleHintReturn *returnData) const
{
    switch (hint) {
    case SH_UnderlineShortcut:
    case SH_MenuBar_AltKeyNavigation:
        return QCommonStyle::styleHint(hint, option, widget, returnData);
    case SH_ItemView_ActivateItemOnSingleClick: {
        const QString path = QStandardPaths::locate(
            QStandardPaths::GenericConfigLocation, QStringLiteral("kdeglobals"));
        if (!path.isEmpty()) {
            QSettings settings(path, QSettings::IniFormat);
            settings.beginGroup(QStringLiteral("KDE"));
            if (settings.contains(QStringLiteral("SingleClick")))
                return settings.value(QStringLiteral("SingleClick")).toBool();
        }
        return QCommonStyle::styleHint(hint, option, widget, returnData);
    }
    case SH_FocusFrame_AboveWidget: return 1;
    case SH_Widget_Animation_Duration:
        return qRound(NP::productiveDuration * motionScale(widget));
    default: return QCommonStyle::styleHint(hint, option, widget, returnData);
    }
}

QSize NoxForgeStyle::sizeFromContents(ContentsType type, const QStyleOption *option,
                                      const QSize &contentsSize, const QWidget *widget) const
{
    QSize size = QCommonStyle::sizeFromContents(type, option, contentsSize, widget);
    switch (type) {
    case CT_PushButton:
    case CT_ComboBox:
    case CT_LineEdit:
    case CT_SpinBox:
        size.setHeight(qMax(size.height(), NP::controlHeight));
        size.setWidth(qMax(size.width(), 48));
        break;
    case CT_MenuItem: {
        const auto *item = qstyleoption_cast<const QStyleOptionMenuItem *>(option);
        if (!item) {
            size.setHeight(qMax(size.height(), 30));
            break;
        }
        if (item->menuItemType == QStyleOptionMenuItem::Separator) {
            size.setHeight(qMax(size.height(), 8));
            size.setWidth(qMax(size.width(), 10));
            break;
        }

        const bool hasLeading = (item->maxIconWidth > 0)
            || item->menuHasCheckableItems
            || !item->icon.isNull()
            || item->checked
            || item->checkType != QStyleOptionMenuItem::NotCheckable;

        const int iconWidth = std::max({item->maxIconWidth, pixelMetric(PM_SmallIconSize, option, widget), 16});
        const int leadingWidth = hasLeading ? (iconWidth + 8) : 0;
        const int leftOffset = hasLeading ? (6 + leadingWidth + 8) : 14;
        const int rightMargin = (item->menuItemType == QStyleOptionMenuItem::SubMenu) ? 28 : 16;

        const QStringList parts = item->text.split(QLatin1Char('\t'));
        const QString mainText = parts.value(0);
        const QString shortcutText = parts.value(1);

        const int textWidth = qMax(
            item->fontMetrics.horizontalAdvance(mainText),
            item->fontMetrics.boundingRect(QRect(0, 0, 10000, 1000), Qt::TextShowMnemonic, mainText).width()
        );
        const int fontHeight = item->fontMetrics.height();
        const int textHeight = qMax(contentsSize.height(), fontHeight);
        const int itemHeight = std::max({textHeight + 10, item->maxIconWidth + 10, 30});

        int itemWidth = leftOffset + textWidth + rightMargin;
        if (!shortcutText.isEmpty()) {
            const int shortcutWidth = item->fontMetrics.horizontalAdvance(shortcutText);
            itemWidth += 20 + shortcutWidth;
        }
        itemWidth += 8;

        size.setWidth(qMax(size.width(), itemWidth));
        size.setHeight(qMax(size.height(), itemHeight));
        break;
    }
    case CT_MenuBarItem: {
        const auto *item = qstyleoption_cast<const QStyleOptionMenuItem *>(option);
        int textWidth = contentsSize.width();
        int fontHeight = contentsSize.height();
        if (item) {
            textWidth = qMax(
                item->fontMetrics.horizontalAdvance(item->text),
                item->fontMetrics.boundingRect(QRect(0, 0, 10000, 1000), Qt::TextShowMnemonic, item->text).width()
            );
            fontHeight = item->fontMetrics.height();
        }
        size.setHeight(std::max({size.height(), fontHeight + 10, 30}));
        size.setWidth(std::max({size.width(), textWidth + 24, 44}));
        break;
    }
    case CT_ToolButton: size.setHeight(qMax(size.height(), 32)); break;
    case CT_TabBarTab: size.setHeight(qMax(size.height(), 32)); break;
    default: break;
    }
    return size;
}

QRect NoxForgeStyle::subControlRect(ComplexControl control, const QStyleOptionComplex *option,
                                    SubControl subControl, const QWidget *widget) const
{
    if (control == CC_ScrollBar) {
        const auto *scroll = qstyleoption_cast<const QStyleOptionSlider *>(option);
        if (!scroll)
            return QCommonStyle::subControlRect(control, option, subControl, widget);
        if (subControl == SC_ScrollBarAddLine || subControl == SC_ScrollBarSubLine) return QRect();
        const QRect groove = option->rect.adjusted(2, 2, -2, -2);
        if (subControl == SC_ScrollBarGroove) return groove;
        if (subControl == SC_ScrollBarSlider) {
            const bool horizontal = scroll->orientation == Qt::Horizontal;
            const int length = horizontal ? groove.width() : groove.height();
            const int range = scroll->maximum - scroll->minimum;
            const int page = qMax(1, scroll->pageStep);
            const int thumb = qBound(18, range > 0 ? (length * page) / (range + page) : length, length);
            const int available = qMax(0, length - thumb);
            const int position = sliderPositionFromValue(scroll->minimum, scroll->maximum,
                                                         scroll->sliderPosition, available,
                                                         scroll->upsideDown);
            return horizontal
                ? QRect(groove.left() + position, groove.top(), thumb, groove.height())
                : QRect(groove.left(), groove.top() + position, groove.width(), thumb);
        }
        if (subControl == SC_ScrollBarSubPage || subControl == SC_ScrollBarAddPage) {
            const bool horizontal = scroll->orientation == Qt::Horizontal;
            const QRect slider = subControlRect(control, option, SC_ScrollBarSlider, widget);
            const QRect before = horizontal
                ? QRect(groove.left(), groove.top(),
                        qMax(0, slider.left() - groove.left()), groove.height())
                : QRect(groove.left(), groove.top(), groove.width(),
                        qMax(0, slider.top() - groove.top()));
            const QRect after = horizontal
                ? QRect(slider.right() + 1, groove.top(),
                        qMax(0, groove.right() - slider.right()), groove.height())
                : QRect(groove.left(), slider.bottom() + 1, groove.width(),
                        qMax(0, groove.bottom() - slider.bottom()));
            const bool subPageIsBefore = !scroll->upsideDown;
            return (subControl == SC_ScrollBarSubPage) == subPageIsBefore ? before : after;
        }
    }
    if (control == CC_ComboBox) {
        const int arrowWidth = 30;
        const QRect logicalArrow(option->rect.right() - arrowWidth + 1, option->rect.top(),
                                 arrowWidth, option->rect.height());
        if (subControl == SC_ComboBoxArrow)
            return visualRect(option->direction, option->rect, logicalArrow);
        if (subControl == SC_ComboBoxEditField)
            return visualRect(option->direction, option->rect,
                              option->rect.adjusted(8, 1, -arrowWidth, -1));
    }
    if (control == CC_SpinBox) {
        const int buttonWidth = 26;
        const int half = option->rect.height() / 2;
        const QRect logicalButtons(option->rect.right() - buttonWidth + 1, option->rect.top(),
                                   buttonWidth, option->rect.height());
        if (subControl == SC_SpinBoxUp)
            return visualRect(option->direction, option->rect,
                              QRect(logicalButtons.left(), logicalButtons.top(), buttonWidth, half));
        if (subControl == SC_SpinBoxDown)
            return visualRect(option->direction, option->rect,
                              QRect(logicalButtons.left(), logicalButtons.top() + half,
                                    buttonWidth, option->rect.height() - half));
        if (subControl == SC_SpinBoxEditField)
            return visualRect(option->direction, option->rect,
                              option->rect.adjusted(8, 1, -buttonWidth, -1));
    }
    if (control == CC_Slider) {
        const auto *slider = qstyleoption_cast<const QStyleOptionSlider *>(option);
        if (!slider)
            return QCommonStyle::subControlRect(control, option, subControl, widget);
        constexpr int handleLength = 18;
        if (subControl == SC_SliderGroove) {
            return slider->orientation == Qt::Horizontal
                ? QRect(option->rect.left() + handleLength / 2, option->rect.center().y() - 2,
                        qMax(1, option->rect.width() - handleLength), 4)
                : QRect(option->rect.center().x() - 2, option->rect.top() + handleLength / 2,
                        4, qMax(1, option->rect.height() - handleLength));
        }
        if (subControl == SC_SliderHandle) {
            const bool horizontal = slider->orientation == Qt::Horizontal;
            const int available = qMax(0, (horizontal ? option->rect.width() : option->rect.height()) - handleLength);
            const int position = sliderPositionFromValue(slider->minimum, slider->maximum,
                                                         slider->sliderPosition, available,
                                                         slider->upsideDown);
            return horizontal
                ? QRect(option->rect.left() + position, option->rect.center().y() - handleLength / 2,
                        handleLength, handleLength)
                : QRect(option->rect.center().x() - handleLength / 2, option->rect.top() + position,
                        handleLength, handleLength);
        }
    }
    if (control == CC_ToolButton) {
        const auto *tool = qstyleoption_cast<const QStyleOptionToolButton *>(option);
        if (!tool)
            return QCommonStyle::subControlRect(control, option, subControl, widget);
        const bool hasMenu = tool->features.testFlag(QStyleOptionToolButton::Menu)
            || tool->features.testFlag(QStyleOptionToolButton::MenuButtonPopup);
        const int menuWidth = hasMenu ? 24 : 0;
        const QRect logicalMenu(option->rect.right() - menuWidth + 1, option->rect.top(),
                                menuWidth, option->rect.height());
        if (subControl == SC_ToolButtonMenu)
            return hasMenu ? visualRect(option->direction, option->rect, logicalMenu) : QRect();
        if (subControl == SC_ToolButton)
            return visualRect(option->direction, option->rect,
                              option->rect.adjusted(0, 0, -menuWidth, 0));
    }
    if (control == CC_MdiControls) {
        const int btnExtent = qMin(22, option->rect.height());
        const int gap = 2;
        const int y = option->rect.top() + (option->rect.height() - btnExtent) / 2;
        int right = option->rect.right();
        QRect closeRect, normalRect, minRect;
        if (option->subControls.testFlag(SC_MdiCloseButton)) {
            closeRect = QRect(right - btnExtent + 1, y, btnExtent, btnExtent);
            right = closeRect.left() - gap - 1;
        }
        if (option->subControls.testFlag(SC_MdiNormalButton)) {
            normalRect = QRect(right - btnExtent + 1, y, btnExtent, btnExtent);
            right = normalRect.left() - gap - 1;
        }
        if (option->subControls.testFlag(SC_MdiMinButton)) {
            minRect = QRect(right - btnExtent + 1, y, btnExtent, btnExtent);
        }
        if (subControl == SC_MdiCloseButton) return visualRect(option->direction, option->rect, closeRect);
        if (subControl == SC_MdiNormalButton) return visualRect(option->direction, option->rect, normalRect);
        if (subControl == SC_MdiMinButton) return visualRect(option->direction, option->rect, minRect);
    }
    return QCommonStyle::subControlRect(control, option, subControl, widget);
}

QStyle::SubControl NoxForgeStyle::hitTestComplexControl(
    ComplexControl control, const QStyleOptionComplex *option,
    const QPoint &position, const QWidget *widget) const
{
    const QList<SubControl> controls = [control] {
        switch (control) {
        case CC_ComboBox:
            return QList<SubControl>{SC_ComboBoxArrow, SC_ComboBoxEditField, SC_ComboBoxFrame};
        case CC_SpinBox:
            return QList<SubControl>{SC_SpinBoxUp, SC_SpinBoxDown, SC_SpinBoxEditField,
                                     SC_SpinBoxFrame};
        case CC_Slider:
            return QList<SubControl>{SC_SliderHandle, SC_SliderGroove};
        case CC_ScrollBar:
            return QList<SubControl>{SC_ScrollBarSlider, SC_ScrollBarSubPage,
                                     SC_ScrollBarAddPage, SC_ScrollBarGroove};
        case CC_ToolButton:
            return QList<SubControl>{SC_ToolButtonMenu, SC_ToolButton};
        default:
            return QList<SubControl>{};
        }
    }();
    for (const SubControl subControl : controls) {
        if (subControlRect(control, option, subControl, widget).contains(position))
            return subControl;
    }
    return QCommonStyle::hitTestComplexControl(control, option, position, widget);
}

QRect NoxForgeStyle::subElementRect(SubElement element, const QStyleOption *option,
                                    const QWidget *widget) const
{
    switch (element) {
    case SE_LineEditContents:
        return option->rect.adjusted(8, 4, -8, -4);
    case SE_ComboBoxFocusRect:
        return visualRect(option->direction, option->rect, option->rect.adjusted(8, 2, -30, -2));
    case SE_SliderFocusRect:
        return option->rect.adjusted(1, 1, -1, -1);
    case SE_ComboBoxLayoutItem:
    case SE_SliderLayoutItem:
    case SE_SpinBoxLayoutItem:
        return option->rect;
    default:
        return QCommonStyle::subElementRect(element, option, widget);
    }
}

void NoxForgeStyle::drawPrimitive(PrimitiveElement element, const QStyleOption *option,
                                  QPainter *painter, const QWidget *widget) const
{
    const bool obsidian = isObsidianMode(option, widget);
    const QColor accent = activeAccent(option);
    const QColor accentPressed = activeAccentPressed(accent);
    switch (element) {
    case PE_PanelButtonCommand:
    case PE_PanelButtonTool: {
        const auto *button = qstyleoption_cast<const QStyleOptionButton *>(option);
        const bool primary = button && button->features.testFlag(QStyleOptionButton::DefaultButton);
        const bool hoverTarget = option->state.testFlag(State_MouseOver);
        const bool pressTarget = option->state.testFlag(State_Sunken);
        const qreal hover = motionValue(widget, NoxForgeMotion::Channel::Hover, hoverTarget);
        const qreal press = motionValue(widget, NoxForgeMotion::Channel::Press, pressTarget);
        QColor fill = primary && enabled(option)
            ? mixedColor(accent, accentPressed, press)
            : stateSurface(option, hover, press, obsidian);
        QColor stroke = option->state.testFlag(State_HasFocus)
            ? (primary ? NP::background(obsidian) : accent) : NP::border();
        const bool focused = option->state.testFlag(State_HasFocus);
        if (enabled(option) && press < 0.98) {
            const QColor shadowBase = obsidian ? QColor(0, 0, 0) : QColor(8, 11, 14);
            const QColor shadow = mixedColor(QColor(shadowBase.red(), shadowBase.green(), shadowBase.blue(), 0),
                                             QColor(shadowBase.red(), shadowBase.green(), shadowBase.blue(), 90), 1.0 - press);
            paintSurface(painter, option->rect.translated(0, 1), shadow, Qt::transparent,
                         0, false);
        }
        paintSurface(painter, option->rect, fill, stroke,
                     focused ? NP::focusWidth : NP::borderWidth, focused);
        return;
    }
    case PE_PanelLineEdit:
    case PE_FrameLineEdit: {
        const bool focused = option->state.testFlag(State_HasFocus);
        const bool hovered = option->state.testFlag(State_MouseOver);
        const qreal hoverVal = motionValue(widget, NoxForgeMotion::Channel::Hover, hovered);
        const qreal focusVal = motionValue(widget, NoxForgeMotion::Channel::Focus, focused);
        const QColor baseStroke = mixedColor(NP::border(obsidian), NP::edgeHighlight(obsidian), hoverVal);
        const QColor stroke = mixedColor(baseStroke, accent, focusVal);
        const bool useFocusWidth = focused || focusVal >= 0.5;
        paintSurface(painter, option->rect, NP::background(obsidian),
                     stroke,
                     useFocusWidth ? NP::focusWidth : NP::borderWidth,
                     focused);
        return;
    }
    case PE_PanelMenu:
    case PE_PanelTipLabel:
        paintSurface(painter, option->rect, NP::surfaceOverlay(obsidian), NP::edgeHighlight());
        return;
    case PE_Frame:
        if (qobject_cast<const QAbstractItemView *>(widget)) {
            painter->fillRect(option->rect, NP::background(obsidian));
            painter->fillRect(QRect(option->rect.left(), option->rect.top(),
                                    option->rect.width(), 1), NP::border());
            painter->fillRect(QRect(option->rect.left(), option->rect.bottom(),
                                    option->rect.width(), 1), NP::border());
        } else {
            paintSurface(painter, option->rect, NP::surface(obsidian), NP::border());
        }
        return;
    case PE_PanelItemViewItem:
        if (option->state.testFlag(State_Selected)) {
            paintSelectedSurface(painter, option->rect.adjusted(1, 1, -1, -1),
                                 option->direction, option->state.testFlag(State_HasFocus), obsidian, accent);
        } else if (option->state.testFlag(State_HasFocus)) {
            paintSurface(painter, option->rect.adjusted(1, 1, -1, -1),
                         option->state.testFlag(State_MouseOver) ? NP::surfaceHover(obsidian) : NP::background(obsidian),
                         accent, NP::focusWidth, true);
        } else if (option->state.testFlag(State_MouseOver)) {
            paintSurface(painter, option->rect.adjusted(1, 1, -1, -1), NP::surfaceHover(obsidian), NP::border());
        }
        return;
    case PE_FrameFocusRect:
        // Owning controls paint their focus once; a second frame creates a neon halo.
        return;
    case PE_IndicatorCheckBox:
    case PE_IndicatorRadioButton:
    case PE_IndicatorItemViewItemCheck: {
        const QRect box = alignedRect(option->direction, Qt::AlignCenter, QSize(16, 16), option->rect);
        const bool radio = element == PE_IndicatorRadioButton;
        const bool mixed = option->state.testFlag(State_NoChange);
        const bool checkedTarget = option->state.testFlag(State_On);
        const qreal checkedProgress = mixed ? 1.0
            : motionValue(widget, NoxForgeMotion::Channel::Checked, checkedTarget);
        painter->save();
        painter->setRenderHint(QPainter::Antialiasing);
        painter->setPen(QPen(option->state.testFlag(State_HasFocus) ? accent : NP::borderStrong(), 1));
        painter->setBrush((option->state.testFlag(State_On) || mixed)
                              ? activeSurfaceSelected(accent, obsidian) : NP::background(obsidian));
        radio
            ? painter->drawEllipse(box.adjusted(1, 1, -1, -1))
            : painter->drawPath(surfacePath(box.adjusted(1, 1, -1, -1),
                                            option->state.testFlag(State_HasFocus), 3));
        if (mixed) {
            painter->setPen(QPen(NP::cyan(), 2, Qt::SolidLine, Qt::SquareCap));
            painter->drawLine(box.left() + 4, box.center().y(), box.right() - 4, box.center().y());
        } else if (checkedProgress > 0.0) {
            QColor indicator = accent;
            indicator.setAlphaF(checkedProgress);
            painter->setPen(QPen(indicator, 2, Qt::SolidLine, Qt::SquareCap, Qt::MiterJoin));
            if (radio) {
                const qreal radius = 1.0 + 2.0 * checkedProgress;
                painter->drawEllipse(QPointF(box.center()), radius, radius);
            } else {
                const QPoint start(box.left() + 4, box.center().y());
                const QPoint middle(box.center().x() - 1, box.bottom() - 4);
                const QPoint end(box.right() - 3, box.top() + 4);
                painter->drawLine(start, middle);
                if (checkedProgress > 0.5) {
                    const qreal second = (checkedProgress - 0.5) * 2.0;
                    painter->drawLine(middle, middle + (end - middle) * second);
                }
            }
        }
        painter->restore();
        return;
    }
    case PE_IndicatorHeaderArrow: {
        const auto *header = qstyleoption_cast<const QStyleOptionHeader *>(option);
        if (!header) break;
        const Qt::ArrowType arrow = header->sortIndicator == QStyleOptionHeader::SortDown
            ? Qt::DownArrow : Qt::UpArrow;
        paintArrow(painter, option->rect, arrow,
                   enabled(option) ? NP::textPrimary() : NP::textDisabled());
        return;
    }
    case PE_IndicatorTabClose:
        if (option->state.testFlag(State_MouseOver))
            paintSurface(painter, option->rect.adjusted(1, 1, -1, -1),
                         option->state.testFlag(State_Sunken) ? activeSurfaceSelected(accent, obsidian)
                                                              : NP::surfaceHover(obsidian),
                         option->state.testFlag(State_HasFocus) ? accent : NP::border());
        paintCloseIndicator(painter, option->rect,
                            enabled(option) ? NP::textPrimary() : NP::textDisabled());
        return;
    case PE_IndicatorBranch: {
        const int midX = option->rect.center().x();
        const int midY = option->rect.center().y();
        painter->save();
        painter->setPen(QPen(NP::outlineMuted(), 1, Qt::SolidLine));
        if (option->state.testFlag(State_Item)) {
            const int startX = (option->direction == Qt::RightToLeft) ? option->rect.left() : midX;
            const int endX = (option->direction == Qt::RightToLeft) ? midX : option->rect.right();
            painter->drawLine(startX, midY, endX, midY);
        }
        if (option->state.testFlag(State_Sibling)) {
            painter->drawLine(midX, option->rect.top(), midX, option->rect.bottom());
        } else if (option->state.testFlag(State_Item)) {
            painter->drawLine(midX, option->rect.top(), midX, midY);
        }
        if (option->state.testFlag(State_Children)) {
            const bool open = option->state.testFlag(State_Open);
            const Qt::ArrowType arrow = open ? Qt::DownArrow
                : (option->direction == Qt::RightToLeft ? Qt::LeftArrow : Qt::RightArrow);
            const QColor color = option->state.testFlag(State_MouseOver)
                ? accent
                : (enabled(option) ? NP::textSecondary() : NP::textDisabled());
            paintArrow(painter, option->rect, arrow, color);
        }
        painter->restore();
        return;
    }
    case PE_FrameTabWidget:
    case PE_FrameDockWidget:
        paintSurface(painter, option->rect, NP::surface(obsidian), NP::border());
        return;
    case PE_PanelStatusBar:
        painter->fillRect(option->rect, NP::surface(obsidian));
        painter->fillRect(QRect(option->rect.left(), option->rect.top(), option->rect.width(), 1), NP::border());
        return;
    case PE_FrameStatusBarItem:
        painter->fillRect(QRect(option->direction == Qt::RightToLeft ? option->rect.left() : option->rect.right(),
                                option->rect.top() + 2, 1, option->rect.height() - 4), NP::outlineMuted());
        return;
    case PE_PanelItemViewRow: {
        if (option->state.testFlag(State_Selected)) {
            paintSelectedSurface(painter, option->rect, option->direction,
                                 option->state.testFlag(State_HasFocus), obsidian, accent);
        } else if (option->state.testFlag(State_MouseOver)) {
            painter->fillRect(option->rect, NP::surfaceHover(obsidian));
        } else {
            const auto *viewOpt = qstyleoption_cast<const QStyleOptionViewItem *>(option);
            const bool alt = viewOpt && viewOpt->features.testFlag(QStyleOptionViewItem::Alternate);
            painter->fillRect(option->rect, alt ? NP::surface(obsidian) : NP::background(obsidian));
        }
        return;
    }
    case PE_PanelScrollAreaCorner:
        painter->fillRect(option->rect, NP::background(obsidian));
        painter->fillRect(QRect(option->rect.left(), option->rect.top(), option->rect.width(), 1),
                          NP::border(obsidian));
        painter->fillRect(QRect(option->rect.left(), option->rect.top(), 1, option->rect.height()),
                          NP::border(obsidian));
        return;
    case PE_IndicatorDockWidgetResizeHandle: {
        painter->fillRect(option->rect, NP::surface(obsidian));
        const QColor grip = option->state.testFlag(State_MouseOver) ? accent : NP::borderStrong(obsidian);
        const QPoint c = option->rect.center();
        const bool horizontal = option->state.testFlag(State_Horizontal);
        for (int offset : {-6, 0, 6}) {
            const QRect dot = horizontal
                ? QRect(c.x() - 1, c.y() + offset - 1, 2, 2)
                : QRect(c.x() + offset - 1, c.y() - 1, 2, 2);
            painter->fillRect(dot, grip);
        }
        return;
    }
    case PE_IndicatorToolBarHandle: {
        const QColor grip = NP::borderStrong(obsidian);
        const QPoint c = option->rect.center();
        const bool horizontal = option->state.testFlag(State_Horizontal);
        for (int offset : {-5, 0, 5}) {
            if (horizontal) {
                painter->fillRect(QRect(c.x() - 2, c.y() + offset - 1, 2, 2), grip);
                painter->fillRect(QRect(c.x() + 1, c.y() + offset - 1, 2, 2), grip);
            } else {
                painter->fillRect(QRect(c.x() + offset - 1, c.y() - 2, 2, 2), grip);
                painter->fillRect(QRect(c.x() + offset - 1, c.y() + 1, 2, 2), grip);
            }
        }
        return;
    }
    case PE_IndicatorToolBarSeparator: {
        const bool horizontal = option->state.testFlag(State_Horizontal);
        if (horizontal) {
            painter->fillRect(QRect(option->rect.center().x(), option->rect.top() + 5,
                                    1, qMax(1, option->rect.height() - 10)),
                              NP::border(obsidian));
        } else {
            painter->fillRect(QRect(option->rect.left() + 5, option->rect.center().y(),
                                    qMax(1, option->rect.width() - 10), 1),
                              NP::border(obsidian));
        }
        return;
    }
    case PE_FrameTabBarBase:
        painter->fillRect(QRect(option->rect.left(), option->rect.bottom(),
                                option->rect.width(), 1),
                          NP::border(obsidian));
        return;
    case PE_IndicatorProgressChunk:
        paintSurface(painter, option->rect, NP::cyan(), NP::cyan());
        return;
    case PE_IndicatorArrowDown: paintArrow(painter, option->rect, Qt::DownArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled()); return;
    case PE_IndicatorArrowUp: paintArrow(painter, option->rect, Qt::UpArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled()); return;
    case PE_IndicatorArrowLeft: paintArrow(painter, option->rect, Qt::LeftArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled()); return;
    case PE_IndicatorArrowRight: paintArrow(painter, option->rect, Qt::RightArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled()); return;
    default:
        break;
    }
    QCommonStyle::drawPrimitive(element, option, painter, widget);
}

void NoxForgeStyle::drawControl(ControlElement element, const QStyleOption *option,
                                QPainter *painter, const QWidget *widget) const
{
    const bool obsidian = isObsidianMode(option, widget);
    const QColor accent = activeAccent(option);
    switch (element) {
    case CE_PushButtonLabel: {
        const auto *button = qstyleoption_cast<const QStyleOptionButton *>(option);
        if (!button) break;
        const bool primary = button->features.testFlag(QStyleOptionButton::DefaultButton);
        QStyleOptionButton copy = *button;
        const QColor text = !enabled(option) ? NP::textDisabled() : (primary ? NP::accentInk(obsidian) : NP::textPrimary());
        copy.palette.setColor(QPalette::ButtonText, text);
        copy.palette.setColor(QPalette::WindowText, text);
        QCommonStyle::drawControl(element, &copy, painter, widget);
        return;
    }
    case CE_CheckBoxLabel:
    case CE_RadioButtonLabel: {
        const auto *button = qstyleoption_cast<const QStyleOptionButton *>(option);
        if (!button) break;
        drawLabelWithPalette(this, element, *button, painter, widget, QPalette::WindowText, obsidian);
        return;
    }
    case CE_TabBarTabLabel: {
        const auto *tab = qstyleoption_cast<const QStyleOptionTab *>(option);
        if (!tab) break;
        drawLabelWithPalette(this, element, *tab, painter, widget, QPalette::WindowText, obsidian);
        return;
    }
    case CE_HeaderLabel: {
        const auto *header = qstyleoption_cast<const QStyleOptionHeader *>(option);
        if (!header) break;
        drawLabelWithPalette(this, element, *header, painter, widget, QPalette::ButtonText, obsidian);
        return;
    }
    case CE_HeaderEmptyArea:
        painter->fillRect(option->rect, NP::surface(obsidian));
        painter->fillRect(QRect(option->rect.left(), option->rect.bottom(),
                                option->rect.width(), 1), NP::border(obsidian));
        return;
    case CE_ComboBoxLabel: {
        const auto *combo = qstyleoption_cast<const QStyleOptionComboBox *>(option);
        if (!combo) break;
        QRect editRect = subControlRect(CC_ComboBox, combo, SC_ComboBoxEditField, widget);
        if (editRect.isEmpty())
            editRect = option->rect.adjusted(8, 1, -30, -1);
        painter->save();
        if (!combo->currentIcon.isNull()) {
            const int iconExtent = qMin(combo->iconSize.isValid() ? combo->iconSize.width() : 16,
                                        qMax(12, editRect.height() - 4));
            const QRect iconRect = visualRect(
                option->direction, editRect,
                QRect(editRect.left(), editRect.center().y() - iconExtent / 2, iconExtent, iconExtent));
            combo->currentIcon.paint(painter, iconRect, Qt::AlignCenter,
                                     enabled(option) ? QIcon::Normal : QIcon::Disabled);
            editRect = option->direction == Qt::RightToLeft
                ? editRect.adjusted(0, 0, -(iconExtent + 6), 0)
                : editRect.adjusted(iconExtent + 6, 0, 0, 0);
        }
        painter->setPen(enabled(option) ? NP::textPrimary(obsidian) : NP::textDisabled(obsidian));
        const QString text = option->fontMetrics.elidedText(combo->currentText, Qt::ElideRight, editRect.width());
        painter->drawText(editRect, Qt::AlignVCenter | Qt::AlignLeading, text);
        painter->restore();
        return;
    }
    case CE_DockWidgetTitle: {
        const auto *dock = qstyleoption_cast<const QStyleOptionDockWidget *>(option);
        if (!dock) break;
        painter->fillRect(option->rect, NP::surfaceSunken(obsidian));
        painter->fillRect(QRect(option->rect.left(), option->rect.bottom(),
                                option->rect.width(), 1), NP::border(obsidian));
        if (enabled(option)) {
            const int railX = option->direction == Qt::RightToLeft
                ? option->rect.right() - NP::activeMarkerWidth + 1 : option->rect.left();
            painter->fillRect(QRect(railX, option->rect.top() + 3,
                                    NP::activeMarkerWidth, qMax(1, option->rect.height() - 6)),
                              accent);
        }
        painter->save();
        painter->setPen(enabled(option) ? NP::textPrimary(obsidian) : NP::textDisabled(obsidian));
        const QRect textRect = option->rect.adjusted(10, 0, -10, 0);
        painter->drawText(textRect, Qt::AlignVCenter | Qt::AlignLeading, dock->title);
        painter->restore();
        return;
    }
    case CE_RubberBand: {
        QColor fill = accent;
        fill.setAlpha(46);
        const bool notch = option->rect.width() >= 12 && option->rect.height() >= 12;
        paintSurface(painter, option->rect, fill, accent, 1, notch);
        return;
    }
    case CE_ShapedFrame: {
        const auto *frame = qstyleoption_cast<const QStyleOptionFrame *>(option);
        if (!frame) break;
        const int shape = frame->frameShape;
        if (shape == QFrame::HLine) {
            painter->fillRect(QRect(option->rect.left(), option->rect.center().y(),
                                    option->rect.width(), 1), NP::border(obsidian));
            return;
        }
        if (shape == QFrame::VLine) {
            painter->fillRect(QRect(option->rect.center().x(), option->rect.top(),
                                    1, option->rect.height()), NP::border(obsidian));
            return;
        }
        if (shape == QFrame::NoFrame) {
            return;
        }
        paintSurface(painter, option->rect, Qt::transparent, NP::border(obsidian), NP::borderWidth, false);
        return;
    }
    case CE_SizeGrip: {
        const QRect r = option->rect;
        const bool rtl = option->direction == Qt::RightToLeft;
        painter->save();
        painter->setRenderHint(QPainter::Antialiasing);
        for (int i = 0; i < 3; ++i) {
            const int d = 4 + i * 4;
            painter->setPen(QPen(i == 0 ? NP::edgeHighlight(obsidian) : NP::borderStrong(obsidian), 1.5));
            if (rtl) {
                painter->drawLine(r.left() + 2, r.bottom() - d, r.left() + d, r.bottom() - 2);
            } else {
                painter->drawLine(r.right() - d, r.bottom() - 2, r.right() - 2, r.bottom() - d);
            }
        }
        painter->restore();
        return;
    }
    case CE_MenuBarItem: {
        const auto *item = qstyleoption_cast<const QStyleOptionMenuItem *>(option);
        if (!item) break;
        if (option->state.testFlag(State_Selected) || option->state.testFlag(State_Sunken)) {
            paintSurface(painter, option->rect.adjusted(2, 2, -2, -2),
                         option->state.testFlag(State_Sunken) ? activeSurfaceSelected(accent, obsidian) : NP::surfaceHover(obsidian),
                         option->state.testFlag(State_Sunken) ? accent : NP::border());
        }
        painter->save();
        painter->setPen(enabled(option) ? NP::textPrimary() : NP::textDisabled());
        painter->drawText(option->rect.adjusted(8, 0, -8, 0), Qt::AlignCenter | Qt::TextShowMnemonic, item->text);
        painter->restore();
        return;
    }
    case CE_MenuBarEmptyArea:
        painter->fillRect(option->rect, NP::surface(obsidian));
        return;
    case CE_MenuItem: {
        const auto *item = qstyleoption_cast<const QStyleOptionMenuItem *>(option);
        if (!item) break;
        if (item->menuItemType == QStyleOptionMenuItem::Separator) {
            painter->fillRect(QRect(option->rect.left() + 10, option->rect.center().y(), option->rect.width() - 20, 1), NP::border());
            return;
        }
        if (option->state.testFlag(State_Selected))
            paintSelectedSurface(painter, option->rect.adjusted(3, 2, -3, -2),
                                 option->direction, option->state.testFlag(State_HasFocus), obsidian, accent);
        const bool hasLeading = (item->maxIconWidth > 0)
            || item->menuHasCheckableItems
            || !item->icon.isNull()
            || item->checked
            || item->checkType != QStyleOptionMenuItem::NotCheckable;

        const int iconWidth = std::max({item->maxIconWidth, pixelMetric(PM_SmallIconSize, option, widget), 16});
        const int leadingWidth = hasLeading ? (iconWidth + 8) : 0;
        const int leftOffset = hasLeading ? (6 + leadingWidth + 8) : 14;
        const int rightMargin = (item->menuItemType == QStyleOptionMenuItem::SubMenu) ? 28 : 16;

        if (hasLeading) {
            const QRect leading = visualRect(option->direction, option->rect,
                                             QRect(option->rect.left() + 6, option->rect.top(), leadingWidth, option->rect.height()));
            if (item->checked) {
                QStyleOption check = *option;
                check.rect = alignedRect(option->direction, Qt::AlignCenter, QSize(16, 16), leading);
                check.state |= State_On;
                drawPrimitive(PE_IndicatorCheckBox, &check, painter, widget);
            } else if (!item->icon.isNull()) {
                const QIcon::Mode mode = enabled(option) ? QIcon::Normal : QIcon::Disabled;
                item->icon.paint(painter, leading, Qt::AlignCenter, mode);
            }
        }

        const QStringList parts = item->text.split(QLatin1Char('\t'));
        QRect logicalText = option->rect.adjusted(leftOffset, 0, -rightMargin, 0);
        QRect logicalShortcut;
        if (parts.size() > 1 && !parts.value(1).isEmpty()) {
            const int shortcutWidth = option->fontMetrics.horizontalAdvance(parts.value(1));
            logicalShortcut = QRect(logicalText.right() - shortcutWidth + 1,
                                    logicalText.top(), shortcutWidth, logicalText.height());
            logicalText.setRight(logicalShortcut.left() - 16);
        }
        const QRect textRect = visualRect(option->direction, option->rect, logicalText);
        painter->save();
        painter->setPen(enabled(option) ? NP::textPrimary() : NP::textDisabled());
        painter->drawText(textRect, Qt::AlignVCenter | Qt::AlignLeading | Qt::TextShowMnemonic, parts.value(0));
        if (!logicalShortcut.isEmpty()) {
            painter->drawText(visualRect(option->direction, option->rect, logicalShortcut),
                              Qt::AlignVCenter | Qt::AlignLeading, parts.value(1));
        }
        painter->restore();
        if (item->menuItemType == QStyleOptionMenuItem::SubMenu) {
            const QRect arrow = visualRect(option->direction, option->rect,
                                           QRect(option->rect.right() - 24, option->rect.top(), 20, option->rect.height()));
            paintArrow(painter, arrow, option->direction == Qt::RightToLeft ? Qt::LeftArrow : Qt::RightArrow,
                       enabled(option) ? NP::textPrimary() : NP::textDisabled());
        }
        return;
    }
    case CE_ProgressBarGroove:
        paintSurface(painter, option->rect, NP::background(obsidian), NP::border());
        return;
    case CE_ProgressBarContents: {
        const auto *progress = qstyleoption_cast<const QStyleOptionProgressBar *>(option);
        if (!progress) break;
        const bool busyRequested = progress->minimum == 0 && progress->maximum == 0;
        const bool busy = m_motion.showsBusyIndicator(widget, busyRequested);
        const int span = progress->maximum - progress->minimum;
        const qreal ratio = span > 0 ? qBound(0.0, qreal(progress->progress - progress->minimum) / span, 1.0) : 0.0;
        QRect fill = option->rect.adjusted(2, 2, -2, -2);
        const bool horizontal = option->state.testFlag(State_Horizontal);
        if (busy && horizontal) {
            const int segment = qMax(8, fill.width() / 3);
            const qreal phase = m_motion.busyProgress(widget, true);
            const int travel = fill.width() + segment;
            fill.setLeft(fill.left() + qRound(phase * travel) - segment);
            fill.setWidth(segment);
            fill = fill.intersected(option->rect.adjusted(2, 2, -2, -2));
        } else if (busy) {
            const int segment = qMax(8, fill.height() / 3);
            const qreal phase = m_motion.busyProgress(widget, true);
            const int travel = fill.height() + segment;
            fill.setTop(fill.top() + qRound(phase * travel) - segment);
            fill.setHeight(segment);
            fill = fill.intersected(option->rect.adjusted(2, 2, -2, -2));
        } else if (horizontal) {
            const int amount = qRound(fill.width() * ratio);
            const bool reverse = progress->invertedAppearance ^ (option->direction == Qt::RightToLeft);
            if (reverse) fill.setLeft(fill.right() - amount + 1);
            else fill.setWidth(amount);
        } else {
            const int amount = qRound(fill.height() * ratio);
            if (progress->invertedAppearance) fill.setHeight(amount);
            else fill.setTop(fill.bottom() - amount + 1);
        }
        paintSurface(painter, fill, NP::cyan(), NP::cyan());
        return;
    }
    case CE_ProgressBarLabel: {
        painter->save();
        painter->setPen(enabled(option) ? NP::textPrimary() : NP::textDisabled());
        const auto *progress = qstyleoption_cast<const QStyleOptionProgressBar *>(option);
        if (progress)
            painter->drawText(option->rect, Qt::AlignCenter, progress->text);
        painter->restore();
        return;
    }
    case CE_TabBarTabShape:
    {
        const bool hoverTarget = option->state.testFlag(State_MouseOver);
        qreal hover = hoverTarget ? 1.0 : 0.0;
        if (const auto *tabBar = qobject_cast<const QTabBar *>(widget)) {
            const int idx = tabBar->tabAt(option->rect.center());
            if (idx >= 0) {
                hover = m_motion.tabHoverValue(widget, idx, hoverTarget);
            }
        }
        if (option->state.testFlag(State_Selected)) {
            paintSelectedSurface(painter, option->rect.adjusted(1, 1, -1, -1),
                                 option->direction, option->state.testFlag(State_HasFocus), obsidian, accent);
        } else {
            paintSurface(painter, option->rect.adjusted(1, 1, -1, -1),
                         mixedColor(NP::surfaceRaised(obsidian), NP::surfaceHover(obsidian), hover),
                         option->state.testFlag(State_HasFocus) ? accent : NP::border(obsidian),
                         option->state.testFlag(State_HasFocus) ? NP::focusWidth : NP::borderWidth,
                         option->state.testFlag(State_HasFocus));
        }
        return;
    }
    case CE_HeaderSection:
        painter->fillRect(option->rect,
                          option->state.testFlag(State_MouseOver)
                              ? NP::surfaceHover(obsidian) : NP::surface(obsidian));
        painter->fillRect(QRect(option->rect.left(), option->rect.bottom(),
                                option->rect.width(), 1), NP::border());
        painter->fillRect(QRect(option->direction == Qt::RightToLeft
                                    ? option->rect.left() : option->rect.right(),
                                option->rect.top(), 1, option->rect.height()), NP::border());
        return;
    case CE_ToolBar:
        painter->fillRect(option->rect, NP::surface(obsidian));
        painter->fillRect(QRect(option->rect.left(), option->rect.bottom(), option->rect.width(), 1), NP::border());
        return;
    case CE_Splitter: {
        const bool horizontal = option->state.testFlag(State_Horizontal);
        const QPoint center = option->rect.center();
        painter->save();
        painter->setPen(QPen(NP::borderStrong(), 1));
        if (horizontal) {
            painter->drawLine(center.x(), center.y() - 6, center.x(), center.y() + 6);
        } else {
            painter->drawLine(center.x() - 6, center.y(), center.x() + 6, center.y());
        }
        painter->restore();
        return;
    }
    default:
        break;
    }
    QCommonStyle::drawControl(element, option, painter, widget);
}

void NoxForgeStyle::drawComplexControl(ComplexControl control, const QStyleOptionComplex *option,
                                       QPainter *painter, const QWidget *widget) const
{
    const bool obsidian = isObsidianMode(option, widget);
    const QColor accent = activeAccent(option);
    const QColor accentPressed = activeAccentPressed(accent);
    switch (control) {
    case CC_ComboBox: {
        const qreal hover = motionValue(
            widget, NoxForgeMotion::Channel::Hover,
            option->state.testFlag(State_MouseOver));
        paintSurface(painter, option->rect,
                     mixedColor(NP::background(obsidian), NP::surfaceSunken(obsidian), hover),
                     option->state.testFlag(State_HasFocus) ? accent : NP::border(),
                     option->state.testFlag(State_HasFocus) ? NP::focusWidth : NP::borderWidth,
                     option->state.testFlag(State_HasFocus));
        const QRect arrowRect = subControlRect(CC_ComboBox, option, SC_ComboBoxArrow, widget);
        paintArrow(painter, arrowRect, Qt::DownArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled());
        return;
    }
    case CC_SpinBox: {
        const auto *spin = qstyleoption_cast<const QStyleOptionSpinBox *>(option);
        if (!spin) break;
        const qreal hover = motionValue(
            widget, NoxForgeMotion::Channel::Hover,
            option->state.testFlag(State_MouseOver));
        paintSurface(painter, option->rect,
                     mixedColor(NP::background(obsidian), NP::surfaceSunken(obsidian), hover),
                     option->state.testFlag(State_HasFocus) ? accent : NP::border(obsidian),
                     option->state.testFlag(State_HasFocus) ? NP::focusWidth : NP::borderWidth,
                     option->state.testFlag(State_HasFocus));
        const QRect up = subControlRect(CC_SpinBox, option, SC_SpinBoxUp, widget);
        const QRect down = subControlRect(CC_SpinBox, option, SC_SpinBoxDown, widget);
        const bool upEnabled = enabled(option) && spin->stepEnabled.testFlag(QAbstractSpinBox::StepUpEnabled);
        const bool downEnabled = enabled(option) && spin->stepEnabled.testFlag(QAbstractSpinBox::StepDownEnabled);
        const bool upActive = spin->activeSubControls.testFlag(SC_SpinBoxUp);
        const bool downActive = spin->activeSubControls.testFlag(SC_SpinBoxDown);
        const bool sunken = option->state.testFlag(State_Sunken);
        const bool mouseOver = option->state.testFlag(State_MouseOver);

        if (upEnabled && upActive && (mouseOver || sunken)) {
            painter->fillRect(up.adjusted(1, 1, -1, 0),
                              sunken ? activeSurfaceSelected(accent, obsidian) : NP::surfaceHover(obsidian));
        }
        if (downEnabled && downActive && (mouseOver || sunken)) {
            painter->fillRect(down.adjusted(1, 0, -1, -1),
                              sunken ? activeSurfaceSelected(accent, obsidian) : NP::surfaceHover(obsidian));
        }
        const int separatorX = option->direction == Qt::RightToLeft
            ? qMax(up.right(), down.right()) : qMin(up.left(), down.left());
        painter->fillRect(QRect(separatorX, option->rect.top() + 2, 1,
                                option->rect.height() - 4), NP::border(obsidian));
        painter->fillRect(QRect(up.left() + 1, up.bottom(), qMax(1, up.width() - 2), 1),
                          NP::border(obsidian));
        if (spin->stepEnabled.testFlag(QAbstractSpinBox::StepUpEnabled)) {
            const QColor upColor = !upEnabled ? NP::textDisabled(obsidian)
                : (upActive && sunken ? accent : NP::textPrimary(obsidian));
            paintArrow(painter, up, Qt::UpArrow, upColor);
        }
        if (spin->stepEnabled.testFlag(QAbstractSpinBox::StepDownEnabled)) {
            const QColor downColor = !downEnabled ? NP::textDisabled(obsidian)
                : (downActive && sunken ? accent : NP::textPrimary(obsidian));
            paintArrow(painter, down, Qt::DownArrow, downColor);
        }
        return;
    }
    case CC_GroupBox: {
        const auto *group = qstyleoption_cast<const QStyleOptionGroupBox *>(option);
        if (!group) break;
        const QRect frame = subControlRect(CC_GroupBox, option, SC_GroupBoxFrame, widget);
        paintSurface(painter, frame.adjusted(0, 6, 0, 0), NP::surface(obsidian), NP::border());
        const QRect label = subControlRect(CC_GroupBox, option, SC_GroupBoxLabel, widget);
        painter->fillRect(label.adjusted(-6, 0, 6, 0), NP::surface(obsidian));
        painter->save();
        painter->setPen(enabled(option) ? NP::textSecondary() : NP::textDisabled());
        painter->drawText(label, group->textAlignment | Qt::AlignVCenter | Qt::TextShowMnemonic, group->text);
        painter->restore();
        if (group->subControls.testFlag(SC_GroupBoxCheckBox)) {
            QStyleOption check = *option;
            check.rect = subControlRect(CC_GroupBox, option, SC_GroupBoxCheckBox, widget);
            drawPrimitive(PE_IndicatorCheckBox, &check, painter, widget);
        }
        return;
    }
    case CC_Slider: {
        const auto *slider = qstyleoption_cast<const QStyleOptionSlider *>(option);
        if (!slider) break;
        const QRect groove = subControlRect(CC_Slider, option, SC_SliderGroove, widget);
        const QRect handle = subControlRect(CC_Slider, option, SC_SliderHandle, widget);
        QRect highlight;
        if (slider->orientation == Qt::Horizontal) {
            highlight = slider->upsideDown
                ? QRect(handle.center().x(), groove.top(), groove.right() - handle.center().x() + 1, groove.height())
                : QRect(groove.left(), groove.top(), handle.center().x() - groove.left() + 1, groove.height());
        } else {
            highlight = slider->upsideDown
                ? QRect(groove.left(), handle.center().y(), groove.width(), groove.bottom() - handle.center().y() + 1)
                : QRect(groove.left(), groove.top(), groove.width(), handle.center().y() - groove.top() + 1);
        }
        const bool focused = option->state.testFlag(State_HasFocus);
        const bool hoverTarget = option->state.testFlag(State_MouseOver);
        const qreal hovered = motionValue(
            widget, NoxForgeMotion::Channel::Hover, hoverTarget);
        painter->save();
        painter->setRenderHint(QPainter::Antialiasing);
        painter->setPen(Qt::NoPen);
        painter->setBrush(NP::borderStrong(obsidian));
        painter->drawRoundedRect(groove, 3, 3);
        painter->setBrush(accent);
        painter->drawRoundedRect(highlight, 3, 3);
        if (slider->tickPosition != QSlider::NoTicks && slider->maximum > slider->minimum) {
            const int interval = slider->tickInterval > 0
                ? slider->tickInterval
                : qMax(1, (slider->maximum - slider->minimum) / 10);
            const bool horizontal = slider->orientation == Qt::Horizontal;
            const int span = horizontal ? groove.width() : groove.height();
            for (int v = slider->minimum; v <= slider->maximum; v += interval) {
                const int offset = sliderPositionFromValue(
                    slider->minimum, slider->maximum, v, span, slider->upsideDown);
                const bool passed = v <= slider->sliderPosition;
                painter->setPen(QPen(passed ? accent : NP::outlineMuted(obsidian), 1));
                if (horizontal) {
                    const int tx = groove.left() + offset;
                    if (slider->tickPosition & QSlider::TicksAbove) {
                        painter->drawLine(tx, qMax(option->rect.top(), groove.top() - 5), tx, groove.top() - 2);
                    }
                    if (slider->tickPosition & QSlider::TicksBelow) {
                        painter->drawLine(tx, groove.bottom() + 2, tx, qMin(option->rect.bottom(), groove.bottom() + 5));
                    }
                } else {
                    const int ty = groove.top() + offset;
                    if (slider->tickPosition & QSlider::TicksLeft) {
                        painter->drawLine(qMax(option->rect.left(), groove.left() - 5), ty, groove.left() - 2, ty);
                    }
                    if (slider->tickPosition & QSlider::TicksRight) {
                        painter->drawLine(groove.right() + 2, ty, qMin(option->rect.right(), groove.right() + 5), ty);
                    }
                }
            }
            painter->setPen(Qt::NoPen);
        }
        painter->setBrush(focused
                              ? accent
                              : mixedColor(NP::textPrimary(obsidian), accent, hovered));
        painter->drawEllipse(handle.adjusted(2, 2, -2, -2));
        if (focused) {
            painter->setPen(QPen(accent, NP::focusWidth));
            painter->setBrush(Qt::NoBrush);
            painter->drawEllipse(handle);
        }
        painter->restore();
        return;
    }
    case CC_Dial: {
        const auto *dial = qstyleoption_cast<const QStyleOptionSlider *>(option);
        if (!dial) break;
        const int side = qMin(option->rect.width(), option->rect.height());
        const QRectF dialRect(
            option->rect.center().x() - side / 2.0 + 4.0,
            option->rect.center().y() - side / 2.0 + 4.0,
            qMax(8.0, side - 8.0),
            qMax(8.0, side - 8.0));
        const qreal span = qMax(1, dial->maximum - dial->minimum);
        const qreal ratio = qBound(0.0, qreal(dial->sliderPosition - dial->minimum) / span, 1.0);
        const bool focused = option->state.testFlag(State_HasFocus);
        const qreal hovered = motionValue(widget, NoxForgeMotion::Channel::Hover,
                                          option->state.testFlag(State_MouseOver));

        painter->save();
        painter->setRenderHint(QPainter::Antialiasing);

        // 270-degree outer track arc (from 225 deg clockwise to -45 deg)
        painter->setPen(QPen(NP::borderStrong(obsidian), 3.0, Qt::SolidLine, Qt::RoundCap));
        painter->setBrush(Qt::NoBrush);
        painter->drawArc(dialRect, 225 * 16, -270 * 16);

        // Active accent value arc
        if (ratio > 0.001) {
            painter->setPen(QPen(enabled(option) ? accent : NP::textDisabled(obsidian),
                                 3.0, Qt::SolidLine, Qt::RoundCap));
            painter->drawArc(dialRect, 225 * 16, -qRound(270.0 * 16.0 * ratio));
        }

        // Machined center knob
        const QRectF inner = dialRect.adjusted(4.5, 4.5, -4.5, -4.5);
        painter->setBrush(mixedColor(NP::surfaceRaised(obsidian), NP::surfaceHover(obsidian), hovered));
        painter->setPen(QPen(focused ? accent : NP::border(obsidian),
                             focused ? NP::focusWidth : NP::borderWidth));
        painter->drawEllipse(inner);

        // Precision indicator needle
        const qreal angleDeg = 225.0 - 270.0 * ratio;
        const qreal angleRad = angleDeg * 3.14159265358979323846 / 180.0;
        const QPointF center = inner.center();
        const qreal rInner = inner.width() * 0.18;
        const qreal rOuter = inner.width() * 0.42;
        const QPointF p1(center.x() + std::cos(angleRad) * rInner,
                         center.y() - std::sin(angleRad) * rInner);
        const QPointF p2(center.x() + std::cos(angleRad) * rOuter,
                         center.y() - std::sin(angleRad) * rOuter);
        painter->setPen(QPen(enabled(option) ? accent : NP::textDisabled(obsidian),
                             2.0, Qt::SolidLine, Qt::RoundCap));
        painter->drawLine(p1, p2);

        // Optional radial notch ticks
        if (dial->subControls.testFlag(SC_DialTickmarks)) {
            const int notches = 9;
            const qreal rTick1 = dialRect.width() * 0.50 + 1.0;
            const qreal rTick2 = rTick1 + 2.5;
            painter->setPen(QPen(NP::outlineMuted(obsidian), 1.0));
            for (int i = 0; i < notches; ++i) {
                const qreal a = (225.0 - 270.0 * (qreal(i) / (notches - 1))) * 3.14159265358979323846 / 180.0;
                painter->drawLine(
                    QPointF(center.x() + std::cos(a) * rTick1, center.y() - std::sin(a) * rTick1),
                    QPointF(center.x() + std::cos(a) * rTick2, center.y() - std::sin(a) * rTick2));
            }
        }
        painter->restore();
        return;
    }
    case CC_MdiControls: {
        for (const SubControl sub : {SC_MdiMinButton, SC_MdiNormalButton, SC_MdiCloseButton}) {
            if (!option->subControls.testFlag(sub)) continue;
            const QRect btnRect = subControlRect(CC_MdiControls, option, sub, widget);
            if (btnRect.isEmpty()) continue;
            const bool active = option->activeSubControls.testFlag(sub);
            const bool hovered = active && option->state.testFlag(State_MouseOver);
            const bool pressed = active && option->state.testFlag(State_Sunken);
            const bool isClose = (sub == SC_MdiCloseButton);
            QColor fill = NP::surfaceRaised(obsidian);
            QColor glyph = enabled(option) ? NP::textPrimary(obsidian) : NP::textDisabled(obsidian);
            if (isClose && (hovered || pressed)) {
                fill = NP::negative(obsidian);
                glyph = NP::accentInk(obsidian);
            } else if (pressed) {
                fill = activeSurfaceSelected(accent, obsidian);
            } else if (hovered) {
                fill = NP::surfaceHover(obsidian);
            }
            paintSurface(painter, btnRect.adjusted(1, 1, -1, -1), fill,
                         hovered ? (isClose ? NP::negative(obsidian) : accent) : NP::border(obsidian));
            paintTitleButtonGlyph(painter, btnRect, sub, glyph);
        }
        return;
    }
    case CC_TitleBar: {
        const auto *tb = qstyleoption_cast<const QStyleOptionTitleBar *>(option);
        if (!tb) break;
        const bool isActive = tb->titleBarState & Qt::WindowActive;
        painter->fillRect(option->rect, NP::surfaceSunken(obsidian));
        painter->fillRect(QRect(option->rect.left(), option->rect.bottom(),
                                option->rect.width(), 1), NP::border(obsidian));
        if (isActive) {
            const int railX = option->direction == Qt::RightToLeft
                ? option->rect.right() - NP::activeMarkerWidth + 1 : option->rect.left();
            painter->fillRect(QRect(railX, option->rect.top() + 2,
                                    NP::activeMarkerWidth, qMax(1, option->rect.height() - 4)),
                              accent);
        }
        const QRect labelRect = subControlRect(CC_TitleBar, tb, SC_TitleBarLabel, widget);
        if (!labelRect.isEmpty()) {
            painter->save();
            painter->setPen(isActive ? NP::textPrimary(obsidian) : NP::textSecondary(obsidian));
            const QString elided = option->fontMetrics.elidedText(tb->text, Qt::ElideRight, labelRect.width());
            painter->drawText(labelRect, Qt::AlignVCenter | Qt::AlignLeading, elided);
            painter->restore();
        }
        for (const SubControl sub : {SC_TitleBarMinButton, SC_TitleBarMaxButton,
                                     SC_TitleBarNormalButton, SC_TitleBarShadeButton,
                                     SC_TitleBarUnshadeButton, SC_TitleBarCloseButton}) {
            if (!tb->subControls.testFlag(sub)) continue;
            const QRect btnRect = subControlRect(CC_TitleBar, tb, sub, widget);
            if (btnRect.isEmpty()) continue;
            const bool over = tb->activeSubControls.testFlag(sub) && option->state.testFlag(State_MouseOver);
            const bool down = tb->activeSubControls.testFlag(sub) && option->state.testFlag(State_Sunken);
            const bool isClose = (sub == SC_TitleBarCloseButton);
            QColor fill = NP::surfaceRaised(obsidian);
            QColor glyph = isActive ? NP::textPrimary(obsidian) : NP::textSecondary(obsidian);
            if (isClose && (over || down)) {
                fill = NP::negative(obsidian);
                glyph = NP::accentInk(obsidian);
            } else if (down) {
                fill = activeSurfaceSelected(accent, obsidian);
            } else if (over) {
                fill = NP::surfaceHover(obsidian);
            }
            paintSurface(painter, btnRect.adjusted(1, 1, -1, -1), fill,
                         over ? (isClose ? NP::negative(obsidian) : accent) : NP::border(obsidian));
            paintTitleButtonGlyph(painter, btnRect, sub, glyph);
        }
        return;
    }
    case CC_ScrollBar: {
        const QRect slider = subControlRect(CC_ScrollBar, option, SC_ScrollBarSlider, widget);
        const auto *scroll = qstyleoption_cast<const QStyleOptionSlider *>(option);
        if (!scroll) break;
        QRect visualSlider = slider;
        if (scroll->orientation == Qt::Horizontal) {
            visualSlider.setHeight(qMin(6, slider.height()));
            visualSlider.moveCenter(QPoint(slider.center().x(), option->rect.center().y()));
        } else {
            visualSlider.setWidth(qMin(6, slider.width()));
            visualSlider.moveCenter(QPoint(option->rect.center().x(), slider.center().y()));
        }
        painter->fillRect(option->rect, NP::background(obsidian));
        const qreal hover = motionValue(
            widget, NoxForgeMotion::Channel::Hover,
            option->state.testFlag(State_MouseOver));
        const qreal active = motionValue(
            widget, NoxForgeMotion::Channel::Press,
            option->state.testFlag(State_Sunken));
        painter->save();
        painter->setRenderHint(QPainter::Antialiasing);
        painter->setPen(Qt::NoPen);
        painter->setBrush(mixedColor(
            mixedColor(NP::border(), accent, hover), accentPressed, active));
        painter->drawRoundedRect(visualSlider, 3, 3);
        painter->restore();
        return;
    }
    case CC_ToolButton: {
        const auto *tool = qstyleoption_cast<const QStyleOptionToolButton *>(option);
        if (!tool) break;
        drawPrimitive(PE_PanelButtonTool, option, painter, widget);
        QStyleOptionToolButton label = *tool;
        label.rect = subControlRect(CC_ToolButton, option, SC_ToolButton, widget);
        QCommonStyle::drawControl(CE_ToolButtonLabel, &label, painter, widget);
        if (tool->features.testFlag(QStyleOptionToolButton::Menu)
            || tool->features.testFlag(QStyleOptionToolButton::MenuButtonPopup)) {
            paintArrow(painter, subControlRect(CC_ToolButton, option, SC_ToolButtonMenu, widget),
                       Qt::DownArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled());
        }
        return;
    }
    default:
        break;
    }
    QCommonStyle::drawComplexControl(control, option, painter, widget);
}
