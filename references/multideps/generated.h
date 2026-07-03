/* extracted from KDK unknown */
/* dwarf2h: https://github.com/fozog/dwarf2h */

union processor_flags {
    unsigned int flags;
    unsigned int cpu_flags;
};

typedef char bool;

typedef struct thread * thread_t;

struct processor {
    union processor_flags flags;
    bool is_recommended;
    int a;
    thread_t current_thread;
    union {
        struct thread * idle_thread;
        struct {
            int b;
            int c;
        };
    };
};

typedef struct processor * processor_t;

struct thread {
    struct {
        processor_t runq;
    } __runq;
    struct thread * next;
};
