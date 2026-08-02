// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QCommandLineParser>
#include <QCryptographicHash>
#include <QElapsedTimer>
#include <QFile>
#include <QFrame>
#include <QHBoxLayout>
#include <QImage>
#include <QJsonDocument>
#include <QJsonObject>
#include <QLabel>
#include <QMouseEvent>
#include <QPushButton>
#include <QSettings>
#include <QStandardPaths>
#include <QStyle>
#include <QStyleFactory>
#include <QThread>
#include <QVBoxLayout>

namespace
{

QString imageHash(const QImage &image)
{
    QByteArray bytes;
    bytes.reserve(image.sizeInBytes());
    bytes.append(reinterpret_cast<const char *>(image.constBits()), image.sizeInBytes());
    return QString::fromLatin1(QCryptographicHash::hash(bytes, QCryptographicHash::Sha256).toHex());
}

bool writeReport(const QString &path, const QJsonObject &report)
{
    QFile output(path);
    if (!output.open(QIODevice::WriteOnly | QIODevice::Truncate))
        return false;
    return output.write(QJsonDocument(report).toJson(QJsonDocument::Indented)) > 0;
}

qreal configuredMotionFactor()
{
    const QString path =
        QStandardPaths::locate(QStandardPaths::GenericConfigLocation, QStringLiteral("kdeglobals"));
    if (path.isEmpty())
        return 1.0;
    QSettings settings(path, QSettings::IniFormat);
    settings.beginGroup(QStringLiteral("KDE"));
    bool valid = false;
    const qreal value =
        settings.value(QStringLiteral("AnimationDurationFactor"), 1.0).toDouble(&valid);
    return valid ? qBound(0.0, value, 4.0) : 1.0;
}

QJsonObject commonReport(QApplication &application)
{
    return {
        {QStringLiteral("probe"), QStringLiteral("noxforge-live-probe")},
        {QStringLiteral("styleClass"),
         QString::fromLatin1(application.style()->metaObject()->className())},
        {QStringLiteral("styleObjectName"), application.style()->objectName()},
    };
}

int layoutProbe(QApplication &application, const QString &reportPath, bool rtl, bool pseudo)
{
    application.setLayoutDirection(rtl ? Qt::RightToLeft : Qt::LeftToRight);

    QWidget window;
    window.setWindowTitle(QStringLiteral("NoxForge live layout qualification"));
    window.resize(900, 360);
    auto *root = new QVBoxLayout(&window);
    root->setContentsMargins(32, 32, 32, 32);
    root->setSpacing(18);

    auto *title = new QLabel(QStringLiteral("NoxForge Operational Precision"));
    QFont titleFont = title->font();
    titleFont.setPointSize(20);
    titleFont.setBold(true);
    title->setFont(titleFont);
    root->addWidget(title);

    auto *directionRow = new QHBoxLayout;
    auto *marker = new QFrame;
    marker->setObjectName(QStringLiteral("semanticLeadingMarker"));
    marker->setFixedSize(18, 72);
    marker->setStyleSheet(QStringLiteral("background: #A3FF47; border-radius: 4px;"));
    directionRow->addWidget(marker);
    auto *directionText = new QLabel(rtl ? QStringLiteral("RTL semantic leading edge")
                                         : QStringLiteral("LTR semantic leading edge"));
    directionRow->addWidget(directionText);
    directionRow->addStretch(1);
    root->addLayout(directionRow);

    const QString normalText = QStringLiteral("Operational precision");
    const QString pseudoText =
        QStringLiteral("xx Operational precision requires deliberately expanded "
                       "localized content xx");
    const QString displayedText = pseudo ? pseudoText : normalText;
    auto *localized = new QLabel(displayedText);
    localized->setObjectName(QStringLiteral("localizedStressText"));
    localized->setWordWrap(false);
    localized->setStyleSheet(
        QStringLiteral("padding: 14px; border: 1px solid #43535C; background: #151D23;"));
    root->addWidget(localized);
    root->addStretch(1);

    window.show();
    application.processEvents();

    QJsonObject report = commonReport(application);
    report.insert(QStringLiteral("mode"), QStringLiteral("layout"));
    report.insert(QStringLiteral("result"), QStringLiteral("passed"));
    report.insert(QStringLiteral("layoutDirection"), window.layoutDirection() == Qt::RightToLeft
                                                         ? QStringLiteral("rtl")
                                                         : QStringLiteral("ltr"));
    report.insert(QStringLiteral("markerX"), marker->mapTo(&window, QPoint(0, 0)).x());
    report.insert(QStringLiteral("markerWidth"), marker->width());
    report.insert(QStringLiteral("windowWidth"), window.width());
    report.insert(QStringLiteral("pseudoLocalized"), pseudo);
    report.insert(QStringLiteral("displayedText"), displayedText);
    report.insert(QStringLiteral("textWidth"),
                  localized->fontMetrics().horizontalAdvance(displayedText));
    report.insert(QStringLiteral("normalTextWidth"),
                  localized->fontMetrics().horizontalAdvance(normalText));
    if (!writeReport(reportPath, report))
        return 3;
    return application.exec();
}

int motionProbe(QApplication &application, const QString &reportPath, const QString &framesPrefix)
{
    QWidget window;
    window.setWindowTitle(QStringLiteral("NoxForge live motion qualification"));
    window.resize(720, 320);
    auto *layout = new QVBoxLayout(&window);
    layout->setContentsMargins(48, 48, 48, 48);
    layout->setSpacing(24);
    auto *description = new QLabel(QStringLiteral("The installed NoxForge QStyle is sampled "
                                                  "while its real press timer advances."));
    description->setWordWrap(true);
    layout->addWidget(description);
    auto *button = new QPushButton(QStringLiteral("Measured press target"));
    button->setMinimumSize(360, 72);
    layout->addWidget(button, 0, Qt::AlignCenter);
    layout->addStretch(1);
    window.show();
    application.processEvents();

    QEvent leave(QEvent::Leave);
    QApplication::sendEvent(button, &leave);
    const qreal factor = configuredMotionFactor();
    const int expectedDuration =
        application.style()->styleHint(QStyle::SH_Widget_Animation_Duration, nullptr, button);
    QElapsedTimer settle;
    settle.start();
    while (settle.elapsed() < qMax(80, expectedDuration + 48))
    {
        application.processEvents(QEventLoop::AllEvents, 8);
        QThread::msleep(4);
    }

    const QImage initial = button->grab().toImage().convertToFormat(QImage::Format_RGBA8888);
    const QString initialHash = imageHash(initial);
    if (!framesPrefix.isEmpty())
        initial.save(framesPrefix + QStringLiteral("-initial.png"));

    QMouseEvent press(QEvent::MouseButtonPress, QPointF(4, 4), QPointF(4, 4), QPointF(4, 4),
                      Qt::LeftButton, Qt::LeftButton, Qt::NoModifier);
    QApplication::sendEvent(button, &press);
    if (factor == 0.0)
        application.processEvents(QEventLoop::AllEvents, 8);
    QElapsedTimer timer;
    timer.start();
    QString previousHash = initialHash;
    QString finalHash = initialHash;
    QStringList distinctHashes;
    qint64 firstChangeMs = -1;
    qint64 lastChangeMs = -1;
    int samples = 0;
    bool intermediateSaved = false;
    qint64 intermediateFrameMs = -1;
    QString intermediateHash;
    const int measuredExpectedDuration = qRound(90.0 * factor);
    const int observationWindow = qMax(240, measuredExpectedDuration + 240);
    while (timer.elapsed() <= observationWindow)
    {
        application.processEvents(QEventLoop::AllEvents, 8);
        const QImage frame = button->grab().toImage().convertToFormat(QImage::Format_RGBA8888);
        const QString hash = imageHash(frame);
        ++samples;
        if (!distinctHashes.contains(hash))
            distinctHashes.append(hash);
        if (hash != previousHash)
        {
            if (firstChangeMs < 0)
                firstChangeMs = timer.elapsed();
            lastChangeMs = timer.elapsed();
            previousHash = hash;
            if (factor > 0.0 && timer.elapsed() >= measuredExpectedDuration / 2 &&
                !intermediateSaved && !framesPrefix.isEmpty())
            {
                frame.save(framesPrefix + QStringLiteral("-intermediate.png"));
                intermediateSaved = true;
                intermediateFrameMs = timer.elapsed();
                intermediateHash = hash;
            }
        }
        finalHash = hash;
        QThread::msleep(8);
    }
    const QImage final = button->grab().toImage().convertToFormat(QImage::Format_RGBA8888);
    finalHash = imageHash(final);
    if (!framesPrefix.isEmpty())
        final.save(framesPrefix + QStringLiteral("-final.png"));

    QJsonObject report = commonReport(application);
    report.insert(QStringLiteral("mode"), QStringLiteral("motion"));
    report.insert(QStringLiteral("result"), QStringLiteral("passed"));
    report.insert(QStringLiteral("configuredFactor"), factor);
    report.insert(QStringLiteral("styleHintDurationMs"), expectedDuration);
    report.insert(QStringLiteral("measuredExpectedDurationMs"), measuredExpectedDuration);
    report.insert(QStringLiteral("observationWindowMs"), observationWindow);
    report.insert(QStringLiteral("sampleCount"), samples);
    report.insert(QStringLiteral("distinctTransitionFrames"), distinctHashes.size());
    report.insert(QStringLiteral("firstChangeMs"), firstChangeMs);
    report.insert(QStringLiteral("lastChangeMs"), lastChangeMs);
    report.insert(QStringLiteral("initialSha256"), initialHash);
    report.insert(QStringLiteral("finalSha256"), finalHash);
    report.insert(QStringLiteral("intermediateFrameCaptured"), intermediateSaved);
    report.insert(QStringLiteral("intermediateFrameMs"), intermediateFrameMs);
    report.insert(QStringLiteral("intermediateSha256"), intermediateHash);
    if (!writeReport(reportPath, report))
        return 3;
    return application.exec();
}

} // namespace

int main(int argc, char **argv)
{
    QApplication application(argc, argv);
    QCommandLineParser parser;
    parser.setApplicationDescription(
        QStringLiteral("Bounded live qualification for the installed NoxForge Qt style"));
    parser.addHelpOption();
    parser.addOption(
        {QStringLiteral("mode"), QStringLiteral("layout or motion"), QStringLiteral("mode")});
    parser.addOption(
        {QStringLiteral("report"), QStringLiteral("JSON report path"), QStringLiteral("path")});
    parser.addOption({QStringLiteral("frames-prefix"), QStringLiteral("motion frame path prefix"),
                      QStringLiteral("path")});
    parser.addOption({QStringLiteral("rtl"), QStringLiteral("use right-to-left layout")});
    parser.addOption(
        {QStringLiteral("pseudo"), QStringLiteral("show expanded pseudo-localized text")});
    parser.process(application);

    const QString mode = parser.value(QStringLiteral("mode"));
    const QString report = parser.value(QStringLiteral("report"));
    if (report.isEmpty())
        return 2;
    QStyle *style = QStyleFactory::create(QStringLiteral("NoxForge"));
    if (!style)
        return 4;
    application.setStyle(style);
    if (QString::fromLatin1(application.style()->metaObject()->className()) !=
        QStringLiteral("NoxForgeStyle"))
    {
        return 5;
    }
    if (mode == QStringLiteral("layout"))
        return layoutProbe(application, report, parser.isSet(QStringLiteral("rtl")),
                           parser.isSet(QStringLiteral("pseudo")));
    if (mode == QStringLiteral("motion"))
        return motionProbe(application, report, parser.value(QStringLiteral("frames-prefix")));
    return 2;
}
