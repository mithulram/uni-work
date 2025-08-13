#pragma once

#include <asoa/core/runtime.hpp>
#include <asoa/driver/rtps.h>
#include <asoa/core/task.hpp>
#include <thread>

#include "interfaces/t_fusedsensors.hpp"
#include "interfaces/t_velocity.hpp"


class S_VelocityComputation : public Service {

public:

    /*
     * Declaration of guarantees and requirements
     */
    static class : public Guarantee<Velocity> {
    } guarantee_velocity;

    static class : public Requirement<FusedSensors, 5> {

        // filter deciding whether the received data is accepted
        bool parameterFilter(const FusedSensors::Parameter*) override {
            return true;
        }
    } requirement_fused_sensors;

    // --------------------------------------------------------------------------------------------------------------

    /*
     * Constructor and Destructor
     */
    explicit S_VelocityComputation(const char *n);
    ~S_VelocityComputation() override = default;


// --------------------------------------------------------------------------------------------------------------
    /*
     * Service Callback Methods
     */
    bool onStartRequest() override;
    bool onStopRequest() override;
// --------------------------------------------------------------------------------------------------------------


    /*
     * Service Tasks
     */

    // The "onWork()" callback is only triggered if there is new data available on the requirement (see service constructor)
    class Foo: public ConditionalTask {

    private:
        std::atomic<bool> moving;
        std::thread t_move;

    public:
        Requirement<FusedSensors>::AccessHandle *access_handle_obstacle;

        static void accelerate(unsigned d, unsigned, unsigned);
        void move();
        void onWork() override;

    } conditional_task_;

};



