// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QFormLayout>
#include <QGroupBox>
#include <QImage>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QMainWindow>
#include <QMenuBar>
#include <QProgressBar>
#include <QPushButton>
#include <QRadioButton>
#include <QScrollBar>
#include <QSlider>
#include <QSpinBox>
#include <QStyleFactory>
#include <QTabWidget>
#include <QToolBar>
#include <QToolButton>
#include <QVBoxLayout>
#include <QWidget>

int main(int argc, char **argv)
{
    QApplication app(argc, argv);
    QStyle *style = QStyleFactory::create(QStringLiteral("NoxForge"));
    if (!style) return 1;
    app.setStyle(style);
    app.setPalette(style->standardPalette());

    if (QCoreApplication::arguments().contains(QStringLiteral("--rtl")))
        app.setLayoutDirection(Qt::RightToLeft);

    QMainWindow window;
    window.setWindowTitle(QStringLiteral("NoxForge Control Gallery"));
    window.resize(960, 760);
    auto *fileMenu = window.menuBar()->addMenu(QStringLiteral("&File"));
    fileMenu->addAction(QStringLiteral("New"));
    auto *save = fileMenu->addAction(QStringLiteral("Save"));
    save->setCheckable(true);
    save->setChecked(true);
    fileMenu->addSeparator();
    fileMenu->addMenu(QStringLiteral("Export"))->addAction(QStringLiteral("Archive"));
    window.menuBar()->addMenu(QStringLiteral("&Edit"));
    auto *toolbar = window.addToolBar(QStringLiteral("Precision tools"));
    toolbar->addAction(QStringLiteral("Inspect"));
    toolbar->addAction(QStringLiteral("Align"));

    auto *central = new QWidget;
    window.setCentralWidget(central);
    auto *rootLayout = new QVBoxLayout(central);
    rootLayout->setContentsMargins(24, 18, 24, 24);
    rootLayout->setSpacing(12);
    auto *tabs = new QTabWidget;
    rootLayout->addWidget(tabs);
    auto *controls = new QWidget;
    tabs->addTab(controls, QStringLiteral("Controls"));
    tabs->addTab(new QLabel(QStringLiteral("Secondary identity surface")), QStringLiteral("Details"));
    auto *layout = new QFormLayout(controls);
    layout->setContentsMargins(18, 18, 18, 18);
    layout->setSpacing(10);

    auto *primary = new QPushButton(QStringLiteral("Primary action"));
    primary->setDefault(true);
    layout->addRow(QStringLiteral("Default"), primary);
    layout->addRow(QStringLiteral("Disabled"), new QPushButton(QStringLiteral("Secondary action")));
    layout->itemAt(layout->count() - 1)->widget()->setEnabled(false);
    layout->addRow(QStringLiteral("Input"), new QLineEdit(QStringLiteral("Industrial precision")));
    auto *combo = new QComboBox;
    combo->addItems({QStringLiteral("Graphite"), QStringLiteral("Lime"), QStringLiteral("Cyan")});
    layout->addRow(QStringLiteral("Combo"), combo);
    auto *spin = new QSpinBox;
    spin->setRange(-20, 200);
    spin->setValue(44);
    layout->addRow(QStringLiteral("Spin"), spin);
    layout->addRow(QStringLiteral("Check"), new QCheckBox(QStringLiteral("Enabled")));
    qobject_cast<QCheckBox *>(layout->itemAt(layout->count() - 1)->widget())->setChecked(true);
    layout->addRow(QStringLiteral("Radio"), new QRadioButton(QStringLiteral("Selected")));
    qobject_cast<QRadioButton *>(layout->itemAt(layout->count() - 1)->widget())->setChecked(true);
    auto *slider = new QSlider(Qt::Horizontal);
    slider->setValue(62);
    layout->addRow(QStringLiteral("Slider"), slider);
    auto *progress = new QProgressBar;
    progress->setValue(68);
    layout->addRow(QStringLiteral("Progress"), progress);
    auto *scrollbar = new QScrollBar(Qt::Horizontal);
    scrollbar->setRange(0, 100);
    scrollbar->setPageStep(20);
    scrollbar->setValue(36);
    layout->addRow(QStringLiteral("Scroll"), scrollbar);
    auto *group = new QGroupBox(QStringLiteral("Forge group"));
    group->setCheckable(true);
    group->setChecked(true);
    auto *groupLayout = new QVBoxLayout(group);
    groupLayout->addWidget(new QLabel(QStringLiteral("Compact bordered component surface")));
    layout->addRow(QStringLiteral("Group"), group);
    auto *list = new QListWidget;
    list->addItems({QStringLiteral("Surface"), QStringLiteral("Selected surface"), QStringLiteral("Focus marker")});
    list->setCurrentRow(1);
    list->setMaximumHeight(110);
    layout->addRow(QStringLiteral("Items"), list);

    window.show();
    app.processEvents();
    QImage image(window.size() * window.devicePixelRatioF(), QImage::Format_ARGB32_Premultiplied);
    image.setDevicePixelRatio(window.devicePixelRatioF());
    image.fill(Qt::transparent);
    window.render(&image);
    if (image.isNull() || image.width() < 900 || image.height() < 700) return 2;
    QString output;
    for (const QString &argument : QCoreApplication::arguments().mid(1))
        if (!argument.startsWith(QLatin1String("--"))) output = argument;
    if (!output.isEmpty() && !image.save(output)) return 3;
    return 0;
}
