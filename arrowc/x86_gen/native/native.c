// +build ignore

#include <stdio.h>

void print_int32(int x) {
    printf("%d\n", x);
}

void print_uint32(unsigned int x) {
    printf("%u\n", x);
}

void print_int8(signed char x) {
    printf("%hhd\n", x);
}

void print_uint8(unsigned char x) {
    printf("%hhu\n", x);
}

void print_float32(float f) {
    printf("%g\n", f);
}

void print(char* str) {
    printf("%s", str);
}