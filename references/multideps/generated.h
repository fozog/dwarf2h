typedef char bool;

typedef struct processor* processor_t;

struct thread {
    struct  {
        processor_t runq;
    } __runq;
};
struct processor {
    bool is_recommended;
    struct thread* active_thread;
};
typedef struct thread* thread_t;