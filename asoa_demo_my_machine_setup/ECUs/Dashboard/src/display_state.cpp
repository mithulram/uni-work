#include "services/display_state.hpp"

S_DisplayState::S_DisplayState(const char *n) : Service(n) {

    addRequirement(&requirement_velocity);
    addRequirement(&requirement_rpm);
    addRequirement(&requirement_temperature);

    ConditionalTask::ConditionalTaskParam_t tp_ct_rpm_velocity;
    ConditionalTask::ConditionalTaskParam_t tp_ct_temperature;

    // register task in the service and pass task parameter
    initializeTask(&ct_rpm_velocity, tp_ct_rpm_velocity);
    initializeTask(&ct_temperature, tp_ct_temperature);

    // create access handle such that the task obtains legal access to the requirement
    taskReadsFromRequirement(ct_rpm_velocity, requirement_rpm, &ct_rpm_velocity.access_handle_rpm);
    taskReadsFromRequirement(ct_rpm_velocity, requirement_velocity, &ct_rpm_velocity.access_handle_velocity);
    taskReadsFromRequirement(ct_temperature, requirement_temperature, &ct_temperature.access_handle_temperature);

    // ConditionalTask starts its execution in onWork() only if all requirements provided in taskAddDataTrigger have new data.
    taskAddDataTrigger(ct_rpm_velocity, requirement_velocity, ct_rpm_velocity.access_handle_velocity);
    taskAddDataTrigger(ct_rpm_velocity, requirement_rpm, ct_rpm_velocity.access_handle_rpm);
    taskAddDataTrigger(ct_temperature, requirement_temperature, ct_temperature.access_handle_temperature);

}


bool S_DisplayState::onStartRequest() {

std::cout << std::endl << name_ << " is being started." << std::endl;

return true;
}

// informs service when it is stopped
bool S_DisplayState::onStopRequest() {

std::cout << std::endl << name_ << " is now being stopped." << std::endl;
ct_rpm_velocity.stopTask();
return true;
}

void S_DisplayState::Foo::onWork() {
    if(!driving.load()) {
        driving = true;
        v_needle_thread = std::thread(&Foo::v_to_needle, this);
        rpm_needle_thread = std::thread(&Foo::rpm_to_needle, this);
    }

    Velocity::Data new_velocity;
    RPM::Data new_rpm;

    access_handle_rpm->pullData(new_rpm);
    access_handle_velocity->pullData(new_velocity);

    std::unique_lock<std::mutex> locker_v(velocity_mutex);
    current_velocity = new_velocity.topic_data;
    locker_v.unlock();


    std::unique_lock<std::mutex> locker_rpm(rpm_mutex);
    current_rpm = new_rpm.topic_data;
    locker_rpm.unlock();
}

void S_DisplayState::Foo::stopTask() {
    driving = false;
    v_needle_thread.join();
    rpm_needle_thread.join();
}

void S_DisplayState::Foo::v_to_needle() {
    std::cout << driving.load() << std::endl;

    char buffer[128];
    while (driving.load()) {
        std::unique_lock<std::mutex> locker(velocity_mutex);
        std::cout << "Velocity: " << current_velocity << "km/h" << std::endl;
        auto speed = static_cast<short>(current_velocity);
        locker.unlock();

        speed = (short)(speed / 0.0070);

        uint8_t speedLo = low8(speed);
        uint8_t speedhigh = hi8(speed);

        // Speed
        std::this_thread::sleep_for(std::chrono::milliseconds(400));
        sprintf(buffer, "cansend can1 5A0#FF%02x%02x0000FFFFAD", speedLo, speedhigh);
        system(buffer);

        // ABS
        std::this_thread::sleep_for(std::chrono::milliseconds(105));
        sprintf(buffer, "cansend can1 1A0#18%02x%02x00FEFE00FF", (uint8_t) speedLo, (uint8_t) speedhigh);
        system(buffer);
    }
}

void S_DisplayState::Foo::rpm_to_needle() {
    char buffer[128];
//    std::cout << "rpm: " << driving << std::endl;
    while(driving.load()) {
//        std::cout << "rpm waiting" << std::endl;
        std::unique_lock<std::mutex> locker(rpm_mutex);

        int rpm = (int)current_rpm;

        if (current_rpm < 10)
            sprintf(buffer, "cansend can1 280#490E000%i0E001B0E", rpm);
        else
            sprintf(buffer, "cansend can1 280#490E00%i0E001B0E", rpm);

        system(buffer);
        system("cansend can1 050#0008F10000000000");

        std::cout << "RPM: " << rpm << std::endl;
        locker.unlock();

        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }

}

void S_DisplayState::Bar::onWork() {
    Temperature::Data current_temperature;
    access_handle_temperature->pullData(current_temperature);
    std::cout << "[R] Temperature: " << current_temperature.topic_data << std::endl;
}

decltype(S_DisplayState::requirement_velocity) S_DisplayState::requirement_velocity;
decltype(S_DisplayState::requirement_rpm) S_DisplayState::requirement_rpm;
decltype(S_DisplayState::requirement_temperature) S_DisplayState::requirement_temperature;
