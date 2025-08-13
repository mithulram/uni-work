#pragma once

#include <asoa/core/runtime.hpp>
#include <asoa/driver/rtps.h>
#include <asoa/core/task.hpp>
#include <thread>


#include "interfaces/t_velocity.hpp"
#include "interfaces/t_rpm.hpp"
#include "interfaces/t_temperature.hpp"

#define low8(x) ((int)(x)&0xff)
#define hi8(x) ((int)(x) >> 8)

class S_DisplayState : public Service {

public:

    /*
     * Declaration of guarantees and requirements
     */
    static class : public Requirement<Velocity, 5> {

        // filter deciding whether the received data is accepted
        bool parameterFilter(const Velocity::Parameter*) override {
            return true; // always accept data
        }
    } requirement_velocity;

    static class : public Requirement<RPM, 5> {

        // filter deciding whether the received data is accepted
        bool parameterFilter(const RPM::Parameter*) override {
            return true; // always accept data
        }
    } requirement_rpm;

    static class : public Requirement<Temperature, 5> {

        // filter deciding whether the received data is accepted
        bool parameterFilter(const Temperature::Parameter*) override {
            return true; // always accept data
        }
    } requirement_temperature;

    // --------------------------------------------------------------------------------------------------------------

    /*
     * Constructor and Destructor
     */
    explicit S_DisplayState(const char *n);
    ~S_DisplayState() override = default;


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

    // The "onWork()" callback is only triggered if there is new data available on the requirement (see service constructor)
    class Foo : public ConditionalTask {

    private:

        std::mutex velocity_mutex;
        std::mutex rpm_mutex;
        std::atomic<bool> driving{};

        float current_velocity = -1;
        float current_rpm = -1;

        std::thread v_needle_thread;
        std::thread rpm_needle_thread;


    public:

        Foo() {
            driving = false;
        }

        // provides an own view on the underlying circular buffer of the requirement
        Requirement<Velocity>::AccessHandle *access_handle_velocity{};
        Requirement<RPM>::AccessHandle *access_handle_rpm{};

        void stopTask();

        void v_to_needle();
        void rpm_to_needle();

        void onWork() override;
    } ;

    Foo ct_rpm_velocity;

    class Bar : public ConditionalTask {
    public:
        Requirement<Temperature>::AccessHandle *access_handle_temperature;
        void onWork() override;
    } ct_temperature;

};