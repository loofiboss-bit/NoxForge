// SPDX-License-Identifier: MIT
#include "noxforgepalette.h"

#include <QDir>
#include <QFont>
#include <QFontDatabase>
#include <QGuiApplication>
#include <QImage>
#include <QPainter>
#include <QPainterPath>

namespace NP = NoxForgePalette;

namespace {

QFont font(int pixels, int weight = QFont::Normal, int tracking = 0)
{
    QFont result = QFontDatabase::systemFont(QFontDatabase::GeneralFont);
    result.setPixelSize(pixels);
    result.setWeight(static_cast<QFont::Weight>(weight));
    result.setLetterSpacing(QFont::AbsoluteSpacing, tracking);
    return result;
}

QColor alpha(QColor color, int value)
{
    color.setAlpha(value);
    return color;
}

QPainterPath notchedPath(const QRectF &rect, qreal radius = 6.0, qreal notch = 0.0)
{
    QPainterPath path;
    if (notch <= 0.0) {
        path.addRoundedRect(rect, radius, radius);
        return path;
    }
    path.moveTo(rect.left() + notch, rect.top());
    path.lineTo(rect.right() - radius, rect.top());
    path.quadTo(rect.right(), rect.top(), rect.right(), rect.top() + radius);
    path.lineTo(rect.right(), rect.bottom() - radius);
    path.quadTo(rect.right(), rect.bottom(), rect.right() - radius, rect.bottom());
    path.lineTo(rect.left() + radius, rect.bottom());
    path.quadTo(rect.left(), rect.bottom(), rect.left(), rect.bottom() - radius);
    path.lineTo(rect.left(), rect.top() + notch);
    path.closeSubpath();
    return path;
}

void surface(
    QPainter &painter,
    const QRectF &rect,
    const QColor &fill,
    const QColor &outline = Qt::transparent,
    qreal radius = 6.0,
    qreal notch = 0.0)
{
    const QPainterPath path = notchedPath(rect, radius, notch);
    painter.fillPath(path, fill);
    if (outline.alpha() > 0) {
        painter.setBrush(Qt::NoBrush);
        painter.setPen(QPen(outline, 1));
        painter.drawPath(path);
    }
}

void label(
    QPainter &painter,
    const QRectF &rect,
    const QString &text,
    int pixels,
    const QColor &color,
    int weight = QFont::Normal,
    Qt::Alignment alignment = Qt::AlignLeft | Qt::AlignVCenter,
    int tracking = 0)
{
    painter.setFont(font(pixels, weight, tracking));
    painter.setPen(color);
    painter.drawText(rect, alignment, text);
}

void button(
    QPainter &painter,
    const QRectF &rect,
    const QString &text,
    bool primary = false,
    bool focused = false)
{
    const QColor fill = primary ? NP::accent() : NP::surfaceRaised();
    const QColor ink = primary ? NP::background() : NP::textPrimary();
    surface(
        painter,
        rect,
        fill,
        focused ? NP::accent() : NP::outlineMuted(),
        NP::radius,
        focused ? NP::notch : 0);
    if (focused) {
        painter.setPen(QPen(NP::accent(), 2));
        painter.drawPath(notchedPath(rect.adjusted(-3, -3, 3, 3), NP::radius + 2, NP::notch));
    }
    label(painter, rect, text, 14, ink, QFont::Medium, Qt::AlignCenter);
}

void forgedBackdrop(QPainter &painter, const QRect &bounds)
{
    painter.fillRect(bounds, NP::background());
    QPolygon leftPlane;
    leftPlane << QPoint(0, 0)
              << QPoint(bounds.width() * 0.46, 0)
              << QPoint(bounds.width() * 0.34, bounds.height())
              << QPoint(0, bounds.height());
    painter.setBrush(NP::surface());
    painter.setPen(Qt::NoPen);
    painter.drawPolygon(leftPlane);
    QPolygon seam;
    seam << QPoint(bounds.width() * 0.34, bounds.height())
         << QPoint(bounds.width() * 0.46, 0)
         << QPoint(bounds.width() * 0.463, 0)
         << QPoint(bounds.width() * 0.353, bounds.height());
    painter.setBrush(NP::accentMuted());
    painter.drawPolygon(seam);
    painter.setOpacity(0.05);
    QPolygon detail;
    detail << QPoint(bounds.width() * 0.68, 0)
           << QPoint(bounds.width() * 0.83, 0)
           << QPoint(bounds.width() * 0.75, bounds.height());
    painter.setBrush(NP::violet());
    painter.drawPolygon(detail);
    painter.setOpacity(1.0);
}

void renderQt(QPainter &painter, const QSize &size)
{
    painter.fillRect(QRect(QPoint(), size), NP::background());
    surface(painter, QRectF(32, 32, size.width() - 64, size.height() - 64), NP::surface());
    label(painter, QRectF(64, 52, 600, 40), QStringLiteral("System settings"), 24,
          NP::textPrimary(), QFont::DemiBold);
    label(painter, QRectF(64, 92, 600, 28), QStringLiteral("Appearance · Kinetic Precision"), 12,
          NP::textSecondary());

    const QRectF navigation(64, 144, 240, 520);
    surface(painter, navigation, NP::surfaceSunken());
    const QStringList items = {
        QStringLiteral("Workspace"),
        QStringLiteral("Colors"),
        QStringLiteral("Window style"),
        QStringLiteral("Icons"),
        QStringLiteral("Cursors"),
    };
    for (int index = 0; index < items.size(); ++index) {
        const QRectF row(76, 164 + index * 52, 216, 40);
        if (index == 1) {
            surface(painter, row, NP::surfaceSelected(), Qt::transparent, NP::compactRadius);
            painter.fillRect(QRectF(row.left(), row.top() + 8, 3, row.height() - 16), NP::accent());
        }
        label(painter, row.adjusted(16, 0, -8, 0), items[index], 14,
              index == 1 ? NP::textPrimary() : NP::textSecondary(),
              index == 1 ? QFont::Medium : QFont::Normal);
    }

    label(painter, QRectF(344, 148, 360, 28), QStringLiteral("Color scheme"), 16,
          NP::textPrimary(), QFont::DemiBold);
    label(painter, QRectF(344, 180, 480, 24),
          QStringLiteral("Graphite surfaces with precise semantic accents"), 14,
          NP::textSecondary());
    surface(painter, QRectF(344, 228, 548, 56), NP::surfaceSunken(), NP::outlineMuted());
    label(painter, QRectF(360, 228, 420, 56), QStringLiteral("NoxForge Dark"), 14,
          NP::textPrimary());
    surface(painter, QRectF(344, 316, 548, 160), NP::surfaceRaised());
    label(painter, QRectF(368, 336, 300, 24), QStringLiteral("Interaction preview"), 16,
          NP::textPrimary(), QFont::DemiBold);
    button(painter, QRectF(368, 388, 128, 36), QStringLiteral("Focused"), false, true);
    button(painter, QRectF(516, 388, 128, 36), QStringLiteral("Secondary"));
    button(painter, QRectF(664, 388, 152, 36), QStringLiteral("Apply"), true);
    label(painter, QRectF(368, 436, 440, 20),
          QStringLiteral("Focus remains distinct from the primary action."), 12,
          NP::textSecondary());

    painter.setBrush(alpha(NP::background(), 110));
    painter.setPen(Qt::NoPen);
    painter.drawRoundedRect(QRectF(604, 516, 288, 132).translated(0, 8), 8, 8);
    surface(painter, QRectF(604, 516, 288, 132), NP::surfaceOverlay(), NP::edgeHighlight(), 8);
    painter.fillRect(QRectF(620, 516, 80, 1), NP::edgeHighlight());
    label(painter, QRectF(624, 536, 240, 24), QStringLiteral("Preview ready"), 16,
          NP::textPrimary(), QFont::DemiBold);
    label(painter, QRectF(624, 568, 240, 42),
          QStringLiteral("Overlay depth uses tone, one keyline, and a neutral shadow."), 12,
          NP::textSecondary());
}

void renderPlasma(QPainter &painter, const QSize &size)
{
    forgedBackdrop(painter, QRect(QPoint(), size));
    surface(painter, QRectF(16, 176, size.width() - 32, 64), NP::surfaceOverlay(),
            NP::edgeHighlight(), 8);
    painter.fillRect(QRectF(16, 176, size.width() - 32, 1), NP::edgeHighlight());
    surface(painter, QRectF(32, 188, 40, 40), NP::surfaceRaised());
    label(painter, QRectF(32, 188, 40, 40), QStringLiteral("N"), 16, NP::accent(),
          QFont::DemiBold, Qt::AlignCenter);
    for (int index = 0; index < 5; ++index) {
        const QRectF task(92 + index * 176, 188, 160, 40);
        if (index == 1) {
            surface(painter, task, NP::surfaceSelected(), Qt::transparent, 4);
            painter.fillRect(QRectF(task.left() + 16, task.bottom() - 3, 56, 3), NP::accent());
        }
        label(painter, task.adjusted(12, 0, -8, 0),
              index == 1 ? QStringLiteral("Active work") : QStringLiteral("Application %1").arg(index + 1),
              13, index == 1 ? NP::textPrimary() : NP::textSecondary());
    }
    label(painter, QRectF(size.width() - 260, 188, 212, 40),
          QStringLiteral("SV  10:42  82%"), 13, NP::textPrimary(), QFont::Medium,
          Qt::AlignRight | Qt::AlignVCenter);
    surface(painter, QRectF(size.width() - 432, 24, 400, 124), NP::surfaceOverlay(),
            NP::edgeHighlight(), 8);
    painter.fillRect(QRectF(size.width() - 416, 24, 96, 1), NP::edgeHighlight());
    label(painter, QRectF(size.width() - 400, 44, 320, 24),
          QStringLiteral("Build completed"), 16, NP::textPrimary(), QFont::DemiBold);
    label(painter, QRectF(size.width() - 400, 76, 320, 44),
          QStringLiteral("NoxForge passed the local design-system checks."), 13,
          NP::textSecondary());
}

void renderSession(QPainter &painter, const QSize &size)
{
    forgedBackdrop(painter, QRect(QPoint(), size));
    label(painter, QRectF(112, 88, 600, 90), QStringLiteral("10:42"), 64,
          NP::textPrimary(), QFont::Light);
    label(painter, QRectF(116, 172, 500, 30), QStringLiteral("Thursday, 30 July"), 14,
          NP::textSecondary());
    const QRectF card(180, 380, 620, 560);
    painter.fillRect(card.translated(0, 12), alpha(NP::background(), 150));
    surface(painter, card, NP::surfaceOverlay(), NP::edgeHighlight(), 8, NP::notch);
    painter.fillRect(QRectF(card.left() + 32, card.top(), 112, 1), NP::edgeHighlight());
    label(painter, QRectF(236, 440, 500, 42), QStringLiteral("Welcome back"), 24,
          NP::textPrimary(), QFont::DemiBold);
    label(painter, QRectF(236, 492, 500, 28),
          QStringLiteral("Sign in to your Plasma workspace"), 14, NP::textSecondary());
    label(painter, QRectF(236, 564, 500, 20), QStringLiteral("Password"), 12,
          NP::textSecondary());
    surface(painter, QRectF(236, 592, 508, 48), NP::surfaceSunken(), NP::outlineMuted());
    label(painter, QRectF(252, 592, 476, 48), QStringLiteral("••••••••••••"), 18,
          NP::textPrimary());
    button(painter, QRectF(236, 680, 508, 48), QStringLiteral("Sign in"), true);
    label(painter, QRectF(236, 760, 508, 24), QStringLiteral("Plasma (Wayland)"), 12,
          NP::textSecondary(), QFont::Normal, Qt::AlignCenter);
    label(painter, QRectF(size.width() - 620, size.height() - 116, 500, 32),
          QStringLiteral("NOXFORGE"), 16, NP::textPrimary(), QFont::DemiBold,
          Qt::AlignRight | Qt::AlignVCenter, 3);
}

void renderTabbox(QPainter &painter, const QSize &size)
{
    forgedBackdrop(painter, QRect(QPoint(), size));
    painter.fillRect(QRect(QPoint(), size), alpha(NP::background(), 168));
    const QRectF card(360, 410, size.width() - 720, 620);
    painter.fillRect(card.translated(0, 12), alpha(NP::background(), 168));
    surface(painter, card, NP::surfaceOverlay(), NP::edgeHighlight(), 8, NP::notch);
    label(painter, QRectF(card.left() + 56, card.top() + 40, card.width() - 112, 40),
          QStringLiteral("Switch window"), 24, NP::textPrimary(), QFont::DemiBold);
    const QStringList windows = {
        QStringLiteral("Documentation"),
        QStringLiteral("Konsole — NoxForge"),
        QStringLiteral("System settings"),
        QStringLiteral("Dolphin"),
    };
    for (int index = 0; index < windows.size(); ++index) {
        const QRectF row(card.left() + 56, card.top() + 116 + index * 104,
                         card.width() - 112, 80);
        if (index == 1) {
            surface(painter, row, NP::surfaceSelected(), Qt::transparent, 6);
            painter.fillRect(QRectF(row.left(), row.top() + 16, 3, 48), NP::accent());
        }
        surface(painter, QRectF(row.left() + 16, row.top() + 16, 48, 48),
                NP::surfaceRaised(), NP::outlineMuted(), 4);
        label(painter, QRectF(row.left() + 88, row.top(), row.width() - 112, row.height()),
              windows[index], 14, index == 1 ? NP::textPrimary() : NP::textSecondary(),
              index == 1 ? QFont::Medium : QFont::Normal);
    }
}

void renderBrandWallpaper(QPainter &painter, const QSize &size)
{
    forgedBackdrop(painter, QRect(QPoint(), size));
    const qreal center = size.width() / 2.0;
    label(painter, QRectF(48, 48, size.width() - 96, 32), QStringLiteral("KINETIC PRECISION"),
          11, NP::textSecondary(), QFont::DemiBold, Qt::AlignCenter, 2);
    painter.setPen(QPen(NP::textPrimary(), 12, Qt::SolidLine, Qt::SquareCap, Qt::MiterJoin));
    painter.drawLine(QPointF(center - 108, 190), QPointF(center - 68, 320));
    painter.drawLine(QPointF(center - 68, 320), QPointF(center - 16, 190));
    painter.drawLine(QPointF(center - 16, 190), QPointF(center + 24, 320));
    painter.drawLine(QPointF(center + 46, 320), QPointF(center + 86, 190));
    painter.drawLine(QPointF(center + 86, 190), QPointF(center + 146, 190));
    painter.drawLine(QPointF(center + 66, 254), QPointF(center + 126, 254));
    painter.setPen(QPen(NP::accent(), 4, Qt::SolidLine, Qt::SquareCap));
    painter.drawLine(QPointF(center - 106, 190), QPointF(center - 68, 316));
    painter.drawLine(QPointF(center + 86, 190), QPointF(center + 146, 190));
    label(painter, QRectF(48, 356, size.width() - 96, 48), QStringLiteral("NOXFORGE"), 24,
          NP::textPrimary(), QFont::DemiBold, Qt::AlignCenter, 3);
    label(painter, QRectF(64, size.height() - 120, size.width() - 128, 48),
          QStringLiteral("Graphite planes. One precise signal."), 14,
          NP::textSecondary(), QFont::Normal, Qt::AlignCenter);
}

void renderMotion(QPainter &painter, const QSize &size)
{
    painter.fillRect(QRect(QPoint(), size), NP::background());
    label(painter, QRectF(96, 64, size.width() - 192, 48),
          QStringLiteral("Container entrance · 180 ms"), 24, NP::textPrimary(),
          QFont::DemiBold);
    label(painter, QRectF(96, 112, size.width() - 192, 32),
          QStringLiteral("Opacity and an eight-pixel transform settle without spring or overshoot."),
          14, NP::textSecondary());
    const QStringList captions = {
        QStringLiteral("START · 0 MS"),
        QStringLiteral("MID · 90 MS"),
        QStringLiteral("SETTLED · 180 MS"),
    };
    const qreal gap = 40;
    const qreal frameWidth = (size.width() - 192 - gap * 2) / 3;
    for (int index = 0; index < 3; ++index) {
        const QRectF frame(96 + index * (frameWidth + gap), 200, frameWidth, 1080);
        surface(painter, frame, NP::surfaceSunken(), NP::outlineMuted(), 8);
        label(painter, QRectF(frame.left() + 24, frame.top() + 20, frame.width() - 48, 24),
              captions[index], 11, NP::textSecondary(), QFont::DemiBold,
              Qt::AlignLeft | Qt::AlignVCenter, 2);
        const qreal travel = index == 0 ? 8 : (index == 1 ? 3 : 0);
        const int alpha = index == 0 ? 92 : (index == 1 ? 196 : 255);
        QColor overlay = NP::surfaceOverlay();
        overlay.setAlpha(alpha);
        const QRectF panel(frame.left() + 64, frame.top() + 260 + travel,
                           frame.width() - 128, 420);
        surface(painter, panel, overlay, NP::edgeHighlight(), 8, NP::notch);
        label(painter, QRectF(panel.left() + 40, panel.top() + 44, panel.width() - 80, 36),
              QStringLiteral("Workspace ready"), 20, NP::textPrimary(), QFont::DemiBold);
        label(painter, QRectF(panel.left() + 40, panel.top() + 96, panel.width() - 80, 48),
              QStringLiteral("Position and opacity resolve together."), 13,
              NP::textSecondary());
        painter.fillRect(QRectF(panel.left() + 40, panel.bottom() - 72,
                                (panel.width() - 80) * (index + 1) / 3.0, 3),
                         NP::accent());
    }
    label(painter, QRectF(96, size.height() - 96, size.width() - 192, 32),
          QStringLiteral("Reduced motion: the settled frame appears immediately."),
          14, NP::textSecondary());
}

bool save(const QString &path, const QSize &size, void (*render)(QPainter &, const QSize &))
{
    QImage image(size, QImage::Format_ARGB32_Premultiplied);
    image.fill(Qt::transparent);
    QPainter painter(&image);
    painter.setRenderHints(QPainter::Antialiasing | QPainter::TextAntialiasing);
    render(painter, size);
    painter.end();
    return image.save(path, "PNG", 9);
}

} // namespace

int main(int argc, char **argv)
{
    QGuiApplication application(argc, argv);
    if (argc != 2) {
        return 2;
    }
    const QString output = QString::fromLocal8Bit(argv[1]);
    if (!QDir().mkpath(output)) {
        return 3;
    }
    const struct {
        const char *name;
        QSize size;
        void (*render)(QPainter &, const QSize &);
    } renders[] = {
        {"north-star-qt.png", {960, 760}, renderQt},
        {"north-star-plasma.png", {1680, 256}, renderPlasma},
        {"north-star-session.png", {2560, 1440}, renderSession},
        {"north-star-tabbox.png", {2560, 1440}, renderTabbox},
        {"north-star-brand-wallpaper.png", {568, 924}, renderBrandWallpaper},
        {"north-star-motion-storyboard.png", {2560, 1440}, renderMotion},
    };
    for (const auto &entry : renders) {
        if (!save(QDir(output).filePath(QString::fromLatin1(entry.name)), entry.size, entry.render)) {
            return 4;
        }
    }
    return 0;
}
