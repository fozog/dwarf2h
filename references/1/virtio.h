#include <stdint.h>

#if defined(__APPLE__) && defined(__arm64__)
    #include <ptrauth.h>
    // Apple Context
    #define SIGN_DESCRIPTOR_PTR(ptr, storage_addr, salt) \
        ptrauth_sign_unauthenticated(ptr, ptrauth_key_asda, ptrauth_blend_discriminator(storage_addr, salt))
        
    #define AUTH_DESCRIPTOR_PTR(ptr, storage_addr, salt) \
        ptrauth_auth_data(ptr, ptrauth_key_asda, ptrauth_blend_discriminator(storage_addr, salt))
#else
    // Linux / Standard GCC Context (Requires -march=armv8.3-a)
    #define SIGN_DESCRIPTOR_PTR(ptr, storage_addr, salt) \
        __builtin_ptrauth_sign_unauthenticated(ptr, 2, __builtin_ptrauth_blend_discriminator(storage_addr, salt))
        
    #define AUTH_DESCRIPTOR_PTR(ptr, storage_addr, salt) \
        __builtin_ptrauth_auth(ptr, 2, __builtin_ptrauth_blend_discriminator(storage_addr, salt))
#endif

#define VIRTQ_SALT 0x5d4f

struct a
{
    int a_a;
    int a_b;
};

typedef struct a a_t;

struct b {
    struct {
        int b___a;
        int b___b;
    };
    int b_c;
};

struct c {
    struct d {
        int d_a;
        int d_b;
    } c_a;
    int c_b;
};

typedef struct d d_t;

typedef volatile struct e {
    struct {
        int e___a;
        int e___b;
    } bp [10];
    int e_a;
} e_t;

typedef const e_t* pe_t;

typedef volatile struct virtq_desc {  
    char flags;
    unsigned long long addr;
} __attribute__((packed)) virtq_desc_t;

typedef enum  {
            MACH_MSG_TYPE_NONE = 0,
            MACH_MSG_TYPE_MOVE_RECEIVE = 16,
            MACH_MSG_TYPE_MOVE_SEND = 17,
            MACH_MSG_TYPE_MOVE_SEND_ONCE = 18,
            MACH_MSG_TYPE_COPY_SEND = 19,
            MACH_MSG_TYPE_MAKE_SEND = 20,
            MACH_MSG_TYPE_MAKE_SEND_ONCE = 21,
} mach_msg_type_name_t;

typedef unsigned int mach_msg_descriptor_type_t;

typedef volatile struct unpacked_virtq_desc {
    char flags;
    union {
        void* address;
        unsigned int flags32;
        unsigned short flags16;
        unsigned char flags8;
    };
    unsigned int pad2 : 16;
    mach_msg_type_name_t disposition : 8;
    mach_msg_descriptor_type_t type : 8;
    uint32_t pad_end;
    unsigned long long addr;
} unpacked_virtq_desc_t;
