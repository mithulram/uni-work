#include <iostream>
#include <unistd.h>

#include <asoa/core/runtime.hpp>

#include "services/sensorobstacle.hpp"
#include <wiringPi.h>


int main() {

    // initialize GPIO pins of Raspberry Pi to catch button clicks
	auto asoa_driver = asoa_init();

	// initialization of the RTPS communication driver
	if(asoa_driver == nullptr) {
		std::cout << "Failed to initialize RTPS protocol." << std::endl;
		return -1;
	}

	char hardware_name[] = "Radar";
	std::cout << "Hello, I am the " << hardware_name << "." << std::endl;
	
	if(strcmp(asoa_driver->hardware_name, "nosec") != 0 && strcmp(asoa_driver->hardware_name, hardware_name) != 0) {
			std::cout << "WARNING: Hardware name does not match the name provided in the security configuration."  << std::endl;
	}


	// The ASOA runtime takes over the communication with the orchestrator.
	Runtime::init(hardware_name);


	//create services
    const char service_name[] = "ObstDet";
	auto* s_sensor_obstacle = new S_SensorObstacle(service_name);

	// pass service to the runtime
	Runtime::get()->publishService(s_sensor_obstacle);
	std::cout << "Looping..." << std::endl;

	// main runtime loop
	Runtime::get()->loop();

	Runtime::get()->destroy();
	
	asoa_destroy();

	std::cout << "Runtime destroyed." << std::endl;
    return 0;

}
