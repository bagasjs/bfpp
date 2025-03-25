# BFPP (Brainfuck++)
A modified and extended brainfuck interpreter

## Language Design
Brainfuck is a simple programming language that consist of 8 instructions. Brainfuck++ add
some more instructions to make the language a bit easier to use and can interact with external
environment easily. 
A brainfuck runtime usually consists of 
- Data/Tape: An array of bytes usually with length of 30000
- Data Pointer: A pointer that point into a byte in Data/Tape
You create a useful program by manipulating this Data/Tape via Data Pointer

## Brainfuck++ sets of Instruction
|----------------|---------------------------------------------------|
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
|----------------|---------------------------------------------------|

