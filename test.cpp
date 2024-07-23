#include <iostream>
#include <cstring>

void process_data() {
    char buffer[10];
    // Deliberately long string to cause buffer overflow
    char input[20] = "ThisIsTooLongData";

    // Buffer overflow vulnerability
    std::strcpy(buffer, input);

    // Loop that can be unrolled
    for (int i = 0; i < 10; i++) {
        buffer[i] = buffer[i] + 1;
    }
    std::cout << "Processed data: " << buffer << std::endl;
}

int main() {
    process_data();
    return 0;
}
