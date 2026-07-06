# dwarf2h

`dwarf2h` parses DWARF information from Elf and macOS to generate C declarations, including dependencies, for selected or all types.

It can extract directly from installed macOS Kernel Debug Kits (the following extracts almost everything for the Hypervisor Framework):
dwarf2h extract --kdk t6031@26.4.1 arm_guest_context_t

It also works on Linux kernels with debug symbols (the follwing extracts the struct page definition and its dependencies):
dwarf2h extract --file linux/vmlinux-6.8.0-31-generic page

## What it prints

```bash
dwarf2h extract --file linux/vmlinux-6.8.0-31-generic page
```
gives

```text
struct list_head {
    struct list_head * next;
    struct list_head * prev;
};

typedef long long int __s64;

typedef __s64 s64;

typedef struct {
    s64 counter;
} atomic64_t;

typedef atomic64_t atomic_long_t;

struct callback_head {
    struct callback_head * next;
    void (*func)(struct callback_head *);
};

typedef struct {
    int counter;
} atomic_t;

struct page {
    long unsigned int flags;
    union {
        struct {
            union {
                struct list_head lru;
                struct {
                    void * __filler;
                    unsigned int mlock_count;
                };
                struct list_head buddy_list;
                struct list_head pcp_list;
            };
            struct address_space * mapping;
            union {
                long unsigned int index;
                long unsigned int share;
            };
            long unsigned int private;
        };
        struct {
            long unsigned int pp_magic;
            struct page_pool * pp;
            long unsigned int _pp_mapping_pad;
            long unsigned int dma_addr;
            atomic_long_t pp_ref_count;
        };
        struct {
            long unsigned int compound_head;
        };
        struct {
            struct dev_pagemap * pgmap;
            void * zone_device_data;
        };
        struct callback_head callback_head;
    };
    union {
        atomic_t _mapcount;
        unsigned int page_type;
    };
    atomic_t _refcount;
    long unsigned int memcg_data;
};
```
It can also analyze complex recursive definitions and make a compilable header
```text
typedef struct node * pnode;

struct node {
    pnode next;
    int a;
};
````
It documents elments that are Apple Arm silicon specific

```text
struct unpacked_virtq_desc {
    char flags;
    union {
        void * /* __ptrauth(0x02, 1, 0x5d4f) */ address;
        unsigned int flags32;
        unsigned short flags16;
        unsigned char flags8;
    };
    unsigned int pad2 : 16;
    mach_msg_type_name_t disposition : 8;
    mach_msg_descriptor_type_t type : 8;
    uint32_t pad_end;
    unsigned long long addr;
};
```

## Install (end users)

Recommended (no virtualenv activation needed):

```bash
# one-time
brew install pipx
pipx ensurepath

#install for the current user
pipx install git+https://github.com/fozog/dwarf2h.git

#install for all users
pipx install --global git+https://github.com/fozog/dwarf2h.git

```

Then run from anywhere:

```bash
dwarf2h --help
```


## Usage

```bash
dwarf2h extract --file main.dSYM --all
```
/* --------------------------- */
/* dwarf2h: https://github.com/fozog/dwarf2h */

typedef unsigned int uint32_t;

typedef unsigned short uint16_t;

typedef unsigned long uint64_t;

union lck_mtx_state {
    struct {
        uint32_t owner : 28;
        uint32_t ilocked : 1;
        uint32_t spin_mode : 1;
        uint32_t needs_wakeup : 1;
        uint32_t profile : 1;
        uint16_t ilk_tail;
        uint16_t as_tail;
    };
    uint32_t data;
    uint64_t val;
};
/* --------------------------- */

```

Or resolve from a KDK tag:

```bash
dwarf2h extract --kdk t6031@26.4.1 arm_guest_context_t
```

On macOS this is done on running kernel version, current hardware:

```bash
dwarf2h extract arm_guest_context_t
```

Write extracted C declarations to a header file:

```bash
dwarf2h extract --kdk t6031@26.5.1 arm_guest_context_t --header /tmp/arm_guest_context.h
```


macOS specific commands: installed KDKs and detected platforms:

```bash
dwarf2h kdk-list
```

`*` marks the KDK matching the currently running macOS version/build.

Print platforms and full path as well:

```bash
dwarf2h kdk-list --full
```

List known platform codes (hand-maintained mapping):

```bash
dwarf2h platforms-list
```

`*` marks the currently running platform.

Export platform codes as CSV:

```bash
dwarf2h platforms-list --csv
```

## VS Code launch config

A ready-to-use debug configuration is provided in `.vscode/launch.json`.
