#include "services/temperature_display.hpp"

S_TemperatureDisplay::S_TemperatureDisplay(const char *name) : Service(name) {
    this->name = name;
    addRequirement(&requirement_temperature);
    addGuarantee(&guarantee_temperature);

    ConditionalTask::ConditionalTaskParam_t task_parameter;
    initializeTask(&conditional_task_, task_parameter);
    taskReadsFromRequirement(conditional_task_, requirement_temperature, &conditional_task_.access_handle_temperature);
    taskAddDataTrigger(conditional_task_, requirement_temperature, conditional_task_.access_handle_temperature);
}

bool S_TemperatureDisplay::onStartRequest() {
    std::cout << std::endl << name << " is being started." << std::endl;
    std::cout << "Temperature display service activated!" << std::endl;
    return true;
}

bool S_TemperatureDisplay::onStopRequest() {
    std::cout << std::endl << name << " is now being stopped." << std::endl;
    return true;
}

void S_TemperatureDisplay::Foo::onWork() {
    Temperature::Data received_temperature;
    access_handle_temperature->pullData(received_temperature);
    std::cout << "[R] Temperature: " << received_temperature.topic_data << "°C" << std::endl;

    // Forward the temperature data
    Temperature::Data display_temperature;
    display_temperature.topic_data = received_temperature.topic_data;
    guarantee_temperature.sendData(display_temperature);
    std::cout << "[S] Display Temperature: " << display_temperature.topic_data << "°C" << std::endl;
}

decltype(S_TemperatureDisplay::requirement_temperature) S_TemperatureDisplay::requirement_temperature;
decltype(S_TemperatureDisplay::guarantee_temperature) S_TemperatureDisplay::guarantee_temperature;
