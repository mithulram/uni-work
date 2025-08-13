#include "services/speed_computation.hpp"

S_VelocityComputation::S_VelocityComputation(const char *n) : Service(n) {
        addRequirement(&requirement_fused_sensors);
        addGuarantee(&guarantee_velocity);

        ConditionalTask::ConditionalTaskParam_t task_parameter;

        // register task in the service and pass task parameter
        initializeTask(&conditional_task_, task_parameter);
        taskReadsFromRequirement(conditional_task_, requirement_fused_sensors, &conditional_task_.access_handle_obstacle);

        // ConditionalTask starts its execution in onWork() only if all requirements provided in taskAddDataTrigger have new data.
        taskAddDataTrigger(conditional_task_, requirement_fused_sensors, conditional_task_.access_handle_obstacle);
}

bool S_VelocityComputation::onStartRequest() {
    std::cout << std::endl << name_ << " is being started." << std::endl;
    return true;
}

bool S_VelocityComputation::onStopRequest()  {
    std::cout << std::endl << name_ << " is now being stopped." << std::endl;
    return true;
}

 void S_VelocityComputation::Foo::accelerate(unsigned v_start, unsigned v_end, unsigned t_s) {
    const int tick_ms = 10; // in milliseconds

    int v_diff = (int)(v_end - v_start);
    auto duration_ms = float(t_s * 1000);
    float v_diff_per_tick = float(v_diff) / float(duration_ms) * tick_ms ;
    Velocity::Data current_velocity;
    current_velocity.topic_data = (float) v_start;
    float current_t_ms = 0;

    while(current_t_ms < duration_ms) {
        current_velocity.topic_data += v_diff_per_tick;
        guarantee_velocity.sendData(current_velocity);
        current_t_ms += tick_ms;
        std::cout << "[S] Velocity: " << current_velocity.topic_data << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(tick_ms));

    }
}

void S_VelocityComputation::Foo::move() {

        static const int maneuver[5][4] = {{0,30,5,4}, {30,50,5,4}, {50,25,8,4}, {25,140,10,2}, {140,0,7,5}};

        int counter = 0;
        while(true) {
            if(moving.load())
                accelerate(maneuver[counter][0], maneuver[counter][1], maneuver[counter][2]);
            else
                break;
            std::this_thread::sleep_for(std::chrono::seconds(maneuver[counter][3]));
            counter++;
            counter %= 5;
        }
        accelerate(maneuver[counter][1], 0, 5);
    }

void S_VelocityComputation::Foo::onWork() {

    FusedSensors::Data is_obstacle;
    access_handle_obstacle->pullData(is_obstacle);
    if(is_obstacle.topic_data == 1.0)
      std::cout << "[R] Fused Sensors: Obstacale spotted. Driving not possible." << std::endl;
    else
      std::cout << "[R] Fused Sensors: No obstacale spotted. Go ahead!" << std::endl;

    if(is_obstacle.topic_data == 0 && !moving.load()) {
        moving = true;
        t_move = std::thread(&Foo::move, this);
    } else if(is_obstacle.topic_data != 0 && moving.load()) {
        moving = false;
        if(t_move.joinable())
	        t_move.join();

	}
}

decltype(S_VelocityComputation::requirement_fused_sensors) S_VelocityComputation::requirement_fused_sensors;
decltype(S_VelocityComputation::guarantee_velocity) S_VelocityComputation::guarantee_velocity;
