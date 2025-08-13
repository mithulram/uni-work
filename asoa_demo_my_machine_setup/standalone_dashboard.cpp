#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

int main() {
    std::cout << "🚀 Standalone Dashboard Starting..." << std::endl;
    std::cout << "📡 Listening for temperature data on UDP port 7400" << std::endl;
    std::cout << "📊 Will display received temperature values" << std::endl;
    
    // Create UDP socket
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        std::cerr << "❌ Failed to create socket" << std::endl;
        return -1;
    }
    
    // Setup server address
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(7400);
    server_addr.sin_addr.s_addr = INADDR_ANY;
    
    // Bind socket
    if (bind(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        std::cerr << "❌ Failed to bind socket" << std::endl;
        close(sockfd);
        return -1;
    }
    
    std::cout << "✅ Socket bound successfully to port 7400" << std::endl;
    std::cout << "📊 Waiting for temperature data..." << std::endl;
    std::cout << "==========================================" << std::endl;
    
    char buffer[1024];
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    
    int packet_count = 0;
    while (packet_count < 30) { // Listen for 30 packets
        // Receive packet
        ssize_t received = recvfrom(sockfd, buffer, sizeof(buffer), 0,
                                   (struct sockaddr*)&client_addr, &client_len);
        
        if (received > 0) {
            // Extract temperature from packet
            float temperature;
            memcpy(&temperature, buffer, sizeof(float));
            
            packet_count++;
            std::cout << "[R] Dashboard received: " << temperature << "°C (packet #" << packet_count << ")" << std::endl;
        } else {
            std::cerr << "❌ Failed to receive packet" << std::endl;
        }
    }
    
    close(sockfd);
    std::cout << "==========================================" << std::endl;
    std::cout << "✅ Dashboard completed! Received " << packet_count << " packets" << std::endl;
    return 0;
}
