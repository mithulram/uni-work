project(asoa_config_compiler)
cmake_minimum_required(VERSION 3.16)


if (${ARCHITECTURE} STREQUAL "armr5")
	add_definitions(-DFREERTOS)
	add_definitions(-DLWIP)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -O0 -g3 -mcpu=cortex-r5 -mfloat-abi=hard  -mfpu=vfpv3-d16")
	set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -O0 -g3 -mcpu=cortex-r5 -mfloat-abi=hard  -mfpu=vfpv3-d16")
elseif (${ARCHITECTURE} STREQUAL "esp32")
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -O0 -std=gnu++11 -mlongcalls")
	set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -O0 -g3 -std=gnu99 -mlongcalls")
else()
	message(FATAL_ERROR "Architecture ${ARCHITECTURE} not supported.")
endif()

add_library(asoa_security_config STATIC "precompiled.c")

target_link_libraries(asoa_security_config)
