all:	main check

main:	*.c
	gcc -gsplit-dwarf -g3 -O0 main.c -o main
	dwarfdump main.dSYM > main.dwf

check:	check.c generated.h
	gcc -gsplit-dwarf -g3 -O0 check.c -o check
	dwarfdump check.dSYM > check.dwf

clean:
	rm main main.dwf check
