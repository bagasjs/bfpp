#ifndef BFPP_H_
#define BFPP_H_

#include <stddef.h>

typedef char  Byte;
typedef short Word;

typedef struct State State;
typedef Byte (*NativeFunc)(State *, Byte[8]);
typedef struct State {
    NativeFunc natives[256];
    char data[30000];
    size_t dp;
    size_t ip;
} State;

void platform_logger_write_text(const char *text);
void platform_logger_write_char(char ch);
void platform_logger_write_int(int value);
void platform_logger_flush(void);

int eval_program(State *state, const char *program, size_t programsz);

#endif // BFPP_H_
