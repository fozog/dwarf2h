#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "virtio.h"

unpacked_virtq_desc_t u = {
    .flags = 0x01,
};
virtq_desc_t v = {
    .flags = 0x02,
    .addr = 0xabcdef1234567890
};


int main(int argc, const char *argv[]) {
    a_t v_a = {};
    struct b v_b = {};
    struct c v_c = {};
    d_t v_d2 = {};
    struct d v_d1 = {};
    struct e v_e1 = {};
    e_t v_e2 = {};
    char payload_buffer[] = "Packet Payload";    
    pe_t p = &v_e2;
    u.address = SIGN_DESCRIPTOR_PTR((void*)payload_buffer, &(u.address), VIRTQ_SALT);
    return v.flags == u.flags;
}
