#include <iostream>
#include <random>
#include <unistd.h>

int main() {
    std::cout << "Testing Temperature Sensor..." << std::endl;
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> temp_dist(10.0f, 30.0f);
    
    for (int i = 0; i < 10; i++) {
        float temp = temp_dist(gen);
        std::cout << "[S] Temperature Sensor: " << temp << "°C" << std::endl;
        sleep(1);
    }
    
    return 0;
}
