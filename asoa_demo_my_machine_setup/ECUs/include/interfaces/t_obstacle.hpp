#pragma once


#include "t_simple.hpp"

class Obstacle : public FloatTopic {

public:
        Obstacle() : FloatTopic() {
           topic_name = "Obstacle";
           topic_id = 12;
        }
};
