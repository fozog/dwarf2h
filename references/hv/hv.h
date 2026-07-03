#define __ptrauth(arch, key, value) 
#define _Bool char

struct ipc_port_t;

struct _CSConfigCallerSignature;

struct _ProfileValidation;

struct _CSConfig;

struct _SignatureValidation;

struct _TXMCodeRegionRBTree;

struct kcov_thread_data;

struct machine_thread;

struct bank_element;

struct hardened_exception_action;

struct ipc_mqueue;

struct sched_clutch_root;

struct SignatureValidation_t;

struct CERuntime_t;

struct CERuntime;

struct None;

struct exception_action;

struct task;

struct ipc_port;

struct None;

struct processor;

struct pset_node;

struct None;

struct None;

struct ipc_port;

struct task_watchport_elem;

struct thread;

struct task;

struct processor_set;

struct None;

typedef unsigned int u_int32_t;

typedef u_int32_t uint32_t;

typedef uint32_t os_ref_count_t;

typedef _Atomic(os_ref_count_t) os_ref_atomic_t;

typedef unsigned long long u_int64_t;

typedef u_int64_t uint64_t;

struct _lck_grp_stat_ {
    uint64_t lgs_count;
    uint32_t lgs_enablings;
    uint32_t lgs_probeid;
    uint64_t lgs_limit;
};
typedef struct _lck_grp_stat_ lck_grp_stat_t;

struct _lck_grp_stats_ {
    lck_grp_stat_t lgss_spin_held;
    lck_grp_stat_t lgss_spin_miss;
    lck_grp_stat_t lgss_spin_spin;
    lck_grp_stat_t lgss_ticket_held;
    lck_grp_stat_t lgss_ticket_miss;
    lck_grp_stat_t lgss_ticket_spin;
    lck_grp_stat_t lgss_mtx_held;
    lck_grp_stat_t lgss_mtx_direct_wait;
    lck_grp_stat_t lgss_mtx_miss;
    lck_grp_stat_t lgss_mtx_wait;
};
typedef struct _lck_grp_stats_ lck_grp_stats_t;

struct _lck_grp_ {
    os_ref_atomic_t lck_grp_refcnt;
    uint32_t lck_grp_attr_id;
    uint32_t lck_grp_spincnt;
    uint32_t lck_grp_ticketcnt;
    uint32_t lck_grp_mtxcnt;
    uint32_t lck_grp_rwcnt;
    char lck_grp_name[64];
    lck_grp_stats_t lck_grp_stats;
};
typedef struct _lck_grp_ lck_grp_t;

typedef enum  {
    LCK_GRP_ATTR_NONE = 0,
    LCK_GRP_ATTR_ID_MASK = 65535,
    LCK_GRP_ATTR_STAT = 65536,
    LCK_GRP_ATTR_TIME_STAT = 131072,
    LCK_GRP_ATTR_DEBUG = 262144,
    LCK_GRP_ATTR_ALLOCATED = 2147483648,
} lck_grp_options_t;

struct lck_grp_spec {
    lck_grp_t* grp;
    char grp_name[64];
    lck_grp_options_t grp_flags;
};
typedef enum  {
    STARTUP_SUB_NONE = 0,
    STARTUP_SUB_TUNABLES = 1,
    STARTUP_SUB_TIMEOUTS = 2,
    STARTUP_SUB_LOCKS = 3,
    STARTUP_SUB_KPRINTF = 4,
    STARTUP_SUB_PMAP_STEAL = 5,
    STARTUP_SUB_KMEM = 6,
    STARTUP_SUB_ZALLOC = 7,
    STARTUP_SUB_KTRACE = 8,
    STARTUP_SUB_PERCPU = 9,
    STARTUP_SUB_EVENT = 10,
    STARTUP_SUB_CODESIGNING = 11,
    STARTUP_SUB_OSLOG = 12,
    STARTUP_SUB_MACH_IPC = 13,
    STARTUP_SUB_THREAD_CALL = 14,
    STARTUP_SUB_SYSCTL = 15,
    STARTUP_SUB_EXCLAVES = 16,
    STARTUP_SUB_EARLY_BOOT = 17,
    STARTUP_SUB_LOCKDOWN = 4294967295ULL,
} startup_subsystem_id_t;

typedef enum  {
    STARTUP_RANK_FIRST = 0,
    STARTUP_RANK_SECOND = 1,
    STARTUP_RANK_THIRD = 2,
    STARTUP_RANK_FOURTH = 3,
    STARTUP_RANK_MIDDLE = 2147483647,
    STARTUP_RANK_LAST = 4294967295ULL,
} startup_rank_t;

struct startup_entry {
    startup_subsystem_id_t subsystem;
    startup_rank_t rank;
    void (*func)(void*);
    void* arg;
};
typedef unsigned char u_int8_t;

typedef u_int8_t uint8_t;

typedef unsigned short u_int16_t;

typedef u_int16_t uint16_t;

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
typedef union lck_mtx_state lck_mtx_state_t;

struct lck_mtx_s {
    uint32_t lck_mtx_tsid: 24;
    uint8_t lck_mtx_type: 8;
    uint32_t lck_mtx_grp;
    lck_mtx_state_t lck_mtx;
};
typedef struct lck_mtx_s lck_mtx_t;

struct _lck_attr_ {
    unsigned int lck_attr_val;
};
typedef struct _lck_attr_ lck_attr_t;

struct lck_mtx_startup_spec {
    lck_mtx_t* lck;
    lck_grp_t* lck_grp;
    lck_attr_t* lck_attr;
};
typedef int kern_return_t;

typedef kern_return_t mach_error_t;

typedef mach_error_t hv_return_t;

typedef enum  {
    MACH_ASSERT_DEFAULT = 0,
    MACH_ASSERT_3P = 1,
    MACH_ASSERT_3S = 2,
    MACH_ASSERT_3U = 3,
} mach_assert_type_t;

struct __attribute__((packed)) mach_assert_hdr {
    mach_assert_type_t type;
    unsigned int lineno: 24;
    const char* filename;
};
struct __attribute__((packed)) mach_assert_default {
    struct mach_assert_hdr hdr;
    const char* expr;
};
enum turnstile_update_flags {
    TURNSTILE_UPDATE_FLAGS_NONE = 0,
    TURNSTILE_IMMEDIATE_UPDATE = 1,
    TURNSTILE_DELAYED_UPDATE = 2,
    TURNSTILE_INHERITOR_THREAD = 4,
    TURNSTILE_INHERITOR_TURNSTILE = 8,
    TURNSTILE_INHERITOR_NEEDS_PRI_UPDATE = 16,
    TURNSTILE_NEEDS_PRI_UPDATE = 32,
    TURNSTILE_INHERITOR_WORKQ = 64,
    TURNSTILE_UPDATE_BOOST = 128,
};
enum perfcontrol_class {
    PERFCONTROL_CLASS_IDLE = 1,
    PERFCONTROL_CLASS_KERNEL = 2,
    PERFCONTROL_CLASS_REALTIME = 3,
    PERFCONTROL_CLASS_BACKGROUND = 4,
    PERFCONTROL_CLASS_UTILITY = 5,
    PERFCONTROL_CLASS_NONUI = 6,
    PERFCONTROL_CLASS_UI = 7,
    PERFCONTROL_CLASS_ABOVEUI = 8,
    PERFCONTROL_CLASS_USER_INITIATED = 9,
    PERFCONTROL_CLASS_MAX = 10,
};
enum thread_urgency {
    THREAD_URGENCY_NONE = 0,
    THREAD_URGENCY_BACKGROUND = 1,
    THREAD_URGENCY_NORMAL = 2,
    THREAD_URGENCY_REAL_TIME = 3,
    THREAD_URGENCY_LOWPRI = 4,
    THREAD_URGENCY_MAX = 5,
};
enum thread_snapshot_wait_flags {
    kThreadWaitNone = 0,
    kThreadWaitKernelMutex = 1,
    kThreadWaitPortReceive = 2,
    kThreadWaitPortSetReceive = 3,
    kThreadWaitPortSend = 4,
    kThreadWaitPortSendInTransit = 5,
    kThreadWaitSemaphore = 6,
    kThreadWaitKernelRWLockRead = 7,
    kThreadWaitKernelRWLockWrite = 8,
    kThreadWaitKernelRWLockUpgrade = 9,
    kThreadWaitUserLock = 10,
    kThreadWaitPThreadMutex = 11,
    kThreadWaitPThreadRWLockRead = 12,
    kThreadWaitPThreadRWLockWrite = 13,
    kThreadWaitPThreadCondVar = 14,
    kThreadWaitParkedWorkQueue = 15,
    kThreadWaitWorkloopSyncWait = 16,
    kThreadWaitOnProcess = 17,
    kThreadWaitSleepWithInheritor = 18,
    kThreadWaitEventlink = 19,
    kThreadWaitCompressor = 20,
    kThreadWaitParkedBoundWorkQueue = 21,
    kThreadWaitPageBusy = 22,
    kThreadWaitPagerInit = 23,
    kThreadWaitPagerReady = 24,
    kThreadWaitPagingActivity = 25,
    kThreadWaitMappingInProgress = 26,
    kThreadWaitMemoryBlocked = 27,
    kThreadWaitPagingInProgress = 28,
    kThreadWaitPageInThrottle = 29,
    kThreadWaitExclaveCore = 30,
    kThreadWaitExclaveKit = 31,
};
typedef enum  {
    SleepState = 2048,
    StartedState = 4096,
    InitState = 8192,
} cpu_flags_t;

typedef unsigned long uintptr_t;

typedef uintptr_t vm_offset_t;

struct thread_group {
};
typedef uint64_t event64_t;

typedef enum  {
    PROCESSOR_OFF_LINE = 0,
    PROCESSOR_START = 2,
    PROCESSOR_PENDING_OFFLINE = 3,
    PROCESSOR_IDLE = 4,
    PROCESSOR_DISPATCHING = 5,
    PROCESSOR_RUNNING = 6,
    PROCESSOR_STATE_LEN = 7,
} processor_state_t;

typedef uint64_t bitmap_t;

typedef bitmap_t cpumap_t;

union hw_lck_ticket_s {
    struct  {
        uint8_t lck_type;
        uint8_t lck_valid: 1;
        uint8_t lck_is_pv: 1;
        uint8_t lck_unused: 6;
        union  {
            struct  {
                uint8_t cticket;
                uint8_t nticket;
            };
            uint16_t tcurnext;
        };
    };
    uint32_t lck_value;
};
typedef union hw_lck_ticket_s hw_lck_ticket_t;

struct lck_ticket_s {
    uint32_t __lck_ticket_unused: 24;
    uint32_t lck_ticket_type: 8;
    uint32_t lck_ticket_padding;
    hw_lck_ticket_t tu;
    uint32_t lck_ticket_owner;
};
typedef struct lck_ticket_s lck_ticket_t;

struct queue_entry {
    struct queue_entry* next;
    struct queue_entry* prev;
};
typedef struct queue_entry* queue_entry_t;

struct circle_queue_head {
    queue_entry_t head;
};
typedef struct circle_queue_head circle_queue_head_t;

struct runq_stats {
    uint64_t count_sum;
    uint64_t last_change_timestamp;
};
struct run_queue {
    int highq;
    bitmap_t bitmap[2];
    int count;
    int urgency;
    circle_queue_head_t queues[96];
    struct runq_stats runq_stats;
};
typedef struct queue_entry queue_head_t;

typedef struct  {
    queue_head_t pri_queue;
    uint64_t pri_earliest_deadline;
    int pri_count;
    uint32_t pri_constraint;
} rt_queue_pri_t;

struct rt_queue {
    _Atomic(uint64_t) earliest_deadline;
    _Atomic(int) count;
    _Atomic(uint32_t) constraint;
    _Atomic(int) ed_index;
    bitmap_t bitmap[1];
    rt_queue_pri_t rt_queue_pri[31];
    struct runq_stats runq_stats;
};
typedef short int16_t;

struct priority_queue_entry_sched {
    struct priority_queue_entry_sched* next;
    struct priority_queue_entry_sched* prev;
    long key: 16;
    unsigned long tag: 4;
    long child: 44;
};
struct priority_queue_sched_max {
    struct priority_queue_entry_sched* pq_root;
};
struct priority_queue_entry_deadline {
    struct priority_queue_entry_deadline* next;
    struct priority_queue_entry_deadline* prev;
    long __key: 16;
    unsigned long tag: 4;
    long child: 44;
    uint64_t deadline;
};
struct priority_queue_deadline_min {
    struct priority_queue_entry_deadline* pq_root;
};
struct sched_clutch_bucket_runq {
    int scbrq_highq;
    int scbrq_count;
    bitmap_t scbrq_bitmap[2];
    circle_queue_head_t scbrq_queues[128];
};
struct sched_clutch_root_bucket {
    uint8_t scrb_bucket;
    _Bool scrb_bound;
    _Bool scrb_starvation_avoidance;
    union  {
        struct sched_clutch_bucket_runq scrb_clutch_buckets;
        struct run_queue scrb_bound_thread_runq;
    };
    struct priority_queue_entry_deadline scrb_pqlink;
    uint64_t scrb_warped_deadline;
    uint64_t scrb_warp_remaining;
    uint64_t scrb_starvation_ts;
};
struct sched_clutch_root {
    int16_t scr_priority;
    uint16_t scr_thr_count;
    int16_t scr_urgency;
    uint16_t scr_shared_rsrc_load_runnable[2];
    uint32_t scr_cluster_id;
    processor_set_t scr_pset;
    queue_head_t scr_clutch_buckets;
    struct priority_queue_sched_max scr_foreign_buckets;
    bitmap_t scr_unbound_runnable_bitmap[1];
    bitmap_t scr_unbound_warp_available[1];
    bitmap_t scr_bound_runnable_bitmap[1];
    bitmap_t scr_bound_warp_available[1];
    struct priority_queue_deadline_min scr_unbound_root_buckets;
    struct priority_queue_deadline_min scr_bound_root_buckets;
    _Atomic(uint16_t) scr_cumulative_run_count[6];
    struct sched_clutch_root_bucket scr_unbound_buckets[6];
    struct sched_clutch_root_bucket scr_bound_buckets[6];
};
struct ipc_service_port_label {
};
struct ipc_conn_port_label {
};
struct ipc_kobject_label {
};
struct mk_timer {
};
struct ipc_object {
    union  {
        void* iol_pointer;
        unsigned long iol_value;
        struct ipc_service_port_label* iol_service;
        struct ipc_conn_port_label* iol_connection;
        struct ipc_kobject_label* iol_kobject;
        struct mk_timer* iol_mktimer;
    };
    os_ref_atomic_t io_references;
};
struct os_refgrp {
    const char* grp_name;
    os_ref_atomic_t grp_children;
    os_ref_atomic_t grp_count;
    _Atomic(uint64_t) grp_retain_total;
    _Atomic(uint64_t) grp_release_total;
    struct os_refgrp* grp_parent;
    void* grp_log;
    uint64_t grp_flags;
};
struct os_refcnt {
    os_ref_atomic_t ref_count;
    struct os_refgrp* ref_group;
};
typedef struct os_refcnt os_refcnt_t;

struct hslock {
    uintptr_t lock_data;
};
struct lck_spin_s {
    struct hslock hwlock;
    unsigned long type;
};
typedef struct lck_spin_s lck_spin_t;

struct _vm_map {
};
typedef struct _vm_map* vm_map_t;

typedef struct queue_entry queue_chain_t;

struct task_watchports {
    os_refcnt_t tw_refcount;
    task_t tw_task;
    thread_t tw_thread;
    uint32_t tw_elem_array_count;
    struct task_watchport_elem tw_elem[0];
};
typedef void* turnstile_inheritor_t;

struct restartable_ranges {
};
struct affinity_space {
};
struct task_suspend_stats_s {
    uint64_t tss_last_start;
    uint64_t tss_last_end;
    uint64_t tss_count;
    uint64_t tss_duration;
};
struct task_suspend_source_s {
    uint64_t tss_time;
    uint64_t tss_tid;
    int tss_pid;
    char tss_procname[65];
    uint8_t tss_padding[3];
};
typedef struct task_suspend_source_s task_suspend_source_array_t[4];

typedef int integer_t;

struct recount_metrics {
    uint64_t rm_time_mach;
    uint64_t rm_instructions;
    uint64_t rm_cycles;
};
struct recount_usage {
    struct recount_metrics ru_metrics[3];
    uint64_t ru_energy_nj;
};
struct recount_track {
    uint32_t rt_pad;
    uint32_t rt_sync;
    struct recount_usage rt_usage;
};
struct recount_task {
    struct recount_track* rtk_lifetime;
    struct recount_usage* rtk_terminated;
};
typedef int thread_state_flavor_t;

typedef int exception_behavior_t;

typedef int boolean_t;

struct label {
    struct label** l_owner;
    long l_perpolicy[7];
};
struct exception_action {
    struct ipc_port* __ptrauth(2, 1, 43517) port;
    thread_state_flavor_t flavor;
    exception_behavior_t behavior;
    boolean_t privileged;
    boolean_t hardened;
    struct label* label;
};
typedef unsigned int exception_mask_t;

struct hardened_exception_action {
    struct exception_action ea;
    uint32_t signed_pc_key;
    exception_mask_t exception;
};
typedef struct ipc_port* ipc_port_t;

struct ipc_space {
};
struct ledger {
};
typedef struct ledger* ledger_t;

typedef struct  {
    uint64_t start;
    uint64_t end;
    _Atomic(uint64_t) handler;
    uint64_t refcon;
} arm64_uexc_region_t;

typedef uint64_t* scalable_counter_t;

typedef scalable_counter_t counter_t;

struct proc_ro {
};
typedef uint64_t mach_vm_address_t;

typedef unsigned char Byte;

typedef Byte Bytef;

typedef unsigned int uInt;

typedef unsigned long uLong;

struct internal_state {
    int dummy;
};
typedef void* voidpf;

typedef voidpf (*alloc_func)(uInt);

typedef void (*free_func)(voidpf);

struct z_stream_s {
    Bytef* next_in;
    uInt avail_in;
    uLong total_in;
    Bytef* next_out;
    uInt avail_out;
    uLong total_out;
    char* msg;
    struct internal_state* state;
    alloc_func zalloc;
    free_func zfree;
    voidpf opaque;
    int data_type;
    uLong adler;
    uLong reserved;
};
typedef struct z_stream_s z_stream;

typedef unsigned long size_t;

typedef enum  {
    KCD_CD_FLAG_IN_MARK = 1,
    KCD_CD_FLAG_FINALIZE = 2,
} kcd_cd_flag_t;

typedef enum  {
    KCDCT_NONE = 0,
    KCDCT_ZLIB = 1,
} kcd_compression_type_t;

struct kcdata_compress_descriptor {
    z_stream kcd_cd_zs;
    void* kcd_cd_base;
    uint64_t kcd_cd_offset;
    size_t kcd_cd_maxoffset;
    uint64_t kcd_cd_mark_begin;
    kcd_cd_flag_t kcd_cd_flags;
    kcd_compression_type_t kcd_cd_compression_type;
    void (*kcd_cd_memcpy_f)(size_t);
    mach_vm_address_t kcd_cd_totalout_addr;
    mach_vm_address_t kcd_cd_totalin_addr;
};
struct kcdata_descriptor {
    uint32_t kcd_length;
    uint16_t kcd_flags;
    uint16_t kcd_user_flags;
    mach_vm_address_t kcd_addr_begin;
    mach_vm_address_t kcd_addr_end;
    struct kcdata_compress_descriptor kcd_comp_d;
    uint32_t kcd_endalloced;
    struct kcdata_descriptor* (*kcd_alloc_callback)(size_t);
};
typedef struct kcdata_descriptor* kcdata_descriptor_t;

typedef uint64_t mach_vm_size_t;

typedef enum  {
    PRIO_DARWIN_GPU_UNKNOWN = 0,
    PRIO_DARWIN_GPU_ALLOW = 1,
    PRIO_DARWIN_GPU_DENY = 2,
    PRIO_DARWIN_GPU_BACKGROUND = 3,
    PRIO_DARWIN_GPU_UTILITY = 4,
    PRIO_DARWIN_GPU_UI_NON_FOCAL = 5,
    PRIO_DARWIN_GPU_UI = 6,
    PRIO_DARWIN_GPU_UI_FOCAL = 7,
} darwin_gpu_role_t;

typedef signed char int8_t;

struct vm_shared_region {
};
typedef enum  {
    THREAD_CALL_INDEX_INVALID = 0,
    THREAD_CALL_INDEX_HIGH = 1,
    THREAD_CALL_INDEX_KERNEL = 2,
    THREAD_CALL_INDEX_USER = 3,
    THREAD_CALL_INDEX_LOW = 4,
    THREAD_CALL_INDEX_KERNEL_HIGH = 5,
    THREAD_CALL_INDEX_QOS_UI = 6,
    THREAD_CALL_INDEX_QOS_IN = 7,
    THREAD_CALL_INDEX_QOS_UT = 8,
    THREAD_CALL_INDEX_MAX = 9,
} thread_call_index_t;

typedef enum  {
    THREAD_CALL_ALLOC = 1,
    THREAD_CALL_WAIT = 2,
    THREAD_CALL_DELAYED = 4,
    THREAD_CALL_RUNNING = 8,
    THREAD_CALL_SIGNAL = 16,
    THREAD_CALL_ONCE = 32,
    THREAD_CALL_RESCHEDULE = 64,
    THREAD_CALL_RATELIMITED = 128,
    THREAD_CALL_FLAG_CONTINUOUS = 256,
    THREAD_CALL_INITIALIZED = 512,
} thread_call_flags_t;

typedef int int32_t;

typedef void* thread_call_param_t;

typedef void (*thread_call_func_t)(thread_call_param_t);

struct thread_call {
    uint64_t tc_soft_deadline;
    struct priority_queue_entry_deadline tc_pqlink;
    queue_head_t* tc_queue;
    queue_chain_t tc_qlink;
    thread_call_index_t tc_index;
    thread_call_flags_t tc_flags;
    int32_t tc_refs;
    uint64_t tc_ttd;
    uint64_t tc_pending_timestamp;
    thread_call_func_t tc_func;
    thread_call_param_t tc_param0;
    thread_call_param_t tc_param1;
    uint64_t tc_submit_count;
    uint64_t tc_finish_count;
};
typedef struct thread_call* thread_call_t;

struct bank_element {
    unsigned int be_type: 31;
    unsigned int be_voucher_ref: 1;
    os_ref_atomic_t be_refs;
    unsigned int be_made;
    task_t be_task;
};
struct proc_persona_info {
    uint64_t unique_pid;
    int32_t pid;
    uint32_t flags;
    uint32_t pidversion;
    uint32_t persona_id;
    uint32_t uid;
    uint32_t gid;
    uint8_t macho_uuid[16];
};
struct bank_task {
    struct bank_element bt_elem;
    struct proc_persona_info bt_proc_persona;
    ledger_t bt_ledger;
    queue_head_t bt_accounts_to_pay;
    queue_head_t bt_accounts_to_charge;
    lck_mtx_t bt_acc_to_pay_lock;
    lck_mtx_t bt_acc_to_charge_lock;
    uint32_t bt_persona_uid;
    uint32_t bt_hasentitlement: 1;
    uint64_t bt_rsrc_coal_id;
    struct thread_group* bt_thread_group;
    queue_chain_t bt_global_elt;
};
struct ipc_importance_task {
};
typedef long long int64_t;

struct vm_extmod_statistics {
    int64_t task_for_pid_count;
    int64_t task_for_pid_caller_count;
    int64_t thread_creation_count;
    int64_t thread_creation_caller_count;
    int64_t thread_set_state_count;
    int64_t thread_set_state_caller_count;
};
typedef struct vm_extmod_statistics vm_extmod_statistics_data_t;

struct task_requested_policy {
    uint64_t trp_int_darwinbg: 1;
    uint64_t trp_ext_darwinbg: 1;
    uint64_t trp_int_iotier: 2;
    uint64_t trp_ext_iotier: 2;
    uint64_t trp_int_iopassive: 1;
    uint64_t trp_ext_iopassive: 1;
    uint64_t trp_bg_iotier: 2;
    uint64_t trp_terminated: 1;
    uint64_t trp_base_latency_qos: 3;
    uint64_t trp_base_through_qos: 3;
    uint64_t trp_apptype: 3;
    uint64_t trp_boosted: 1;
    uint64_t trp_role: 5;
    uint64_t trp_over_latency_qos: 3;
    uint64_t trp_over_through_qos: 3;
    uint64_t trp_sfi_managed: 1;
    uint64_t trp_qos_clamp: 3;
    uint64_t trp_sup_active: 1;
    uint64_t trp_sup_lowpri_cpu: 1;
    uint64_t trp_sup_timer: 3;
    uint64_t trp_sup_disk: 1;
    uint64_t trp_sup_throughput: 3;
    uint64_t trp_sup_cpu: 1;
    uint64_t trp_sup_bg_sockets: 1;
    uint64_t trp_runaway_mitigation: 1;
    uint64_t trp_reserved: 16;
};
struct task_effective_policy {
    uint64_t tep_darwinbg: 1;
    uint64_t tep_lowpri_cpu: 1;
    uint64_t tep_io_tier: 2;
    uint64_t tep_io_passive: 1;
    uint64_t tep_all_sockets_bg: 1;
    uint64_t tep_new_sockets_bg: 1;
    uint64_t tep_bg_iotier: 2;
    uint64_t tep_terminated: 1;
    uint64_t tep_qos_ui_is_urgent: 1;
    uint64_t tep_latency_qos: 3;
    uint64_t tep_through_qos: 3;
    uint64_t tep_tal_engaged: 1;
    uint64_t tep_watchers_bg: 1;
    uint64_t tep_sup_active: 1;
    uint64_t tep_role: 4;
    uint64_t tep_suppressed_cpu: 1;
    uint64_t tep_sfi_managed: 1;
    uint64_t tep_live_donor: 1;
    uint64_t tep_qos_clamp: 3;
    uint64_t tep_qos_ceiling: 3;
    uint64_t tep_promote_above_task: 1;
    uint64_t tep_coalition_bg: 1;
    uint64_t tep_runaway_mitigation: 1;
    uint64_t tep_reserved: 28;
};
struct task_pend_token {
    union  {
        struct  {
            uint32_t tpt_update_sockets: 1;
            uint32_t tpt_update_timers: 1;
            uint32_t tpt_update_watchers: 1;
            uint32_t tpt_update_live_donor: 1;
            uint32_t tpt_update_coal_sfi: 1;
            uint32_t tpt_update_throttle: 1;
            uint32_t tpt_update_thread_sfi: 1;
            uint32_t tpt_force_recompute_pri: 1;
            uint32_t tpt_update_tg_ui_flag: 1;
            uint32_t tpt_update_turnstile: 1;
            uint32_t tpt_update_tg_app_flag: 1;
            uint32_t tpt_update_game_mode: 1;
            uint32_t tpt_update_carplay_mode: 1;
            uint32_t tpt_update_appnap: 1;
        };
        uint32_t tpt_value;
    };
};
typedef enum  {
    TASK_MEMLIMIT_IS_ACTIVE = 1,
    TASK_MEMLIMIT_IS_FATAL = 2,
    TASK_MEMLIMIT_ACTIVE_EXC_RESOURCE = 4,
    TASK_MEMLIMIT_INACTIVE_EXC_RESOURCE = 8,
} task_memlimit_flags_t;

struct io_stat_entry {
    uint64_t count;
    uint64_t size;
};
struct io_stat_info {
    struct io_stat_entry disk_reads;
    struct io_stat_entry io_priority[4];
    struct io_stat_entry paging;
    struct io_stat_entry metadata;
    struct io_stat_entry total_io;
};
typedef struct io_stat_info* io_stat_info_t;

struct task_writes_counters {
    uint64_t task_immediate_writes;
    uint64_t task_deferred_writes;
    uint64_t task_invalidated_writes;
    uint64_t task_metadata_writes;
};
struct _cpu_time_qos_stats {
    uint64_t cpu_time_qos_default;
    uint64_t cpu_time_qos_maintenance;
    uint64_t cpu_time_qos_background;
    uint64_t cpu_time_qos_utility;
    uint64_t cpu_time_qos_legacy;
    uint64_t cpu_time_qos_user_initiated;
    uint64_t cpu_time_qos_user_interactive;
};
struct coalition {
};
typedef struct coalition* coalition_t;

typedef uint32_t task_exc_guard_behavior_t;

typedef unsigned char __darwin_uuid_t[16];

typedef __darwin_uuid_t uuid_t;

typedef unsigned long long vm_object_id_t;

struct _vm_object_query_data_ {
    vm_object_id_t object_id;
    mach_vm_size_t virtual_size;
    mach_vm_size_t resident_size;
    mach_vm_size_t wired_size;
    mach_vm_size_t reusable_size;
    mach_vm_size_t compressed_size;
    struct  {
        uint64_t vo_no_footprint: 1;
        uint64_t vo_ledger_tag: 3;
        uint64_t purgable: 2;
    };
};
typedef struct _vm_object_query_data_ vm_object_query_data_t;

struct _vmobject_list_output_ {
    uint64_t entries;
    vm_object_query_data_t data[0];
};
typedef struct _vmobject_list_output_* vmobject_list_output_t;

struct vm_deferred_reclamation_metadata_s {
};
typedef struct vm_deferred_reclamation_metadata_s* vm_deferred_reclamation_metadata_t;

struct task_security_config {
    union  {
        struct  {
            uint8_t hardened_heap: 1;
            uint8_t tpro: 1;
            uint8_t reserved: 1;
        };
        uint8_t value;
    };
};
typedef struct task_security_config task_security_config_s;

struct task {
    lck_mtx_t lock;
    os_refcnt_t ref_count;
    struct os_refgrp* ref_group;
    lck_spin_t ref_group_lock;
    _Bool active;
    _Bool ipc_active;
    _Bool halting;
    _Bool message_app_suspended;
    uint32_t vtimers;
    uint32_t loadTag;
    uint64_t task_uniqueid;
    vm_map_t __ptrauth(2, 1, 24312) map;
    queue_chain_t tasks;
    struct task_watchports* watchports;
    turnstile_inheritor_t returnwait_inheritor;
    queue_head_t threads;
    struct restartable_ranges* t_rr_ranges;
    processor_set_t pset_hint;
    struct affinity_space* affinity_space;
    int thread_count;
    uint32_t active_thread_count;
    int suspend_count;
    struct task_suspend_stats_s t_suspend_stats;
    task_suspend_source_array_t t_suspend_sources;
    integer_t user_stop_count;
    integer_t legacy_stop_count;
    int16_t priority;
    int16_t max_priority;
    integer_t importance;
    uint64_t total_runnable_time;
    struct recount_task tk_recount;
    lck_mtx_t itk_lock_data;
    struct ipc_port* __ptrauth(2, 1, 26821) itk_task_ports[4];
    struct ipc_port* __ptrauth(2, 1, 17479) itk_settable_self;
    struct exception_action exc_actions[14];
    struct hardened_exception_action hardened_exception_action;
    struct ipc_port* __ptrauth(2, 1, 47953) itk_host;
    struct ipc_port* __ptrauth(2, 1, 59496) itk_bootstrap;
    struct ipc_port* __ptrauth(2, 1, 47281) itk_debug_control;
    struct ipc_port* __ptrauth(2, 1, 47763) itk_task_access;
    struct ipc_port* __ptrauth(2, 1, 3791) itk_resume;
    struct ipc_port* __ptrauth(2, 1, 42068) itk_registered[3];
    ipc_port_t* __ptrauth(2, 1, 60539) itk_dyld_notify;
    struct ipc_port* __ptrauth(2, 1, 18151) itk_resource_notify;
    struct ipc_space* __ptrauth(2, 1, 33408) itk_space;
    ledger_t ledger;
    queue_head_t semaphore_list;
    int semaphores_owned;
    unsigned int priv_flags;
    void* __ptrauth(2, 1, 7578) task_debug;
    uint64_t rop_pid;
    uint64_t jop_pid;
    uint8_t disable_user_jop;
    _Atomic(uint8_t) has_jitbox;
    uint64_t jitbox_version;
    uint64_t jitbox_start;
    uint64_t jitbox_size;
    boolean_t jitbox_enabled;
    arm64_uexc_region_t uexc;
    _Bool preserve_x18;
    _Bool apt_traceable;
    _Bool uses_1ghz_timebase;
    counter_t faults;
    counter_t pageins;
    counter_t cow_faults;
    counter_t messages_sent;
    counter_t messages_received;
    uint32_t decompressions;
    uint32_t syscalls_mach;
    uint32_t syscalls_unix;
    uint32_t c_switch;
    uint32_t p_switch;
    uint32_t ps_switch;
    struct proc_ro* bsd_info_ro;
    kcdata_descriptor_t corpse_info;
    uint64_t crashed_thread_id;
    queue_chain_t corpse_tasks;
    struct label* crash_label;
    volatile uint32_t t_flags;
    uint32_t t_procflags;
    mach_vm_address_t all_image_info_addr;
    mach_vm_size_t all_image_info_size;
    uint32_t t_kpc;
    _Atomic(darwin_gpu_role_t) t_gpu_role;
    _Bool pidsuspended;
    _Bool frozen;
    _Bool changing_freeze_state;
    _Bool is_large_corpse;
    uint16_t policy_ru_cpu: 4;
    uint16_t policy_ru_cpu_ext: 4;
    uint16_t applied_ru_cpu: 4;
    uint16_t applied_ru_cpu_ext: 4;
    uint8_t rusage_cpu_flags;
    uint8_t rusage_cpu_percentage;
    uint8_t rusage_cpu_perthr_percentage;
    int8_t suspends_outstanding;
    uint8_t t_returnwaitflags;
    _Bool shared_region_auth_remapped;
    char* shared_region_id;
    struct vm_shared_region* shared_region;
    uint64_t rusage_cpu_interval;
    uint64_t rusage_cpu_perthr_interval;
    uint64_t rusage_cpu_deadline;
    thread_call_t rusage_cpu_callt;
    queue_head_t task_watchers;
    int num_taskwatchers;
    int watchapplying;
    struct bank_task* bank_context;
    struct ipc_importance_task* task_imp_base;
    vm_extmod_statistics_data_t extmod_statistics;
    struct task_requested_policy requested_policy;
    struct task_effective_policy effective_policy;
    struct task_pend_token pended_coalition_changes;
    uint32_t low_mem_notified_warn: 1;
    uint32_t low_mem_notified_critical: 1;
    uint32_t purged_memory_warn: 1;
    uint32_t purged_memory_critical: 1;
    uint32_t low_mem_privileged_listener: 1;
    uint32_t mem_notify_reserved: 27;
    _Atomic(task_memlimit_flags_t) memlimit_flags;
    io_stat_info_t task_io_stats;
    struct task_writes_counters task_writes_counters_internal;
    struct task_writes_counters task_writes_counters_external;
    struct _cpu_time_qos_stats cpu_time_eqos_stats;
    struct _cpu_time_qos_stats cpu_time_rqos_stats;
    uint32_t task_timer_wakeups_bin_1;
    uint32_t task_timer_wakeups_bin_2;
    uint64_t task_gpu_ns;
    uint8_t task_can_transfer_memory_ownership;
    uint8_t task_no_footprint_for_debug;
    uint8_t task_objects_disowning;
    uint8_t task_objects_disowned;
    int task_volatile_objects;
    int task_nonvolatile_objects;
    int task_owned_objects;
    queue_head_t task_objq;
    lck_mtx_t task_objq_lock;
    unsigned int task_thread_limit: 16;
    unsigned int task_legacy_footprint: 1;
    unsigned int task_extra_footprint_limit: 1;
    unsigned int task_ios13extended_footprint_limit: 1;
    unsigned int task_region_footprint: 1;
    unsigned int task_region_info_flags: 1;
    unsigned int task_has_crossed_thread_limit: 1;
    unsigned int task_rr_in_flight: 1;
    unsigned int task_jetsam_realtime_audio: 1;
    coalition_t coalition[2];
    queue_chain_t task_coalition[2];
    uint64_t dispatchqueue_offset;
    boolean_t task_unnested;
    int task_disconnected_count;
    void* __ptrauth(2, 1, 8023) hv_task_target;
    task_exc_guard_behavior_t task_exc_guard;
    mach_vm_address_t mach_header_vm_address;
    queue_head_t io_user_clients;
    boolean_t donates_own_pages;
    uint32_t task_shared_region_slide;
    uint64_t task_fs_metadata_writes;
    uuid_t task_shared_region_uuid;
    uint64_t memstat_dirty_start;
    vmobject_list_output_t corpse_vmobject_list;
    uint64_t corpse_vmobject_list_size;
    vm_deferred_reclamation_metadata_t deferred_reclamation_metadata;
    uint64_t task_cs_auxiliary_info;
    task_security_config_s security_config;
};
typedef struct task* task_t;

struct task_watchport_elem {
    task_t twe_task;
    ipc_port_t twe_port;
    ipc_port_t __ptrauth(2, 1, 50204) twe_pdrequest;
};
typedef unsigned int __darwin_natural_t;

typedef __darwin_natural_t natural_t;

typedef natural_t mach_port_seqno_t;

typedef natural_t mach_port_name_t;

typedef enum  {
    KN_ACTIVE = 1,
    KN_QUEUED = 2,
    KN_DISABLED = 4,
    KN_DROPPING = 8,
    KN_LOCKED = 16,
    KN_POSTING = 32,
    KN_DEFERDELETE = 128,
    KN_MERGE_QOS = 256,
    KN_REQVANISH = 512,
    KN_VANISHED = 1024,
    KN_SUPPRESSED = 2048,
} kn_status_t;

struct fileproc {
};
struct proc {
};
struct ipc_pset {
};
struct kevent_internal_s {
    uint64_t kei_ident;
    int8_t kei_filter;
    uint8_t kei_filtid;
    uint16_t kei_flags;
    int32_t kei_qos;
    uint64_t kei_udata;
    uint32_t kei_fflags;
    uint32_t kei_sfflags;
    int64_t kei_sdata;
    uint64_t kei_ext[4];
};
struct knote {
    struct  {
        struct knote* tqe_next;
        struct knote** tqe_prev;
    } kn_tqe;
    struct  {
        struct knote* sle_next;
    } kn_link;
    struct  {
        struct knote* sle_next;
    } kn_selnext;
    kn_status_t kn_status: 12;
    uintptr_t kn_qos_index: 4;
    uintptr_t kn_qos_override: 3;
    uintptr_t kn_is_fd: 1;
    uintptr_t kn_vnode_kqok: 1;
    uintptr_t kn_vnode_use_ofst: 1;
    uintptr_t kn_kq_packed: 42;
    union  {
        struct fileproc* __ptrauth(2, 1, 9899) kn_fp;
        struct proc* __ptrauth(2, 1, 12649) kn_proc;
        struct ipc_port* __ptrauth(2, 1, 7250) kn_ipc_port;
        struct ipc_pset* __ptrauth(2, 1, 48313) kn_ipc_pset;
        struct thread_call* __ptrauth(2, 1, 15222) kn_thcall;
        struct thread* __ptrauth(2, 1, 59459) kn_thread;
    };
    struct kevent_internal_s kn_kevent;
};
struct klist {
    struct knote* slh_first;
};
struct turnstile_list {
    struct turnstile* slh_first;
};
typedef enum turnstile_update_flags turnstile_update_flags_t;

struct turnstile {
    union  {
        struct turnstile_list ts_free_turnstiles;
        struct  {
            struct turnstile* sle_next;
        } ts_free_elm;
    };
    struct priority_queue_sched_max ts_inheritor_queue;
    struct priority_queue_entry_sched ts_inheritor_links;
    struct  {
        struct turnstile* sle_next;
    } ts_htable_link;
    uintptr_t ts_proprietor;
    os_ref_atomic_t ts_refcount;
    _Atomic(uint32_t) ts_type_gencount;
    uint32_t ts_prim_count;
    turnstile_update_flags_t ts_inheritor_flags;
    uint8_t ts_priority;
    uint8_t ts_state;
    thread_t ts_thread;
    thread_t ts_prev_thread;
};
struct ipc_mqueue {
    circle_queue_head_t imq_messages;
    mach_port_seqno_t imq_seqno;
    mach_port_name_t imq_receiver_name;
    uint16_t imq_msgcount;
    uint16_t imq_qlimit;
    uint32_t imq_context;
    union  {
        struct klist imq_klist;
        struct knote* __ptrauth(2, 1, 63730) imq_inheritor_knote;
        struct turnstile* __ptrauth(2, 1, 63484) imq_inheritor_turnstile;
        thread_t __ptrauth(2, 1, 10866) imq_inheritor_thread_ref;
        thread_t __ptrauth(2, 1, 62678) imq_srp_owner_thread;
    };
};
struct ipc_port_request_table {
};
typedef struct ipc_port_request_table* ipc_port_request_table_t;

typedef natural_t mach_port_mscount_t;

typedef natural_t mach_port_rights_t;

struct ipc_port {
    struct ipc_object ip_object;
    union  {
        int ip_pid;
        struct task_watchport_elem* __ptrauth(2, 1, 60129) ip_twe;
        struct ipc_port* __ptrauth(2, 1, 30908) ip_pdrequest;
    };
    struct ipc_mqueue ip_messages;
    ipc_port_request_table_t __ptrauth(2, 1, 47580) ip_requests;
    struct turnstile* ip_send_turnstile;
    mach_vm_address_t ip_context;
    natural_t ip_impcount;
    mach_port_mscount_t ip_mscount;
    mach_port_rights_t ip_srights;
    mach_port_rights_t ip_sorights;
    unsigned long ip_timetrack;
    uint32_t ip_made_bt;
    uint32_t ip_made_pid;
};
typedef enum  {
    PSET_SMP = 0,
    PSET_AMP_E = 1,
    PSET_AMP_P = 2,
    MAX_PSET_TYPES = 3,
} pset_cluster_type_t;

typedef bitmap_t pset_map_t;

struct pset_node {
    processor_set_t psets;
    pset_node_t node_list;
    pset_cluster_type_t pset_cluster_type;
    pset_map_t pset_map;
    _Atomic(pset_map_t) pset_idle_map;
    _Atomic(pset_map_t) pset_non_rt_map;
    _Atomic(pset_map_t) pset_recommended_map;
};
typedef struct pset_node* pset_node_t;

typedef enum  {
    CLUSTER_TYPE_INVALID = -1,
    CLUSTER_TYPE_SMP = 0,
    CLUSTER_TYPE_E = 1,
    CLUSTER_TYPE_P = 2,
    MAX_CPU_TYPES = 3,
} cluster_type_t;

typedef enum  {
    TH_BUCKET_FIXPRI = 0,
    TH_BUCKET_SHARE_FG = 1,
    TH_BUCKET_SHARE_IN = 2,
    TH_BUCKET_SHARE_DF = 3,
    TH_BUCKET_SHARE_UT = 4,
    TH_BUCKET_SHARE_BG = 5,
    TH_BUCKET_RUN = 6,
    TH_BUCKET_SCHED_MAX = 6,
    TH_BUCKET_MAX = 7,
} sched_bucket_t;

typedef union  {
    struct  {
        uint64_t pset_avg_thread_execution_time;
        uint64_t pset_execution_time_last_update;
    };
    unsigned __int128 pset_execution_time_packed;
} pset_execution_time_t;

union sched_clutch_edge {
    struct  {
        uint32_t sce_migration_allowed: 1;
        uint32_t sce_steal_allowed: 1;
        uint32_t _reserved: 30;
        uint32_t sce_migration_weight;
    };
    uint64_t sce_edge_packed;
};
typedef union sched_clutch_edge sched_clutch_edge;

typedef uint8_t pset_id_t;

typedef union  {
    pset_id_t spso_search_order[1];
    unsigned __int128 spso_packed;
} sched_pset_search_order_t;

struct processor_set {
    int pset_id;
    int online_processor_count;
    int cpu_set_low;
    int cpu_set_hi;
    int cpu_set_count;
    int last_chosen;
    uint64_t pset_load_average[6];
    uint32_t pset_runnable_depth[6];
    uint64_t pset_load_last_update;
    cpumap_t cpu_bitmask;
    cpumap_t recommended_bitmask;
    cpumap_t cpu_state_map[7];
    cpumap_t realtime_map;
    cpumap_t cpu_available_map;
    lck_ticket_t sched_lock;
    struct run_queue pset_runq;
    struct rt_queue rt_runq;
    _Atomic(uint64_t) stealable_rt_threads_earliest_deadline;
    struct sched_clutch_root pset_clutch_root;
    cpumap_t pending_AST_URGENT_cpu_mask;
    cpumap_t pending_AST_PREEMPT_cpu_mask;
    cpumap_t pending_deferred_AST_cpu_mask;
    cpumap_t pending_spill_cpu_mask;
    cpumap_t rt_pending_spill_cpu_mask;
    struct ipc_port* pset_self;
    struct ipc_port* pset_name_self;
    processor_set_t pset_list;
    pset_node_t node;
    uint32_t pset_cluster_id;
    pset_cluster_type_t pset_cluster_type;
    cluster_type_t pset_type;
    cpumap_t cpu_running_foreign;
    cpumap_t cpu_running_cluster_shared_rsrc_thread[2];
    sched_bucket_t cpu_running_buckets[10];
    bitmap_t foreign_psets[1];
    bitmap_t native_psets[1];
    bitmap_t local_psets[1];
    bitmap_t remote_psets[1];
    pset_execution_time_t pset_execution_time[6];
    uint64_t pset_cluster_shared_rsrc_load[2];
    _Atomic(sched_clutch_edge) sched_edges[2];
    sched_pset_search_order_t spill_search_order[6];
    uint8_t max_parallel_cores[6];
    uint8_t max_parallel_clusters[6];
    sched_clutch_edge sched_rt_edges[2];
    sched_pset_search_order_t sched_rt_spill_search_order;
    sched_pset_search_order_t sched_rt_steal_search_order;
    cpumap_t perfcontrol_cpu_preferred_bitmask;
    cpumap_t perfcontrol_cpu_migration_bitmask;
    int cpu_preferred_last_chosen;
};
typedef struct processor_set* processor_set_t;

typedef uint32_t sfi_class_id_t;

typedef enum perfcontrol_class perfcontrol_class_t;

typedef enum thread_urgency thread_urgency_t;

typedef lck_spin_t usimple_lock_data_t;

typedef usimple_lock_data_t simple_lock_data_t;

typedef void* timer_call_param_t;

typedef void (*timer_call_func_t)(timer_call_param_t);

struct timer_call {
    uint64_t tc_soft_deadline;
    simple_lock_data_t tc_lock;
    struct priority_queue_entry_deadline tc_pqlink;
    queue_head_t* tc_queue;
    queue_chain_t tc_qlink;
    timer_call_func_t tc_func;
    timer_call_param_t tc_param0;
    timer_call_param_t tc_param1;
    uint64_t tc_ttd;
    uint64_t tc_entry_time;
    uint32_t tc_flags;
    _Bool tc_async_dequeue;
};
struct recount_snap {
    uint64_t rsn_time_mach;
    uint64_t rsn_insns;
    uint64_t rsn_cycles;
};
typedef enum  {
    RCT_LVL_KERNEL = 0,
    RCT_LVL_USER = 1,
    RCT_LVL_SECURE = 2,
    RCT_LVL_COUNT = 3,
} recount_level_t;

struct recount_processor {
    struct recount_snap rpr_snap;
    struct recount_track rpr_active;
    recount_level_t rpr_current_level;
    uint64_t rpr_interrupt_duration_mach;
    uint64_t rpr_last_interrupt_enter_time_mach;
    uint64_t rpr_last_interrupt_leave_time_mach;
    uint64_t rpr_idle_time_mach;
    _Atomic(uint64_t) rpr_state_last_abs_time;
    uint8_t rpr_cpu_kind_index;
};
typedef enum  {
    REASON_NONE = 0,
    REASON_SYSTEM = 1,
    REASON_USER = 2,
    REASON_CLPC_SYSTEM = 3,
    REASON_CLPC_USER = 4,
    REASON_PMGR_SYSTEM = 5,
} processor_reason_t;

typedef enum  {
    PROCESSOR_OFFLINE_NOT_BOOTED = 0,
    PROCESSOR_OFFLINE_STARTING = 1,
    PROCESSOR_OFFLINE_STARTED_NOT_RUNNING = 2,
    PROCESSOR_OFFLINE_STARTED_NOT_WAITED = 3,
    PROCESSOR_OFFLINE_RUNNING = 4,
    PROCESSOR_OFFLINE_BEGIN_SHUTDOWN = 5,
    PROCESSOR_OFFLINE_PENDING_OFFLINE = 6,
    PROCESSOR_OFFLINE_CPU_OFFLINE = 7,
    PROCESSOR_OFFLINE_FULLY_OFFLINE = 8,
    PROCESSOR_OFFLINE_FINAL_SYSTEM_SLEEP = 9,
    PROCESSOR_OFFLINE_MAX = 10,
} processor_offline_state_t;

struct processor {
    processor_state_t state;
    _Bool is_recommended;
    _Bool current_is_bound;
    _Bool current_is_eagerpreempt;
    _Bool pending_nonurgent_preemption;
    struct thread* active_thread;
    struct thread* idle_thread;
    struct thread* startup_thread;
    processor_set_t processor_set;
    int current_pri;
    sfi_class_id_t current_sfi_class;
    perfcontrol_class_t current_perfctl_class;
    pset_cluster_type_t current_recommended_pset_type;
    thread_urgency_t current_urgency;
    struct thread_group* current_thread_group;
    int starting_pri;
    int cpu_id;
    uint64_t quantum_end;
    uint64_t last_dispatch;
    uint64_t kperf_last_sample_time;
    uint64_t deadline;
    _Bool first_timeslice;
    _Bool must_idle;
    _Bool next_idle_short;
    _Bool running_timers_active;
    struct timer_call running_timers[3];
    struct run_queue runq;
    struct recount_processor pr_recount;
    struct ipc_port* processor_self;
    processor_t processor_list;
    uint64_t timer_call_ttd;
    processor_reason_t last_startup_reason;
    processor_reason_t last_shutdown_reason;
    processor_reason_t last_recommend_reason;
    processor_reason_t last_derecommend_reason;
    _Bool processor_instartup;
    _Bool processor_booted;
    _Bool shutdown_temporary;
    _Bool processor_online;
    _Bool processor_inshutdown;
    processor_offline_state_t processor_offline_state;
    _Atomic(int) stir_the_pot_inbox_cpu;
};
typedef struct processor* processor_t;

struct waitq_link_list_entry {
    struct waitq_link_list_entry* next;
};
typedef struct waitq_link_list_entry waitq_link_list_t;

struct mpsc_queue_chain {
    _Atomic(struct mpsc_queue_chain*) mpqc_next;
};
struct waitq {
    union  {
        circle_queue_head_t waitq_links;
        waitq_link_list_t waitq_sellinks;
        void* waitq_inheritor;
        struct mpsc_queue_chain waitq_defer;
    };
    hw_lck_ticket_t waitq_interlock;
    uint8_t waitq_padding[0];
};
struct waitq_set {
    union  {
        circle_queue_head_t wqset_links;
        waitq_link_list_t wqset_sellinks;
        void* wqset_inheritor;
        struct mpsc_queue_chain wqset_defer;
    };
    hw_lck_ticket_t wqset_interlock;
    uint8_t wqset_padding[0];
    circle_queue_head_t wqset_preposts;
};
struct select_set {
    union  {
        circle_queue_head_t selset_links;
        waitq_link_list_t selset_sellinks;
        void* selset_inheritor;
        struct mpsc_queue_chain selset_defer;
    };
    hw_lck_ticket_t selset_interlock;
    uint8_t selset_padding[0];
    uint64_t selset_id;
};
typedef union  {
    struct waitq* wq_q;
    struct waitq_set* wqs_set;
    struct select_set* wqs_sel;
} waitq_t;

struct priority_queue_entry_stable {
    struct priority_queue_entry_stable* next;
    struct priority_queue_entry_stable* prev;
    long key: 16;
    unsigned long tag: 4;
    long child: 44;
    uint64_t stamp;
};
typedef enum  {
    AST_PREEMPT = 1,
    AST_QUANTUM = 2,
    AST_URGENT = 4,
    AST_HANDOFF = 8,
    AST_YIELD = 16,
    AST_APC = 32,
    AST_LEDGER = 64,
    AST_BSD = 128,
    AST_KPERF = 256,
    AST_MACF = 512,
    AST_RESET_PCS = 1024,
    AST_ARCADE = 2048,
    AST_MACH_EXCEPTION = 4096,
    AST_TELEMETRY_USER = 8192,
    AST_TELEMETRY_KERNEL = 16384,
    AST_TELEMETRY_PMI = 32768,
    AST_SFI = 65536,
    AST_DTRACE = 131072,
    AST_TELEMETRY_IO = 262144,
    AST_KEVENT = 524288,
    AST_REBALANCE = 1048576,
    AST_PROC_RESOURCE = 4194304,
    AST_DEBUG_ASSERT = 8388608,
    AST_TELEMETRY_MACF = 16777216,
} ast_t;

typedef int wait_result_t;

union thread_rr_state {
    uint32_t trr_value;
    struct  {
        uint8_t trr_fault_state;
        uint8_t trr_sync_waiting;
        uint16_t trr_ipi_ack_pending;
    };
};
typedef union thread_rr_state thread_rr_state_t;

typedef void (*thread_continue_t)(wait_result_t);

struct arm_state_hdr {
    uint32_t flavor;
    uint32_t count;
};
typedef struct arm_state_hdr arm_state_hdr_t;

struct arm_saved_state32 {
    uint32_t r[13];
    uint32_t sp;
    uint32_t lr;
    uint32_t pc;
    uint32_t cpsr;
    uint32_t far;
    uint32_t esr;
    uint32_t exception;
};
struct arm_saved_state64 {
    uint64_t x[29];
    uint64_t fp;
    uint64_t lr;
    uint64_t sp;
    uint64_t pc;
    uint32_t cpsr;
    uint32_t aspsr;
    uint64_t far;
    uint64_t esr;
    uint64_t jophash;
};
struct arm_saved_state {
    arm_state_hdr_t ash;
    union  {
        struct arm_saved_state32 ss_32;
        struct arm_saved_state64 ss_64;
    } uss;
};
typedef unsigned __int128 __uint128_t;

typedef __uint128_t uint128_t;

struct arm_neon_saved_state32 {
    union  {
        uint128_t q[16];
        uint64_t d[32];
        uint32_t s[32];
    } v;
    uint32_t fpsr;
    uint32_t fpcr;
};
typedef uint64_t uint64x2_t[2];

typedef uint32_t uint32x4_t[4];

struct arm_neon_saved_state64 {
    union  {
        uint128_t q[32];
        uint64x2_t d[32];
        uint32x4_t s[32];
    } v;
    uint32_t fpsr;
    uint32_t fpcr;
    uint32_t afpcr;
    uint32_t reserved;
};
struct arm_neon_saved_state {
    arm_state_hdr_t nsh;
    union  {
        struct arm_neon_saved_state32 ns_32;
        struct arm_neon_saved_state64 ns_64;
    } uns;
};
struct arm_context {
    struct arm_saved_state ss;
    struct arm_neon_saved_state ns;
};
typedef struct arm_context arm_context_t;

typedef struct arm_saved_state arm_saved_state_t;

typedef struct arm_neon_saved_state arm_neon_saved_state_t;

typedef unsigned int __uint32_t;

typedef unsigned long long __uint64_t;

struct arm_debug_state32 {
    __uint32_t bvr[16];
    __uint32_t bcr[16];
    __uint32_t wvr[16];
    __uint32_t wcr[16];
    __uint64_t mdscr_el1;
};
typedef struct arm_debug_state32 arm_debug_state32_t;

struct arm_debug_state64 {
    __uint64_t bvr[16];
    __uint64_t bcr[16];
    __uint64_t wvr[16];
    __uint64_t wcr[16];
    __uint64_t mdscr_el1;
};
typedef struct arm_debug_state64 arm_debug_state64_t;

struct arm_debug_aggregate_state {
    arm_state_hdr_t dsh;
    union  {
        arm_debug_state32_t ds32;
        arm_debug_state64_t ds64;
    } uds;
    os_refcnt_t ref;
};
typedef struct arm_debug_aggregate_state arm_debug_state_t;

typedef vm_offset_t vm_address_t;

struct perfcontrol_state {
    uint64_t opaque[8];
};
typedef _Bool (*expected_fault_handler_t)(arm_saved_state_t*);

struct machine_thread {
    uint32_t arm_machine_flags;
    arm_context_t* contextData;
    arm_saved_state_t* __ptrauth(2, 1, 7825) upcb;
    arm_neon_saved_state_t* __ptrauth(2, 1, 13674) uNeon;
    arm_saved_state_t* kpcb;
    union  {
        long pcpu_data_base_and_cpu_number;
        const uint16_t cpu_number;
    };
    long x86_64_compat;
    uint64_t recover_far;
    arm_debug_state_t* DebugData;
    vm_address_t cthread_self;
    uint64_t recover_esr;
    void* __ptrauth(2, 1, 27970) kstackptr;
    struct perfcontrol_state perfctrl_state;
    uint64_t aprr_shadow_mask_el0_value;
    volatile expected_fault_handler_t expected_fault_handler;
    volatile uintptr_t expected_fault_addr;
    volatile uintptr_t expected_fault_pc;
    uint64_t jitbox_ctl_el0;
    struct cpu_data* CpuDatap;
    unsigned int preemption_count;
    uint16_t exception_trace_code;
    _Bool vcpu_dirtied_matrix_context;
    uint64_t rop_pid;
    uint64_t jop_pid;
    uint64_t sprr_kern_perm;
    uint64_t tpidr2_el0;
    _Bool reserved15;
};
struct fakestack_header {
};
struct fakestack_header_list {
    struct fakestack_header* lh_first;
};
struct kasan_thread_data {
    struct fakestack_header_list fakestack_head;
};
typedef enum  {
    KS_MODE_NONE = 0,
    KS_MODE_TRACE = 1,
    KS_MODE_COUNTERS = 2,
    KS_MODE_STKSIZE = 3,
    KS_MODE_MAX = 4,
} ksancov_mode_t;

struct ksancov_header {
    uint32_t kh_magic;
    _Atomic(uint32_t) kh_enabled;
};
typedef struct ksancov_header ksancov_header_t;

struct ksancov_trace {
    ksancov_header_t kt_hdr;
    uint32_t kt_maxent;
    _Atomic(uint32_t) kt_head;
    uint64_t kt_entries[0];
};
typedef struct ksancov_trace ksancov_trace_t;

typedef enum  {
    KS_CMPS_MODE_NONE = 0,
    KS_CMPS_MODE_TRACE = 1,
    KS_CMPS_MODE_TRACE_FUNC = 2,
    KS_CMPS_MODE_MAX = 3,
} ksancov_cmps_mode_t;

typedef long dev_t;

struct ksancov_dev {
    ksancov_mode_t mode;
    union  {
        ksancov_header_t* cmps_hdr;
        ksancov_trace_t* cmps_trace;
    };
    size_t sz;
    size_t maxpcs;
    ksancov_cmps_mode_t cmps_mode;
    size_t cmps_sz;
    thread_t thread;
    dev_t dev;
    lck_mtx_t lock;
};
typedef struct ksancov_dev* ksancov_dev_t;

struct kcov_thread_data {
    uint32_t ktd_disabled;
    ksancov_dev_t ktd_device;
};
typedef struct kcov_thread_data kcov_thread_data_t;

typedef enum  {
    TH_MODE_NONE = 0,
    TH_MODE_REALTIME = 1,
    TH_MODE_FIXED = 2,
    TH_MODE_TIMESHARE = 3,
} sched_mode_t;

struct smrq_slink {
    __smrq_slink_t next;
};
typedef struct  {
    volatile struct smrq_slink* __smr_ptr;
} __smrq_slink_t;

struct smrq_slist_head {
    __smrq_slink_t first;
};
typedef union  {
    struct  {
        uint16_t shared_count;
        uint16_t interlock: 1;
        uint16_t priv_excl: 1;
        uint16_t want_upgrade: 1;
        uint16_t want_excl: 1;
        uint16_t r_waiting: 1;
        uint16_t w_waiting: 1;
        uint16_t can_sleep: 1;
        uint16_t _pad2: 8;
        uint16_t tag_valid: 1;
    };
    uint32_t data;
} lck_rw_word_t;

struct lck_rw_s {
    uint32_t lck_rw_unused: 24;
    uint32_t lck_rw_type: 8;
    uint32_t lck_rw_padding;
    lck_rw_word_t lck_rw;
    uint32_t lck_rw_owner;
};
typedef struct lck_rw_s lck_rw_t;

struct rw_lock_debug_entry {
    lck_rw_t* rwlde_lock;
    int8_t rwlde_mode_count;
    uintptr_t rwlde_caller_packed: 48;
};
struct rw_lock_debug {
    struct rw_lock_debug_entry rwld_locks[3];
    uint8_t rwld_locks_saved: 7;
    uint8_t rwld_overflow: 1;
    uint32_t rwld_locks_acquired;
};
typedef struct rw_lock_debug rw_lock_debug_t;

typedef struct timer_call* timer_call_t;

struct timer {
    uint64_t tstamp;
    uint64_t all_bits;
};
typedef struct timer timer_data_t;

struct recount_thread {
    struct recount_track* rth_lifetime;
    uint64_t rth_interrupt_duration_mach;
    recount_level_t rth_current_level;
};
struct affinity_set {
    struct affinity_space* aset_space;
    queue_chain_t aset_affinities;
    queue_head_t aset_threads;
    uint32_t aset_thread_count;
    uint32_t aset_tag;
    uint32_t aset_num;
    processor_set_t aset_pset;
};
typedef struct affinity_set* affinity_set_t;

struct task_watcher {
};
typedef struct task_watcher task_watch_t;

typedef natural_t mach_msg_size_t;

typedef struct  {
    mach_vm_address_t recv_msg_addr;
    mach_vm_address_t recv_aux_addr;
    mach_msg_size_t recv_msg_size;
    mach_msg_size_t recv_aux_size;
} mach_msg_recv_bufs_t;

typedef enum  {
    MACH64_MSG_OPTION_NONE = 0,
    MACH64_SEND_MSG = 1,
    MACH64_RCV_MSG = 2,
    MACH64_RCV_LARGE = 4,
    MACH64_RCV_LARGE_IDENTITY = 8,
    MACH64_SEND_TIMEOUT = 16,
    MACH64_SEND_OVERRIDE = 32,
    MACH64_SEND_INTERRUPT = 64,
    MACH64_SEND_NOTIFY = 128,
    MACH64_SEND_ALWAYS = 65536,
    MACH64_SEND_IMPORTANCE = 524288,
    MACH64_SEND_KERNEL = 4194304,
    MACH64_SEND_FILTER_NONFATAL = 65536,
    MACH64_SEND_TRAILER = 131072,
    MACH64_SEND_NOIMPORTANCE = 262144,
    MACH64_SEND_NODENAP = 262144,
    MACH64_SEND_SYNC_OVERRIDE = 1048576,
    MACH64_SEND_PROPAGATE_QOS = 2097152,
    MACH64_SEND_SYNC_BOOTSTRAP_CHECKIN = 8388608,
    MACH64_RCV_TIMEOUT = 256,
    MACH64_RCV_INTERRUPT = 1024,
    MACH64_RCV_VOUCHER = 2048,
    MACH64_RCV_GUARDED_DESC = 4096,
    MACH64_RCV_SYNC_WAIT = 16384,
    MACH64_RCV_SYNC_PEEK = 32768,
    MACH64_MSG_STRICT_REPLY = 512,
    MACH64_MSG_VECTOR = 4294967296ULL,
    MACH64_SEND_KOBJECT_CALL = 8589934592ULL,
    MACH64_SEND_MQ_CALL = 17179869184ULL,
    MACH64_SEND_ANY = 34359738368ULL,
    MACH64_SEND_DK_CALL = 68719476736ULL,
    MACH64_POLICY_KERNEL_EXTENSION = 137438953472ULL,
    MACH64_POLICY_FILTER_NON_FATAL = 274877906944ULL,
    MACH64_POLICY_FILTER_MSG = 549755813888ULL,
    MACH64_POLICY_DEFAULT = 1099511627776ULL,
    MACH64_POLICY_ENHANCED = 2199023255552ULL,
    MACH64_POLICY_PLATFORM = 4398046511104ULL,
    MACH64_POLICY_CONTAINED = 8796093022208ULL,
    MACH64_POLICY_KERNEL = 17592186044416ULL,
    MACH64_POLICY_SIMULATED = 35184372088832ULL,
    MACH64_POLICY_TRANSLATED = 70368744177664ULL,
    MACH64_POLICY_OPTED_OUT = 140737488355328ULL,
    MACH64_POLICY_ENHANCED_V0 = 281474976710656ULL,
    MACH64_POLICY_ENHANCED_V1 = 562949953421312ULL,
    MACH64_POLICY_ENHANCED_V2 = 844424930131968ULL,
    MACH64_POLICY_ENHANCED_VERSION_MASK = 844424930131968ULL,
    MACH64_POLICY_MASK = 280375465082880ULL,
    MACH64_RCV_LINEAR_VECTOR = 1152921504606846976ULL,
    MACH64_RCV_STACK = 2305843009213693952ULL,
    MACH64_MACH_MSG2 = 9223372036854775808ULL,
} mach_msg_option64_t;

typedef struct ipc_object* ipc_object_t;

typedef kern_return_t mach_msg_return_t;

struct ipc_importance_elem {
};
typedef enum  {
    IKM_KEEP_ALIVE_NONE = 0,
    IKM_KEEP_ALIVE_OWNED = 1,
    IKM_KEEP_ALIVE_IN_USE = 2,
} ipc_kmsg_keep_alive_t;

typedef enum  {
    IPC_OBJECT_COPYIN_FLAGS_NONE = 0,
    IPC_OBJECT_COPYIN_FLAGS_ALLOW_IMMOVABLE_SEND = 1,
    IPC_OBJECT_COPYIN_FLAGS_DEADOK = 2,
    IPC_OBJECT_COPYIN_FLAGS_DEST_EXTRA_COPY = 4,
    IPC_OBJECT_COPYIN_FLAGS_DEST_EXTRA_MOVE = 8,
} ipc_object_copyin_flags_t;

typedef uint8_t mach_msg_qos_t;

typedef enum  {
    MACH_MSG_TYPE_NONE = 0,
    MACH_MSG_TYPE_MOVE_RECEIVE = 16,
    MACH_MSG_TYPE_MOVE_SEND = 17,
    MACH_MSG_TYPE_MOVE_SEND_ONCE = 18,
    MACH_MSG_TYPE_COPY_SEND = 19,
    MACH_MSG_TYPE_MAKE_SEND = 20,
    MACH_MSG_TYPE_MAKE_SEND_ONCE = 21,
} mach_msg_type_name_t;

typedef enum  {
    IKM_TYPE_ALL_INLINED = 0,
    IKM_TYPE_UDATA_OOL = 1,
    IKM_TYPE_KDATA_OOL = 2,
    IKM_TYPE_ALL_OOL = 3,
} ipc_kmsg_type_t;

struct ipc_kmsg {
    queue_chain_t ikm_link;
    ipc_port_t __ptrauth(2, 1, 50242) ikm_voucher_port;
    struct ipc_importance_elem* ikm_importance;
    queue_chain_t ikm_inheritance;
    uint16_t ikm_aux_size;
    ipc_kmsg_keep_alive_t ikm_keep_alive;
    uint8_t __ikm_padding;
    uint32_t ikm_ppriority;
    uint32_t ikm_signature;
    ipc_object_copyin_flags_t ikm_flags;
    mach_msg_qos_t ikm_qos_override;
    mach_msg_type_name_t ikm_voucher_type: 6;
    ipc_kmsg_type_t ikm_type: 2;
    union  {
        uint32_t ikm_big_data[48];
        struct  {
            uint32_t ikm_small_data[42];
            void* __ptrauth(2, 1, 10397) ikm_kdata;
            void* __ptrauth(2, 1, 40087) ikm_udata;
            mach_msg_size_t ikm_kdata_size;
            mach_msg_size_t ikm_udata_size;
        };
    };
};
struct semaphore {
};
typedef void (*mach_msg_continue_t)(mach_msg_return_t);

typedef ipc_port_t mach_port_t;

struct thread_test_context {
};
struct ucred {
};
struct thread_ro_creds {
    struct ucred* tro_cred;
    struct ucred* tro_realcred;
};
struct thread_ro {
    struct thread* tro_owner;
    union  {
        struct  {
            struct ucred* tro_cred;
            struct ucred* tro_realcred;
        };
        struct thread_ro_creds tro_creds;
    };
    struct proc* tro_proc;
    struct proc_ro* tro_proc_ro;
    struct task* tro_task;
    struct ipc_port* tro_ports[3];
    struct ipc_port* tro_settable_self_port;
    struct exception_action* tro_exc_actions;
};
typedef unsigned long clock_sec_t;

typedef natural_t iv_index_t;

struct ipc_voucher {
    os_ref_atomic_t iv_refs;
    iv_index_t iv_table[8];
    ipc_port_t iv_port;
    struct smrq_slink iv_hash_link;
};
typedef struct ipc_voucher* ipc_voucher_t;

struct thread_requested_policy {
    uint64_t thrp_int_darwinbg: 1;
    uint64_t thrp_ext_darwinbg: 1;
    uint64_t thrp_int_iotier: 2;
    uint64_t thrp_ext_iotier: 2;
    uint64_t thrp_int_iopassive: 1;
    uint64_t thrp_ext_iopassive: 1;
    uint64_t thrp_latency_qos: 3;
    uint64_t thrp_through_qos: 3;
    uint64_t thrp_pidbind_bg: 1;
    uint64_t thrp_qos: 3;
    uint64_t thrp_qos_relprio: 4;
    uint64_t thrp_qos_override: 3;
    uint64_t thrp_qos_promote: 3;
    uint64_t thrp_qos_kevent_override: 3;
    uint64_t thrp_terminated: 1;
    uint64_t thrp_qos_workq_override: 3;
    uint64_t thrp_qos_wlsvc_override: 3;
    uint64_t thrp_iotier_kevent_override: 2;
    uint64_t thrp_wi_driven: 1;
    uint64_t thrp_reserved: 23;
};
struct thread_effective_policy {
    uint64_t thep_darwinbg: 1;
    uint64_t thep_io_tier: 2;
    uint64_t thep_io_passive: 1;
    uint64_t thep_all_sockets_bg: 1;
    uint64_t thep_new_sockets_bg: 1;
    uint64_t thep_terminated: 1;
    uint64_t thep_qos_ui_is_urgent: 1;
    uint64_t thep_latency_qos: 3;
    uint64_t thep_through_qos: 3;
    uint64_t thep_qos: 3;
    uint64_t thep_qos_relprio: 4;
    uint64_t thep_qos_promote: 3;
    uint64_t thep_promote_above_task: 1;
    uint64_t thep_wi_driven: 1;
    uint64_t thep_reserved: 38;
};
typedef u_int64_t user_addr_t;

struct thread_qos_override {
    struct thread_qos_override* override_next;
    uint32_t override_contended_resource_count;
    int16_t override_qos;
    int16_t override_resource_type;
    user_addr_t override_resource;
};
typedef enum  {
    THREAD_TAG_MAINTHREAD = 1,
    THREAD_TAG_CALLOUT = 2,
    THREAD_TAG_IOWORKLOOP = 4,
    THREAD_TAG_PTHREAD = 16,
    THREAD_TAG_WORKQUEUE = 32,
    THREAD_TAG_USER_JOIN = 64,
    THREAD_TAG_AIO_WORKQUEUE = 128,
} thread_tag_t;

struct work_interval {
};
typedef enum  {
    TH_WORK_INTERVAL_FLAGS_NONE = 0,
    TH_WORK_INTERVAL_FLAGS_AUTO_JOIN_LEAK = 1,
    TH_WORK_INTERVAL_FLAGS_HAS_WORKLOAD_ID = 2,
    TH_WORK_INTERVAL_FLAGS_RT_ALLOWED = 4,
} thread_work_interval_flags_t;

typedef enum thread_snapshot_wait_flags block_hint_t;

struct thread {
    uint64_t thread_magic;
    union  {
        struct thread_group* auto_join_thread_group;
        struct thread_group* work_interval_thread_group;
    };
    event64_t wait_event;
    struct  {
        processor_t runq;
    } __runq;
    waitq_t waitq;
    struct turnstile* turnstile;
    void* inheritor;
    struct priority_queue_sched_max sched_inheritor_queue;
    struct priority_queue_sched_max base_inheritor_queue;
    _Bool th_bound_cluster_enqueued;
    _Bool th_shared_rsrc_enqueued[2];
    _Bool th_shared_rsrc_heavy_user[2];
    _Bool th_shared_rsrc_heavy_perf_control[2];
    uint8_t th_expired_quantum_on_lower_core: 1;
    uint8_t th_expired_quantum_on_higher_core: 1;
    struct priority_queue_entry_stable th_clutch_runq_link;
    struct priority_queue_entry_sched th_clutch_pri_link;
    queue_chain_t th_clutch_timeshare_link;
    simple_lock_data_t sched_lock;
    simple_lock_data_t wake_lock;
    uint16_t options;
    _Bool wake_active;
    _Bool at_safe_point;
    uint8_t sched_saved_run_weight;
    _Bool pmap_footprint_suspended;
    ast_t reason;
    uint32_t quantum_remaining;
    wait_result_t wait_result;
    thread_rr_state_t t_rr_state;
    thread_continue_t continuation;
    void* parameter;
    vm_offset_t kernel_stack;
    vm_offset_t reserved_stack;
    struct machine_thread machine;
    struct kasan_thread_data kasan_data;
    kcov_thread_data_t kcov_data;
    int state;
    sched_mode_t sched_mode;
    sched_mode_t saved_mode;
    sched_bucket_t th_sched_bucket;
    sfi_class_id_t sfi_class;
    sfi_class_id_t sfi_wait_class;
    uint32_t sched_flags;
    int16_t sched_pri;
    int16_t base_pri;
    int16_t req_base_pri;
    int16_t max_priority;
    int16_t task_priority;
    uint16_t priority_floor_count;
    int16_t suspend_count;
    int iotier_override;
    os_ref_atomic_t ref_count;
    uint32_t rwlock_count;
    struct smrq_slist_head smr_stack;
    rw_lock_debug_t rw_lock_held;
    integer_t importance;
    integer_t depress_timer_active;
    timer_call_t depress_timer;
    struct  {
        uint32_t period;
        uint32_t computation;
        uint32_t constraint;
        _Bool preemptible;
        uint8_t priority_offset;
        uint64_t deadline;
    } realtime;
    uint64_t last_run_time;
    uint64_t last_made_runnable_time;
    uint64_t last_basepri_change_time;
    uint64_t same_pri_latency;
    uint64_t workq_quantum_deadline;
    struct thread_group* thread_group;
    processor_t bound_processor;
    processor_t last_processor;
    processor_t chosen_processor;
    uint64_t computation_metered;
    uint64_t computation_epoch;
    uint64_t computation_interrupt_epoch;
    uint64_t safe_release;
    void (*sched_call)(thread_t);
    natural_t sched_stamp;
    natural_t sched_usage;
    natural_t pri_shift;
    natural_t cpu_usage;
    natural_t cpu_delta;
    uint32_t c_switch;
    uint32_t p_switch;
    uint32_t ps_switch;
    uint64_t sched_time_save;
    uint64_t vtimer_user_save;
    uint64_t vtimer_prof_save;
    uint64_t vtimer_rlim_save;
    uint64_t vtimer_qos_save;
    timer_data_t runnable_timer;
    struct recount_thread th_recount;
    uint64_t wait_sfi_begin_time;
    queue_chain_t affinity_threads;
    affinity_set_t affinity_set;
    task_watch_t* taskwatch;
    union  {
        struct  {
            mach_msg_recv_bufs_t recv_bufs;
            mach_msg_option64_t option;
            ipc_object_t object;
            mach_msg_return_t state;
            mach_port_seqno_t seqno;
            mach_msg_size_t msize;
            mach_msg_size_t asize;
            mach_port_name_t receiver_name;
            struct ipc_kmsg* __ptrauth(2, 1, 13311) kmsg;
        } receive;
        struct  {
            struct semaphore* waitsemaphore;
            struct semaphore* signalsemaphore;
            int options;
            kern_return_t result;
            mach_msg_continue_t continuation;
        } sema;
        struct  {
            void* tls[8];
        } iokit;
    } saved;
    int32_t user_stop_count;
    natural_t ith_assertions;
    circle_queue_head_t ith_messages;
    mach_port_t ith_kernel_reply_port;
    _Bool th_vm_faults_disabled;
    _Bool recover;
    struct thread_test_context* th_test_ctx;
    queue_chain_t threads;
    queue_chain_t task_threads;
    struct thread_ro* t_tro;
    vm_map_t map;
    thread_t handoff_thread;
    timer_call_t wait_timer;
    uint16_t wait_timer_active;
    _Bool wait_timer_armed;
    uint32_t active: 1;
    uint32_t ipc_active: 1;
    uint32_t started: 1;
    uint32_t static_param: 1;
    uint32_t inspection: 1;
    uint32_t policy_reset: 1;
    uint32_t suspend_parked: 1;
    uint32_t corpse_dup: 1;
    volatile _Atomic(ast_t) ast;
    lck_mtx_t mutex;
    struct ipc_port* ith_special_reply_port;
    uint16_t t_dtrace_flags;
    uint16_t t_dtrace_inprobe;
    uint32_t t_dtrace_predcache;
    int64_t t_dtrace_tracing;
    int64_t t_dtrace_vtime;
    clock_sec_t t_page_creation_time;
    uint32_t t_page_creation_count;
    uint32_t t_page_creation_throttled;
    uint64_t t_page_creation_throttled_hard;
    uint64_t t_page_creation_throttled_soft;
    int t_pagein_error;
    mach_port_name_t ith_voucher_name;
    ipc_voucher_t ith_voucher;
    uint32_t kperf_ast;
    uint32_t kperf_pet_gen;
    uint32_t kperf_c_switch;
    uint32_t kperf_pet_cnt;
    uint64_t* kpc_buf;
    void* hv_thread_target;
    uint32_t syscalls_unix;
    uint32_t syscalls_mach;
    ledger_t t_ledger;
    ledger_t t_threadledger;
    ledger_t t_bankledger;
    uint64_t t_deduct_bank_ledger_time;
    uint64_t t_deduct_bank_ledger_energy;
    uint64_t thread_id;
    uint32_t ctid;
    uint32_t ctsid;
    struct thread_requested_policy requested_policy;
    struct thread_effective_policy effective_policy;
    struct thread_qos_override* overrides;
    uint32_t kevent_overrides;
    uint8_t user_promotion_basepri;
    uint8_t kern_promotion_schedpri;
    _Atomic(uint16_t) kevent_ast_bits;
    io_stat_info_t thread_io_stats;
    uint32_t thread_callout_interrupt_wakeups;
    uint32_t thread_callout_platform_idle_wakeups;
    uint32_t thread_timer_wakeups_bin_1;
    uint32_t thread_timer_wakeups_bin_2;
    thread_tag_t thread_tag;
    uint16_t callout_woken_from_icontext: 1;
    uint16_t callout_woken_from_platform_idle: 1;
    uint16_t callout_woke_thread: 1;
    uint16_t mach_exc_fatal: 1;
    uint16_t mach_exc_ktriage: 1;
    uint16_t thread_bitfield_unused: 11;
    uint32_t th_bound_cluster_id;
    struct thread_group* preadopt_thread_group;
    struct thread_group* old_preadopt_thread_group;
    struct thread_group* bank_thread_group;
    struct work_interval* th_work_interval;
    thread_work_interval_flags_t th_work_interval_flags;
    turnstile_update_flags_t inheritor_flags;
    block_hint_t pending_block_hint;
    block_hint_t block_hint;
    uint32_t decompressions;
    int thread_region_page_shift;
    void* decmp_upl;
    struct knote* ith_knote;
    uintptr_t txm_thread_stack;
};
typedef struct thread* thread_t;

typedef void* cpu_id_t;

typedef enum  {
    SIGPnop = 0,
    SIGPxcall = 4,
    SIGPast = 8,
    SIGPdebug = 16,
    SIGPLWFlush = 32,
    SIGPLWClean = 64,
    SIGPkppet = 256,
    SIGPxcallImm = 512,
    SIGPTimerLocal = 1024,
    SIGPdeferred = 2048,
    SIGPtimeout = 4096,
    SIGPdisabled = 2147483648,
} cpu_signal_t;

typedef void (*cache_dispatch_t)(unsigned int);

typedef uint32_t (*get_decrementer_t)(void);

typedef void (*set_decrementer_t)(uint32_t);

typedef void (*fiq_handler_t)(void);

typedef void (*processor_idle_t)(uint64_t*);

typedef void (*IOInterruptHandler)(int);

typedef void (*idle_timer_t)(uint64_t*);

struct mpqueue_head {
    struct queue_entry head;
    struct priority_queue_deadline_min mpq_pqhead;
    uint64_t earliest_soft_deadline;
    uint64_t count;
    lck_ticket_t lock_data;
};
typedef struct mpqueue_head mpqueue_head_t;

struct rtclock_timer {
    mpqueue_head_t queue;
    uint64_t deadline;
    uint32_t is_set: 1;
    uint32_t has_expired: 1;
};
typedef struct rtclock_timer rtclock_timer_t;

struct _rtclock_data_ {
};
typedef void (*platform_error_handler_t)(vm_offset_t);

struct mt_cpu {
    uint64_t mtc_snaps[2];
    uint64_t mtc_counts[2];
    uint64_t mtc_counts_last[2];
    uint64_t mtc_npmis;
    _Bool mtc_active;
};
typedef struct  {
    uint64_t irq_ex_cnt;
    uint64_t irq_ex_cnt_wake;
    uint64_t ipi_cnt;
    uint64_t ipi_cnt_wake;
    uint64_t timer_cnt;
    uint64_t pmi_cnt_wake;
    uint64_t undef_ex_cnt;
    uint64_t unaligned_cnt;
    uint64_t vfp_cnt;
    uint64_t data_ex_cnt;
    uint64_t instr_ex_cnt;
} cpu_stat_t;

typedef uint64_t tt_entry_t;

typedef uint64_t pmap_paddr_t;

typedef uint64_t vm_map_address_t;

struct page_table_attr {
};
typedef uint64_t vm_map_offset_t;

typedef __uint128_t TXMWidePointer_t;

struct _TXMTaggedPointer {
    union  {
        TXMWidePointer_t raw;
        struct  {
            uintptr_t tag;
            uintptr_t addr;
        };
    };
};
typedef struct _TXMTaggedPointer TXMTaggedPointer_t;

typedef uint8_t _TryLock;

typedef _Atomic(_TryLock) TryLock_t;

struct _TXMSlabObject {
    TXMTaggedPointer_t objectLink;
    TryLock_t objectLock;
    _Bool objectActive;
};
typedef struct _TXMSlabObject TXMSlabObject_t;

typedef uint64_t TXMAddressSpaceFlags_t;

typedef enum  {
    kCSRestrictedModePermNever = 0,
    kCSRestrictedModePermBefore = 1,
    kCSRestrictedModePermAfter = 2,
    kCSRestrictedModePermBoth = 3,
} CSRestrictedModePerms_t;

typedef uint16_t TXMAddressSpaceIdentifier_t;

typedef uint16_t TXMAddressSpaceIDType_t;

struct _TXMAddressSpaceID {
    TXMAddressSpaceIdentifier_t identifier;
    TXMAddressSpaceIDType_t type;
};
typedef struct _TXMAddressSpaceID TXMAddressSpaceID_t;

typedef _Atomic(uint32_t) TXMReferenceCount_t;

typedef uint64_t CT_uint64_t;

typedef CT_uint64_t CoreTrustPolicyFlags;

typedef CoreTrustPolicyFlags CMSPolicyFlags_t;

struct _CSConfigFeatureSet {
    _Bool restrictedExecutionMode;
    _Bool OOPJit;
    _Bool localSigning;
    _Bool compilationService;
    _Bool appleInternalProfiles;
    _Bool developerMode;
    _Bool demoMode;
    _Bool JIT;
    _Bool executableCommPage;
};
typedef struct _CSConfigFeatureSet CSConfigFeatureSet_t;

struct _CSConfigOSPolicy {
    uint32_t minimumCodeDirectoryVersion;
    uint8_t minimumHashTypeForPlatformCode;
    _Bool trustCacheCodeOnly;
    _Bool platformCodeOnly;
    CMSPolicyFlags_t platformCTFlags;
    CMSPolicyFlags_t appStoreCTFlags;
    CMSPolicyFlags_t profileValidatedCTFlags;
    CMSPolicyFlags_t appStoreQACTFlags;
    CMSPolicyFlags_t profileValidatedQACTFlags;
    CMSPolicyFlags_t profileCTFlags;
    const char** developerLimit;
    CSConfigFeatureSet_t featureSet;
    struct  {
        const char* appContainerPath;
    } specialPaths;
};
typedef struct _CSConfigOSPolicy CSConfigOSPolicy_t;

typedef void* (*CERuntimeMalloc)(size_t);

typedef void (*CERuntimeFree)(void*);

typedef void (*CERuntimeLog)(const char*);

typedef void (*CERuntimeAbort)(const char*);

typedef const struct CERuntime* CERuntime_t;

typedef _Bool (*CERuntimeInternalStatus)(const CERuntime_t);

typedef void* (*CERuntimeAllocIndex)(size_t);

typedef void (*CERuntimeFreeIndex)(size_t);

struct CERuntime {
    const uint64_t version;
    const CERuntimeMalloc alloc;
    const CERuntimeFree free;
    const CERuntimeLog log;
    const CERuntimeAbort abort;
    const CERuntimeInternalStatus internalStatus;
    const CERuntimeAllocIndex allocIndex;
    const CERuntimeFreeIndex freeIndex;
};
typedef struct CERuntime EntitlementsRuntime_t;

struct _TCReturn {
    union  {
        uint32_t rawValue;
        struct  {
            uint8_t component;
            uint8_t error;
            uint16_t uniqueError;
        };
    };
};
typedef struct _TCReturn TCReturn_t;

typedef uint8_t TCType_t;

struct _TrustCacheModuleBase {
    uint32_t version;
};
typedef struct _TrustCacheModuleBase TrustCacheModuleBase_t;

struct _TrustCache {
    _Atomic(struct _TrustCache*) next;
    TCType_t type;
    _Bool tombstoned;
    size_t moduleSize;
    const TrustCacheModuleBase_t* module;
};
typedef struct _TrustCache TrustCache_t;

struct _TrustCacheQueryToken {
    const TrustCache_t* trustCache;
    void* trustCacheEntry;
};
typedef struct _TrustCacheQueryToken TrustCacheQueryToken_t;

struct _CSConfigTrustCaches {
    TCReturn_t (*queryCDHash)(TrustCacheQueryToken_t*);
    TCReturn_t (*queryCDHashForREM)(CSRestrictedModePerms_t*);
    _Bool queryTokenSupported;
};
typedef struct _CSConfigTrustCaches CSConfigTrustCaches_t;

struct _CSConfigProvisioningProfiles {
    char deviceUDID[32];
    _Bool (*auxiliaryValidate)(void*);
};
typedef struct _CSConfigProvisioningProfiles CSConfigProvisioningProfiles_t;

struct _CSBuffer {
    const uint8_t* data;
    size_t dataSize;
};
typedef struct _CSBuffer CSBuffer_t;

typedef enum  {
    kCEContextTypeEntitlements = 0,
    kCEContextTypeProvisioningProfileEntitlements = 1,
    kCEContextTypeProvisioningProfile = 2,
    kCEContextTypeLWCR = 3,
    kCEContextTypeTotal = 4,
} CEContextType_t;

typedef uint32_t CEFormatVersion_t;

struct _CEContextInfo {
    CEContextType_t type;
    CEFormatVersion_t version;
};
typedef struct _CEContextInfo CEContextInfo_t;

struct CEAccelerationElement {
    uint32_t key_offset;
    uint32_t key_length;
};
typedef struct CEAccelerationElement CEAccelerationElement_t;

struct CEAccelerationContext {
    CEAccelerationElement_t* index;
    size_t index_count;
};
typedef unsigned long ccder_tag;

struct ccder_read_blob {
    const uint8_t* der;
    const uint8_t* der_end;
};
typedef struct ccder_read_blob ccder_read_blob;

struct der_vm_context {
    CERuntime_t runtime;
    struct CEAccelerationContext lookup;
    ccder_tag dictionary_tag;
    _Bool sorted;
    _Bool valid;
    union  {
        ccder_read_blob ccstate;
        struct  {
            const uint8_t* der_start;
            const uint8_t* der_end;
        } state;
    };
};
typedef struct der_vm_context der_vm_context_t;

struct CEQueryContext {
    der_vm_context_t der_context;
    _Bool managed;
};
struct _CEContext {
    CEContextInfo_t info;
    struct CEQueryContext legacyContext;
};
typedef struct _CEContext CEContext_t;

typedef CEContext_t EntitlementsContext_t;

struct _CSConfigLocalSigning {
    CSBuffer_t (*getPublicKey)(void);
    _Bool (*matchAuthentication)(const uint8_t*);
    EntitlementsContext_t* allowedEntitlementsSet;
};
typedef struct _CSConfigLocalSigning CSConfigLocalSigning_t;

struct _CSConfigCompilationService {
    _Bool (*matchCDHash)(const uint8_t*);
};
typedef struct _CSConfigCompilationService CSConfigCompilationService_t;

struct _CSConfigCallerSignature {
    const SignatureValidation_t* (*acquireSig)(void**);
    void (*releaseSig)(void*);
};
typedef struct _CSConfigCallerSignature CSConfigCallerSignature_t;

struct _CSConfigEnvironmentState {
    _Bool (*developerMode)(void);
    _Bool (*demoMode)(void);
    _Bool (*lockdownMode)(void);
    _Bool (*researchMode)(void);
    _Bool (*extendedResearchMode)(void);
};
typedef struct _CSConfigEnvironmentState CSConfigEnvironmentState_t;

struct _CSMutableBuffer {
    uint8_t* data;
    size_t dataSize;
};
typedef struct _CSMutableBuffer CSMutableBuffer_t;

struct _CSConfig {
    const CSConfigOSPolicy_t* systemPolicy;
    _Bool (*platformCodeOnly)(void);
    const EntitlementsRuntime_t* entitlementsRuntime;
    CSConfigTrustCaches_t trustCaches;
    CSConfigProvisioningProfiles_t provisioningProfiles;
    CSConfigLocalSigning_t localSigning;
    CSConfigCompilationService_t compilationService;
    CSConfigCallerSignature_t callerSignature;
    CSConfigEnvironmentState_t environmentState;
    CSMutableBuffer_t (*getMutableBuffer)(CSBuffer_t);
    struct  {
        _Bool skipTrustEvaluation;
        _Bool allowAnySignature;
        _Bool allowUnrestrictedLocalSigning;
        _Bool allowInternalCAs;
        _Bool enforceCoreTrust;
        _Bool relaxRestrictedModePerms;
        _Bool relaxProfileTrust;
    } exemptions;
};
typedef struct _CSConfig CSConfig_t;

struct _CSSuperBlobIndex {
    uint32_t type;
    uint32_t offset;
};
typedef struct _CSSuperBlobIndex CSSuperBlobIndex_t;

struct _CSSuperBlob {
    uint32_t magic;
    uint32_t length;
    uint32_t count;
    CSSuperBlobIndex_t index[0];
};
typedef struct _CSSuperBlob CSSuperBlob_t;

struct _CSSuperBlobSafe {
    const CSSuperBlob_t* data;
    uint32_t dataSize;
};
typedef struct _CSSuperBlobSafe CSSuperBlobSafe_t;

struct _CSCodeDirectory {
    uint32_t magic;
    uint32_t length;
    uint32_t version;
    uint32_t flags;
    uint32_t hashesOffset;
    uint32_t signingIdentifierOffset;
    uint32_t numSpecialSlots;
    uint32_t numCodeSlots;
    uint32_t codeLimit;
    uint8_t hashSize;
    uint8_t hashType;
    uint8_t platformIdentifier;
    uint8_t pageShift;
    uint32_t spare0;
};
typedef struct _CSCodeDirectory CSCodeDirectory_t;

struct _CSCodeDirectorySafe {
    const CSCodeDirectory_t* data;
    uint32_t dataSize;
};
typedef struct _CSCodeDirectorySafe CSCodeDirectorySafe_t;

typedef uint8_t CSTrust_t;

typedef struct _CSConfig CSConfig_t;

typedef uint32_t CT_uint32_t;

typedef CT_uint32_t CoreTrustDigestType;

typedef CoreTrustDigestType CMSDigestType_t;

struct _CMSValidation {
    const uint8_t* cmsData;
    size_t cmsDataSize;
    const uint8_t* cmsLeafCert;
    size_t cmsLeafCertSize;
    const uint8_t* cmsContent;
    size_t cmsContentSize;
    CMSDigestType_t agilityHashType;
    const uint8_t* agilityHash;
    size_t agilityHashSize;
    CMSDigestType_t digestType;
    CMSPolicyFlags_t policyFlags;
    _Bool cmsInitialized;
    _Bool cmsVerified;
    _Bool allowDebuggingRoots;
};
typedef struct _CMSValidation CMSValidation_t;

typedef CEContext_t ProfileContext_t;

struct _CSProfileProperties {
    uint32_t developer: 1;
    uint32_t testFlight: 1;
    uint32_t universal: 1;
    uint32_t appleInternal: 1;
    uint32_t demoMode: 1;
    uint32_t appShack: 1;
    uint32_t internalBuild: 1;
    uint32_t noExecute: 1;
    uint32_t reserved: 23;
};
typedef struct _CSProfileProperties CSProfileProperties_t;

struct _ProfileValidation {
    const CSConfig_t* config;
    CMSValidation_t profileCMS;
    ProfileContext_t profileCtx;
    EntitlementsContext_t entCtx;
    _Bool entInit;
    CSProfileProperties_t properties;
    _Bool profileInitialized;
    _Bool profileVerified;
    _Bool profileTrusted;
};
typedef struct _ProfileValidation ProfileValidation_t;

struct _SignatureValidation {
    const CSConfig_t* config;
    CSBuffer_t signatureBlob;
    CSSuperBlobSafe_t superBlob;
    _Bool unusedBufferAllocated;
    _Bool signatureParsed;
    _Bool appContainerPath;
    CSCodeDirectorySafe_t codeDirectory;
    uint8_t CDHash[20];
    EntitlementsContext_t entCtx;
    _Bool entInit;
    CSTrust_t trustLevelInterim;
    CSTrust_t trustLevel;
    const ProfileValidation_t* profile;
    CSBuffer_t leafCert;
};
typedef struct _SignatureValidation SignatureValidation_t;

struct _TXMCodeSignature {
    TXMSlabObject_t slabObject;
    uint8_t sptmType;
    TXMReferenceCount_t referenceCount;
    _Bool reconstituted;
    void* kernelEntitlements;
    SignatureValidation_t sig;
};
typedef struct _TXMCodeSignature TXMCodeSignature_t;

struct _TXMCodeRegion {
    TXMSlabObject_t slabObject;
    struct  {
        enum  {
            kTXMCodeRegionTypeExecutable = 0,
            kTXMCodeRegionTypeSharedRegion = 1,
            kTXMCodeRegionTypeJIT = 2,
            kTXMCodeRegionTypeDebug = 3,
        } type : 7;
        uint8_t debugged: 1;
    } properties;
    union  {
        struct  {
            size_t offsetInFile;
            TXMCodeSignature_t* codeSignature;
        } executable;
        struct  {
            struct _TXMAddressSpace* nestedSpace;
        } sharedCache;
    };
    uintptr_t addr;
    uintptr_t addrEnd;
    struct  {
        struct _TXMCodeRegion* rbe_left;
        struct _TXMCodeRegion* rbe_right;
        struct _TXMCodeRegion* rbe_parent;
    } RBLink;
};
struct _TXMCodeRegionRBTree {
    struct _TXMCodeRegion* rbh_root;
};
typedef struct _TXMCodeRegionRBTree TXMCodeRegionRBTree_t;

struct _TXMAddressSpace {
    TXMSlabObject_t slabObject;
    TXMAddressSpaceFlags_t addrSpaceFlags;
    CSRestrictedModePerms_t remPerms;
    TXMAddressSpaceID_t addrSpaceID;
    TXMCodeRegionRBTree_t codeRegions;
    struct  {
        uintptr_t baseAddr;
        uintptr_t baseAddrEnd;
        TXMReferenceCount_t referenceCount;
    };
};
typedef struct _TXMAddressSpace TXMAddressSpace_t;

typedef void* vm_map_serial_t;

struct pmap {
    tt_entry_t* tte;
    pmap_paddr_t ttep;
    vm_map_address_t min;
    vm_map_address_t max;
    const struct page_table_attr* pmap_pt_attr;
    ledger_t ledger;
    lck_rw_t rwlock;
    queue_chain_t pmaps;
    vm_map_address_t nested_region_addr;
    vm_map_offset_t nested_region_size;
    vm_map_offset_t nested_region_true_start;
    vm_map_offset_t nested_region_true_end;
    union  {
        uint16_t asid;
        uint16_t vmid;
    };
    os_ref_atomic_t ref_count;
    int pmap_pid;
    char pmap_procname[17];
    _Bool xprr_jit_enabled;
    _Bool pmap_vm_map_cs_enforced;
    _Bool is_x86_64;
    _Bool is_rosetta;
    _Bool footprint_suspended;
    _Bool footprint_was_suspended;
    _Bool nx_enabled;
    _Bool is_64bit;
    _Bool disable_jop;
    _Bool xprr_tpro_enabled;
    uint8_t type;
    lck_rw_t txm_lck;
    TXMAddressSpace_t* __ptrauth(2, 1, 2749) txm_addr_space;
    CSTrust_t txm_trust_level;
    vm_map_serial_t associated_vm_map_serial_id;
};
typedef uint64_t pt_entry_t;

struct pv_entry {
    struct pv_entry* pve_next;
    pt_entry_t* pve_ptep[2];
};
typedef struct pv_entry pv_entry_t;

typedef struct  {
    pv_entry_t* list;
    uint32_t count;
} pv_free_list_t;

struct pmap_cpu_data {
    _Atomic(const volatile struct pmap*) active_stage2_pmap;
    unsigned int cpu_number;
    _Bool copywindow_strong_sync[4];
    pv_free_list_t pv_free;
    pv_entry_t* pv_free_spill_marker;
};
struct arm_thread_state64 {
    __uint64_t x[29];
    __uint64_t fp;
    __uint64_t lr;
    __uint64_t sp;
    __uint64_t pc;
    __uint32_t cpsr;
    __uint32_t flags;
};
typedef struct arm_thread_state64 arm_thread_state64_t;

typedef arm_thread_state64_t dbgwrap_thread_state_t;

struct kcov_cpu_data {
    uint32_t kcd_enabled;
};
typedef struct kcov_cpu_data kcov_cpu_data_t;

struct cpu_data {
    unsigned short cpu_number;
    _Atomic(cpu_flags_t) cpu_flags;
    int cpu_type;
    int cpu_subtype;
    int cpu_threadtype;
    void* __ptrauth(2, 1, 59725) istackptr;
    vm_offset_t intstack_top;
    void* __ptrauth(2, 1, 1127) excepstackptr;
    vm_offset_t excepstack_top;
    thread_t cpu_active_thread;
    vm_offset_t cpu_active_stack;
    cpu_id_t cpu_id;
    volatile cpu_signal_t cpu_signal;
    ast_t cpu_pending_ast;
    cache_dispatch_t cpu_cache_dispatch;
    uint64_t cpu_base_timebase;
    uint64_t cpu_timebase;
    _Bool cpu_hibernate;
    _Bool cpu_running;
    _Bool cluster_master;
    _Bool sync_on_cswitch;
    _Bool in_state_transition;
    uint32_t cpu_decrementer;
    get_decrementer_t cpu_get_decrementer_func;
    set_decrementer_t cpu_set_decrementer_func;
    fiq_handler_t cpu_get_fiq_handler;
    void* cpu_tbd_hardware_addr;
    void* cpu_tbd_hardware_val;
    processor_idle_t cpu_idle_notify;
    uint64_t cpu_idle_latency;
    uint64_t cpu_idle_pop;
    vm_offset_t cpu_reset_handler;
    uintptr_t cpu_reset_assist;
    uint32_t cpu_reset_type;
    unsigned int interrupt_source;
    void* cpu_int_state;
    IOInterruptHandler interrupt_handler;
    void* interrupt_nub;
    void* interrupt_target;
    void* interrupt_refCon;
    idle_timer_t idle_timer_notify;
    void* idle_timer_refcon;
    uint64_t idle_timer_deadline;
    uint64_t rtcPop;
    rtclock_timer_t rtclock_timer;
    struct _rtclock_data_* rtclock_datap;
    arm_debug_state_t* cpu_user_debug;
    vm_offset_t cpu_debug_interface_map;
    volatile int debugger_active;
    volatile int PAB_active;
    void* cpu_xcall_p0;
    void* cpu_xcall_p1;
    void* cpu_imm_xcall_p0;
    void* cpu_imm_xcall_p1;
    vm_offset_t coresight_base[4];
    uint64_t cpu_regmap_paddr;
    uint32_t cpu_phys_id;
    platform_error_handler_t platform_error_handler;
    int cpu_mcount_off;
    volatile unsigned int cpu_sleep_token;
    unsigned int cpu_sleep_token_last;
    cluster_type_t cpu_cluster_type;
    uint32_t cpu_cluster_id;
    uint32_t cpu_l2_id;
    uint32_t cpu_l2_size;
    uint32_t cpu_l3_id;
    uint32_t cpu_l3_size;
    enum  {
        CPU_NOT_HALTED = 0,
        CPU_HALTED = 1,
        CPU_HALTED_WITH_STATE = 2,
    } halt_status;
    uint64_t rop_key;
    uint64_t jop_key;
    uint64_t jitbox_version;
    uint64_t jitbox_start;
    uint64_t jitbox_size;
    boolean_t jitbox_enabled;
    uint64_t* cpu_kpc_buf[2];
    uint64_t* cpu_kpc_shadow;
    uint64_t* cpu_kpc_reload;
    struct mt_cpu cpu_monotonic;
    cpu_stat_t cpu_stat;
    struct pmap_cpu_data cpu_pmap_cpu_data;
    dbgwrap_thread_state_t halt_state;
    uint64_t wfe_count;
    uint64_t wfe_deadline_checks;
    uint64_t wfe_terminations;
    kcov_cpu_data_t cpu_kcov_data;
    uint64_t ipi_pc;
    uint64_t ipi_lr;
    uint64_t ipi_fp;
    uint64_t cpu_tpidr_el0;
};
typedef enum  {
    IOT_PORT_SET = 0,
    IOT_PORT = 1,
    IOT_SERVICE_PORT = 2,
    IOT_WEAK_SERVICE_PORT = 3,
    IOT_CONNECTION_PORT = 4,
    IOT_CONNECTION_PORT_WITH_PORT_ARRAY = 5,
    IOT_EXCEPTION_PORT = 6,
    IOT_TIMER_PORT = 7,
    IOT_REPLY_PORT = 8,
    IOT_SPECIAL_REPLY_PORT = 9,
    IOT_PROVISIONAL_REPLY_PORT = 10,
    __IKOT_FIRST = 11,
    IKOT_THREAD_CONTROL = 11,
    IKOT_THREAD_READ = 12,
    IKOT_THREAD_INSPECT = 13,
    IKOT_TASK_CONTROL = 14,
    IKOT_TASK_READ = 15,
    IKOT_TASK_INSPECT = 16,
    IKOT_TASK_NAME = 17,
    IKOT_TASK_RESUME = 18,
    IKOT_TASK_ID_TOKEN = 19,
    IKOT_TASK_FATAL = 20,
    IKOT_HOST = 21,
    IKOT_HOST_PRIV = 22,
    IKOT_CLOCK = 23,
    IKOT_PROCESSOR = 24,
    IKOT_PROCESSOR_SET = 25,
    IKOT_PROCESSOR_SET_NAME = 26,
    IKOT_EVENTLINK = 27,
    IKOT_FILEPORT = 28,
    IKOT_SEMAPHORE = 29,
    IKOT_VOUCHER = 30,
    IKOT_WORK_INTERVAL = 31,
    IKOT_MEMORY_OBJECT = 32,
    IKOT_NAMED_ENTRY = 33,
    IKOT_MAIN_DEVICE = 34,
    IKOT_IOKIT_IDENT = 35,
    IKOT_IOKIT_CONNECT = 36,
    IKOT_IOKIT_OBJECT = 37,
    IKOT_UEXT_OBJECT = 38,
    IKOT_EXCLAVES_RESOURCE = 39,
    IKOT_ARCADE_REG = 40,
    IKOT_AU_SESSIONPORT = 41,
    IKOT_HYPERVISOR = 42,
    IKOT_KCDATA = 43,
    IKOT_UND_REPLY = 44,
    IKOT_UX_HANDLER = 45,
    IOT_UNKNOWN = 46,
    IOT_ANY = 255,
} ipc_object_type_t;

typedef enum  {
    IO_STATE_INACTIVE = 0,
    IO_STATE_IN_SPACE = 1,
    IO_STATE_IN_SPACE_IMMOVABLE = 2,
    IO_STATE_IN_LIMBO = 3,
    IO_STATE_IN_LIMBO_PD = 4,
    IO_STATE_IN_TRANSIT = 5,
    IO_STATE_IN_TRANSIT_PD = 6,
} ipc_object_state_t;

typedef natural_t ipc_object_bits_t;

typedef enum  {
    WQT_INVALID = 0,
    WQT_QUEUE = 1,
    WQT_TURNSTILE = 2,
    WQT_PORT = 3,
    WQT_SELECT = 4,
    WQT_PORT_SET = 5,
    WQT_SELECT_SET = 6,
} waitq_type_t;

typedef uint32_t waitq_flags_t;

typedef unsigned long ipc_port_timestamp_t;

typedef struct ipc_importance_task* ipc_importance_task_t;

typedef struct  {
    uint8_t zt0[64];
    uint8_t __z_p_za[0];
} arm_sme_context_t;

struct arm_sme_saved_state {
    arm_state_hdr_t hdr;
    uint64_t svcr;
    uint16_t svl_b;
    arm_sme_context_t context;
};
typedef struct arm_sme_saved_state arm_sme_saved_state_t;

struct arm_amx_saved_state_v1 {
    uint8_t x[8];
    uint8_t y[8];
    uint8_t z[64];
    uint64_t amx_state_t_el1;
};
struct arm_amx_saved_state {
    arm_state_hdr_t ash;
    union  {
        struct arm_amx_saved_state_v1 as_v1;
    } uas;
};
typedef struct arm_amx_saved_state arm_amx_saved_state_t;

struct ksancov_counters {
    ksancov_header_t kc_hdr;
    uint32_t kc_nedges;
    uint8_t kc_hits[0];
};
typedef struct ksancov_counters ksancov_counters_t;

struct thread_call_thread_state {
};
typedef int exception_type_t;

typedef int64_t mach_exception_data_type_t;

typedef mach_exception_data_type_t mach_exception_code_t;

typedef mach_exception_data_type_t mach_exception_subcode_t;

typedef uint8_t TCQueryType_t;

typedef struct _TXMCodeRegion TXMCodeRegion_t;

typedef struct cpu_data cpu_data_t;

typedef struct  {
    _Atomic(hv_vcpu_t*) vcpu;
    _Atomic(cpu_data_t*) pcpu;
    _Atomic(_Bool) notified;
    _Atomic(int) wfk_state;
} _hv_vcpu_notify_t;

struct hv_vm_percpu_t {
    uint64_t last_vcpu_gen;
    bitmap_t stale_vmid_bitmap[2];
};
typedef struct hv_vm_percpu_t hv_vm_percpu_t;

typedef struct  {
    uint64_t fixed;
    uint64_t variable;
    uint64_t overridable;
} hv_caps_t;

struct vm_caps {
    hv_caps_t hcr;
    hv_caps_t hacr;
    hv_caps_t mdcr;
    hv_caps_t ich_hcr;
    hv_caps_t actlr_el1_guest;
    hv_caps_t actlr_el1_vmm;
    uint64_t restricted_state_mask;
};
typedef uint32_t hv_vm_isa_t;

struct hv_mem_notify_t {
    vm_map_t map;
    uint64_t context;
    uint64_t base_ipa;
    uint64_t end_ipa;
    mach_port_t port;
    struct  {
        struct hv_mem_notify_t* rbe_left;
        struct hv_mem_notify_t* rbe_right;
        struct hv_mem_notify_t* rbe_parent;
    } link;
};
struct hv_mem_notify_tree_s {
    struct hv_mem_notify_t* rbh_root;
};
typedef struct hv_mem_notify_tree_s hv_mem_notify_tree_t;

struct hv_vm_t {
    _hv_vcpu_notify_t vcpu_byid[64];
    hv_vm_percpu_t* percpu;
    lck_mtx_t* mtx;
    bitmap_t vcpu_online_mask[1];
    struct vm_caps caps;
    vm_map_t user_map;
    vm_map_t default_space;
    os_refcnt_t refcnt;
    hv_vm_isa_t isa;
    uint64_t oem_hc;
    hv_mem_notify_tree_t mem_notify_tree;
    uint8_t mem_notify_count;
};
typedef struct  {
    uint64_t mdscr_el1;
    uint64_t tpidr_el1;
    uint64_t tpidr_el0;
    uint64_t tpidrro_el0;
    uint64_t sp_el0;
    uint64_t sp_el1;
    uint64_t par_el1;
    uint64_t csselr_el1;
    uint64_t apstate;
    uint64_t afpcr_el0;
    uint64_t scxtnum_el0;
    uint64_t tpidr2_el0;
    uint64_t smpri_el1;
} arm_guest_shared_sysregs_t;

typedef struct  {
    uint64_t ttbr0_el1;
    uint64_t ttbr1_el1;
    uint64_t tcr_el1;
    uint64_t elr_el1;
    uint64_t far_el1;
    uint64_t esr_el1;
    uint64_t mair_el1;
    uint64_t amair_el1;
    uint64_t vbar_el1;
    uint64_t cntv_cval_el0;
    uint64_t cntp_cval_el0;
    uint64_t actlr_el1;
    uint64_t sctlr_el1;
    uint64_t cpacr_el1;
    uint64_t spsr_el1;
    uint64_t afsr0_el1;
    uint64_t afsr1_el1;
    uint64_t contextidr_el1;
    uint64_t cntv_ctl_el0;
    uint64_t cntp_ctl_el0;
    uint64_t cntkctl_el1;
    uint64_t ich_vmcr_el2;
    uint64_t scxtnum_el1;
    uint64_t smcr_el1;
} arm_guest_banked_sysregs_t;

typedef struct  {
    struct  {
        uint64_t bvr;
        uint64_t bcr;
    } bp[16];
    struct  {
        uint64_t wvr;
        uint64_t wcr;
    } wp[16];
    uint64_t mdccint_el1;
    uint64_t osdtrrx_el1;
    uint64_t osdtrtx_el1;
    uint8_t dbgclaim_el1;
} arm_guest_dbgregs_t;

typedef struct  {
    uint64_t ich_ap0r0_el2;
    uint64_t ich_ap1r0_el2;
} arm_vgic_sysregs_t;

typedef struct  {
    uint64_t hcr_el2;
    uint64_t hacr_el2;
    uint64_t cptr_el2;
    uint64_t mdcr_el2;
    uint64_t vmpidr_el2;
    uint64_t vpidr_el2;
    uint64_t virtual_timer_offset;
    uint64_t hfgrtr_el2;
    uint64_t hfgwtr_el2;
    uint64_t hfgitr_el2;
    uint64_t hdfgrtr_el2;
    uint64_t hdfgwtr_el2;
    uint64_t cnthctl_el2;
    uint64_t timer;
    uint64_t vmkeyhi_el2;
    uint64_t vmkeylo_el2;
    uint64_t apsts_el1;
    uint64_t ich_hcr_el2;
    uint64_t ich_lr_el2[8];
    uint64_t hcrx_el2;
} arm_guest_controls_t;

typedef struct  {
    uint64_t actlr_el1;
} arm_guest_frozen_t;

typedef struct  {
    uint64_t amx_state_t_el1;
    uint64_t amx_config_el1;
    uint64_t aspsr_el1;
    uint64_t ctrr_ctl_el1;
    uint64_t ctrr_lock_el1;
    uint64_t ctrr_a_lwr_el1;
    uint64_t ctrr_a_upr_el1;
    uint64_t ctrr_b_lwr_el1;
    uint64_t ctrr_b_upr_el1;
    uint64_t ctrr_c_lwr_el1;
    uint64_t ctrr_c_upr_el1;
    uint64_t ctrr_c_ctl_el1;
    uint64_t ctrr_d_lwr_el1;
    uint64_t ctrr_d_upr_el1;
    uint64_t ctrr_d_ctl_el1;
    uint64_t ctxr_a_lwr_el1;
    uint64_t ctxr_a_upr_el1;
    uint64_t ctxr_a_ctl_el1;
    uint64_t ctxr_b_lwr_el1;
    uint64_t ctxr_b_upr_el1;
    uint64_t ctxr_b_ctl_el1;
    uint64_t ctxr_c_lwr_el1;
    uint64_t ctxr_c_upr_el1;
    uint64_t ctxr_c_ctl_el1;
    uint64_t ctxr_d_lwr_el1;
    uint64_t ctxr_d_upr_el1;
    uint64_t ctxr_d_ctl_el1;
    uint64_t vmsa_lock_el1;
    uint64_t pmcr1_el1;
    uint64_t apctl_el1;
    uint64_t apgakeyhi_el1;
    uint64_t apgakeylo_el1;
    uint64_t apiakeyhi_el1;
    uint64_t apiakeylo_el1;
    uint64_t apibkeyhi_el1;
    uint64_t apibkeylo_el1;
    uint64_t apdakeyhi_el1;
    uint64_t apdakeylo_el1;
    uint64_t apdbkeyhi_el1;
    uint64_t apdbkeylo_el1;
    uint64_t kernkeyhi_el1;
    uint64_t kernkeylo_el1;
    uint64_t gxf_config_el1;
    uint64_t gxf_entry_el1;
    uint64_t gxf_pabentry_el1;
    uint64_t sp_gl1;
    uint64_t tpidr_gl1;
    uint64_t aspsr_gl1;
    uint64_t vbar_gl1;
    uint64_t far_gl1;
    uint64_t esr_gl1;
    uint64_t elr_gl1;
    uint64_t spsr_gl1;
    uint64_t pmcr1_gl1;
    uint64_t afsr1_gl1;
    uint64_t sprr_config_el1;
    uint64_t sprr_amrange_el1;
    uint64_t sprr_pperm_el1;
    uint64_t sprr_uperm_el0;
    uint64_t sprr_pmprr_el1;
    uint64_t sprr_umprr_el1;
    uint64_t sprr_pperm_sh1_el1;
    uint64_t sprr_pperm_sh2_el1;
    uint64_t sprr_pperm_sh3_el1;
    uint64_t sprr_pperm_sh4_el1;
    uint64_t sprr_pperm_sh5_el1;
    uint64_t sprr_pperm_sh6_el1;
    uint64_t sprr_pperm_sh7_el1;
    uint64_t sprr_uperm_sh1_el1;
    uint64_t sprr_uperm_sh2_el1;
    uint64_t sprr_uperm_sh3_el1;
    uint64_t sprr_uperm_sh4_el1;
    uint64_t sprr_uperm_sh5_el1;
    uint64_t sprr_uperm_sh6_el1;
    uint64_t sprr_uperm_sh7_el1;
    uint64_t acfg_el1;
    uint64_t jrange_el1;
    uint64_t jctl_el1;
    uint64_t japiakeyhi_el1;
    uint64_t japiakeylo_el1;
    uint64_t japibkeyhi_el1;
    uint64_t japibkeylo_el1;
    uint64_t agtcntrdir_el1;
} arm_guest_extregs_t;

typedef struct  {
    uint8_t __res_00_20[32];
    uint64_t vttbr_el2;
    uint64_t __res_28;
    uint64_t vsttbr_el2;
    uint64_t __res_38;
    uint64_t vtcr_el2;
    uint64_t vstcr_el2;
    uint64_t vmpidr_el2;
    uint64_t __res_58;
    uint64_t cntvoff_el2;
    uint8_t __res_68_78[16];
    uint64_t hcr_el2;
    uint64_t hstr_el2;
    uint64_t vpidr_el2;
    uint64_t tpidr_el2;
    uint8_t __res_98_b0[24];
    uint64_t vncr_el2;
    uint8_t __res_b8_100[72];
    uint64_t cpacr_el1;
    uint64_t contextidr_el1;
    uint64_t sctlr_el1;
    uint64_t actlr_el1;
    uint64_t tcr_el1;
    uint64_t afsr0_el1;
    uint64_t afsr1_el1;
    uint64_t esr_el1;
    uint64_t mair_el1;
    uint64_t amair_el1;
    uint8_t __res_158_150[8];
    uint64_t mdscr_el1;
    uint64_t spsr_el1;
    uint64_t cntv_cval_el0;
    uint64_t cntv_ctl_el0;
    uint64_t cntp_cval_el0;
    uint64_t cntp_ctl_el0;
    uint64_t scxtnum_el1;
    uint64_t tfsr_el1;
    uint8_t __res_198_1a8[16];
    uint64_t cntpoff_el2;
    uint8_t __res_1b0_1b8[8];
    uint64_t hfgrtr_el2;
    uint64_t hfgwtr_el2;
    uint64_t hfgitr_el2;
    uint64_t hdfgrtr_el2;
    uint64_t hdfgwtr_el2;
    uint64_t zcr_el1;
    uint8_t __res_1e8_1f0[8];
    uint64_t smcr_el1;
    uint64_t smprimap_el2;
    uint64_t ttbr0_el1;
    uint8_t __res_208_210[8];
    uint64_t ttbr1_el1;
    uint8_t __res_218_220[8];
    uint64_t far_el1;
    uint8_t __res_228_230[8];
    uint64_t elr_el1;
    uint8_t __res_238_240[8];
    uint64_t sp_el1;
    uint8_t __res_248_250[8];
    uint64_t vbar_el1;
    uint8_t __res_400_258[424];
    uint64_t ich_lr_el2[16];
    uint64_t ich_ap0r_el2[4];
    uint64_t ich_ap1r_el2[4];
    uint64_t ich_hcr_el2;
    uint64_t ich_vmcr_el2;
    uint8_t __res_4d0_500[48];
    uint64_t vdisr_el2;
    uint64_t vsesr_el2;
    uint8_t __res_510_800[752];
    uint64_t pmblimitr_el1;
    uint8_t __res_808_810[8];
    uint64_t pmbptr_el1;
    uint8_t __res_818_820[8];
    uint64_t pmbsr_el1;
    uint64_t pmscr_el1;
    uint64_t pmsevfr_el1;
    uint64_t pmsicr_el1;
    uint64_t pmsirr_el1;
    uint64_t pmslatfr_el1;
    uint8_t __res_850_880[48];
    uint64_t trfcr_el1;
    uint8_t __res_888_1000[1912];
} arm_vncr_context_t;

typedef struct  {
    uint8_t __res_000_008[8];
    uint64_t avncr_el2;
    uint64_t aspsr_el1;
    uint8_t __res_018_100[232];
    uint64_t apctl_el1;
    uint64_t apsts_el1;
    uint64_t vmkey_lo_el2;
    uint64_t vmkey_hi_el2;
    uint64_t apgakeylo_el1;
    uint64_t apgakeyhi_el1;
    uint64_t apiakeylo_el1;
    uint64_t apiakeyhi_el1;
    uint64_t apibkeylo_el1;
    uint64_t apibkeyhi_el1;
    uint64_t apdakeylo_el1;
    uint64_t apdakeyhi_el1;
    uint64_t apdbkeylo_el1;
    uint64_t apdbkeyhi_el1;
    uint64_t kernkeylo_el1;
    uint64_t kernkeyhi_el1;
    uint8_t __res_180_2d0[336];
    uint64_t jctl_el1;
    uint64_t jrange_el1;
    uint64_t japiakeylo_el1;
    uint64_t japiakeyhi_el1;
    uint64_t japibkeylo_el1;
    uint64_t japibkeyhi_el1;
    uint64_t amx_config_el1;
    uint8_t __res_308_360[88];
    uint64_t vmsa_lock_el1;
    uint8_t __res_368_3c0[88];
    uint64_t pmcr1_el1;
    uint8_t __res_3c8_400[56];
    uint64_t apl_lrtmr_el2;
    uint64_t apl_intenable_el2;
    uint8_t __res_410_1000[3056];
} apple_vncr_context_t;

typedef union  {
    struct  {
        union  {
            arm_context_t guest_context;
            struct  {
                uint64_t res1[1];
                struct  {
                    uint64_t x[29];
                    uint64_t fp;
                    uint64_t lr;
                    uint64_t sp;
                    uint64_t pc;
                    uint32_t cpsr;
                    uint32_t pad;
                } regs;
                uint64_t res2[4];
                struct  {
                    __uint128_t q[32];
                    uint32_t fpsr;
                    uint32_t fpcr;
                } neon;
            };
        };
        arm_guest_shared_sysregs_t shared_sysregs;
        arm_guest_banked_sysregs_t banked_sysregs;
        arm_guest_dbgregs_t dbgregs;
        arm_vgic_sysregs_t vgic_sysregs;
        volatile arm_guest_controls_t controls;
        volatile arm_guest_frozen_t frozen;
        volatile uint64_t state_dirty;
        uint64_t guest_tick_count;
        arm_guest_extregs_t extregs;
        arm_vncr_context_t vncr;
        apple_vncr_context_t avncr;
    };
    uint8_t page[16384];
} arm_guest_rw_context_t;

typedef struct  {
    uint32_t vmexit_reason;
    uint32_t vmexit_esr;
    uint32_t vmexit_instr;
    uint64_t vmexit_far;
    uint64_t vmexit_hpfar;
} arm_guest_vmexit_t;

typedef struct  {
    uint8_t zt0[64];
    uint8_t __z_p_za[0];
} arm_guest_sme_context_t;

struct arm_guest_amx_context {
    uint8_t x[8];
    uint8_t y[8];
    uint8_t z[64];
    uint64_t amx_state_t_el1;
};
typedef struct arm_guest_amx_context arm_guest_amx_context_t;

typedef union  {
    struct  {
        uint64_t ver;
        arm_guest_vmexit_t exit;
        arm_guest_controls_t controls;
        uint64_t state_valid;
        uint64_t state_dirty;
        uint64_t state_used;
        uint32_t ich_vtr_el2;
        uint32_t ich_misr_el2;
        uint32_t ich_elrsr_el2;
        uint64_t svcr;
        uint16_t svl_b;
        uint16_t padding[3];
        arm_guest_sme_context_t* sme;
        arm_guest_amx_context_t* amx;
    };
    uint8_t page[16384];
} arm_guest_ro_context_t;

typedef struct  {
    arm_guest_rw_context_t rw;
    arm_guest_ro_context_t ro;
} arm_guest_context_t;

typedef struct  {
    uint64_t cptr_el2;
    uint64_t mdscr_el1;
    uint64_t tpidr_el1;
    uint64_t tpidr_el0;
    uint64_t tpidrro_el0;
    uint64_t sp_el0;
    uint64_t jop_hash;
    uint64_t vmenter_ticks;
    uint64_t vmexit_ticks;
    uint64_t vncr_el2;
    uint64_t avncr_el2;
    vm_map_t guest_map;
    _Bool flush_local_tlb;
    uint64_t acfg_el1;
    void* guest_context;
    _Bool amx_config_el2_eng;
    arm_guest_amx_context_t* amx_ss;
    _Bool amx_state_t_dirty;
    arm_guest_sme_context_t* sme_ss;
} arm_host_context_t;

typedef struct  {
    struct hv_vm_t* vm;
    arm_guest_context_t* kif;
    arm_guest_context_t* uif;
    arm_host_context_t host_context;
    uint64_t generation;
    ipc_port_t active_space;
    uint8_t id;
} hv_vcpu_t;

typedef struct hv_vm_t hv_vm_t;

typedef struct  {
    uint32_t arm_rev: 4;
    uint32_t arm_part: 12;
    uint32_t arm_arch: 4;
    uint32_t arm_variant: 4;
    uint32_t arm_implementor: 8;
} arm_cpuid_bits_t;

typedef union  {
    arm_cpuid_bits_t arm_info;
    uint32_t value;
} arm_cpu_info_t;

struct OpaqueDTEntry {
    uint32_t nProperties;
    uint32_t nChildren;
};
typedef const struct OpaqueDTEntry* DTEntry;

typedef struct arm_saved_state64 arm_saved_state64_t;

typedef struct __attribute__((packed))  {
    uint64_t control_hcr;
    uint64_t control_hacr;
    uint64_t control_cptr;
    uint64_t control_mdcr;
    uint64_t control_ich_hcr;
    uint64_t control_timer;
    uint64_t control_apsts;
    uint64_t control_hfgrtr;
    uint64_t control_hfgwtr;
    uint64_t control_hfgitr;
    uint64_t control_hdfgrtr;
    uint64_t control_hdfgwtr;
    uint64_t control_cnthctl;
    uint64_t actlr_el1;
    uint64_t ctr_el0;
    uint64_t dczid_el0;
    uint64_t clidr_el1;
    uint64_t ccsidr_el1_inst[8];
    uint64_t ccsidr_el1_data_or_unified[8];
    uint64_t id_aa64dfr0_el1;
    uint64_t id_aa64dfr1_el1;
    uint64_t id_aa64isar0_el1;
    uint64_t id_aa64isar1_el1;
    uint64_t id_aa64mmfr0_el1;
    uint64_t id_aa64mmfr1_el1;
    uint64_t id_aa64mmfr2_el1;
    uint64_t id_aa64pfr0_el1;
    uint64_t id_aa64pfr1_el1;
    uint64_t id_aa64smfr0_el1;
    uint64_t id_aa64zfr0_el1;
    uint8_t gic_npie_active_pending_bug;
    uint64_t ipa_bits_4k;
    uint64_t ipa_bits_16k;
    uint16_t svl_b_max;
} hv_capabilities_t;
