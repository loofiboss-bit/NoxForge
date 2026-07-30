// SPDX-License-Identifier: MIT
#include "noxforgemotion.h"

#include <QApplication>
#include <QCheckBox>
#include <QEnterEvent>
#include <QFocusEvent>
#include <QMouseEvent>
#include <QProgressBar>
#include <QPushButton>
#include <QTextStream>

namespace {

bool between(qreal value)
{
    return value > 0.0 && value < 1.0;
}

void sendEnter(QWidget *widget)
{
    QEnterEvent event(QPointF(2, 2), QPointF(2, 2), QPointF(2, 2));
    QApplication::sendEvent(widget, &event);
}

void sendMouse(QWidget *widget, QEvent::Type type)
{
    QMouseEvent event(type, QPointF(2, 2), QPointF(2, 2), QPointF(2, 2),
                      Qt::LeftButton,
                      type == QEvent::MouseButtonPress ? Qt::LeftButton : Qt::NoButton,
                      Qt::NoModifier);
    QApplication::sendEvent(widget, &event);
}

} // namespace

int main(int argc, char **argv)
{
    QApplication application(argc, argv);

    NoxForgeMotion motion;
    motion.setDurationScale(1.0);
    auto *button = new QPushButton(QStringLiteral("Motion target"));
    motion.polish(button, true);
    if (motion.trackedWidgetCount() != 1 || motion.timerActive()) return 1;

    sendEnter(button);
    if (!motion.timerActive()) return 2;
    motion.advanceForTest(60);
    if (!between(motion.value(button, NoxForgeMotion::Channel::Hover, true))) return 3;
    motion.advanceForTest(120);
    if (motion.value(button, NoxForgeMotion::Channel::Hover, false) != 1.0
        || motion.timerActive()) return 4;

    QFocusEvent focusIn(QEvent::FocusIn, Qt::TabFocusReason);
    QApplication::sendEvent(button, &focusIn);
    if (motion.value(button, NoxForgeMotion::Channel::Focus, false) != 1.0
        || motion.timerActive()) return 5;

    sendMouse(button, QEvent::MouseButtonPress);
    motion.advanceForTest(40);
    if (!between(motion.value(button, NoxForgeMotion::Channel::Press, true))) return 6;
    sendMouse(button, QEvent::MouseButtonRelease);
    motion.advanceForTest(120);
    if (motion.value(button, NoxForgeMotion::Channel::Press, true) != 0.0) return 7;

    button->setEnabled(false);
    motion.advanceForTest(160);
    if (motion.value(button, NoxForgeMotion::Channel::Hover, true) != 0.0
        || motion.value(button, NoxForgeMotion::Channel::Press, true) != 0.0
        || motion.timerActive()) return 8;
    button->setEnabled(true);

    QEvent leave(QEvent::Leave);
    QApplication::sendEvent(button, &leave);
    QFocusEvent focusOut(QEvent::FocusOut, Qt::TabFocusReason);
    QApplication::sendEvent(button, &focusOut);

    QCheckBox check;
    check.setCheckable(true);
    motion.polish(&check, true);
    check.setChecked(true);
    motion.advanceForTest(40);
    if (!between(motion.value(&check, NoxForgeMotion::Channel::Checked, true))) return 9;
    motion.advanceForTest(100);
    if (motion.value(&check, NoxForgeMotion::Channel::Checked, false) != 1.0) return 10;

    QProgressBar progress;
    progress.setRange(0, 0);
    motion.polish(&progress, true);
    progress.show();
    application.processEvents();
    if (!motion.timerActive()) return 11;
    const qreal firstBusy = motion.busyProgress(&progress, true);
    motion.advanceForTest(100);
    if (qFuzzyCompare(firstBusy + 1.0, motion.busyProgress(&progress, true) + 1.0))
        return 12;
    progress.hide();
    application.processEvents();
    if (motion.timerActive()) return 13;

    motion.unpolish(&check);
    if (motion.trackedWidgetCount() != 2) return 14;
    delete button;
    application.processEvents();
    if (motion.trackedWidgetCount() != 1) return 15;
    motion.unpolish(&progress);
    if (motion.trackedWidgetCount() != 0 || motion.timerActive()) return 16;

    NoxForgeMotion reducedMotion;
    reducedMotion.setDurationScale(0.0);
    QPushButton reduced;
    reducedMotion.polish(&reduced, true);
    sendEnter(&reduced);
    if (reducedMotion.value(&reduced, NoxForgeMotion::Channel::Hover, false) != 1.0
        || reducedMotion.timerActive()) return 17;
    sendMouse(&reduced, QEvent::MouseButtonPress);
    if (reducedMotion.value(&reduced, NoxForgeMotion::Channel::Press, false) != 1.0
        || reducedMotion.timerActive()) return 18;

    QProgressBar reducedBusy;
    reducedBusy.setRange(0, 0);
    reducedMotion.polish(&reducedBusy, true);
    reducedBusy.show();
    application.processEvents();
    if (reducedMotion.timerActive()) return 19;
    reducedMotion.setDurationScale(1.0);
    if (!reducedMotion.timerActive()) return 20;
    reducedBusy.hide();
    application.processEvents();
    if (reducedMotion.timerActive()) return 21;

    QTextStream(stdout)
        << "Motion enter, leave, focus, press, release, disable, busy, destroy, "
           "idle, reduced-motion, and duration re-enable probes passed\n";
    return 0;
}
