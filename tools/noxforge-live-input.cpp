// SPDX-License-Identifier: MIT
// Bounded libei input helper for isolated NoxForge Wayland qualification.

#include <QCoreApplication>
#include <QDBusInterface>
#include <QDBusMessage>
#include <QDBusUnixFileDescriptor>
#include <QThread>

#include <libei.h>
#include <linux/input-event-codes.h>

#include <cerrno>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <poll.h>
#include <unistd.h>

namespace {

constexpr auto service = "org.kde.KWin";
constexpr auto path = "/org/kde/KWin/EIS/RemoteDesktop";
constexpr auto interface = "org.kde.KWin.EIS.RemoteDesktop";
constexpr int keyboardCapability = 1;
constexpr int pointerCapability = 2;

struct Devices {
    ei_device *keyboard = nullptr;
    ei_device *pointer = nullptr;
    ei_device *button = nullptr;
    bool keyboardResumed = false;
    bool pointerResumed = false;
    bool buttonResumed = false;
};

void usage(const char *program)
{
    std::fprintf(stderr,
                 "Usage:\n"
                 "  %s keys [--hold-ms N] KEYCODE [KEYCODE ...]\n"
                 "  %s move DX DY\n"
                 "  %s absolute X Y\n"
                 "  %s absolute-click X Y\n"
                 "  %s click [BUTTON_CODE]\n"
                 "  %s double-click [BUTTON_CODE]\n",
                 program, program, program, program, program, program);
}

bool parseInteger(const char *text, int *value)
{
    char *end = nullptr;
    errno = 0;
    const long parsed = std::strtol(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0' || parsed < 0 || parsed > INT32_MAX) {
        return false;
    }
    *value = static_cast<int>(parsed);
    return true;
}

bool waitForDevices(ei *context, int capabilities, Devices *devices)
{
    const int fd = ei_get_fd(context);
    for (int iteration = 0; iteration < 100; ++iteration) {
        pollfd descriptor{fd, POLLIN, 0};
        const int ready = ::poll(&descriptor, 1, 100);
        if (ready < 0 && errno != EINTR) {
            std::fprintf(stderr, "libei poll failed: %s\n", std::strerror(errno));
            return false;
        }
        ei_dispatch(context);
        while (ei_event *event = ei_get_event(context)) {
            const auto type = ei_event_get_type(event);
            if (type == EI_EVENT_DISCONNECT) {
                std::fprintf(stderr, "KWin disconnected the libei client\n");
                ei_event_unref(event);
                return false;
            }
            if (type == EI_EVENT_SEAT_ADDED) {
                ei_seat *seat = ei_event_get_seat(event);
                ei_seat_bind_capabilities(
                    seat,
                    EI_DEVICE_CAP_POINTER,
                    EI_DEVICE_CAP_POINTER_ABSOLUTE,
                    EI_DEVICE_CAP_BUTTON,
                    EI_DEVICE_CAP_SCROLL,
                    EI_DEVICE_CAP_KEYBOARD,
                    nullptr);
            } else if (type == EI_EVENT_DEVICE_ADDED) {
                ei_device *device = ei_event_get_device(event);
                if (!devices->keyboard && ei_device_has_capability(device, EI_DEVICE_CAP_KEYBOARD)) {
                    devices->keyboard = ei_device_ref(device);
                }
                if (!devices->pointer &&
                    (ei_device_has_capability(device, EI_DEVICE_CAP_POINTER) ||
                     ei_device_has_capability(device, EI_DEVICE_CAP_POINTER_ABSOLUTE))) {
                    devices->pointer = ei_device_ref(device);
                }
                if (!devices->button && ei_device_has_capability(device, EI_DEVICE_CAP_BUTTON)) {
                    devices->button = ei_device_ref(device);
                }
            } else if (type == EI_EVENT_DEVICE_RESUMED) {
                ei_device *device = ei_event_get_device(event);
                if (devices->keyboard == device) {
                    devices->keyboardResumed = true;
                }
                if (devices->pointer == device) {
                    devices->pointerResumed = true;
                }
                if (devices->button == device) {
                    devices->buttonResumed = true;
                }
            }
            ei_event_unref(event);
        }
        const bool keyboardReady = !(capabilities & keyboardCapability) ||
                                   (devices->keyboard && devices->keyboardResumed);
        const bool pointerReady = !(capabilities & pointerCapability) ||
                                  (devices->pointer && devices->pointerResumed &&
                                   devices->button && devices->buttonResumed);
        if (keyboardReady && pointerReady) {
            return true;
        }
    }
    std::fprintf(stderr, "Timed out waiting for required libei devices\n");
    return false;
}

void releaseDevices(Devices *devices)
{
    devices->keyboard = ei_device_unref(devices->keyboard);
    devices->pointer = ei_device_unref(devices->pointer);
    devices->button = ei_device_unref(devices->button);
}

void frame(ei *context, ei_device *device)
{
    ei_device_frame(device, ei_now(context));
}

} // namespace

int main(int argc, char **argv)
{
    QCoreApplication application(argc, argv);
    if (argc < 2) {
        usage(argv[0]);
        return 2;
    }

    const QByteArray operation(argv[1]);
    int capabilities = 0;
    int holdMs = 100;
    int keyStart = 2;
    double dx = 0.0;
    double dy = 0.0;
    int button = BTN_LEFT;

    if (operation == "keys") {
        capabilities = keyboardCapability;
        if (argc >= 4 && QByteArray(argv[2]) == "--hold-ms") {
            if (!parseInteger(argv[3], &holdMs)) {
                usage(argv[0]);
                return 2;
            }
            keyStart = 4;
        }
        if (argc <= keyStart) {
            usage(argv[0]);
            return 2;
        }
    } else if (operation == "move" || operation == "absolute" ||
               operation == "absolute-click") {
        capabilities = pointerCapability;
        if (argc != 4) {
            usage(argv[0]);
            return 2;
        }
        char *endX = nullptr;
        char *endY = nullptr;
        dx = std::strtod(argv[2], &endX);
        dy = std::strtod(argv[3], &endY);
        if (!endX || *endX != '\0' || !endY || *endY != '\0') {
            usage(argv[0]);
            return 2;
        }
    } else if (operation == "click" || operation == "double-click") {
        capabilities = pointerCapability;
        if (argc > 3 || (argc == 3 && !parseInteger(argv[2], &button))) {
            usage(argv[0]);
            return 2;
        }
    } else {
        usage(argv[0]);
        return 2;
    }

    QDBusInterface remote(service, path, interface, QDBusConnection::sessionBus());
    const QDBusMessage reply = remote.call("connectToEIS", capabilities);
    if (reply.type() == QDBusMessage::ErrorMessage || reply.arguments().size() != 2) {
        std::fprintf(stderr, "KWin connectToEIS failed: %s\n",
                     reply.errorMessage().toUtf8().constData());
        return 1;
    }
    const auto descriptor = qvariant_cast<QDBusUnixFileDescriptor>(reply.arguments().at(0));
    const int cookie = reply.arguments().at(1).toInt();
    const int fd = ::dup(descriptor.fileDescriptor());
    if (fd < 0) {
        std::fprintf(stderr, "Could not duplicate EIS descriptor: %s\n", std::strerror(errno));
        remote.call("disconnect", cookie);
        return 1;
    }

    ei *context = ei_new_sender(nullptr);
    ei_configure_name(context, "NoxForge isolated qualification");
    if (ei_setup_backend_fd(context, fd) < 0) {
        std::fprintf(stderr, "Could not initialize libei backend\n");
        ::close(fd);
        ei_unref(context);
        remote.call("disconnect", cookie);
        return 1;
    }

    Devices devices;
    int result = 0;
    if (!waitForDevices(context, capabilities, &devices)) {
        result = 1;
    } else if (operation == "keys") {
        int keys[32]{};
        const int count = argc - keyStart;
        if (count > 32) {
            std::fprintf(stderr, "Too many keys; maximum is 32\n");
            result = 2;
        } else {
            for (int index = 0; index < count; ++index) {
                if (!parseInteger(argv[keyStart + index], &keys[index])) {
                    std::fprintf(stderr, "Invalid key code: %s\n", argv[keyStart + index]);
                    result = 2;
                    break;
                }
            }
            if (result == 0) {
                ei_device_start_emulating(devices.keyboard, 1);
                for (int index = 0; index < count; ++index) {
                    ei_device_keyboard_key(devices.keyboard, keys[index], true);
                }
                frame(context, devices.keyboard);
                QThread::msleep(static_cast<unsigned long>(holdMs));
                for (int index = count - 1; index >= 0; --index) {
                    ei_device_keyboard_key(devices.keyboard, keys[index], false);
                }
                frame(context, devices.keyboard);
                ei_device_stop_emulating(devices.keyboard);
            }
        }
    } else if (operation == "move") {
        ei_device_start_emulating(devices.pointer, 1);
        ei_device_pointer_motion(devices.pointer, dx, dy);
        frame(context, devices.pointer);
        ei_device_stop_emulating(devices.pointer);
    } else if (operation == "absolute" || operation == "absolute-click") {
        ei_device_start_emulating(devices.pointer, 1);
        ei_device_pointer_motion_absolute(devices.pointer, dx, dy);
        frame(context, devices.pointer);
        if (operation == "absolute-click") {
            ei_device_start_emulating(devices.button, 1);
            QThread::msleep(100);
            ei_device_button_button(devices.button, static_cast<uint32_t>(button), true);
            frame(context, devices.button);
            QThread::msleep(80);
            ei_device_button_button(devices.button, static_cast<uint32_t>(button), false);
            frame(context, devices.button);
            ei_device_stop_emulating(devices.button);
        }
        ei_device_stop_emulating(devices.pointer);
    } else if (operation == "click" || operation == "double-click") {
        ei_device_start_emulating(devices.button, 1);
        const int clicks = operation == "double-click" ? 2 : 1;
        for (int index = 0; index < clicks; ++index) {
            ei_device_button_button(devices.button, static_cast<uint32_t>(button), true);
            frame(context, devices.button);
            QThread::msleep(80);
            ei_device_button_button(devices.button, static_cast<uint32_t>(button), false);
            frame(context, devices.button);
            if (index + 1 < clicks) {
                QThread::msleep(120);
            }
        }
        ei_device_stop_emulating(devices.button);
    }

    releaseDevices(&devices);
    ei_disconnect(context);
    ei_unref(context);
    remote.call("disconnect", cookie);
    if (result == 0) {
        std::printf("NoxForge isolated input event sent through KWin EIS\n");
    }
    return result;
}
