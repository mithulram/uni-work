#pragma once


#include "t_simple.hpp"

class Temperature : public FloatTopic {

public:
    Temperature() : FloatTopic() {
        topic_name = "Temp";
        topic_id = 15;
    }
};
