// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QFormLayout>
#include <QGroupBox>
#include <QHeaderView>
#include <QHBoxLayout>
#include <QImage>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QMainWindow>
#include <QMenuBar>
#include <QMenu>
#include <QProgressBar>
#include <QPushButton>
#include <QRadioButton>
#include <QScrollBar>
#include <QSlider>
#include <QSpinBox>
#include <QStyleFactory>
#include <QTabWidget>
#include <QTableWidget>
#include <QTextEdit>
#include <QToolBar>
#include <QToolButton>
#include <QTreeWidget>
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
    auto *dataPage = new QWidget;
    tabs->addTab(dataPage, QStringLiteral("Data"));
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

    auto *dataLayout = new QVBoxLayout(dataPage);
    dataLayout->setContentsMargins(18, 18, 18, 18);
    dataLayout->setSpacing(12);
    auto *dataHeading = new QLabel(QStringLiteral("Dense application surfaces"));
    QFont headingFont = dataHeading->font();
    headingFont.setBold(true);
    dataHeading->setFont(headingFont);
    dataLayout->addWidget(dataHeading);
    auto *table = new QTableWidget(3, 3);
    table->setHorizontalHeaderLabels({QStringLiteral("State"), QStringLiteral("Owner"), QStringLiteral("Result")});
    table->horizontalHeader()->setStretchLastSection(true);
    const QStringList tableValues = {
        QStringLiteral("Ready"), QStringLiteral("Forge"), QStringLiteral("Passed"),
        QStringLiteral("Waiting"), QStringLiteral("Shell"), QStringLiteral("Pending"),
        QStringLiteral("Disabled"), QStringLiteral("System"), QStringLiteral("Unavailable"),
    };
    for (int row = 0; row < 3; ++row)
        for (int column = 0; column < 3; ++column)
            table->setItem(row, column, new QTableWidgetItem(tableValues.at(row * 3 + column)));
    table->setCurrentCell(0, 0);
    table->setMaximumHeight(150);
    dataLayout->addWidget(table);
    auto *tree = new QTreeWidget;
    tree->setHeaderLabels({QStringLiteral("Component"), QStringLiteral("Coverage")});
    auto *shell = new QTreeWidgetItem(tree, {QStringLiteral("Plasma shell"), QStringLiteral("Complete")});
    new QTreeWidgetItem(shell, {QStringLiteral("Panel edges"), QStringLiteral("4")});
    new QTreeWidgetItem(shell, {QStringLiteral("Scale captures"), QStringLiteral("4")});
    shell->setExpanded(true);
    tree->setMaximumHeight(120);
    dataLayout->addWidget(tree);
    auto *notes = new QTextEdit;
    notes->setPlainText(QStringLiteral("Long-form editable content remains readable without nested decoration."));
    notes->setMaximumHeight(88);
    dataLayout->addWidget(notes);
    auto *stateRow = new QHBoxLayout;
    auto *verticalSlider = new QSlider(Qt::Vertical);
    verticalSlider->setValue(64);
    verticalSlider->setMaximumHeight(100);
    stateRow->addWidget(verticalSlider);
    auto *verticalScroll = new QScrollBar(Qt::Vertical);
    verticalScroll->setRange(0, 100);
    verticalScroll->setPageStep(25);
    verticalScroll->setValue(40);
    verticalScroll->setMaximumHeight(100);
    stateRow->addWidget(verticalScroll);
    auto *popupButton = new QToolButton;
    popupButton->setText(QStringLiteral("Popup states"));
    popupButton->setPopupMode(QToolButton::InstantPopup);
    auto *popupMenu = new QMenu(popupButton);
    auto *checkedAction = popupMenu->addAction(QStringLiteral("Checked action"));
    checkedAction->setCheckable(true);
    checkedAction->setChecked(true);
    auto *disabledAction = popupMenu->addAction(QStringLiteral("Disabled action with a deliberately long label"));
    disabledAction->setEnabled(false);
    popupButton->setMenu(popupMenu);
    stateRow->addWidget(popupButton, 1);
    dataLayout->addLayout(stateRow);

    if (QCoreApplication::arguments().contains(QStringLiteral("--data")))
        tabs->setCurrentWidget(dataPage);

    window.show();
    if (!QCoreApplication::arguments().contains(QStringLiteral("--data")))
        primary->setFocus(Qt::OtherFocusReason);
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
