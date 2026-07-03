main:	*.c *.h
	gcc -arch arm64e -gsplit-dwarf -g3 -O0 main.c -o main
	dwarfdump main.dSYM > main.dwf

clean:
	rm main main.dwf
