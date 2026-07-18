// SPDX-License-Identifier: MIT
#include <QAbstractListModel>
#include <QGuiApplication>
#include <QQmlContext>
#include <QQuickView>
#include <QTimer>
#include <QUrl>
#include <QVariantList>

class SessionModel final : public QAbstractListModel
{
    Q_OBJECT
    Q_PROPERTY(int lastIndex READ lastIndex CONSTANT)
public:
    enum Role { NameRole = Qt::UserRole + 1 };
    using QAbstractListModel::QAbstractListModel;
    int rowCount(const QModelIndex &parent = {}) const override { return parent.isValid() ? 0 : 2; }
    QVariant data(const QModelIndex &index, int role) const override
    {
        if (!index.isValid() || role != NameRole) return {};
        return index.row() == 0 ? QStringLiteral("Plasma (Wayland)") : QStringLiteral("Plasma (X11)");
    }
    QHash<int, QByteArray> roleNames() const override { return {{NameRole, "name"}}; }
    int lastIndex() const { return 0; }
};

class UserModel final : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QString lastUser READ lastUser CONSTANT)
public:
    using QObject::QObject;
    QString lastUser() const { return QStringLiteral("loofi"); }
};

class Keyboard final : public QObject
{
    Q_OBJECT
    Q_PROPERTY(QVariantList layouts READ layouts CONSTANT)
    Q_PROPERTY(int currentLayout READ currentLayout WRITE setCurrentLayout NOTIFY currentLayoutChanged)
public:
    using QObject::QObject;
    QVariantList layouts() const
    {
        return {QVariantMap{{QStringLiteral("longName"), QStringLiteral("Swedish")}},
                QVariantMap{{QStringLiteral("longName"), QStringLiteral("English (US)")}}};
    }
    int currentLayout() const { return m_currentLayout; }
    void setCurrentLayout(int value) { if (m_currentLayout != value) { m_currentLayout = value; Q_EMIT currentLayoutChanged(); } }
Q_SIGNALS:
    void currentLayoutChanged();
private:
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
    explicit Config(const QUrl &background, QObject *parent = nullptr) : QObject(parent), m_background(background) {}
    QUrl background() const { return m_background; }
private:
    QUrl m_background;
};

int main(int argc, char **argv)
{
    QGuiApplication app(argc, argv);
    if (argc != 4) return 2;
    const QUrl qml = QUrl::fromLocalFile(QString::fromLocal8Bit(argv[1]));
    Config config(QUrl::fromLocalFile(QString::fromLocal8Bit(argv[2])));
    SessionModel sessions;
    UserModel users;
    Keyboard keyboard;
    Sddm sddm;
    QQuickView view;
    view.setResizeMode(QQuickView::SizeRootObjectToView);
    view.rootContext()->setContextProperty(QStringLiteral("config"), &config);
    view.rootContext()->setContextProperty(QStringLiteral("sessionModel"), &sessions);
    view.rootContext()->setContextProperty(QStringLiteral("userModel"), &users);
    view.rootContext()->setContextProperty(QStringLiteral("keyboard"), &keyboard);
    view.rootContext()->setContextProperty(QStringLiteral("sddm"), &sddm);
    view.setSource(qml);
    if (view.status() == QQuickView::Error) return 3;
    view.resize(960, 540);
    view.show();
    QTimer::singleShot(450, &app, [&]() {
        const QImage image = view.grabWindow();
        app.exit(!image.isNull() && image.save(QString::fromLocal8Bit(argv[3])) ? 0 : 4);
    });
    return app.exec();
}

#include "sddm_renderer.moc"
