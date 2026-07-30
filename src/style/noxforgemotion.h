// SPDX-License-Identifier: MIT
#pragma once

#include <QBasicTimer>
#include <QElapsedTimer>
#include <QHash>
#include <QObject>

class QEvent;
class QTimerEvent;
class QWidget;

class NoxForgeMotion final : public QObject
{
public:
    enum class Channel {
        Hover,
        Focus,
        Press,
        Checked,
    };

    explicit NoxForgeMotion(QObject *parent = nullptr);

    void polish(QWidget *widget, bool hoverEffectsEnabled);
    void unpolish(QWidget *widget);
    void setDurationScale(qreal scale);

    qreal value(const QWidget *widget, Channel channel, bool target) const;
    qreal busyProgress(const QWidget *widget, bool busy) const;

    bool timerActive() const;
    int trackedWidgetCount() const;

    // Deterministic advancement for the internal probe; production uses one shared timer.
    void advanceForTest(int elapsedMs);

protected:
    bool eventFilter(QObject *watched, QEvent *event) override;
    void timerEvent(QTimerEvent *event) override;

private:
    struct Transition {
        qreal current = 0.0;
        qreal start = 0.0;
        qreal target = 0.0;
        int elapsedMs = 0;
        int durationMs = 0;
    };

    struct WidgetState {
        Transition hover;
        Transition focus;
        Transition press;
        Transition checked;
        qreal busyPhase = 0.0;
        bool busy = false;
        bool hoverEffectsEnabled = true;
        bool hoverAttributeWasSet = false;
    };

    static bool supports(const QWidget *widget);
    static bool checked(const QWidget *widget);
    static Transition &transition(WidgetState &state, Channel channel);
    static const Transition &transition(const WidgetState &state, Channel channel);

    int duration(Channel channel) const;
    void setTarget(QWidget *widget, Channel channel, bool target);
    void synchronizeBusy(QWidget *widget);
    void removeWidget(QWidget *widget);
    void advance(int elapsedMs);
    void updateTimer();

    QHash<QWidget *, WidgetState> m_states;
    QBasicTimer m_timer;
    QElapsedTimer m_clock;
    qreal m_durationScale = 1.0;
};
