UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

# Default compiler and standard flags
CC = gcc
CFLAGS = -O2 -Wall

# 2. Apply OS-specific configuration
ifeq ($(UNAME_S), Darwin)
    # macOS Configuration
    # Note: Target must be arm64e for macOS native ptrauth
    CFLAGS += -arch arm64e
else ifeq ($(UNAME_S), Linux)
    # Linux Configuration
    # Ensure we are targeting an AArch64 (ARM64) system before applying the flag
    ifeq ($(UNAME_M), aarch64)
        CFLAGS += -mbranch-protection=standard
    endif
endif

CFLAGS += -g -g3 -O0 -Wno-unused-variable

all:	main-dbg main-split

main-dbg:	*.c *.h
	gcc $(CFLAGS)  main.c -o main-dbg

main-split:	*.c *.h
ifeq ($(UNAME_S), Linux)
	objcopy --only-keep-debug main-dbg main.dwarf
else
	gcc $(CFLAGS) -gsplit-dwarf main.c -o main-split
endif

clean:
	rm main-dbg main-split

.PHONY: all clean
