#include "bfpp.h"

void reset_state(State *state)
{
    state->dp = 0;
    internal_memset(state->data, 0, sizeof(state->data));
}

int eval_program(State *state, const char *program, size_t programsz)
{
    state->dp = 0;
    state->ip = 0;
    while(state->ip < programsz) {
        char inst = program[state->ip];

        switch(inst) {
            case '+':
                state->data[state->dp] += 1;
                break;
            case '-':
                state->data[state->dp] -= 1;
                break;
            case '.':
                platform_logger_write_char(state->data[state->dp]);
                platform_logger_flush();
                break;
            case '>':
                state->dp += 1;
                break;
            case '<':
                state->dp -= 1;
                break;
            case '[':
                {
                    if(state->data[state->dp] == 0) {
                        size_t i = state->ip;
                        size_t stack = 0;
                        for(; i < programsz; ++i) {
                            if(program[i] == '[') stack += 1;
                            if(program[i] == ']') {
                                stack -= 1;
                                if(stack == 0) break;
                            }
                        }
                        if(program[i] != ']') {
                            platform_logger_write_text("ERROR: could not find matching  ']' for '[' at ");
                            platform_logger_write_int(i);
                            platform_logger_flush();
                            return -2;
                        }
                        state->ip = i;
                    }
                } break;
            case ']':
                {
                    if(state->data[state->dp] != 0) {
                        // Evaluation dp
                        int i = (int)state->ip;
                        size_t stack = 0;
                        for(; i >= 0; i--) {
                            if(program[i] == ']') stack += 1;
                            if(program[i] == '[') {
                                stack -= 1;
                                if(stack == 0) break;
                            }
                        }
                        if(program[i] != '[') {
                            platform_logger_write_text("ERROR: could not find matching  '[' for ']' at ");
                            platform_logger_write_int(i);
                            platform_logger_flush();
                            return -3;
                        }
                        size_t jmp = (size_t)i;
                        state->ip = jmp - 1;
                    }
                } break;
            
            // Extended instructions
            case '$':
                {
                    reset_state(state);
                } break;
            case '?':
                {
                    platform_logger_write_text("[dp=");
                    platform_logger_write_int(state->dp);
                    platform_logger_write_text("] ");
                    platform_logger_write_int(state->data[state->dp]);
                    platform_logger_flush();
                } break;
            case '!':
                {
                    size_t edp = state->dp;
                    Byte pfn  = state->data[edp];
                    if(state->natives[(size_t)pfn] == NULL) {
                        platform_logger_write_text("ERROR: invalid native function with index ");
                        platform_logger_write_int(pfn);
                        platform_logger_flush();
                        return -4;
                    }
                    edp -= 1;
                    Byte a[8] = {0};
                    for(int i = 7; i >= 0; i--, edp--) {
                        a[8 - i - 1] = state->data[edp];
                    }
                    state->data[state->dp] = state->natives[(int)pfn](state, a);
                    // Calling native function
                } break;

            // Comments
            case ';':
                while(program[state->ip] != '\n') {
                    state->ip += 1;
                }
                break;

            // Skipping whitespace
            case ' ':
                break;
            case '\t':
                break;
            case '\r':
                break;
            case '\n':
                break;
            default:
                {
                    platform_logger_write_text("ERROR: unknown instruction '");
                    platform_logger_write_char(inst);
                    platform_logger_write_char('\'');
                    platform_logger_flush();
                }
                return -1;
        }
        state->ip += 1;
    }

    return 0;
}

size_t internal_strlen(const char *cstr)
{
    size_t size;
    for(size = 0; cstr[size]; ++size);
    return size;
}

void *internal_memset(void *dst, const int value, size_t size)
{
    for(size_t i = 0; i < size; ++i)
        ((char*)dst)[i] = ((const char)value);
    return dst;
}

void *internal_memcpy(void *dst, const void *src, size_t size)
{
    for(size_t i = 0; i < size; ++i)
        ((char*)dst)[i] = ((const char *)src)[i];
    return dst;
}

#ifndef BFPP_WASM
#include <stdio.h>
void platform_logger_write_text(const char *text)
{
    printf("%s", text);
}

void platform_logger_write_char(Byte ch)
{
    printf("%c", ch);
}

void platform_logger_write_int(int value)
{
    printf("%d", value);
}

void platform_logger_flush(void)
{
    putchar('\n');
}
#endif

