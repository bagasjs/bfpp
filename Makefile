CC := clang
CFLAGS := -Wall -Wextra -pedantic -D_CRT_SECURE_NO_WARNINGS
# LFLAGS := -L lib -lraylibdll
WASM_CFLAGS := --target=wasm32 --no-standard-libraries
WASM_LFLAGS := -Wl,--allow-undefined -Wl,--export-all -Wl,--no-entry

# CFLAGS += -g -fsanitize=address

all: index.wasm build/bfpp.exe demos/game_of_life.bf

demos/game_of_life.bf: ./demos/game_of_life.bfc
	python ./bfcat2.py com ./demos/game_of_life.bfc demos/game_of_life.bf

index.wasm: src/bfpp.c src/index.c
	$(CC) $(CFLAGS) $(WASM_CFLAGS) -DBFPP_WASM -o $@ $^ $(WASM_LFLAGS)

build/bfpp.exe: src/bfpp.c ./src/main.c
	$(CC) $(CFLAGS) -o $@ $^ $(LFLAGS)
