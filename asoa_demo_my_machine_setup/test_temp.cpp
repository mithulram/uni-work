#include <iostream>
#include <random>
#include <chrono>
#include <thread>

int main() {
    std::cout << "Testing temperature generation..." << std::endl;
    
    // Same random generation code as in the sensor
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> temp_dist(10.0f, 30.0f);
    
    for (int i = 0; i < 10; i++) {
        float temp = temp_dist(gen);
        std::cout << "[S] Temperature Sensor: " << temp << "°C" << std::endl;
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    
    std::cout << "Test completed!" << std::endl;
    return 0;
}
