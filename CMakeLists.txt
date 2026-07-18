cmake_minimum_required(VERSION 3.24)

project(NoxForge VERSION 2.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_AUTOMOC ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(Qt6 6.7 REQUIRED COMPONENTS Core Gui Widgets)

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

enable_testing()
add_test(NAME style-plugin-discovery COMMAND noxforge_style_probe)
add_test(NAME widget-gallery-offscreen COMMAND noxforge_widget_gallery)
add_test(NAME widget-gallery-rtl COMMAND noxforge_widget_gallery --rtl)
add_test(NAME widget-gallery-scale-140 COMMAND noxforge_widget_gallery)
set_tests_properties(style-plugin-discovery widget-gallery-offscreen widget-gallery-rtl PROPERTIES
    ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_PLUGIN_PATH=${CMAKE_BINARY_DIR}/plugins"
)
set_tests_properties(widget-gallery-scale-140 PROPERTIES
    ENVIRONMENT "QT_QPA_PLATFORM=offscreen;QT_PLUGIN_PATH=${CMAKE_BINARY_DIR}/plugins;QT_SCALE_FACTOR=1.4"
)

include(GNUInstallDirs)
install(TARGETS noxforge_style
    LIBRARY DESTINATION "${CMAKE_INSTALL_LIBDIR}/qt6/plugins/styles"
)
