#include <sys/cdefs.h>
#define SET1_1
#define SET1_2
#define SET1_3
#define SET2
#define SET3

#ifdef SET1_1
typedef struct  {
        enum  {
            kTXMCodeRegionTypeExecutable1_1 = 0,
            kTXMCodeRegionTypeSharedRegion1_1 = 1,
            kTXMCodeRegionTypeJIT1_1 = 2,
            kTXMCodeRegionTypeDebug1_1 = 3,
        } type : 7;
        char debugged : 1;
    } properties1_1;
#endif

#ifdef SET1_2
enum  CRT1_2{
    kTXMCodeRegionTypeExecutable1_2 = 0,
    kTXMCodeRegionTypeSharedRegion1_2 = 1,
    kTXMCodeRegionTypeJIT1_2 = 2,
    kTXMCodeRegionTypeDebug1_2 = 3,
};

typedef struct  {
        enum  CRT1_2 type2 : 7;
        char debugged2 : 1;
} properties1_2;
#endif

#ifdef SET1_3

typedef struct  {
    enum  CRT1_3  {
        kTXMCodeRegionTypeExecutable1_3 = 0,
        kTXMCodeRegionTypeSharedRegion1_3 = 1,
        kTXMCodeRegionTypeJIT1_3 = 2,
        kTXMCodeRegionTypeDebug1_3 = 3,
    } type3 : 7;
    char debugged3 : 1;
} properties1_3;
#endif

#ifdef SET2
typedef enum  {
    kTXMCodeRegionTypeExecutable2 = 0,
    kTXMCodeRegionTypeSharedRegion2 = 1,
    kTXMCodeRegionTypeJIT2 = 2,
    kTXMCodeRegionTypeDebug2 = 3,
} CRT2;

struct node2;

typedef struct node {
    struct node* next;
    struct node2* prev;
    CRT2 type;
} CRT2Node;

typedef struct node2 {
    struct node2* next;
    CRT2 type;
} node2_t;
#endif

#ifdef SET3

typedef unsigned short u16;
#if __has_feature(objc_fixed_enum) || __has_extension(cxx_fixed_enum) || \
        __has_extension(cxx_strong_enums)
#define __enum_decl(_name, _type, ...) \
	        typedef enum : _type __VA_ARGS__ __enum_open _name
#define __enum_closed_decl(_name, _type, ...) \
	        typedef enum : _type __VA_ARGS__ __enum_closed _name
#define __options_decl(_name, _type, ...) \
	        typedef enum : _type __VA_ARGS__ __enum_open __enum_options _name
#define __options_closed_decl(_name, _type, ...) \
	        typedef enum : _type __VA_ARGS__ __enum_closed __enum_options _name
#else
#define __enum_decl(_name, _type, ...) \
	        typedef _type _name; enum __VA_ARGS__ __enum_open
#define __enum_closed_decl(_name, _type, ...) \
	        typedef _type _name; enum __VA_ARGS__ __enum_closed
#define __options_decl(_name, _type, ...) \
	        typedef _type _name; enum __VA_ARGS__ __enum_open __enum_options
#define __options_closed_decl(_name, _type, ...) \
	        typedef _type _name; enum __VA_ARGS__ __enum_closed __enum_options
#endif

__options_closed_decl(cpu_flags_t, u16, {
    SleepState      = 0x0800,
    /* For the boot processor, StartedState means 'interrupts initialized' - it is already running */
    StartedState    = 0x1000,
    /* For the boot processor, InitState means 'cpu_data fully initialized' - it is already running */
    InitState       = 0x2000,
});

typedef struct cpu_data {
    unsigned short                  cpu_number;
    _Atomic cpu_flags_t             cpu_flags;
    int                             cpu_type;
    int                             cpu_subtype;
    int                             cpu_threadtype;
} cpu_data_t;
#endif

int main() {
#ifdef SET1_1
    properties1_1 p1_1 = {};
#endif
#ifdef SET1_2
    properties1_2 p1_2 = {};
#endif
#ifdef SET1_3
    properties1_3 p1_3 = {};
#endif
#ifdef SET2
    CRT2 p2 = kTXMCodeRegionTypeExecutable2;
    CRT2Node node2 = {0};
    node2_t node2_t_instance = {(node2_t*)0, p2};
#endif
#ifdef SET3
    cpu_data_t data = {0};
#endif
	return 0;
}
