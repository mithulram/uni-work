#pragma once

#include "interfaces/t_obstacle.hpp"

#include <asoa/core/runtime.hpp>
#include <asoa/driver/rtps.h>
#include <asoa/core/task.hpp>
#include <thread>
#include <wiringPi.h>


class S_SensorObstacle : public Service {

private:
    int key;
    std::string name;
    std::thread button_listener;
    std::atomic<bool> running;
    std::atomic<bool> obstacle;

public:

    S_SensorObstacle(const char *name);
    ~S_SensorObstacle();

    static class : public Guarantee<Obstacle> {
    } guarantee_obstacle;

    // informs service when it is started
    virtual bool onStartRequest() override;

    // informs service when it is stopped
    virtual bool onStopRequest() override;

    class Foo: public PeriodicTask {
    private:
        std::atomic<bool> obstacle{};

    public:
        Foo();
        void revert_obstacle();
        virtual void onWork() override;
    } periodic_task_;
};
