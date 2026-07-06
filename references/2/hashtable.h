#include <stddef.h>
#include <stdatomic.h>

typedef struct hentry hentry_t;
typedef unsigned short u16;
typedef unsigned char u8;

struct o {
    int a;
    int b;
};

union uu
{
    int ua;
    int ub;
};

enum {
    TEST1,
    TEST2
};

typedef struct htable {
    union {
        struct  { // we assume this struct fits into a 64 bytes cacheline, otherwise need to change layout
            u16                object_size;
            struct o           options; // options for the hashtable
            atomic_llong       count;
        };
        struct zzz {
            int a1;
            int a2;
        } yyy;
        u8 cache_line[64];
    };
    void* address;
    union uu muu;
    int test1:16;
    int test2:8;
    hentry_t* buckets;
} htable_t;

typedef struct {
    int unknown_a;
} noname_struct_t;
