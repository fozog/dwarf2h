#include <sys/cdefs.h>
#define SET1_1

#ifdef SET1_1
typedef unsigned int    uint32_t;
typedef unsigned long   uint64_t;
typedef unsigned short  uint16_t;

union lck_mtx_state {
    struct  {
        uint32_t owner: 28;
        uint32_t ilocked: 1;
        uint32_t spin_mode: 1;
        uint32_t needs_wakeup: 1;
        uint32_t profile: 1;
        uint16_t ilk_tail;
        uint16_t as_tail;
    };
    uint32_t data;
    uint64_t val;
};
#endif

int main() {
#ifdef SET1_1
    union lck_mtx_state u1_1 = {};
#endif
	return 0;
}
