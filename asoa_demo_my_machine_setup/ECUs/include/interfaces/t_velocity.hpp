#pragma once


#include "t_simple.hpp"

class Velocity : public FloatTopic {

public:
    Velocity() : FloatTopic() {
        topic_name = "Velocity";
        topic_id = 13;
    }
};


