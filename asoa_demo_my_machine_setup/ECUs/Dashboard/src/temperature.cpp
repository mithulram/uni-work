#include "services/temperature.hpp"

S_TemperatureComputation::S_TemperatureComputation(const char *name) : Service(name) {

    this->name = name;
    addGuarantee(&guarantee_temperature);

    // add periodic task
    PeriodicTask::PeriodicTaskParam_t p_task_param;
    p_task_param.frequencyHz = 1;
    p_task_param.start_ref = asoa::OS::time::getTime();
    initializeTask(&periodic_task_, p_task_param);
}

bool S_TemperatureComputation::onStartRequest()  {
    std::cout << std::endl << name << " is being started." << std::endl;
    return true;
}

// informs service when it is stopped
bool S_TemperatureComputation::onStopRequest()  {
    std::cout << std::endl << name << " is now being stopped." << std::endl;
    return true;
}

void S_TemperatureComputation::Foo::onWork() {
    Temperature::Data temperature;
    temperature.topic_data = 10.0f;
    std::cout << "[S] Temperature: " << temperature.topic_data << std::endl;
    guarantee_temperature.sendData(temperature);
}

decltype(S_TemperatureComputation::guarantee_temperature) S_TemperatureComputation::guarantee_temperature;
