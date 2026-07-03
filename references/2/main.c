#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "hashtable.h"
#include "virtio.h"

virtq_desc_ptr* descp;
unpacked_virtq_desc_t* unpacked_descp;

htable_t* tablep;

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

typedef long long s64;

int main(int argc, const char *argv[]) {
    // Print the number of command line arguments
    printf("Number of command line arguments: %d\n", argc);
    tablep = malloc(sizeof(htable_t));
    tablep->buckets = malloc(1000);
    struct o aa={};
    struct zzz z= {};
    descp = NULL;
    s64 t=0;
    noname_struct_t testnoname = {};
    gssd_mechtype_e mech = fff(0);
    atomic_fetch_add(&tablep->count, 1);
    // Print each command line argument
    printf("%d", TEST1);
    for (int i = 0; i < argc; i++) {
        printf("Argument %d: %s\n", i, argv[i]);
    }
    printf("Hash %lld, %d\n", tablep->count, aa.a);
    return 0;
}