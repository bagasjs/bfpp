#include "bfpp.h"

Byte TEMP_BUFFER[8 * 1024] = {0};

size_t internal_strlen(const char *cstr)
{
    size_t size;
    for(size = 0; cstr[size]; ++size);
    return size;
}

void eval_brainfuck_program(const char *program)
{
    State state = {0};
    eval_program(&state, program, internal_strlen(program));
}
