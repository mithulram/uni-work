#pragma once


#include "t_simple.hpp"

class RPM : public FloatTopic {

public:
    RPM() : FloatTopic() {
        topic_name = "RPM";
        topic_id = 14;
    }
};
