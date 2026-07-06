UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)

# Default compiler and standard flags
CC = gcc
CFLAGS = -O2 -Wall

# Apply OS-specific configuration
ifeq ($(UNAME_S), Darwin)
	# macOS Configuration
	# Note: Target must be arm64e for macOS native ptrauth
	CFLAGS += -arch arm64e
else ifeq ($(UNAME_S), Linux)
	# Linux Configuration
	# Ensure we are targeting an AArch64 (ARM64) system before applying the flag
	CC = clang
	ifeq ($(UNAME_M), aarch64)
		CFLAGS += -march=armv8.6-a -mbranch-protection=standard
	endif
endif

CFLAGS += -g -g3 -O0 -Wno-unused-variable

all:	main main.dwarf

main:	*.c *.h
	$(CC) $(CFLAGS) main.c -o main

main.dwarf:	*.c *.h
ifeq ($(UNAME_S), Linux)
	objcopy --only-keep-debug main main.dwarf
endif

clean:
	rm main main.dwarf
ifeq ($(UNAME_S), Darwin)
	rm -rf main.dSYM
endif

.PHONY: all clean
