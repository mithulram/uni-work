#pragma once

#include "interfaces/t_temperature.hpp"

#include <asoa/core/runtime.hpp>
#include <asoa/driver/rtps.h>
#include <asoa/core/task.hpp>
#include <thread>
#include <random>

class S_TemperatureSensor : public Service {

private:
    std::string name;
    std::random_device rd;
    std::mt19937 gen;
    std::uniform_real_distribution<float> temp_dist;

public:
    explicit S_TemperatureSensor(const char *name);
    ~S_TemperatureSensor() override = default;

    static class : public Guarantee<Temperature> {
    } guarantee_temperature;

    bool onStartRequest() override;
    bool onStopRequest() override;

    class Foo : public PeriodicTask {
    public:
        void onWork() override;
    } periodic_task_;
};
