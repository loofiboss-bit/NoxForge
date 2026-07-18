// SPDX-License-Identifier: MIT
#include "noxforgestyle.h"

#include "noxforgepalette.h"

#include <QApplication>
#include <QPainter>
#include <QPainterPath>
#include <QStyleOption>
#include <QStyleOptionButton>
#include <QStyleOptionComboBox>
#include <QStyleOptionGroupBox>
#include <QStyleOptionMenuItem>
#include <QStyleOptionProgressBar>
#include <QStyleOptionSlider>
#include <QStyleOptionSpinBox>
#include <QStyleOptionTab>

namespace NP = NoxForgePalette;

namespace {

QPainterPath notchedPath(const QRectF &rect, qreal radius = NP::radius)
{
    const qreal left = rect.left();
    const qreal top = rect.top();
    const qreal right = rect.right();
    const qreal bottom = rect.bottom();
    QPainterPath path;
    path.moveTo(left + NP::notch, top);
    path.lineTo(right - radius, top);
    path.quadTo(right, top, right, top + radius);
    path.lineTo(right, bottom - radius);
    path.quadTo(right, bottom, right - radius, bottom);
    path.lineTo(left + radius, bottom);
    path.quadTo(left, bottom, left, bottom - radius);
    path.lineTo(left, top + NP::notch);
    path.closeSubpath();
    return path;
}

bool enabled(const QStyleOption *option)
{
    return option->state.testFlag(QStyle::State_Enabled);
}

QColor stateSurface(const QStyleOption *option)
{
    if (!enabled(option)) {
        return NP::surface();
    }
    if (option->state.testFlag(QStyle::State_Sunken)) {
        return NP::surfaceSelected();
    }
    if (option->state.testFlag(QStyle::State_MouseOver)) {
        return NP::surfaceHover();
    }
    return NP::surfaceRaised();
}

void paintSurface(QPainter *painter, const QRect &rect, const QColor &fill,
                  const QColor &stroke, int width = NP::borderWidth)
{
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing);
    painter->setPen(QPen(stroke, width));
    painter->setBrush(fill);
    painter->drawPath(notchedPath(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5)));
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

} // namespace

NoxForgeStyle::NoxForgeStyle()
{
    setObjectName(QStringLiteral("NoxForge"));
}

QPalette NoxForgeStyle::standardPalette() const
{
    QPalette palette;
    const_cast<NoxForgeStyle *>(this)->polish(palette);
    return palette;
}

void NoxForgeStyle::polish(QPalette &palette)
{
    palette.setColor(QPalette::Window, NP::surface());
    palette.setColor(QPalette::WindowText, NP::textPrimary());
    palette.setColor(QPalette::Base, NP::background());
    palette.setColor(QPalette::AlternateBase, NP::surface());
    palette.setColor(QPalette::Text, NP::textPrimary());
    palette.setColor(QPalette::Button, NP::surfaceRaised());
    palette.setColor(QPalette::ButtonText, NP::textPrimary());
    palette.setColor(QPalette::Light, NP::borderStrong());
    palette.setColor(QPalette::Midlight, NP::border());
    palette.setColor(QPalette::Mid, NP::border());
    palette.setColor(QPalette::Dark, NP::background());
    palette.setColor(QPalette::Shadow, QColor(QStringLiteral("#080B0E")));
    palette.setColor(QPalette::Highlight, NP::surfaceSelected());
    palette.setColor(QPalette::HighlightedText, NP::textPrimary());
    palette.setColor(QPalette::PlaceholderText, NP::textDisabled());
    palette.setColor(QPalette::Link, NP::cyan());
    palette.setColor(QPalette::LinkVisited, NP::violet());
    palette.setColor(QPalette::ToolTipBase, NP::surfaceRaised());
    palette.setColor(QPalette::ToolTipText, NP::textPrimary());
    for (QPalette::ColorRole role : {QPalette::WindowText, QPalette::Text, QPalette::ButtonText}) {
        palette.setColor(QPalette::Disabled, role, NP::textDisabled());
    }
}

int NoxForgeStyle::pixelMetric(PixelMetric metric, const QStyleOption *option, const QWidget *widget) const
{
    switch (metric) {
    case PM_DefaultFrameWidth: return 1;
    case PM_ButtonMargin: return 8;
    case PM_ButtonDefaultIndicator: return 0;
    case PM_LayoutHorizontalSpacing:
    case PM_LayoutVerticalSpacing: return 8;
    case PM_ScrollBarExtent: return 10;
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
    default: return QCommonStyle::pixelMetric(metric, option, widget);
    }
}

int NoxForgeStyle::styleHint(StyleHint hint, const QStyleOption *option,
                             const QWidget *widget, QStyleHintReturn *returnData) const
{
    switch (hint) {
    case SH_UnderlineShortcut: return 0;
    case SH_ItemView_ActivateItemOnSingleClick: return 0;
    case SH_MenuBar_AltKeyNavigation: return 1;
    case SH_Widget_Animate: return 1;
    case SH_FocusFrame_AboveWidget: return 1;
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
    case CT_MenuItem: size.setHeight(qMax(size.height(), 30)); break;
    case CT_MenuBarItem:
        size.setHeight(qMax(size.height(), 30));
        size.setWidth(qMax(size.width() + 12, 44));
        break;
    case CT_ToolButton: size.setHeight(qMax(size.height(), 32)); break;
    case CT_TabBarTab: size.setHeight(qMax(size.height(), 32)); break;
    default: break;
    }
    return size;
}

void NoxForgeStyle::drawPrimitive(PrimitiveElement element, const QStyleOption *option,
                                  QPainter *painter, const QWidget *widget) const
{
    switch (element) {
    case PE_PanelButtonCommand:
    case PE_PanelButtonTool: {
        const auto *button = qstyleoption_cast<const QStyleOptionButton *>(option);
        const bool primary = button && button->features.testFlag(QStyleOptionButton::DefaultButton);
        QColor fill = primary ? (option->state.testFlag(State_Sunken) ? NP::accentPressed() : NP::accent()) : stateSurface(option);
        QColor stroke = option->state.testFlag(State_HasFocus) ? NP::accent() : NP::border();
        paintSurface(painter, option->rect, fill, stroke, option->state.testFlag(State_HasFocus) ? 2 : 1);
        return;
    }
    case PE_PanelLineEdit:
    case PE_FrameLineEdit:
        paintSurface(painter, option->rect, NP::background(), option->state.testFlag(State_HasFocus) ? NP::accent() : NP::border(), option->state.testFlag(State_HasFocus) ? 2 : 1);
        return;
    case PE_PanelMenu:
    case PE_PanelTipLabel:
    case PE_Frame:
        paintSurface(painter, option->rect, NP::surface(), NP::border());
        return;
    case PE_PanelItemViewItem:
        if (option->state.testFlag(State_Selected)) {
            paintSurface(painter, option->rect.adjusted(1, 1, -1, -1), NP::surfaceSelected(), NP::accent());
        } else if (option->state.testFlag(State_MouseOver)) {
            paintSurface(painter, option->rect.adjusted(1, 1, -1, -1), NP::surfaceHover(), NP::border());
        }
        return;
    case PE_FrameFocusRect:
        paintSurface(painter, option->rect.adjusted(1, 1, -1, -1), Qt::transparent, NP::accent(), 2);
        return;
    case PE_IndicatorCheckBox:
    case PE_IndicatorRadioButton: {
        const QRect box = alignedRect(option->direction, Qt::AlignCenter, QSize(16, 16), option->rect);
        painter->save();
        painter->setRenderHint(QPainter::Antialiasing);
        painter->setPen(QPen(option->state.testFlag(State_HasFocus) ? NP::accent() : NP::borderStrong(), 1));
        painter->setBrush(option->state.testFlag(State_On) ? NP::surfaceSelected() : NP::background());
        element == PE_IndicatorRadioButton ? painter->drawEllipse(box.adjusted(1, 1, -1, -1)) : painter->drawPath(notchedPath(box.adjusted(1, 1, -1, -1), 3));
        if (option->state.testFlag(State_On)) {
            painter->setPen(QPen(NP::accent(), 2, Qt::SolidLine, Qt::SquareCap, Qt::MiterJoin));
            if (element == PE_IndicatorRadioButton) painter->drawEllipse(box.center(), 3, 3);
            else painter->drawPolyline(QPolygon() << QPoint(box.left() + 4, box.center().y()) << QPoint(box.center().x() - 1, box.bottom() - 4) << QPoint(box.right() - 3, box.top() + 4));
        }
        painter->restore();
        return;
    }
    case PE_IndicatorArrowDown: paintArrow(painter, option->rect, Qt::DownArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled()); return;
    case PE_IndicatorArrowUp: paintArrow(painter, option->rect, Qt::UpArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled()); return;
    case PE_IndicatorArrowLeft: paintArrow(painter, option->rect, Qt::LeftArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled()); return;
    case PE_IndicatorArrowRight: paintArrow(painter, option->rect, Qt::RightArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled()); return;
    default:
        QCommonStyle::drawPrimitive(element, option, painter, widget);
    }
}

void NoxForgeStyle::drawControl(ControlElement element, const QStyleOption *option,
                                QPainter *painter, const QWidget *widget) const
{
    switch (element) {
    case CE_PushButtonLabel: {
        const auto *button = qstyleoption_cast<const QStyleOptionButton *>(option);
        if (!button) break;
        const bool primary = button->features.testFlag(QStyleOptionButton::DefaultButton);
        QStyleOptionButton copy = *button;
        const QColor text = !enabled(option) ? NP::textDisabled() : (primary ? NP::accentInk() : NP::textPrimary());
        copy.palette.setColor(QPalette::ButtonText, text);
        copy.palette.setColor(QPalette::WindowText, text);
        QCommonStyle::drawControl(element, &copy, painter, widget);
        return;
    }
    case CE_MenuBarItem: {
        const auto *item = qstyleoption_cast<const QStyleOptionMenuItem *>(option);
        if (!item) break;
        if (option->state.testFlag(State_Selected) || option->state.testFlag(State_Sunken)) {
            paintSurface(painter, option->rect.adjusted(2, 2, -2, -2),
                         option->state.testFlag(State_Sunken) ? NP::surfaceSelected() : NP::surfaceHover(),
                         option->state.testFlag(State_Sunken) ? NP::accent() : NP::border());
        }
        painter->save();
        painter->setPen(enabled(option) ? NP::textPrimary() : NP::textDisabled());
        painter->drawText(option->rect.adjusted(8, 0, -8, 0), Qt::AlignCenter | Qt::TextShowMnemonic, item->text);
        painter->restore();
        return;
    }
    case CE_MenuBarEmptyArea:
        painter->fillRect(option->rect, NP::surface());
        return;
    case CE_MenuItem: {
        const auto *item = qstyleoption_cast<const QStyleOptionMenuItem *>(option);
        if (!item) break;
        if (item->menuItemType == QStyleOptionMenuItem::Separator) {
            painter->fillRect(QRect(option->rect.left() + 10, option->rect.center().y(), option->rect.width() - 20, 1), NP::border());
            return;
        }
        if (option->state.testFlag(State_Selected)) paintSurface(painter, option->rect.adjusted(3, 2, -3, -2), NP::surfaceSelected(), NP::accent());
        const int leadingWidth = 28;
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
        const QStringList parts = item->text.split(QLatin1Char('\t'));
        const QRect textRect = option->rect.adjusted(leadingWidth + 8, 0, -28, 0);
        painter->save();
        painter->setPen(enabled(option) ? NP::textPrimary() : NP::textDisabled());
        painter->drawText(textRect, Qt::AlignVCenter | Qt::AlignLeading | Qt::TextShowMnemonic, parts.value(0));
        if (parts.size() > 1) painter->drawText(textRect, Qt::AlignVCenter | Qt::AlignTrailing, parts.value(1));
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
        paintSurface(painter, option->rect, NP::background(), NP::border());
        return;
    case CE_ProgressBarContents: {
        const auto *progress = qstyleoption_cast<const QStyleOptionProgressBar *>(option);
        if (!progress) break;
        const int span = progress->maximum - progress->minimum;
        const qreal ratio = span > 0 ? qBound(0.0, qreal(progress->progress - progress->minimum) / span, 1.0) : 0.0;
        QRect fill = option->rect.adjusted(2, 2, -2, -2);
        const bool horizontal = option->state.testFlag(State_Horizontal);
        if (horizontal) {
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
    case CE_TabBarTabShape:
    case CE_HeaderSection:
        paintSurface(painter, option->rect.adjusted(1, 1, -1, -1), option->state.testFlag(State_Selected) ? NP::surfaceSelected() : stateSurface(option), option->state.testFlag(State_Selected) ? NP::accent() : NP::border());
        return;
    case CE_ToolBar:
        painter->fillRect(option->rect, NP::surface());
        painter->fillRect(QRect(option->rect.left(), option->rect.bottom(), option->rect.width(), 1), NP::border());
        return;
    default:
        QCommonStyle::drawControl(element, option, painter, widget);
    }
}

void NoxForgeStyle::drawComplexControl(ComplexControl control, const QStyleOptionComplex *option,
                                       QPainter *painter, const QWidget *widget) const
{
    switch (control) {
    case CC_ComboBox: {
        paintSurface(painter, option->rect, NP::background(), option->state.testFlag(State_HasFocus) ? NP::accent() : NP::border());
        const QRect arrowRect = subControlRect(CC_ComboBox, option, SC_ComboBoxArrow, widget);
        paintArrow(painter, arrowRect, Qt::DownArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled());
        return;
    }
    case CC_SpinBox: {
        const auto *spin = qstyleoption_cast<const QStyleOptionSpinBox *>(option);
        if (!spin) break;
        paintSurface(painter, option->rect, NP::background(),
                     option->state.testFlag(State_HasFocus) ? NP::accent() : NP::border());
        const QRect up = subControlRect(CC_SpinBox, option, SC_SpinBoxUp, widget);
        const QRect down = subControlRect(CC_SpinBox, option, SC_SpinBoxDown, widget);
        painter->fillRect(visualRect(option->direction, option->rect,
                                    QRect(qMin(up.left(), down.left()), option->rect.top() + 2, 1, option->rect.height() - 4)), NP::border());
        if (spin->stepEnabled.testFlag(QAbstractSpinBox::StepUpEnabled))
            paintArrow(painter, up, Qt::UpArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled());
        if (spin->stepEnabled.testFlag(QAbstractSpinBox::StepDownEnabled))
            paintArrow(painter, down, Qt::DownArrow, enabled(option) ? NP::textPrimary() : NP::textDisabled());
        return;
    }
    case CC_GroupBox: {
        const auto *group = qstyleoption_cast<const QStyleOptionGroupBox *>(option);
        if (!group) break;
        const QRect frame = subControlRect(CC_GroupBox, option, SC_GroupBoxFrame, widget);
        paintSurface(painter, frame.adjusted(0, 6, 0, 0), NP::surface(), NP::border());
        const QRect label = subControlRect(CC_GroupBox, option, SC_GroupBoxLabel, widget);
        painter->fillRect(label.adjusted(-6, 0, 6, 0), NP::surface());
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
        const int handleLength = 18;
        QRect groove;
        QRect handle;
        QRect highlight;
        if (slider->orientation == Qt::Horizontal) {
            groove = QRect(option->rect.left() + handleLength / 2, option->rect.center().y() - 2,
                           option->rect.width() - handleLength, 4);
            const int position = sliderPositionFromValue(slider->minimum, slider->maximum,
                                                         slider->sliderPosition,
                                                         groove.width() - handleLength,
                                                         slider->upsideDown);
            handle = QRect(groove.left() + position, option->rect.center().y() - handleLength / 2,
                           handleLength, handleLength);
            highlight = QRect(groove.left(), groove.top(), handle.center().x() - groove.left(), groove.height());
        } else {
            groove = QRect(option->rect.center().x() - 2, option->rect.top() + handleLength / 2,
                           4, option->rect.height() - handleLength);
            const int position = sliderPositionFromValue(slider->minimum, slider->maximum,
                                                         slider->sliderPosition,
                                                         groove.height() - handleLength,
                                                         slider->upsideDown);
            handle = QRect(option->rect.center().x() - handleLength / 2, groove.top() + position,
                           handleLength, handleLength);
            highlight = QRect(groove.left(), groove.top(), groove.width(), handle.center().y() - groove.top());
        }
        painter->save();
        painter->setRenderHint(QPainter::Antialiasing);
        painter->setPen(Qt::NoPen);
        painter->setBrush(NP::borderStrong());
        painter->drawRoundedRect(groove, 3, 3);
        painter->setBrush(NP::accent());
        painter->drawRoundedRect(highlight, 3, 3);
        painter->setBrush(option->state.testFlag(State_MouseOver) ? NP::accent() : NP::textPrimary());
        painter->drawEllipse(handle.adjusted(2, 2, -2, -2));
        painter->restore();
        return;
    }
    case CC_ScrollBar: {
        const QRect groove = subControlRect(CC_ScrollBar, option, SC_ScrollBarGroove, widget);
        const QRect slider = subControlRect(CC_ScrollBar, option, SC_ScrollBarSlider, widget);
        painter->fillRect(groove, NP::background());
        painter->save();
        painter->setRenderHint(QPainter::Antialiasing);
        painter->setPen(Qt::NoPen);
        painter->setBrush(option->state.testFlag(State_MouseOver) ? NP::accent() : NP::borderStrong());
        painter->drawRoundedRect(slider, 4, 4);
        painter->restore();
        return;
    }
    case CC_ToolButton:
        drawPrimitive(PE_PanelButtonTool, option, painter, widget);
        QCommonStyle::drawControl(CE_ToolButtonLabel, option, painter, widget);
        return;
    default:
        QCommonStyle::drawComplexControl(control, option, painter, widget);
    }
}
