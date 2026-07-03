#include <stddef.h>
#include <stdatomic.h>

typedef unsigned long long (*htable_hash_f)(void* object);

typedef struct hentry hentry_t;
typedef unsigned short u16;
typedef unsigned char u8;

struct o {
    int a;
    int b;
};

typedef const struct hentry* const_hentry_t;

typedef struct htable {
    union {
        struct  { // we assume this struct fits into a 64 bytes cacheline, otherwise need to change layout
            u16                object_size;
            struct o           options; // options for the hashtable
            atomic_llong       count;
            htable_hash_f      hash;
            int (*bidon)(void*, char*);
        };
        u8 cache_line[64];
    };
    hentry_t* buckets;
} htable_t;