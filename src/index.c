#include "bfpp.h"

// Here where the brainfuck source code will be placed
Byte TEMP_BUFFER[8 * 1024] = {0};
static State state = {0};

// Javascript API
void clear_background(void);
int get_cols(void);
int get_rows(void);
void draw_cell(int x, int y, unsigned char r, unsigned char g, unsigned char b);

// Brainfuck Native
Byte f_clear_background(State *s, Byte args[8]) {
    (void)s;
    (void)args;
    clear_background();
    return 0;
}

Byte f_draw_cell(State *s, Byte args[8]) {
    (void)s;
    draw_cell(args[0], args[1], args[2], args[3], args[4]);
    return 0;
}


void _frame(float timestamp)
{
    eval_program(&state, (char*)TEMP_BUFFER, internal_strlen((char*)TEMP_BUFFER));
}

void _start(void)
{
    reset_state(&state);
    state.natives[0] = f_clear_background;
    state.natives[1] = f_draw_cell;

    platform_logger_write_text("Start function called");
    platform_logger_flush();
}
