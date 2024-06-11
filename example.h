#include <stdint.h>

#ifndef EXAMPLE_H_
#define EXAMPLE_H_

typedef struct {
    uint32_t foo;
    uint32_t noo;
    uint8_t baz;
} FooStruct;

typedef struct {
    float bar;
    uint8_t baz;
} BarStruct;


typedef struct {
    FooStruct foo;
    BarStruct bar;
    uint8_t baz;
} NestedStruct;

typedef struct {
    NestedStruct nested;
    FooStruct foo;
} DoubleNestedStruct;

#endif 
