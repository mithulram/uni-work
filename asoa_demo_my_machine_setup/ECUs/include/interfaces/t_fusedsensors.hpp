#pragma once

#include "t_simple.hpp"

class FusedSensors : public FloatTopic {

public:
  FusedSensors() : FloatTopic() {
    topic_name = "FusedSens";
    topic_id = 16;
  }
};
