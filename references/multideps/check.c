#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

//#define SET1  
//#define SET2    
#define SET3
#include "generated.h"

int main() {
    #ifdef SET1
    CSConfig_t config = {};
    #endif
    #ifdef SET2
    pv_entry_t pe = {0};
    #endif
    #ifdef SET3
    struct processor p = {0};
    thread_t t = {0}; 
    #endif
    return 0;
}
