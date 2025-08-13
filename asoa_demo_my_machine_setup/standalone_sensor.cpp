#include <iostream>
#include <random>
#include <chrono>
#include <thread>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

int main() {
    std::cout << "🚀 Standalone Temperature Sensor Starting..." << std::endl;
    std::cout << "📡 Will generate random temperatures between 10-30°C every second" << std::endl;
    std::cout << "🎯 Will send data to MITM interceptor on UDP port 7401" << std::endl;
    
    // Initialize random number generator
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<float> temp_dist(10.0f, 30.0f);
    
    // Create UDP socket
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        std::cerr << "❌ Failed to create socket" << std::endl;
        return -1;
    }
    
    // Setup destination address (MITM interceptor)
    struct sockaddr_in dest_addr;
    memset(&dest_addr, 0, sizeof(dest_addr));
    dest_addr.sin_family = AF_INET;
    dest_addr.sin_port = htons(7401);  // Send to MITM interceptor
    dest_addr.sin_addr.s_addr = inet_addr("127.0.0.1"); // Localhost
    
    std::cout << "✅ Socket created successfully" << std::endl;
    std::cout << "📊 Starting temperature generation..." << std::endl;
    std::cout << "==========================================" << std::endl;
    
    int counter = 0;
    while (counter < 30) { // Run for 30 seconds
        // Generate random temperature
        float temperature = temp_dist(gen);
        
        // Create packet data (simple format: temperature as float)
        char packet_data[sizeof(float)];
        memcpy(packet_data, &temperature, sizeof(float));
        
        // Send packet
        ssize_t sent = sendto(sockfd, packet_data, sizeof(packet_data), 0,
                             (struct sockaddr*)&dest_addr, sizeof(dest_addr));
        
        if (sent > 0) {
            std::cout << "[S] Temperature Sensor: " << temperature << "°C (packet sent to MITM)" << std::endl;
        } else {
            std::cerr << "❌ Failed to send packet" << std::endl;
        }
        
        counter++;
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }
    
    close(sockfd);
    std::cout << "==========================================" << std::endl;
    std::cout << "✅ Standalone sensor completed!" << std::endl;
    return 0;
}
