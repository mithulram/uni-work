#include "services/rpm_computation.hpp"

S_RPMComputation::S_RPMComputation(const char *n) : Service(n) {

    addRequirement(&requirement_velocity);
    addGuarantee(&guarantee_rpm);

    ConditionalTask::ConditionalTaskParam_t task_parameter;

    // register task in the service and pass task parameter
    initializeTask(&conditional_task_, task_parameter);

    taskReadsFromRequirement(conditional_task_, requirement_velocity, &conditional_task_.access_handle_velocity);

    // ConditionalTask starts its execution in onWork() only if all requirements provided in taskAddDataTrigger have new data.
    taskAddDataTrigger(conditional_task_, requirement_velocity, conditional_task_.access_handle_velocity);
}

bool S_RPMComputation::onStartRequest() {
    std::cout << std::endl << name_ << " is being started." << std::endl;
    return true;
}

// informs service when it is stopped
bool S_RPMComputation::onStopRequest()  {
    std::cout << std::endl << name_ << " is now being stopped." << std::endl;
    return true;
}

void S_RPMComputation::Foo::onWork() {
    Velocity::Data received_velocity;
    access_handle_velocity->pullData(received_velocity);
    float current_velocity = received_velocity.topic_data;
    std::cout << "[R] Velocity: " << current_velocity << std::endl;

    RPM::Data rpm_data;
    rpm_data.topic_data = float(-0.00162517 * current_velocity * current_velocity + 0.42792 * current_velocity + 0.342904);

    std::cout << "[S] RPM: " << rpm_data.topic_data << std::endl;
    guarantee_rpm.sendData(rpm_data);
}

decltype(S_RPMComputation::requirement_velocity) S_RPMComputation::requirement_velocity;
decltype(S_RPMComputation::guarantee_rpm) S_RPMComputation::guarantee_rpm;
