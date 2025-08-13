if(ESP_PLATFORM)
set(INC_PATHS	"../include"
				"../../include/"
				"/opt/toolchains/cross-esp32/rootfs/usr/include/asoa_core-0.4.0"
				"/opt/toolchains/cross-esp32/rootfs/usr/include/asoa_platform_driver-0.4.0")

set(SRC_FILES	"runtime.cpp"
				"speed_computation.cpp"
				)

idf_component_register(SRCS ${SRC_FILES} INCLUDE_DIRS "${INC_PATHS}")

add_library(asoa STATIC IMPORTED PRIVATE)
set_property(TARGET asoa PROPERTY IMPORTED_LOCATION "${CMAKE_CURRENT_SOURCE_DIR}/../../lib/asoa/esp32/libasoa.a")

add_library(asoa_config STATIC IMPORTED PRIVATE)
set_property(TARGET asoa_config PROPERTY IMPORTED_LOCATION "${CMAKE_CURRENT_SOURCE_DIR}/../config/build/esp32/Release/libasoa_security_config.a")

add_definitions(-DESP32)

target_link_libraries(asoa INTERFACE idf::lwip)

target_link_libraries(${COMPONENT_TARGET} PRIVATE asoa asoa_config)
endif()
