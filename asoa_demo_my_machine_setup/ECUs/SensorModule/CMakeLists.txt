if(ESP_PLATFORM)

	set(EXTRA_COMPONENT_DIRS src)

	include($ENV{IDF_PATH}/tools/cmake/project.cmake)
	project(sensormodule)

else()
	cmake_minimum_required(VERSION 3.15)

	project(sensormodule)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

	# C++11
	set(CMAKE_CXX_STANDARD 11)
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")
	set(CMAKE_POSITION_INDEPENDENT_CODE ON)

	find_package(asoa_core 0.4.0 REQUIRED)

	add_executable(main src/runtime.cpp src/sensor_fusion.cpp src/temperature_sensor.cpp)
	target_include_directories(main PRIVATE include "${CMAKE_SOURCE_DIR}/../include")
	target_link_libraries(main asoa_core)
endif()

