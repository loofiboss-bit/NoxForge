// SPDX-License-Identifier: MIT
#include "noxforgemotion.h"

#include "noxforgepalette.h"

#include <QAbstractButton>
#include <QAbstractSlider>
#include <QAbstractSpinBox>
#include <QComboBox>
#include <QEvent>
#include <QKeyEvent>
#include <QMouseEvent>
#include <QProgressBar>
#include <QPushButton>
#include <QTabBar>
#include <QTimerEvent>
#include <QVariant>
#include <QWidget>

#include <cmath>

namespace NP = NoxForgePalette;

namespace {

qreal eased(qreal progress)
{
    const qreal bounded = qBound(0.0, progress, 1.0);
    return 1.0 - std::pow(1.0 - bounded, 3.0);
}

template<typename Transition>
bool transitionActive(const Transition &transition)
{
    return !qFuzzyCompare(transition.current + 1.0, transition.target + 1.0);
}

QByteArray testPropertyName(NoxForgeMotion::Channel channel)
{
    switch (channel) {
    case NoxForgeMotion::Channel::Hover: return QByteArrayLiteral("_noxforgeMotionTestHover");
    case NoxForgeMotion::Channel::Focus: return QByteArrayLiteral("_noxforgeMotionTestFocus");
    case NoxForgeMotion::Channel::Press: return QByteArrayLiteral("_noxforgeMotionTestPress");
    case NoxForgeMotion::Channel::Checked: return QByteArrayLiteral("_noxforgeMotionTestChecked");
    }
    return QByteArray();
}

} // namespace

NoxForgeMotion::NoxForgeMotion(QObject *parent)
    : QObject(parent)
{
}

bool NoxForgeMotion::supports(const QWidget *widget)
{
    return qobject_cast<const QAbstractButton *>(widget)
        || qobject_cast<const QTabBar *>(widget)
        || qobject_cast<const QComboBox *>(widget)
        || qobject_cast<const QAbstractSpinBox *>(widget)
        || qobject_cast<const QAbstractSlider *>(widget)
        || qobject_cast<const QProgressBar *>(widget);
}

bool NoxForgeMotion::checked(const QWidget *widget)
{
    const auto *button = qobject_cast<const QAbstractButton *>(widget);
    return button && button->isCheckable() && button->isChecked();
}

NoxForgeMotion::Transition &NoxForgeMotion::transition(WidgetState &state, Channel channel)
{
    switch (channel) {
    case Channel::Hover: return state.hover;
    case Channel::Focus: return state.focus;
    case Channel::Press: return state.press;
    case Channel::Checked: return state.checked;
    }
    return state.hover;
}

const NoxForgeMotion::Transition &NoxForgeMotion::transition(
    const WidgetState &state, Channel channel)
{
    switch (channel) {
    case Channel::Hover: return state.hover;
    case Channel::Focus: return state.focus;
    case Channel::Press: return state.press;
    case Channel::Checked: return state.checked;
    }
    return state.hover;
}

void NoxForgeMotion::polish(QWidget *widget, bool hoverEffectsEnabled)
{
    if (!widget || !supports(widget) || m_states.contains(widget))
        return;

    WidgetState state;
    state.hoverAttributeWasSet = widget->testAttribute(Qt::WA_Hover);
    state.hoverEffectsEnabled = hoverEffectsEnabled;
    state.hover.current = state.hover.target =
        hoverEffectsEnabled && widget->underMouse() ? 1.0 : 0.0;
    state.focus.current = state.focus.target = widget->hasFocus() ? 1.0 : 0.0;
    state.checked.current = state.checked.target = checked(widget) ? 1.0 : 0.0;
    m_states.insert(widget, state);

    if (hoverEffectsEnabled)
        widget->setAttribute(Qt::WA_Hover, true);
    widget->installEventFilter(this);

    connect(widget, &QObject::destroyed, this, [this](QObject *object) {
        removeWidget(static_cast<QWidget *>(object));
    });
    if (auto *button = qobject_cast<QAbstractButton *>(widget)) {
        connect(button, &QAbstractButton::toggled, this, [this, button](bool on) {
            setTarget(button, Channel::Checked, on);
        });
    }
}

void NoxForgeMotion::unpolish(QWidget *widget)
{
    if (!widget)
        return;
    const auto found = m_states.constFind(widget);
    if (found == m_states.cend())
        return;
    const bool restoreHover = found->hoverAttributeWasSet;
    widget->removeEventFilter(this);
    widget->setAttribute(Qt::WA_Hover, restoreHover);
    disconnect(widget, nullptr, this, nullptr);
    removeWidget(widget);
}

void NoxForgeMotion::setDurationScale(qreal scale)
{
    const bool wasReduced = m_durationScale <= 0.0;
    m_durationScale = qMax(0.0, scale);
    if (m_durationScale > 0.0) {
        if (wasReduced) {
            for (auto state = m_states.begin(); state != m_states.end(); ++state) {
                state->busyVisible = false;
                state->busyPendingMs = 0;
                state->busyVisibleMs = 0;
            }
        }
        updateTimer();
        return;
    }
    for (auto state = m_states.begin(); state != m_states.end(); ++state) {
        for (Channel channel : {Channel::Hover, Channel::Focus, Channel::Press,
                                Channel::Checked}) {
            Transition &item = transition(state.value(), channel);
            item.current = item.target;
            item.start = item.target;
            item.elapsedMs = 0;
            item.durationMs = 0;
        }
        state->busyVisible = state->busyRequested;
        state->busyPhase = 0.5;
        state->busyPendingMs = 0;
        state->busyVisibleMs = 0;
        state.key()->update();
    }
    updateTimer();
}

int NoxForgeMotion::duration(Channel channel) const
{
    const int base = channel == Channel::Hover ? NP::productiveDuration
        : channel == Channel::Focus ? NP::instantDuration
        : NP::pressDuration;
    return qRound(base * m_durationScale);
}

void NoxForgeMotion::setTarget(QWidget *widget, Channel channel, bool target)
{
    auto found = m_states.find(widget);
    if (found == m_states.end())
        return;
    Transition &item = transition(found.value(), channel);
    const qreal next = target ? 1.0 : 0.0;
    if (qFuzzyCompare(item.target + 1.0, next + 1.0))
        return;
    item.start = item.current;
    item.target = next;
    item.elapsedMs = 0;
    item.durationMs = duration(channel);
    if (item.durationMs == 0)
        item.current = item.target;
    widget->update();
    updateTimer();
}

void NoxForgeMotion::synchronizeBusy(QWidget *widget)
{
    auto found = m_states.find(widget);
    const auto *progress = qobject_cast<QProgressBar *>(widget);
    if (found == m_states.end() || !progress)
        return;
    const bool requested = progress->minimum() == 0 && progress->maximum() == 0
        && progress->isVisible() && progress->isEnabled();
    if (found->busyRequested == requested)
        return;
    found->busyRequested = requested;
    if (requested) {
        found->busyPendingMs = 0;
        found->busyVisibleMs = 0;
        found->busyVisible = m_durationScale <= 0.0;
        found->busyPhase = m_durationScale > 0.0 ? 0.0 : 0.5;
    } else if (!found->busyVisible
               || m_durationScale <= 0.0
               || found->busyVisibleMs >= busyIndicatorMinimumVisibleMs) {
        found->busyVisible = false;
        found->busyPendingMs = 0;
        found->busyVisibleMs = 0;
    }
    widget->update();
    updateTimer();
}

bool NoxForgeMotion::eventFilter(QObject *watched, QEvent *event)
{
    auto *widget = qobject_cast<QWidget *>(watched);
    if (!widget || !m_states.contains(widget))
        return QObject::eventFilter(watched, event);

    switch (event->type()) {
    case QEvent::Enter:
        if (m_states.value(widget).hoverEffectsEnabled)
            setTarget(widget, Channel::Hover, true);
        break;
    case QEvent::Leave:
        setTarget(widget, Channel::Hover, false);
        setTarget(widget, Channel::Press, false);
        break;
    case QEvent::FocusIn:
        setTarget(widget, Channel::Focus, true);
        break;
    case QEvent::FocusOut:
        setTarget(widget, Channel::Focus, false);
        setTarget(widget, Channel::Press, false);
        break;
    case QEvent::MouseButtonPress: {
        const auto *mouse = static_cast<QMouseEvent *>(event);
        if (widget->isEnabled() && mouse->button() == Qt::LeftButton)
            setTarget(widget, Channel::Press, true);
        break;
    }
    case QEvent::MouseButtonRelease: {
        const auto *mouse = static_cast<QMouseEvent *>(event);
        if (mouse->button() == Qt::LeftButton) {
            setTarget(widget, Channel::Press, false);
            setTarget(widget, Channel::Checked, checked(widget));
        }
        break;
    }
    case QEvent::KeyPress:
    case QEvent::KeyRelease: {
        const auto *key = static_cast<QKeyEvent *>(event);
        const auto *button = qobject_cast<QAbstractButton *>(widget);
        const bool activationKey = key->key() == Qt::Key_Space
            || (qobject_cast<const QPushButton *>(button)
                && (key->key() == Qt::Key_Return || key->key() == Qt::Key_Enter));
        if (button && button->isEnabled() && activationKey && !key->isAutoRepeat())
            setTarget(widget, Channel::Press, event->type() == QEvent::KeyPress);
        break;
    }
    case QEvent::EnabledChange:
        if (!widget->isEnabled()) {
            setTarget(widget, Channel::Hover, false);
            setTarget(widget, Channel::Press, false);
        }
        break;
    case QEvent::Hide: {
        auto found = m_states.find(widget);
        if (found != m_states.end()) {
            found->busyRequested = false;
            found->busyVisible = false;
            found->busyPendingMs = 0;
            found->busyVisibleMs = 0;
            for (Channel channel : {Channel::Hover, Channel::Focus, Channel::Press,
                                    Channel::Checked}) {
                Transition &item = transition(found.value(), channel);
                item.current = item.target;
                item.start = item.target;
                item.elapsedMs = 0;
                item.durationMs = 0;
            }
        }
        updateTimer();
        break;
    }
    case QEvent::Show:
    case QEvent::Paint:
        synchronizeBusy(widget);
        break;
    case QEvent::Destroy:
        removeWidget(widget);
        break;
    default:
        break;
    }
    return QObject::eventFilter(watched, event);
}

qreal NoxForgeMotion::value(const QWidget *widget, Channel channel, bool target) const
{
    if (widget) {
        const QVariant forced = widget->property(testPropertyName(channel).constData());
        if (forced.isValid())
            return target ? qBound(0.0, forced.toDouble(), 1.0) : 0.0;
        const auto found = m_states.constFind(const_cast<QWidget *>(widget));
        if (found != m_states.cend())
            return transition(found.value(), channel).current;
    }
    return target ? 1.0 : 0.0;
}

bool NoxForgeMotion::showsBusyIndicator(const QWidget *widget, bool requested) const
{
    if (widget) {
        const QVariant forced = widget->property("_noxforgeMotionTestBusy");
        if (forced.isValid())
            return requested;
        const auto found = m_states.constFind(const_cast<QWidget *>(widget));
        if (found != m_states.cend())
            return found->busyVisible;
    }
    return requested;
}

qreal NoxForgeMotion::busyProgress(const QWidget *widget, bool busy) const
{
    if (!busy)
        return 0.0;
    if (widget) {
        const QVariant forced = widget->property("_noxforgeMotionTestBusy");
        if (forced.isValid())
            return qBound(0.0, forced.toDouble(), 1.0);
        const auto found = m_states.constFind(const_cast<QWidget *>(widget));
        if (found != m_states.cend())
            return found->busyPhase;
    }
    return m_durationScale > 0.0 ? 0.0 : 0.5;
}

void NoxForgeMotion::advance(int elapsedMs)
{
    if (elapsedMs <= 0)
        return;
    for (auto state = m_states.begin(); state != m_states.end(); ++state) {
        bool repaint = false;
        bool becameBusyVisible = false;
        for (Channel channel : {Channel::Hover, Channel::Focus, Channel::Press,
                                Channel::Checked}) {
            Transition &item = transition(state.value(), channel);
            if (!transitionActive(item))
                continue;
            item.elapsedMs += elapsedMs;
            const qreal progress = item.durationMs > 0
                ? qreal(item.elapsedMs) / qreal(item.durationMs) : 1.0;
            item.current = item.start + (item.target - item.start) * eased(progress);
            if (progress >= 1.0)
                item.current = item.target;
            repaint = true;
        }
        if (state->busyRequested && !state->busyVisible && m_durationScale > 0.0) {
            state->busyPendingMs += elapsedMs;
            if (state->busyPendingMs >= busyIndicatorDelayMs) {
                state->busyVisible = true;
                state->busyVisibleMs = state->busyPendingMs - busyIndicatorDelayMs;
                state->busyPhase = 0.0;
                becameBusyVisible = true;
            }
            repaint = true;
        }
        if (state->busyVisible && m_durationScale > 0.0) {
            if (!becameBusyVisible)
                state->busyVisibleMs += elapsedMs;
            const qreal cycle = qMax(1, qRound(NP::busyCycleDuration * m_durationScale));
            state->busyPhase = std::fmod(state->busyPhase + qreal(elapsedMs) / cycle, 1.0);
            repaint = true;
            if (!state->busyRequested
                && state->busyVisibleMs >= busyIndicatorMinimumVisibleMs) {
                state->busyVisible = false;
                state->busyVisibleMs = 0;
            }
        }
        if (repaint)
            state.key()->update();
    }
    updateTimer();
}

void NoxForgeMotion::advanceForTest(int elapsedMs)
{
    advance(elapsedMs);
}

void NoxForgeMotion::timerEvent(QTimerEvent *event)
{
    if (event->timerId() != m_timer.timerId()) {
        QObject::timerEvent(event);
        return;
    }
    const int elapsed = qMax(1, qBound(1, int(m_clock.restart()), 50));
    advance(elapsed);
}

void NoxForgeMotion::updateTimer()
{
    bool active = false;
    for (auto state = m_states.cbegin(); state != m_states.cend() && !active; ++state) {
        active = m_durationScale > 0.0
            && ((state->busyRequested && !state->busyVisible)
                || state->busyVisible);
        for (Channel channel : {Channel::Hover, Channel::Focus, Channel::Press,
                                Channel::Checked})
            active = active || transitionActive(transition(state.value(), channel));
    }
    if (active && !m_timer.isActive()) {
        m_clock.start();
        m_timer.start(16, Qt::PreciseTimer, this);
    } else if (!active && m_timer.isActive()) {
        m_timer.stop();
        m_clock.invalidate();
    }
}

void NoxForgeMotion::removeWidget(QWidget *widget)
{
    m_states.remove(widget);
    updateTimer();
}

bool NoxForgeMotion::timerActive() const
{
    return m_timer.isActive();
}

int NoxForgeMotion::trackedWidgetCount() const
{
    return m_states.size();
}
