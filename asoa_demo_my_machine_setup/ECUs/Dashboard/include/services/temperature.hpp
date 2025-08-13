#pragma once

#include "interfaces/t_temperature.hpp"

#include <asoa/core/runtime.hpp>
#include <asoa/driver/rtps.h>
#include <asoa/core/task.hpp>
#include <thread>



class S_TemperatureComputation : public Service {

private:
    std::string name;

public:

    explicit S_TemperatureComputation(const char *name);
    ~S_TemperatureComputation() override = default;

    static class : public Guarantee<Temperature> {
    } guarantee_temperature;

    // informs service when it is started
    bool onStartRequest() override;

    // informs service when it is stopped
    bool onStopRequest() override;

    class Foo : public PeriodicTask {
    public:
        void onWork() override;
    } periodic_task_;
};