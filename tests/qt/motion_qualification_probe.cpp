// SPDX-License-Identifier: MIT
#include "noxforgemotion.h"

#include <QApplication>
#include <QCheckBox>
#include <QElapsedTimer>
#include <QEnterEvent>
#include <QJsonDocument>
#include <QJsonObject>
#include <QMouseEvent>
#include <QProgressBar>
#include <QPushButton>
#include <QScrollBar>
#include <QSlider>
#include <QTextStream>

#if defined(__GLIBC__)
#include <malloc.h>
#endif

namespace {

constexpr int warmupCycles = 50;
constexpr int measuredCycles = 500;
constexpr qint64 maximumHeapGrowthBytes = 262144;
constexpr qreal maximumAverageCycleMs = 5.0;

bool settled(qreal value, qreal target)
{
    return qFuzzyCompare(value + 1.0, target + 1.0);
}

void sendEnter(QWidget *widget)
{
    QEnterEvent event(QPointF(2, 2), QPointF(2, 2), QPointF(2, 2));
    QApplication::sendEvent(widget, &event);
}

void sendLeave(QWidget *widget)
{
    QEvent event(QEvent::Leave);
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

qint64 allocatedHeapBytes()
{
#if defined(__GLIBC__)
    malloc_trim(0);
    return static_cast<qint64>(mallinfo2().uordblks);
#else
    return -1;
#endif
}

int exerciseCycle(
    QApplication &application,
    NoxForgeMotion &motion,
    QPushButton &button,
    QCheckBox &check,
    QSlider &slider,
    QScrollBar &scrollBar,
    QProgressBar &progress,
    int cycle)
{
    sendEnter(&button);
    if (!motion.timerActive())
        return 1;
    motion.advanceForTest(60);
    const qreal hover = motion.value(&button, NoxForgeMotion::Channel::Hover, true);
    if (!(hover > 0.0 && hover < 1.0))
        return 2;

    sendMouse(&button, QEvent::MouseButtonPress);
    motion.advanceForTest(20);
    sendMouse(&button, QEvent::MouseButtonRelease);
    sendLeave(&button);
    button.setChecked((cycle % 2) == 0);
    check.setChecked((cycle % 2) != 0);
    slider.setValue(cycle % 101);
    scrollBar.setValue((cycle * 3) % 101);
    motion.advanceForTest(500);

    if (!settled(
            motion.value(&button, NoxForgeMotion::Channel::Hover, false), 0.0)
        || !settled(
            motion.value(&button, NoxForgeMotion::Channel::Press, false), 0.0)
        || !settled(
            motion.value(&button, NoxForgeMotion::Channel::Checked, false),
            button.isChecked() ? 1.0 : 0.0)
        || !settled(
            motion.value(&check, NoxForgeMotion::Channel::Checked, false),
            check.isChecked() ? 1.0 : 0.0)) {
        return 3;
    }

    progress.setRange(0, 0);
    progress.show();
    application.processEvents();
    if (!motion.timerActive())
        return 4;
    motion.advanceForTest(150);
    if (!motion.showsBusyIndicator(&progress, true))
        return 5;
    const qreal busyBefore = motion.busyProgress(&progress, true);
    motion.advanceForTest(100);
    if (settled(motion.busyProgress(&progress, true), busyBefore))
        return 6;
    progress.setRange(0, 100);
    application.processEvents();
    motion.advanceForTest(500);
    if (motion.timerActive())
        return 7;
    progress.hide();

    auto *ephemeral = new QPushButton(QStringLiteral("Ephemeral"));
    motion.polish(ephemeral, true);
    sendEnter(ephemeral);
    motion.advanceForTest(200);
    delete ephemeral;
    application.processEvents();
    if (motion.trackedWidgetCount() != 5 || motion.timerActive())
        return 8;

    return 0;
}

} // namespace

int main(int argc, char **argv)
{
    QApplication application(argc, argv);

    NoxForgeMotion motion;
    motion.setDurationScale(1.0);
    QPushButton button(QStringLiteral("Motion target"));
    button.setCheckable(true);
    QCheckBox check(QStringLiteral("Toggle"));
    QSlider slider(Qt::Horizontal);
    QScrollBar scrollBar(Qt::Horizontal);
    QProgressBar progress;
    progress.setRange(0, 0);

    for (QWidget *widget : {
             static_cast<QWidget *>(&button),
             static_cast<QWidget *>(&check),
             static_cast<QWidget *>(&slider),
             static_cast<QWidget *>(&scrollBar),
             static_cast<QWidget *>(&progress),
         }) {
        motion.polish(widget, true);
    }
    if (motion.trackedWidgetCount() != 5 || motion.timerActive())
        return 1;

    for (int cycle = 0; cycle < warmupCycles; ++cycle) {
        if (const int result = exerciseCycle(
                application, motion, button, check, slider, scrollBar, progress, cycle)) {
            return 10 + result;
        }
    }

    const qint64 heapBefore = allocatedHeapBytes();
    QElapsedTimer timer;
    timer.start();
    int failedCases = 0;
    for (int cycle = 0; cycle < measuredCycles; ++cycle) {
        if (exerciseCycle(
                application, motion, button, check, slider, scrollBar, progress, cycle)
            != 0) {
            ++failedCases;
        }
    }
    const qint64 elapsedNs = timer.nsecsElapsed();
    const qint64 heapAfter = allocatedHeapBytes();
    const qint64 heapGrowth =
        heapBefore >= 0 && heapAfter >= 0 ? qMax<qint64>(0, heapAfter - heapBefore) : -1;
    const qreal averageCycleMs =
        qreal(elapsedNs) / qreal(measuredCycles) / 1'000'000.0;

    for (QWidget *widget : {
             static_cast<QWidget *>(&button),
             static_cast<QWidget *>(&check),
             static_cast<QWidget *>(&slider),
             static_cast<QWidget *>(&scrollBar),
             static_cast<QWidget *>(&progress),
         }) {
        motion.unpolish(widget);
    }

    const bool memoryPassed =
        heapGrowth >= 0 && heapGrowth <= maximumHeapGrowthBytes;
    const bool performancePassed = averageCycleMs <= maximumAverageCycleMs;
    const bool idlePassed =
        !motion.timerActive() && motion.trackedWidgetCount() == 0;
    const bool passed =
        failedCases == 0 && memoryPassed && performancePassed && idlePassed;

    const QJsonObject report{
        {QStringLiteral("averageCycleMs"), averageCycleMs},
        {QStringLiteral("cycles"), measuredCycles},
        {QStringLiteral("failedCases"), failedCases},
        {QStringLiteral("heapGrowthBytes"), heapGrowth},
        {QStringLiteral("heapGrowthLimitBytes"), maximumHeapGrowthBytes},
        {QStringLiteral("idleTimerActive"), motion.timerActive()},
        {QStringLiteral("memoryResult"), memoryPassed ? QStringLiteral("passed")
                                                      : QStringLiteral("failed")},
        {QStringLiteral("performanceResult"),
         performancePassed ? QStringLiteral("passed") : QStringLiteral("failed")},
        {QStringLiteral("result"), passed ? QStringLiteral("passed")
                                          : QStringLiteral("failed")},
        {QStringLiteral("trackedWidgetsAfterCleanup"), motion.trackedWidgetCount()},
    };
    QTextStream(stdout)
        << QJsonDocument(report).toJson(QJsonDocument::Compact) << '\n';
    return passed ? 0 : 2;
}
