#include <stddef.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include "bfpp.h"

char *load_file_content(const char *filepath)
{
    FILE *file = fopen(filepath, "rb"); // Open file in binary mode
    if (!file) {
        perror("Failed to open file");
        return NULL;
    }

    fseek(file, 0, SEEK_END); // Move to the end of the file
    long filesize = ftell(file); // Get the file size
    fseek(file, 0, SEEK_SET); // Reset the file pointer to the beginning

    if (filesize < 0) {
        fclose(file);
        return NULL;
    }

    char *buffer = malloc(filesize + 1); // Allocate memory (+1 for null terminator)
    if (!buffer) {
        fclose(file);
        return NULL;
    }

    fread(buffer, 1, filesize, file); // Read file into buffer
    buffer[filesize] = '\0'; // Null-terminate the string

    fclose(file);
    return buffer;
}

Byte raylib_init_window(State *state, Byte args[8])
{
    Word width  = ((Word)args[0] << 8) | (Word)args[1];
    Word height = ((Word)args[2] << 8) | (Word)args[3];
    const char *title  = &state->data[args[4]];
    printf("Creating window(%s, %d, %d)", title, width, height);
    return 0;
}

Byte raylib_close_window(State *state, Byte args[8])
{
    return 0;
}

Byte raylib_window_should_close(State *state, Byte args[8])
{
    return 0;
}

Byte raylib_begin_drawing(State *stae, Byte args[8])
{
    return 0;
}

Byte raylib_end_drawing(State *stae, Byte args[8])
{
    return 0;
}

int main(int argc, const char **argv)
{
    if(argc < 2) {
        fprintf(stderr, "Error: Provide a valid input filepath\n");
        fprintf(stderr, "Usage: bfpp <input.bf>\n");
        return -2;
    }

    State state = {0};
    memset(state.natives, 0, sizeof(state.natives));
    state.natives[0] = raylib_init_window;
    state.natives[1] = raylib_close_window;
    state.natives[2] = raylib_window_should_close;
    state.natives[3] = raylib_begin_drawing;
    state.natives[4] = raylib_end_drawing;
    const char *program = load_file_content(argv[1]);
    return eval_program(&state, program, strlen(program));
}
