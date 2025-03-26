/**
 * @param {ArrayBuffer} mem
 * @param {number} ptr
 * @return {number}
 */
function cstrlen(mem, ptr) {
    let len = 0;
    while (mem[ptr] != 0) {
        len++;
        ptr++;
    }
    return len;
}

/**
 * @param {ArrayBuffer} buf
 * @param {number} ptr
 * @return {string}
 */
function stringFromPtr(buf, ptr) {
    const mem = new Uint8Array(buf);
    const len = cstrlen(mem, ptr);
    const bytes = new Uint8Array(buf, ptr, len);
    return new TextDecoder().decode(bytes);
}

(async () => {
    /** @type {HTMLCanvasElement} */
    const canvas = document.getElementById("game");
    /** @type {CanvasRenderingContext2D} */
    const ctx = canvas.getContext("2d");

    const rows = 40;
    const cols = 40;
    const cellWidth = canvas.clientWidth / cols;
    const cellHeight = canvas.clientHeight / rows; 


    let loggingBuffer = "";
    const wasm = await WebAssembly.instantiateStreaming(fetch("index.wasm"), {
        "env": {
            platform_logger_write_text(pText) {
                const buffer = wasm.instance.exports.memory.buffer;
                loggingBuffer += stringFromPtr(buffer, pText);
            },
            platform_logger_write_int(value) {
                loggingBuffer += `${value}`
            },
            platform_logger_write_char(ch) {
                loggingBuffer += String.fromCharCode(ch)
            },
            platform_logger_flush() {
                console.log(loggingBuffer);
                loggingBuffer = "";
            },
            clear_background() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = "rgba(0, 0, 0, 1.0)"
                ctx.fillRect(0, 0, canvas.clientWidth, canvas.clientHeight);
            },
            get_rows() {
                return rows;
            },
            get_cols() {
                return cols;
            },
            draw_cell(x, y, r, g, b) {
                ctx.fillStyle = `rgb(${r}, ${g}, ${b})`
                ctx.fillRect(x * cellWidth, y * cellHeight, cellWidth, cellHeight);
            },
        }
    });

    const sourceFileUrl = "examples/game_of_life.bf";
    const sourceText = await (await fetch(sourceFileUrl)).text();
    const wasmMemory = new Uint8Array(wasm.instance.exports.memory.buffer);
    const encodedText = (new TextEncoder()).encode(sourceText + "\0")
    wasmMemory.set(encodedText, wasm.instance.exports.TEMP_BUFFER.value);
    wasm.instance.exports._start();
    // wasm.instance.exports.eval_brainfuck_program(wasm.instance.exports.TEMP_BUFFER.value);

    if(wasm.instance.exports._frame) {
        console.log("Per frame function is defined. Starting the frame mainloop");
        let prev = null;
        const webAnimationFrameLoop = timestamp => {
            if(prev) {
                wasm.instance.exports._frame(timestamp);
            }
            prev = timestamp;
            window.requestAnimationFrame(webAnimationFrameLoop)
        }
        window.requestAnimationFrame(webAnimationFrameLoop);
    }
})();
