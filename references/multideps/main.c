#include <stdio.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <ptrauth.h>


//#define SET1
//#define SET2
#define SET3

#ifdef SET1
struct _CSConfig;
typedef struct _CSConfig CSConfig_t;

struct _SignatureValidation {
    const CSConfig_t* config;
};
typedef struct _SignatureValidation SignatureValidation_t;

struct _CSConfigCallerSignature {
    const SignatureValidation_t* (*acquireSig)(void**);
};
typedef struct _CSConfigCallerSignature CSConfigCallerSignature_t;

struct _CSConfig {
    CSConfigCallerSignature_t callerSignature;
    int bb;
};
#endif

#ifdef SET2
typedef uint64_t pt_entry_t;
struct pv_entry;
typedef struct pv_entry pv_entry_t;

typedef struct  {
    pv_entry_t* list;
    uint32_t count;
} pv_free_list_t;

struct pv_entry {
    struct pv_entry* pve_next;
    pv_free_list_t* pve_free_list;
    pt_entry_t* pve_ptep[2];
};
#endif

#ifdef SET3

typedef struct thread                   *thread_t;
typedef struct processor                *processor_t;


struct thread {
	struct { processor_t    runq; } __runq; 
    struct thread*   next;
};

typedef char bool;

union processor_flags {
    unsigned int flags;
    unsigned int cpu_flags;
};

struct processor {
    union processor_flags flags;
	bool                    is_recommended;
    int a;
	thread_t               current_thread;          /* thread running on processor */
    union {
        struct thread* idle_thread;            /* thread running when no work to do */
        struct {
            int b;
            int c;
        };
    };
};

#endif

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
