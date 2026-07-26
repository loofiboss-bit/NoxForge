// SPDX-License-Identifier: MIT
#include <QApplication>
#include <QCheckBox>
#include <QComboBox>
#include <QDial>
#include <QFormLayout>
#include <QGridLayout>
#include <QGroupBox>
#include <QHeaderView>
#include <QHBoxLayout>
#include <QImage>
#include <QLabel>
#include <QLineEdit>
#include <QListWidget>
#include <QMainWindow>
#include <QMenu>
#include <QMenuBar>
#include <QProgressBar>
#include <QPushButton>
#include <QRadioButton>
#include <QScrollBar>
#include <QSlider>
#include <QSpinBox>
#include <QStyleFactory>
#include <QTabBar>
#include <QTabWidget>
#include <QTableWidget>
#include <QTextEdit>
#include <QToolBar>
#include <QToolButton>
#include <QTreeWidget>
#include <QVBoxLayout>
#include <QWidget>

namespace {

QWidget *controlsPage(QPushButton **focusTarget)
{
    auto *page = new QWidget;
    auto *layout = new QFormLayout(page);
    layout->setContentsMargins(18, 18, 18, 18);
    layout->setSpacing(10);

    auto *primary = new QPushButton(QStringLiteral("Primary action"));
    primary->setDefault(true);
    *focusTarget = primary;
    layout->addRow(QStringLiteral("Default"), primary);
    auto *disabled = new QPushButton(QStringLiteral("Secondary action"));
    disabled->setEnabled(false);
    layout->addRow(QStringLiteral("Disabled"), disabled);
    layout->addRow(QStringLiteral("Input"), new QLineEdit(QStringLiteral("Industrial precision")));
    auto *combo = new QComboBox;
    combo->addItems({QStringLiteral("Graphite"), QStringLiteral("Lime"), QStringLiteral("Cyan")});
    layout->addRow(QStringLiteral("Combo"), combo);
    auto *spin = new QSpinBox;
    spin->setRange(-20, 200);
    spin->setValue(44);
    layout->addRow(QStringLiteral("Spin"), spin);
    auto *check = new QCheckBox(QStringLiteral("Enabled"));
    check->setChecked(true);
    layout->addRow(QStringLiteral("Check"), check);
    auto *radio = new QRadioButton(QStringLiteral("Selected"));
    radio->setChecked(true);
    layout->addRow(QStringLiteral("Radio"), radio);
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
    list->addItems({QStringLiteral("Surface"), QStringLiteral("Selected surface"),
                    QStringLiteral("Focus marker")});
    list->setCurrentRow(1);
    list->setMaximumHeight(110);
    layout->addRow(QStringLiteral("Items"), list);
    return page;
}

QWidget *dataPage()
{
    auto *page = new QWidget;
    auto *layout = new QVBoxLayout(page);
    layout->setContentsMargins(18, 18, 18, 18);
    layout->setSpacing(12);
    auto *heading = new QLabel(QStringLiteral("Dense application surfaces"));
    QFont headingFont = heading->font();
    headingFont.setBold(true);
    heading->setFont(headingFont);
    layout->addWidget(heading);
    auto *table = new QTableWidget(3, 3);
    table->setHorizontalHeaderLabels({QStringLiteral("State"), QStringLiteral("Owner"),
                                      QStringLiteral("Result")});
    table->horizontalHeader()->setStretchLastSection(true);
    table->horizontalHeader()->setSortIndicator(0, Qt::AscendingOrder);
    table->horizontalHeader()->setSortIndicatorShown(true);
    const QStringList values = {
        QStringLiteral("Ready"), QStringLiteral("Forge"), QStringLiteral("Passed"),
        QStringLiteral("Waiting"), QStringLiteral("Shell"), QStringLiteral("Pending"),
        QStringLiteral("Disabled"), QStringLiteral("System"), QStringLiteral("Unavailable"),
    };
    for (int row = 0; row < 3; ++row)
        for (int column = 0; column < 3; ++column)
            table->setItem(row, column, new QTableWidgetItem(values.at(row * 3 + column)));
    table->setCurrentCell(0, 0);
    table->setMaximumHeight(150);
    layout->addWidget(table);
    auto *tree = new QTreeWidget;
    tree->setHeaderLabels({QStringLiteral("Component"), QStringLiteral("Coverage")});
    auto *shell = new QTreeWidgetItem(tree, {QStringLiteral("Plasma shell"),
                                             QStringLiteral("Complete")});
    new QTreeWidgetItem(shell, {QStringLiteral("Panel edges"), QStringLiteral("4")});
    new QTreeWidgetItem(shell, {QStringLiteral("Scale captures"), QStringLiteral("4")});
    shell->setExpanded(true);
    tree->setMaximumHeight(130);
    layout->addWidget(tree);
    auto *notes = new QTextEdit;
    notes->setPlainText(QStringLiteral(
        "Long-form editable content remains readable without nested decoration."));
    notes->setMaximumHeight(88);
    layout->addWidget(notes);
    auto *row = new QHBoxLayout;
    auto *verticalSlider = new QSlider(Qt::Vertical);
    verticalSlider->setValue(64);
    verticalSlider->setMaximumHeight(100);
    row->addWidget(verticalSlider);
    auto *verticalScroll = new QScrollBar(Qt::Vertical);
    verticalScroll->setRange(0, 100);
    verticalScroll->setPageStep(25);
    verticalScroll->setValue(40);
    verticalScroll->setMaximumHeight(100);
    row->addWidget(verticalScroll);
    row->addStretch();
    layout->addLayout(row);
    return page;
}

QWidget *menuPage()
{
    auto *page = new QWidget;
    auto *layout = new QGridLayout(page);
    layout->setContentsMargins(18, 18, 18, 18);
    layout->setSpacing(16);

    auto *menu = new QMenu;
    menu->setWindowFlags(Qt::Widget);
    menu->addAction(QStringLiteral("&New configuration\tCtrl+N"));
    auto *checked = menu->addAction(QStringLiteral("&Lock geometry\tCtrl+L"));
    checked->setCheckable(true);
    checked->setChecked(true);
    menu->addSeparator();
    menu->addMenu(QStringLiteral("Export"))->addAction(QStringLiteral("Archive"));
    auto *disabled = menu->addAction(QStringLiteral("Unavailable action"));
    disabled->setEnabled(false);
    menu->setSizePolicy(QSizePolicy::Expanding, QSizePolicy::Preferred);
    menu->setMinimumWidth(360);
    menu->setMinimumHeight(170);
    layout->addWidget(new QLabel(QStringLiteral("Menu and command surfaces")), 0, 0, 1, 2);
    layout->addWidget(menu, 1, 0, 3, 1);

    auto *instant = new QToolButton;
    instant->setText(QStringLiteral("Instant popup"));
    instant->setPopupMode(QToolButton::InstantPopup);
    auto *instantMenu = new QMenu(instant);
    instantMenu->addAction(QStringLiteral("Inspect"));
    instantMenu->addAction(QStringLiteral("Align"));
    instant->setMenu(instantMenu);
    layout->addWidget(instant, 1, 1);
    auto *split = new QToolButton;
    split->setText(QStringLiteral("Split action"));
    split->setPopupMode(QToolButton::MenuButtonPopup);
    split->setMenu(instantMenu);
    layout->addWidget(split, 2, 1);
    auto *choice = new QComboBox;
    choice->addItems({QStringLiteral("Compact"), QStringLiteral("Comfortable"),
                      QStringLiteral("Dense")});
    layout->addWidget(choice, 3, 1);
    layout->setRowStretch(4, 1);
    return page;
}

QWidget *statesPage()
{
    auto *page = new QWidget;
    auto *layout = new QGridLayout(page);
    layout->setContentsMargins(18, 18, 18, 18);
    layout->setHorizontalSpacing(16);
    layout->setVerticalSpacing(12);
    layout->addWidget(new QLabel(QStringLiteral("Native interaction state coverage")), 0, 0, 1, 3);

    auto *normal = new QPushButton(QStringLiteral("Default"));
    auto *focused = new QPushButton(QStringLiteral("Focused"));
    focused->setDefault(true);
    auto *pressed = new QPushButton(QStringLiteral("Checked"));
    pressed->setCheckable(true);
    pressed->setChecked(true);
    auto *disabled = new QPushButton(QStringLiteral("Disabled"));
    disabled->setEnabled(false);
    layout->addWidget(normal, 1, 0);
    layout->addWidget(focused, 1, 1);
    layout->addWidget(pressed, 1, 2);
    layout->addWidget(disabled, 2, 0);

    auto *unchecked = new QCheckBox(QStringLiteral("Unchecked"));
    auto *checked = new QCheckBox(QStringLiteral("Checked"));
    checked->setChecked(true);
    auto *mixed = new QCheckBox(QStringLiteral("Mixed / tri-state"));
    mixed->setTristate(true);
    mixed->setCheckState(Qt::PartiallyChecked);
    layout->addWidget(unchecked, 3, 0);
    layout->addWidget(checked, 3, 1);
    layout->addWidget(mixed, 3, 2);

    auto *busy = new QProgressBar;
    busy->setRange(0, 0);
    busy->setFormat(QStringLiteral("Busy"));
    layout->addWidget(new QLabel(QStringLiteral("Static reduced-motion busy state")), 4, 0);
    layout->addWidget(busy, 4, 1, 1, 2);
    auto *selected = new QListWidget;
    selected->addItems({QStringLiteral("Default row"), QStringLiteral("Selected row"),
                        QStringLiteral("Disabled row")});
    selected->setCurrentRow(1);
    selected->item(2)->setFlags(selected->item(2)->flags() & ~Qt::ItemIsEnabled);
    selected->setMaximumHeight(110);
    layout->addWidget(selected, 5, 0, 1, 3);
    layout->setRowStretch(6, 1);
    focused->setFocus(Qt::OtherFocusReason);
    return page;
}

QWidget *stressPage()
{
    auto *page = new QWidget;
    auto *layout = new QVBoxLayout(page);
    layout->setContentsMargins(18, 18, 18, 18);
    layout->setSpacing(12);
    layout->addWidget(new QLabel(QStringLiteral(
        "Stress surface — long labels, close indicators, dense geometry, and extremes")));
    auto *closable = new QTabBar;
    closable->setTabsClosable(true);
    closable->addTab(QStringLiteral("Short"));
    closable->addTab(QStringLiteral(
        "A deliberately long localized tab label that must remain geometrically safe"));
    closable->addTab(QStringLiteral("آخر"));
    closable->setCurrentIndex(1);
    layout->addWidget(closable);
    auto *form = new QFormLayout;
    auto *longInput = new QLineEdit(QStringLiteral(
        "A long editable value with 0123456789 punctuation — / : [ ]"));
    form->addRow(QStringLiteral("Long visible label with mnemonic &Name"), longInput);
    auto *extremeSpin = new QSpinBox;
    extremeSpin->setRange(-999999, 999999);
    extremeSpin->setValue(-999999);
    form->addRow(QStringLiteral("Extreme"), extremeSpin);
    layout->addLayout(form);
    auto *dense = new QHBoxLayout;
    auto *dial = new QDial;
    dial->setValue(73);
    dial->setMaximumSize(92, 92);
    dense->addWidget(dial);
    auto *vertical = new QSlider(Qt::Vertical);
    vertical->setInvertedAppearance(true);
    vertical->setValue(85);
    vertical->setMaximumHeight(110);
    dense->addWidget(vertical);
    auto *scroll = new QScrollBar(Qt::Vertical);
    scroll->setRange(0, 1000);
    scroll->setPageStep(1);
    scroll->setValue(999);
    scroll->setMaximumHeight(110);
    dense->addWidget(scroll);
    auto *text = new QTextEdit(QStringLiteral(
        "Multiline text\nSecond line with mixed العربية and Latin content.\n"
        "Keyboard focus and clipping remain inspectable."));
    text->setMaximumHeight(120);
    dense->addWidget(text, 1);
    layout->addLayout(dense);
    layout->addStretch();
    return page;
}

QString requestedPage()
{
    const QStringList arguments = QCoreApplication::arguments();
    if (arguments.contains(QStringLiteral("--data")))
        return QStringLiteral("data");
    for (const QString &argument : arguments)
        if (argument.startsWith(QStringLiteral("--page=")))
            return argument.mid(7);
    return QStringLiteral("controls");
}

} // namespace

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
    window.setWindowTitle(QStringLiteral("NoxForge Native Qt Gallery"));
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
    auto *rootLayout = new QVBoxLayout(central);
    rootLayout->setContentsMargins(24, 18, 24, 24);
    rootLayout->setSpacing(12);
    auto *tabs = new QTabWidget;
    QPushButton *focusTarget = nullptr;
    const QList<QPair<QString, QWidget *>> pages = {
        {QStringLiteral("controls"), controlsPage(&focusTarget)},
        {QStringLiteral("data"), dataPage()},
        {QStringLiteral("menu"), menuPage()},
        {QStringLiteral("states"), statesPage()},
        {QStringLiteral("stress"), stressPage()},
    };
    for (const auto &[name, page] : pages)
        tabs->addTab(page, name.at(0).toUpper() + name.mid(1));
    rootLayout->addWidget(tabs);
    window.setCentralWidget(central);

    const QString pageName = requestedPage();
    for (int index = 0; index < pages.size(); ++index)
        if (pages.at(index).first == pageName)
            tabs->setCurrentIndex(index);
    window.show();
    if (pageName == QStringLiteral("controls") && focusTarget)
        focusTarget->setFocus(Qt::OtherFocusReason);
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
