#ifndef BFPP_H_
#define BFPP_H_

#include <stddef.h>

#define TAPE_LENGTH 30000

typedef unsigned char  Byte;
typedef unsigned short Word;

typedef struct State State;
typedef Byte (*NativeFunc)(State *, Byte[8]);
typedef struct State {
    NativeFunc natives[256];
    Byte data[TAPE_LENGTH];
    size_t dp;
    size_t ip;
} State;


size_t internal_strlen(const char *cstr);
void *internal_memset(void *dst, const int value, size_t size);
void *internal_memcpy(void *dst, const void *src, size_t size);

void platform_logger_write_text(const char *text);
void platform_logger_write_char(Byte ch);
void platform_logger_write_int(int value);
void platform_logger_flush(void);

int eval_program(State *state, const char *program, size_t programsz);
void reset_state(State *state);

#endif // BFPP_H_
