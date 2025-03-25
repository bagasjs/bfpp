function cstrlen(mem, ptr) {
    let len = 0;
    while (mem[ptr] != 0) {
        len++;
        ptr++;
    }
    return len;
}

const stringFromPtr = (buf, ptr) => {
    const mem = new Uint8Array(buf);
    const len = cstrlen(mem, ptr);
    const bytes = new Uint8Array(buf, ptr, len);
    return new TextDecoder().decode(bytes);
}

(async () => {
    const canvas = document.getElementById("game")
    const sourceFileUrl = "examples/helloworld.bf";
    const sourceText = await (await fetch(sourceFileUrl)).text();

    let loggingBuffer = "";
    const wasm = await WebAssembly.instantiateStreaming(fetch("index.wasm"), {
        "env": {
            platform_logger_write_text: (pText) => {
                const buffer = wasm.instance.exports.memory.buffer;
                loggingBuffer += stringFromPtr(buffer, pText);
            },
            platform_logger_write_int: (value) => {
                loggingBuffer += `${value}`
            },
            platform_logger_write_char: (ch) => {
                loggingBuffer += String.fromCharCode(ch)
            },
            platform_logger_flush: () => {
                console.log(loggingBuffer);
                loggingBuffer = "";
            },
        }
    });

    const wasmMemory = new Uint8Array(wasm.instance.exports.memory.buffer);
    const encodedText = (new TextEncoder()).encode(sourceText + "\0")
    wasmMemory.set(encodedText, wasm.instance.exports.TEMP_BUFFER.value);
    wasm.instance.exports.eval_brainfuck_program(wasm.instance.exports.TEMP_BUFFER.value);
})();
