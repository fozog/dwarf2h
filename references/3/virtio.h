typedef volatile struct virtq_desc {
    char flags;
    unsigned long long addr;
} __attribute__((packed)) virtq_desc_t;

typedef volatile struct unpacked_virtq_desc {
    char flags;
    unsigned long long addr;
} unpacked_virtq_desc_t;
