#include <iostream>
#include <unistd.h>

#include <asoa/core/runtime.hpp>
#include "services/sensor_fusion.hpp"
#include "services/temperature_sensor.hpp"

int main() {

	auto asoa_driver = asoa_init();

	// initialization of the RTPS communication driver
	if(asoa_driver == nullptr) {
		std::cout << "Failed to initialize RTPS protocol." << std::endl;
		return -1;
	}

	char hardware_name[] = "SensorModule";
	std::cout << "Hello, I am the " << hardware_name << "." << std::endl;
	
	if(strcmp(asoa_driver->hardware_name, "nosec") != 0 && strcmp(asoa_driver->hardware_name, hardware_name) != 0) {
			std::cout << "WARNING: Hardware name does not match the name provided in the security configuration."  << std::endl;
	}

	// The ASOA runtime takes over the communication with the orchestrator.
	Runtime::init(hardware_name);

	//create services
	const char service_name1[] = "SensFusion";
	auto* s_sensor_fusion = new S_SensorFusion(service_name1);

	const char service_name2[] = "TempSensor";
	auto* s_temperature_sensor = new S_TemperatureSensor(service_name2);

	// pass services to the runtime
	Runtime::get()->publishService(s_sensor_fusion);
	Runtime::get()->publishService(s_temperature_sensor);
	std::cout << "Looping..." << std::endl;

	// main runtime loop
	Runtime::get()->loop();

	Runtime::get()->destroy();
	
	asoa_destroy();

	std::cout << "Runtime destroyed." << std::endl;

	return 0;
}

// for ESP32
extern "C" {
void app_main() {
	main();
}
}
