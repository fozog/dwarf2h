#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "hashtable.h"
#include "virtio.h"

unsigned long long hash(void* object)
{
    return 1234;
}

virtq_desc_t* descp;
unpacked_virtq_desc_t* unpacked_descp;

htable_t* tablep;

// function f(void) returns a pointer to a function that takes a void* and returns an unsigned long long
unsigned long long (*f(void))(void*)
{
    return hash;
}

enum gssd_mechtype {
    GSSD_NO_MECH = -1,
    GSSD_KRB5_MECH = 0,
    GSSD_SPNEGO_MECH,
    GSSD_NTLM_MECH,
    GSSD_IAKERB_MECH
};

typedef enum gssd_mechtype gssd_mechtype_e;

enum gssd_mechtype fff(int x) {
    if (x == 0) {
        return GSSD_NO_MECH;
    } else
        return GSSD_IAKERB_MECH;
}

int f2(const const_hentry_t e)
{
    return 0;
}

void f3(const void* p)
{
}


typedef int (*complex)(const const_hentry_t e);
typedef void (*cv)(const void* p);

int main(int argc, const char *argv[]) {
    // Print the number of command line arguments
    printf("Number of command line arguments: %d\n", argc);
    tablep = malloc(sizeof(htable_t));
    tablep->buckets = malloc(1000);
    tablep->hash = f();
    gssd_mechtype_e mech = fff(0);
    atomic_fetch_add(&tablep->count, 1);
    const const_hentry_t p = {0};
    complex g = f2;
    cv h = f3;
    h(NULL);
    int z = g(p);
    // Print each command line argument
    for (int i = 0; i < argc; i++) {
        printf("Argument %d: %s\n", i, argv[i]);
    }
    printf("Hash %lld %d\n", tablep->hash((void*)argv[0]), z);
    return 0;
}