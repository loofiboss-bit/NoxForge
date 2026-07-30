// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QFormLayout>
#include <QHBoxLayout>
#include <QImage>
#include <QLabel>
#include <QProgressBar>
#include <QPushButton>
#include <QRadioButton>
#include <QScrollBar>
#include <QSlider>
#include <QStyle>
#include <QStyleFactory>
#include <QTabBar>
#include <QTextStream>
#include <QToolButton>
#include <QVBoxLayout>
#include <QWidget>

namespace {

void forceProgress(QWidget *widget, qreal progress)
{
    for (const char *property : {
             "_noxforgeMotionTestHover",
             "_noxforgeMotionTestPress",
             "_noxforgeMotionTestChecked",
             "_noxforgeMotionTestBusy",
         })
        widget->setProperty(property, progress);
}

QLabel *sectionLabel(const QString &text)
{
    auto *label = new QLabel(text);
    QFont font = label->font();
    font.setBold(true);
    label->setFont(font);
    return label;
}

} // namespace

int main(int argc, char **argv)
{
    QApplication application(argc, argv);
    if (argc != 3) {
        QTextStream(stderr) << "usage: noxforge_motion_state_renderer OUTPUT PROGRESS\n";
        return 1;
    }
    bool valid = false;
    const qreal progress = QString::fromLocal8Bit(argv[2]).toDouble(&valid);
    if (!valid || progress < 0.0 || progress > 1.0)
        return 2;

    QStyle *style = QStyleFactory::create(QStringLiteral("NoxForge"));
    if (!style)
        return 3;
    application.setStyle(style);
    application.setPalette(style->standardPalette());

    QWidget window;
    window.setWindowTitle(QStringLiteral("NoxForge deterministic motion states"));
    window.resize(960, 540);
    auto *root = new QVBoxLayout(&window);
    root->setContentsMargins(28, 24, 28, 24);
    root->setSpacing(16);

    auto *title = new QLabel(QStringLiteral("Kinetic Precision — deterministic transition state"));
    QFont titleFont = title->font();
    titleFont.setPixelSize(22);
    titleFont.setBold(true);
    title->setFont(titleFont);
    root->addWidget(title);
    root->addWidget(new QLabel(QStringLiteral(
        "The same public QStyle path is rendered at 0, 50, and 100 percent.")));

    auto *columns = new QHBoxLayout;
    columns->setSpacing(28);
    auto *actions = new QFormLayout;
    actions->setSpacing(12);
    actions->addRow(sectionLabel(QStringLiteral("Actions and choices")));

    auto *primary = new QPushButton(QStringLiteral("Forge changes"));
    primary->setDefault(true);
    primary->setDown(true);
    primary->setAttribute(Qt::WA_UnderMouse, true);
    forceProgress(primary, progress);
    actions->addRow(QStringLiteral("Primary"), primary);

    auto *secondary = new QPushButton(QStringLiteral("Review details"));
    secondary->setAttribute(Qt::WA_UnderMouse, true);
    forceProgress(secondary, progress);
    actions->addRow(QStringLiteral("Secondary"), secondary);

    auto *tool = new QToolButton;
    tool->setText(QStringLiteral("Precision tool"));
    tool->setAttribute(Qt::WA_UnderMouse, true);
    forceProgress(tool, progress);
    actions->addRow(QStringLiteral("Tool"), tool);

    auto *check = new QCheckBox(QStringLiteral("Semantic state enabled"));
    check->setChecked(true);
    forceProgress(check, progress);
    actions->addRow(QStringLiteral("Check"), check);

    auto *radio = new QRadioButton(QStringLiteral("Selected profile"));
    radio->setChecked(true);
    forceProgress(radio, progress);
    actions->addRow(QStringLiteral("Radio"), radio);

    auto *combo = new QComboBox;
    combo->addItems({QStringLiteral("Graphite"), QStringLiteral("Neutral"),
                     QStringLiteral("Accent")});
    combo->setAttribute(Qt::WA_UnderMouse, true);
    forceProgress(combo, progress);
    actions->addRow(QStringLiteral("Combo"), combo);
    columns->addLayout(actions, 1);

    auto *precision = new QFormLayout;
    precision->setSpacing(12);
    precision->addRow(sectionLabel(QStringLiteral("Position and progress")));

    auto *tabs = new QTabBar;
    tabs->addTab(QStringLiteral("Default"));
    tabs->addTab(QStringLiteral("Motion"));
    tabs->addTab(QStringLiteral("Reduced"));
    tabs->setCurrentIndex(1);
    tabs->setAttribute(Qt::WA_UnderMouse, true);
    forceProgress(tabs, progress);
    precision->addRow(QStringLiteral("Tabs"), tabs);

    auto *slider = new QSlider(Qt::Horizontal);
    slider->setValue(62);
    slider->setAttribute(Qt::WA_UnderMouse, true);
    forceProgress(slider, progress);
    precision->addRow(QStringLiteral("Slider"), slider);

    auto *scroll = new QScrollBar(Qt::Horizontal);
    scroll->setRange(0, 100);
    scroll->setPageStep(20);
    scroll->setValue(36);
    scroll->setAttribute(Qt::WA_UnderMouse, true);
    forceProgress(scroll, progress);
    precision->addRow(QStringLiteral("Scrollbar"), scroll);

    auto *busy = new QProgressBar;
    busy->setRange(0, 0);
    busy->setFormat(QStringLiteral("Busy"));
    forceProgress(busy, progress);
    precision->addRow(QStringLiteral("Busy"), busy);

    auto *determinate = new QProgressBar;
    determinate->setRange(0, 100);
    determinate->setValue(qRound(progress * 100.0));
    determinate->setFormat(QStringLiteral("%p%"));
    precision->addRow(QStringLiteral("Determinate"), determinate);
    columns->addLayout(precision, 1);
    root->addLayout(columns, 1);

    auto *footer = new QLabel(QStringLiteral(
        "Motion changes color, opacity, indicator extent, and shallow elevation only."));
    footer->setAlignment(Qt::AlignRight);
    root->addWidget(footer);

    window.show();
    application.processEvents();
    QImage image(window.size(), QImage::Format_ARGB32_Premultiplied);
    image.fill(Qt::transparent);
    window.render(&image);
    if (image.isNull() || !image.save(QString::fromLocal8Bit(argv[1])))
        return 4;
    return 0;
}
