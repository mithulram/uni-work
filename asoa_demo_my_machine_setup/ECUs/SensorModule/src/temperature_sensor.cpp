#include "services/temperature_sensor.hpp"

S_TemperatureSensor::S_TemperatureSensor(const char *n) : Service(n), 
    gen(rd()), temp_dist(10.0f, 30.0f) {
    
    this->name = n;
    addGuarantee(&guarantee_temperature);

    // add periodic task
    PeriodicTask::PeriodicTaskParam_t p_task_param;
    p_task_param.frequencyHz = 1;
    p_task_param.start_ref = asoa::OS::time::getTime();
    initializeTask(&periodic_task_, p_task_param);
    
    // Manual trigger to start generating temperature immediately
    std::cout << "Temperature sensor initialized - will generate values between 10-30°C" << std::endl;
}

bool S_TemperatureSensor::onStartRequest() {
    std::cout << std::endl << name << " is being started." << std::endl;
    std::cout << "Temperature sensor service activated!" << std::endl;
    
    // Immediately generate a temperature value
    Temperature::Data temperature;
    temperature.topic_data = temp_dist(gen);
    std::cout << "[S] Temperature Sensor: " << temperature.topic_data << "°C" << std::endl;
    guarantee_temperature.sendData(temperature);
    
    return true;
}

bool S_TemperatureSensor::onStopRequest() {
    std::cout << std::endl << name << " is now being stopped." << std::endl;
    return true;
}

void S_TemperatureSensor::Foo::onWork() {
    Temperature::Data temperature;
    // Generate random temperature between 10-30°C
    static std::random_device rd;
    static std::mt19937 gen(rd());
    static std::uniform_real_distribution<float> temp_dist(10.0f, 30.0f);
    
    temperature.topic_data = temp_dist(gen);
    std::cout << "[S] Temperature Sensor: " << temperature.topic_data << "°C" << std::endl;
    guarantee_temperature.sendData(temperature);
}

decltype(S_TemperatureSensor::guarantee_temperature) S_TemperatureSensor::guarantee_temperature;
