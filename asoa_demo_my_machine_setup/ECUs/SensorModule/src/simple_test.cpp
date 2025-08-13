#include <iostream>
#include <unistd.h>
#include <asoa/core/runtime.hpp>
#include "services/temperature_sensor.hpp"

int main() {
    std::cout << "Starting simple temperature sensor test..." << std::endl;
    
    auto asoa_driver = asoa_init();
    if(asoa_driver == nullptr) {
        std::cout << "Failed to initialize RTPS protocol." << std::endl;
        return -1;
    }

    char hardware_name[] = "SensorModule";
    std::cout << "Hello, I am the " << hardware_name << "." << std::endl;
    
    Runtime::init(hardware_name);

    // Create temperature sensor service
    auto* s_temperature_sensor = new S_TemperatureSensor("TempSensor");
    Runtime::get()->publishService(s_temperature_sensor);
    
    // Manually activate the service
    s_temperature_sensor->onStartRequest();
    
    std::cout << "Service activated manually. Running for 10 seconds..." << std::endl;
    
    // Run for 10 seconds
    for (int i = 0; i < 10; i++) {
        sleep(1);
        std::cout << "Running... " << (i+1) << "/10" << std::endl;
    }
    
    Runtime::get()->destroy();
    asoa_destroy();
    
    return 0;
}
