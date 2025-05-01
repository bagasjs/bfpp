# BFPP (Brainf*ck++)
A modified and extended brainf*ck interpreter

## Language Design
Brainf\*ck is a simple programming language that consist of 8 instructions. BFPP add some 
more instructions to make the language a bit easier to use and can interact with external
environment easily. A brainf\*ck runtime usually consists of 
- Data/Tape: An array of bytes usually with length of 30000
- Data Pointer: A pointer that point into a byte in Data/Tape
You create a useful program by manipulating this Data/Tape via Data Pointer

Since working with the tape only is a bit limiting. BFPP has FFI or native functions. BFPP provide 256 slots 
for native functions that can be provided by external system. You can call each function by using "!" instruction. 
The instruction will evaluate the current byte pointed by the data pointer then it will call the native functions in that slot. 
You can provide up to 8 arguments to the native function by setting up the previous 8 tape slot. Here's a simple example
where we want to call a function with the following signature `void init_window(byte width, byte height)`
which's set to the native functions slot 5.
```bfpp
; set tape[0] as height with value of 200
>++++++++++[<++++++++++++++++++++>-]
; set tape[1] as width with value of 200
>
>++++++++++[<++++++++++++++++++++>-]
; set tape[2] as 5 which is the slot for native function init_window
>
+++++
; then call the function
!
```


## BFPP sets of Instruction

| Instruction    | Description                                       | 
|----------------|---------------------------------------------------|
| +              | Increment the byte at the data pointer by 1       |
| -              | Decrement the byte at the data pointer by 1       |
| >              | Increment the data pointer by 1                   |
| <              | Decrement the data pointer by 1                   |
| [              | If the data[dp] == 0 then jump into matching ]    |
| ]              | If the data[dp] != 0 then jump into matching [    |
| .              | Print the byte at data pointer as ASCII character |
| ,              | Not implemented (in bf it accepts an input)       |
| !              | Native function call based on provided call table |
| ?              | Dump the value of byte at data pointer (debugging)|
| $              | Reset data to zeros and dp to zero                |
