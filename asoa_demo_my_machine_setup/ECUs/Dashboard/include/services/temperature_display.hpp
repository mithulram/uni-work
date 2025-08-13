#pragma once

#include "interfaces/t_temperature.hpp"

#include <asoa/core/runtime.hpp>
#include <asoa/driver/rtps.h>
#include <asoa/core/task.hpp>
#include <thread>

class S_TemperatureDisplay : public Service {

private:
    std::string name;

public:
    explicit S_TemperatureDisplay(const char *name);
    ~S_TemperatureDisplay() override = default;

    static class : public Requirement<Temperature, 5> {
        // filter deciding whether the received data is accepted
        bool parameterFilter(const Temperature::Parameter *) override {
            return true; // always accept data
        }
    } requirement_temperature;

    static class : public Guarantee<Temperature> {
    } guarantee_temperature;

    bool onStartRequest() override;
    bool onStopRequest() override;

    class Foo : public ConditionalTask {
    public:
        Requirement<Temperature>::AccessHandle *access_handle_temperature;
        void onWork() override;
    } conditional_task_;
};
