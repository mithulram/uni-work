#pragma once

#include <asoa/core/runtime.hpp>
#include <asoa/driver/rtps.h>
#include <asoa/core/task.hpp>
#include <thread>

#include "interfaces/t_obstacle.hpp"
#include "interfaces/t_fusedsensors.hpp"


class S_SensorFusion : public Service {

public:

    /*
     * Declaration of guarantees and requirements
     */
    static class : public Guarantee<FusedSensors> {
    } guarantee_fused_sensors;

    static class : public Requirement<Obstacle, 5> {

        // filter deciding whether the received data is accepted
        bool parameterFilter(const Obstacle::Parameter *) override {
            return true; // always accept data
        }
    } requirement_obstacle;

    // --------------------------------------------------------------------------------------------------------------

    /*
     * Constructor and Destructor
     */
    explicit S_SensorFusion(const char *n);
    ~S_SensorFusion() override = default;


// --------------------------------------------------------------------------------------------------------------
    /*
     * Service Callback Methods
     */
    bool onStartRequest() override;
    bool onStopRequest() override;
// --------------------------------------------------------------------------------------------------------------

    class Foo: public ConditionalTask {

    private:
    public:
        Requirement<Obstacle>::AccessHandle *access_handle_obstacle;
        void onWork() override;
    } conditional_task_;

};



