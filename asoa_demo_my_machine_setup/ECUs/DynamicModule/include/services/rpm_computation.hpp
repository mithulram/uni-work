#pragma once

#include <asoa/core/runtime.hpp>
#include <asoa/driver/rtps.h>
#include <asoa/core/task.hpp>
#include <thread>

#include "interfaces/t_rpm.hpp"
#include "interfaces/t_velocity.hpp"


class S_RPMComputation : public Service {

public:

    /*
     * Declaration of guarantees and requirements
     */
    static class : public Guarantee<RPM> {
    } guarantee_rpm;

    static class : public Requirement<Velocity, 5> {

        // filter deciding whether the received data is accepted
        bool parameterFilter(const Velocity::Parameter*) override {
            return true; // always accept data
        }
    } requirement_velocity;

    // --------------------------------------------------------------------------------------------------------------

    /*
     * Constructor and Destructor
     */
    explicit S_RPMComputation(const char *n);
    ~S_RPMComputation() override = default;

// --------------------------------------------------------------------------------------------------------------
    /*
     * Service Callback Methods
     */
    // informs service when it is started
    bool onStartRequest() override;
    bool onStopRequest() override;

// --------------------------------------------------------------------------------------------------------------
    /*
     * Service Tasks
     */
    class Foo : public ConditionalTask {

    public:
        Requirement<Velocity>::AccessHandle *access_handle_velocity;
        void onWork() override;
    } conditional_task_;
};



