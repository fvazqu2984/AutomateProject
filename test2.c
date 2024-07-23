#include <stdio.h>
#include <string.h>

void process_data() {
    char buffer[10];
    //Deliberately long string to cause buffer overflow
    char input[20] = "ThisIsTooLongData";

    //Buffer overflow vulnerability
    strcpy(buffer, input);

    //Loop that can be unrolled
    for (int i = 0; i < 10; i++) {
        buffer[i] = buffer[i] + 1;
    }
    printf("Processed data: %s\n", buffer);
}

int main() {
    process_data();
    return 0;
}

