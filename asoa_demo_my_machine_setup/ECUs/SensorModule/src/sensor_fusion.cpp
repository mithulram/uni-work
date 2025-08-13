#include "services/sensor_fusion.hpp"

S_SensorFusion::S_SensorFusion(const char *n) : Service(n) {
        addRequirement(&requirement_obstacle);
        addGuarantee(&guarantee_fused_sensors);

        ConditionalTask::ConditionalTaskParam_t task_parameter;

        // register task in the service and pass task parameter
        initializeTask(&conditional_task_, task_parameter);
        taskReadsFromRequirement(conditional_task_, requirement_obstacle, &conditional_task_.access_handle_obstacle);

        // ConditionalTask starts its execution in onWork() only if all requirements provided in taskAddDataTrigger have new data.
        taskAddDataTrigger(conditional_task_, requirement_obstacle, conditional_task_.access_handle_obstacle);
}

bool S_SensorFusion::onStartRequest() {
    std::cout << std::endl << name_ << " is being started." << std::endl;
    return true;
}

bool S_SensorFusion::onStopRequest()  {
    std::cout << std::endl << name_ << " is now being stopped." << std::endl;
    return true;
}


void S_SensorFusion::Foo::onWork() {

    Obstacle::Data is_obstacle;
    access_handle_obstacle->pullData(is_obstacle);
    std::cout << "[R] Obstacle: " << is_obstacle.topic_data << std::endl;

    FusedSensors::Data fusedSensors;
    fusedSensors.topic_data = is_obstacle.topic_data;
    guarantee_fused_sensors.sendData(fusedSensors);
    std::cout << "[S] Fused Obstacle: " << fusedSensors.topic_data << std::endl;

}

decltype(S_SensorFusion::requirement_obstacle)
    S_SensorFusion::requirement_obstacle;
decltype(S_SensorFusion::guarantee_fused_sensors) S_SensorFusion::guarantee_fused_sensors;
