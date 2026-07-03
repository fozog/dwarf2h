#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#define LOOP_ONLY 1

#ifndef LOOP_ONLY
typedef struct c {
    struct d {
        int d_a;
        int d_b;
    } c_a;
    int c_b;
} c_t;

struct OpaqueDTEntry {
    uint32_t nProperties;
    uint32_t nChildren;
};

typedef const struct OpaqueDTEntry* DTEntry;

typedef struct list {
    struct list* next_list;
    int b;
} list_t;


#endif

struct node;
typedef struct node* pnode;

struct node {
    pnode next;
    int a;
};


#ifndef LOOP_ONLY
int main() {
    c_t v_c1 = {};
    DTEntry entry = NULL;
    list_t l = {};
#else
int main() {
#endif
    pnode p = NULL;
    return 0;
}
