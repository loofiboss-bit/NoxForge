cmake_minimum_required(VERSION 3.24)

file(STRINGS "${CMAKE_CURRENT_SOURCE_DIR}/VERSION" NOXFORGE_VERSION LIMIT_COUNT 1)
project(NoxForge VERSION "${NOXFORGE_VERSION}" LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(Qt6 6.7 REQUIRED COMPONENTS Core Gui Qml Quick Widgets)

add_library(noxforge_style MODULE
    src/style/noxforgepalette.h
    src/style/noxforgestyle.h
    src/style/noxforgestyle.cpp
    src/style/noxforgestyleplugin.cpp
    src/style/noxforgestyleplugin.json
)
target_link_libraries(noxforge_style PRIVATE Qt6::Core Qt6::Gui Qt6::Widgets)
target_compile_definitions(noxforge_style PRIVATE QT_NO_KEYWORDS)
set_target_properties(noxforge_style PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/plugins/styles"
    OUTPUT_NAME "noxforge6"
)

add_executable(noxforge_style_probe tests/qt/style_probe.cpp)
target_link_libraries(noxforge_style_probe PRIVATE Qt6::Core Qt6::Widgets)

add_executable(noxforge_widget_gallery tools/widget_gallery.cpp)
target_link_libraries(noxforge_widget_gallery PRIVATE Qt6::Core Qt6::Gui Qt6::Widgets)

add_executable(noxforge_sddm_renderer tools/sddm_renderer.cpp)
target_link_libraries(noxforge_sddm_renderer PRIVATE Qt6::Core Qt6::Gui Qt6::Qml Qt6::Quick)

enable_testing()
add_test(NAME style-plugin-discovery COMMAND noxforge_style_probe)
set_tests_properties(style-plugin-discovery PROPERTIES
    ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_PLUGIN_PATH=${CMAKE_BINARY_DIR}/plugins")

function(add_noxforge_gallery_test name scale rtl)
    if(rtl)
        add_test(NAME ${name} COMMAND noxforge_widget_gallery --rtl)
    else()
        add_test(NAME ${name} COMMAND noxforge_widget_gallery)
    endif()
    set_tests_properties(${name} PROPERTIES
        ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_PLUGIN_PATH=${CMAKE_BINARY_DIR}/plugins;QT_SCALE_FACTOR=${scale}")
endfunction()

add_noxforge_gallery_test(widget-gallery-ltr-100 1.0 FALSE)
add_noxforge_gallery_test(widget-gallery-ltr-125 1.25 FALSE)
add_noxforge_gallery_test(widget-gallery-ltr-140 1.4 FALSE)
add_noxforge_gallery_test(widget-gallery-ltr-200 2.0 FALSE)
add_noxforge_gallery_test(widget-gallery-rtl-100 1.0 TRUE)
add_noxforge_gallery_test(widget-gallery-rtl-125 1.25 TRUE)
add_noxforge_gallery_test(widget-gallery-rtl-140 1.4 TRUE)
add_noxforge_gallery_test(widget-gallery-rtl-200 2.0 TRUE)
add_test(NAME widget-gallery-data-page COMMAND noxforge_widget_gallery --data)
set_tests_properties(widget-gallery-data-page PROPERTIES
    ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_PLUGIN_PATH=${CMAKE_BINARY_DIR}/plugins;QT_SCALE_FACTOR=1.0")
add_test(
    NAME sddm-qml-surface
    COMMAND noxforge_sddm_renderer
        "${CMAKE_SOURCE_DIR}/sddm/NoxForge/Main.qml"
        "${CMAKE_SOURCE_DIR}/sddm/NoxForge/background.png"
        "${CMAKE_BINARY_DIR}/sddm-qml-surface.png"
)
set_tests_properties(sddm-qml-surface PROPERTIES ENVIRONMENT "QT_QPA_PLATFORM=offscreen")

include(GNUInstallDirs)
install(TARGETS noxforge_style
    LIBRARY DESTINATION "${QT6_INSTALL_PLUGINS}/styles"
)

set(NOXFORGE_THEME_ID "io.github.loofiboss.noxforge.desktop")

install(
    FILES color-schemes/NoxForgeDark.colors
    DESTINATION "${CMAKE_INSTALL_DATADIR}/color-schemes"
)
install(
    DIRECTORY "plasma/desktoptheme/${NOXFORGE_THEME_ID}/"
    DESTINATION "${CMAKE_INSTALL_DATADIR}/plasma/desktoptheme/${NOXFORGE_THEME_ID}"
)
install(
    DIRECTORY "aurorae/${NOXFORGE_THEME_ID}/"
    DESTINATION "${CMAKE_INSTALL_DATADIR}/aurorae/themes/${NOXFORGE_THEME_ID}"
)
install(
    DIRECTORY icons/NoxForge/
    DESTINATION "${CMAKE_INSTALL_DATADIR}/icons/NoxForge"
)
install(
    DIRECTORY cursors/NoxForge-Cursors/
    DESTINATION "${CMAKE_INSTALL_DATADIR}/icons/NoxForge-Cursors"
)
install(
    DIRECTORY sounds/NoxForge/
    DESTINATION "${CMAKE_INSTALL_DATADIR}/sounds/NoxForge"
)
install(
    DIRECTORY "look-and-feel/${NOXFORGE_THEME_ID}/"
    DESTINATION "${CMAKE_INSTALL_DATADIR}/plasma/look-and-feel/${NOXFORGE_THEME_ID}"
)
install(
    DIRECTORY "kwin/tabbox/${NOXFORGE_THEME_ID}/"
    DESTINATION "${CMAKE_INSTALL_DATADIR}/kwin/tabbox/${NOXFORGE_THEME_ID}"
)
install(
    DIRECTORY wallpapers/NoxForge/
    DESTINATION "${CMAKE_INSTALL_DATADIR}/wallpapers/NoxForge"
)
install(
    DIRECTORY sddm/NoxForge/
    DESTINATION "${CMAKE_INSTALL_DATADIR}/sddm/themes/NoxForge"
)
install(
    PROGRAMS tools/noxforge-doctor
    DESTINATION "${CMAKE_INSTALL_BINDIR}"
)
install(
    FILES VERSION
    DESTINATION "${CMAKE_INSTALL_DATADIR}/noxforge"
)
install(
    FILES docs/man/noxforge-doctor.1
    DESTINATION "${CMAKE_INSTALL_MANDIR}/man1"
)
