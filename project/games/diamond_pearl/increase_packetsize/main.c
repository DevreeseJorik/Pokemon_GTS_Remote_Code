#include "wifi/packet_handler.h"

__attribute__((naked))
__attribute__((section(".text.main")))
__attribute__((target("thumb")))
void main(void) {
    __asm__ volatile (
        "push {r1-r7, lr}\n"
    );
    setPacketSizes();
    __asm__ volatile (
        "pop {r1-r7, pc}\n"
    );
}
