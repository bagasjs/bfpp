CC := clang
CFLAGS := -Wall -Wextra -pedantic -D_CRT_SECURE_NO_WARNINGS
# LFLAGS := -L lib -lraylibdll
WASM_CFLAGS := --target=wasm32 --no-standard-libraries
WASM_LFLAGS := -Wl,--allow-undefined -Wl,--export-all -Wl,--no-entry

# CFLAGS += -g -fsanitize=address

all: index.wasm bfpp.exe

test: bfpp.exe ./tests/test.bf
	bfpp.exe ./tests/loop.bf

./tests/test.bf: ./tests/loop.bfc
	python ./tools/bfcat.py $^ $@


index.wasm: src/bfpp.c src/index.c
	$(CC) $(CFLAGS) $(WASM_CFLAGS) -DBFPP_WASM -o $@ $^ $(WASM_LFLAGS)

bfpp.exe: src/bfpp.c ./src/main.c
	$(CC) $(CFLAGS) -o $@ $^ $(LFLAGS)
