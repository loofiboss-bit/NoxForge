// SPDX-License-Identifier: MIT
#pragma once

#include <QColor>

namespace NoxForgePalette {

inline QColor background() { return QColor(QStringLiteral("#0E1318")); }
inline QColor surface() { return QColor(QStringLiteral("#141B21")); }
inline QColor surfaceRaised() { return QColor(QStringLiteral("#1A232B")); }
inline QColor surfaceHover() { return QColor(QStringLiteral("#202C34")); }
inline QColor surfaceSelected() { return QColor(QStringLiteral("#26361D")); }
inline QColor border() { return QColor(QStringLiteral("#2B3942")); }
inline QColor borderStrong() { return QColor(QStringLiteral("#3B4B55")); }
inline QColor textPrimary() { return QColor(QStringLiteral("#E8F0F2")); }
inline QColor textSecondary() { return QColor(QStringLiteral("#A6B4B9")); }
inline QColor textDisabled() { return QColor(QStringLiteral("#6F7C82")); }
inline QColor accent() { return QColor(QStringLiteral("#A3FF47")); }
inline QColor accentPressed() { return QColor(QStringLiteral("#82D936")); }
inline QColor accentInk() { return background(); }
inline QColor cyan() { return QColor(QStringLiteral("#22D3EE")); }
inline QColor violet() { return QColor(QStringLiteral("#A78BFA")); }
inline QColor negative() { return QColor(QStringLiteral("#FF6B7A")); }
inline QColor warning() { return QColor(QStringLiteral("#FBBF24")); }

constexpr int radius = 6;
constexpr int compactRadius = 4;
constexpr int notch = 4;
constexpr int borderWidth = 1;
constexpr int focusWidth = 2;
constexpr int controlHeight = 32;

} // namespace NoxForgePalette
