// SPDX-License-Identifier: MIT
#include <QAbstractListModel>
#include <QDateTime>
#include <QDir>
#include <QFile>
#include <QGuiApplication>
#include <QImage>
#include <QIcon>
#include <QLocale>
#include <QQmlContext>
#include <QQuickItem>
#include <QQuickView>
#include <QRect>
#include <QTimer>
#include <QTemporaryDir>
#include <QUrl>
#include <QVariantList>

class SessionModel final : public QAbstractListModel
{
    Q_OBJECT
    Q_PROPERTY(int lastIndex READ lastIndex CONSTANT)
public:
    enum Role { NameRole = Qt::UserRole + 1 };
    explicit SessionModel(bool longText, QObject *parent = nullptr)
        : QAbstractListModel(parent)
        , m_longText(longText)
    {
    }
    int rowCount(const QModelIndex &parent = {}) const override { return parent.isValid() ? 0 : 2; }
    QVariant data(const QModelIndex &index, int role) const override
    {
        if (!index.isValid() || role != NameRole) {
            return {};
        }
        if (m_longText) {
            return index.row() == 0
                ? QStringLiteral("Plasma-Arbeitsbereich (Wayland, vollständige Sitzung)")
                : QStringLiteral("Plasma-Arbeitsbereich (X11, Kompatibilitätssitzung)");
        }
        return index.row() == 0 ? QStringLiteral("Plasma (Wayland)") : QStringLiteral("Plasma (X11)");
    }
    QHash<int, QByteArray> roleNames() const override { return {{NameRole, "name"}}; }
    int lastIndex() const { return 0; }

private:
    bool m_longText;
};

class WindowModel final : public QAbstractListModel
{
    Q_OBJECT
public:
    enum Role {
        CaptionRole = Qt::UserRole + 1,
        IconRole,
        MinimizedRole,
    };
    explicit WindowModel(bool empty, bool longText, bool many, QObject *parent = nullptr)
        : QAbstractListModel(parent)
        , m_count(empty ? 0 : many ? 12 : 5)
        , m_longText(longText)
    {
    }
    int rowCount(const QModelIndex &parent = {}) const override { return parent.isValid() ? 0 : m_count; }
    QVariant data(const QModelIndex &index, int role) const override
    {
        if (!index.isValid()) {
            return {};
        }
        switch (role) {
        case CaptionRole:
            if (m_longText && index.row() == 0) {
                return QStringLiteral("Ein außergewöhnlich langer lokalisierter Fenstertitel zur Prüfung der Auslassung");
            }
            return QStringLiteral("NoxForge window %1").arg(index.row() + 1);
        case IconRole:
            return QStringLiteral("applications-system");
        case MinimizedRole:
            return index.row() == 3;
        default:
            return {};
        }
    }
    QHash<int, QByteArray> roleNames() const override
    {
        return {
            {CaptionRole, "caption"},
            {IconRole, "icon"},
            {MinimizedRole, "minimized"},
        };
    }
    Q_INVOKABLE void activate(int index) { m_lastActivated = index; }

private:
    int m_count;
    bool m_longText;
    int m_lastActivated = -1;
};

class UserModel final : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QString lastUser READ lastUser CONSTANT)
public:
    explicit UserModel(bool longText, QObject *parent = nullptr)
        : QObject(parent)
        , m_longText(longText)
    {
    }
    QString lastUser() const
    {
        return m_longText ? QStringLiteral("alexandra-mustermann-mit-langem-benutzernamen") : QStringLiteral("loofi");
    }

private:
    bool m_longText;
};

class Keyboard final : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QVariantList layouts READ layouts CONSTANT)
    Q_PROPERTY(int currentLayout READ currentLayout WRITE setCurrentLayout NOTIFY currentLayoutChanged)
public:
    explicit Keyboard(bool longText, QObject *parent = nullptr)
        : QObject(parent)
        , m_longText(longText)
    {
    }
    QVariantList layouts() const
    {
        return {
            QVariantMap{{QStringLiteral("longName"), m_longText
                    ? QStringLiteral("Deutsch (Schweiz, erweiterte Tastatur)")
                    : QStringLiteral("Swedish")}},
            QVariantMap{{QStringLiteral("longName"), QStringLiteral("English (US)")}},
        };
    }
    int currentLayout() const { return m_currentLayout; }
    void setCurrentLayout(int value)
    {
        if (m_currentLayout != value) {
            m_currentLayout = value;
            Q_EMIT currentLayoutChanged();
        }
    }
Q_SIGNALS:
    void currentLayoutChanged();

private:
    bool m_longText;
    int m_currentLayout = 0;
};

class Sddm final : public QObject
{
    Q_OBJECT
    Q_PROPERTY(bool canSuspend READ available CONSTANT)
    Q_PROPERTY(bool canReboot READ available CONSTANT)
    Q_PROPERTY(bool canPowerOff READ available CONSTANT)
public:
    using QObject::QObject;
    bool available() const { return true; }
    Q_INVOKABLE void login(const QString &, const QString &, int) {}
    Q_INVOKABLE void suspend() {}
    Q_INVOKABLE void reboot() {}
    Q_INVOKABLE void powerOff() {}
Q_SIGNALS:
    void loginFailed();
    void loginSucceeded();
};

class Config final : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QUrl background READ background CONSTANT)
public:
    explicit Config(const QUrl &background, QObject *parent = nullptr)
        : QObject(parent)
        , m_background(background)
    {
    }
    QUrl background() const { return m_background; }

private:
    QUrl m_background;
};

static void setPropertyIfPresent(QObject *object, const char *name, const QVariant &value)
{
    if (object->metaObject()->indexOfProperty(name) >= 0) {
        object->setProperty(name, value);
    }
}

int main(int argc, char **argv)
{
    if (argc != 9) {
        return 2;
    }
    QTemporaryDir isolatedRuntime(QStringLiteral("noxforge-session-renderer-XXXXXX"));
    if (!isolatedRuntime.isValid()) {
        return 5;
    }
    const QString repositoryRoot = QString::fromLocal8Bit(argv[8]);
    const QString configRoot = isolatedRuntime.path() + QStringLiteral("/config");
    QDir().mkpath(configRoot);
    QFile plasmaConfig(configRoot + QStringLiteral("/plasmarc"));
    if (!plasmaConfig.open(QIODevice::WriteOnly | QIODevice::Text)) {
        return 5;
    }
    plasmaConfig.write(
        "[Theme]\n"
        "name=io.github.loofiboss.noxforge.desktop\n");
    plasmaConfig.close();
    qputenv("XDG_CONFIG_HOME", configRoot.toUtf8());
    const QByteArray existingDataDirs = qgetenv("XDG_DATA_DIRS");
    qputenv(
        "XDG_DATA_DIRS",
        repositoryRoot.toUtf8() + ":"
            + (existingDataDirs.isEmpty() ? QByteArray("/usr/share") : existingDataDirs));
    qputenv("KDE_SESSION_VERSION", "6");
    const QString scenarioArgument = QString::fromLocal8Bit(argv[7]);
    QString scenario = scenarioArgument;
    qreal testProgress = 1.0;
    if (scenario.endsWith(QStringLiteral("-start"))) {
        scenario.chop(6);
        testProgress = 0.0;
    } else if (scenario.endsWith(QStringLiteral("-mid"))) {
        scenario.chop(4);
        testProgress = 0.5;
    } else if (scenario.endsWith(QStringLiteral("-end"))) {
        scenario.chop(4);
    }
    const bool rtl = scenario == QStringLiteral("long-rtl");
    if (rtl) {
        QLocale::setDefault(QLocale(QStringLiteral("ar_EG")));
    }
    QGuiApplication app(argc, argv);
    QStringList iconPaths = QIcon::themeSearchPaths();
    iconPaths.prepend(repositoryRoot + QStringLiteral("/icons"));
    QIcon::setThemeSearchPaths(iconPaths);
    QIcon::setThemeName(QStringLiteral("NoxForge"));
    if (rtl) {
        app.setLayoutDirection(Qt::RightToLeft);
    }

    const QString surface = QString::fromLocal8Bit(argv[1]);
    const QUrl qml = QUrl::fromLocalFile(QString::fromLocal8Bit(argv[2]));
    const QString output = QString::fromLocal8Bit(argv[4]);
    const int width = QString::fromLocal8Bit(argv[5]).toInt();
    const int height = QString::fromLocal8Bit(argv[6]).toInt();
    if (width < 1 || height < 1) {
        return 2;
    }

    const bool longText = scenario == QStringLiteral("long-rtl");
    const bool empty = scenario == QStringLiteral("empty")
        || scenario == QStringLiteral("empty-reduced");
    const bool reduced = scenario == QStringLiteral("reduced")
        || scenario == QStringLiteral("empty-reduced");
    const bool many = scenario == QStringLiteral("many");
    Config config(QUrl::fromLocalFile(QString::fromLocal8Bit(argv[3])));
    SessionModel sessions(longText);
    WindowModel windows(empty, longText, many);
    UserModel users(longText);
    Keyboard keyboard(longText);
    Sddm sddm;
    QQuickView view;
    view.setColor(QColor(QStringLiteral("#0E1318")));
    view.setResizeMode(QQuickView::SizeRootObjectToView);
    view.rootContext()->setContextProperty(QStringLiteral("config"), &config);
    view.rootContext()->setContextProperty(QStringLiteral("sessionModel"), &sessions);
    view.rootContext()->setContextProperty(QStringLiteral("userModel"), &users);
    view.rootContext()->setContextProperty(QStringLiteral("keyboard"), &keyboard);
    view.rootContext()->setContextProperty(QStringLiteral("sddm"), &sddm);
    view.rootContext()->setContextProperty(QStringLiteral("screenGeometry"), QRect(0, 0, width, height));
    view.setSource(qml);
    if (view.status() == QQuickView::Error || !view.rootObject()) {
        return 3;
    }

    QObject *root = view.rootObject();
    setPropertyIfPresent(root, "testProgress", testProgress);
    if (surface == QStringLiteral("splash")) {
        setPropertyIfPresent(root, "stage", qRound(testProgress * 5));
    } else if (surface == QStringLiteral("tabbox")) {
        setPropertyIfPresent(root, "compositionMode", true);
        setPropertyIfPresent(root, "windowModel", QVariant::fromValue(static_cast<QObject *>(&windows)));
        setPropertyIfPresent(root, "screenGeometry", QRect(0, 0, width, height));
        setPropertyIfPresent(root, "currentIndex", 1);
    }
    if (surface == QStringLiteral("sddm")) {
        setPropertyIfPresent(root, "freezeClock", true);
        setPropertyIfPresent(root, "currentDateTime", QDateTime(QDate(2026, 7, 26), QTime(8, 30)));
    }
    if (reduced) {
        setPropertyIfPresent(root, "reducedMotion", true);
    }
    if (longText && surface == QStringLiteral("sddm")) {
        setPropertyIfPresent(
            root,
            "statusMessage",
            QStringLiteral("Die Anmeldung ist vorübergehend nicht verfügbar. Bitte prüfen Sie Ihre Zugangsdaten."));
        setPropertyIfPresent(root, "statusDanger", true);
        setPropertyIfPresent(root, "sessionMenuOpen", true);
    }
    if (scenario == QStringLiteral("error") && surface == QStringLiteral("sddm")) {
        setPropertyIfPresent(root, "statusMessage", QStringLiteral("Login failed"));
        setPropertyIfPresent(root, "statusDanger", true);
    }
    if (scenario == QStringLiteral("busy") && surface == QStringLiteral("sddm")) {
        setPropertyIfPresent(root, "statusMessage", QStringLiteral("Authenticating…"));
        setPropertyIfPresent(root, "authenticating", true);
    }

    view.resize(width, height);
    view.show();
    if (scenario == QStringLiteral("keyboard")) {
        QTimer::singleShot(150, root, [root]() {
            QMetaObject::invokeMethod(root, "focusFirstAction");
        });
    }
    QTimer::singleShot(500, &app, [&]() {
        const QImage image = view.grabWindow();
        app.exit(!image.isNull() && image.save(output) ? 0 : 4);
    });
    return app.exec();
}

#include "session_renderer.moc"
