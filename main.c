#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "generated_serde.h"

void print_hex(const char* label, const uint8_t* bytes, size_t size)
{
    printf("%s[%zu] = 0x", label, size);
    for (int i=0; i<size; i++) {
        printf("%02X", bytes[i]);
    }
    printf("\n");
}

NestedStruct nest = {
    .foo = {
        .foo = 0xfeedbeef,
        .noo = 0xdeadc0de,
        .baz = 0x69,
    },
    .bar = {
        .bar = 3.1415,
        .baz = 0x69,
    },
    .baz = 0x69,
};

DoubleNestedStruct dns = {
    .nested = 
    {
        .foo = {
            .foo = 0xfeedbeef,
            .noo = 0xdeadc0de,
            .baz = 0x69,
        },
        .bar = {
            .bar = 3.1415,
            .baz = 0x69,
        },
        .baz = 0x69,
    },
        .foo = {
            .foo = 0xfeedbeef,
            .noo = 0xdeadc0de,
            .baz = 0x69,
        },
};


uint8_t buf[2048] = {0};

int main(void) 
{
    /* Serialize and deserialize foo */
    NestedStructSerialize(&nest, (uint8_t*)&buf, sizeof(buf));

    NestedStruct nestOut = {0};
    NestedStructDeserialize((uint8_t*)&buf, sizeof(buf), &nestOut);
    if (0 != memcmp(&nestOut, &nest, sizeof(nest))) {
        printf("ERROR, STRUCTS DONT MATCH\n");
    }
    else {
        printf("SUCCESS\n");
    }

    memset(buf, 0, sizeof(buf));

    DoubleNestedStructSerialize(&dns, (uint8_t*)buf, sizeof(buf));
    DoubleNestedStruct dNestOut = {0};
    DoubleNestedStructDeserialize((uint8_t*)&buf, sizeof(buf), &dNestOut);
    if (0 != memcmp(&dNestOut, &dns, sizeof(dns))) {
        printf("ERROR, STRUCTS DONT MATCH\n");
    }
    else {
        printf("SUCCESS\n");
    }


    return 0;

}
