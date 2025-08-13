#include "services/sensorobstacle.hpp"

S_SensorObstacle::S_SensorObstacle(const char *name) : Service(name) {

    this->name = name;
    this->key = 0;
    running = true;

    // add listener to button connected to GPIO pin
    button_listener = std::thread([&](int &key, std::atomic<bool> &running, Foo &periodicTask) {

        if (wiringPiSetup() < 0) {
            std::cout << "Could not initialize GPIO pins.";
            return;
        }

        pinMode(key, INPUT);
        pullUpDnControl(key, PUD_UP);
        while (running) {
            if (digitalRead(key) == 0) {
            	std::cout << "Click" << std::endl;
                periodicTask.revert_obstacle();
                while (digitalRead(key) == 0)
                    delay(100);
            }
            delay(100);
        }
        std::cout << "Stop listening to button clicks.";

    }, std::ref(this->key), std::ref(running), std::ref(periodic_task_));

    addGuarantee(&guarantee_obstacle);

    // add periodic task
    PeriodicTask::PeriodicTaskParam_t p_task_param;
    p_task_param.frequencyHz = 1;
    p_task_param.start_ref = asoa::OS::time::getTime();
    initializeTask(&periodic_task_, p_task_param);
}

S_SensorObstacle::~S_SensorObstacle() {
    running = false;
    this->button_listener.join();
}

bool S_SensorObstacle::onStartRequest() {
    std::cout << std::endl << name << " is being started." << std::endl;
    return true;
}

bool S_SensorObstacle::onStopRequest() {
    std::cout << std::endl << name << " is now being stopped." << std::endl;
    return true;
}

S_SensorObstacle::Foo::Foo() {
    obstacle = true;
}

void S_SensorObstacle::Foo::revert_obstacle() {
    if (obstacle.load()) {
        std::cout << "Obstacle removed." << std::endl;
        obstacle = false;
    } else {
        std::cout << "Obstacle added." << std::endl;
        obstacle = true;
    }
}

void S_SensorObstacle::Foo::onWork() {
    Obstacle::Data obstacle;
    obstacle.topic_data = this->obstacle.load();
    std::cout << "[S] Obstacle: " << obstacle.topic_data << std::endl;
    guarantee_obstacle.sendData(obstacle);
}

decltype(S_SensorObstacle::guarantee_obstacle) S_SensorObstacle::guarantee_obstacle;
