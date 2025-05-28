#
# A full fledge compiler of bfcat.
# If you simply want to look at 
# how bfcat compile core operations
# like add, greater_than, less_than
# look at bfcat.py not bfcat2.py
#

from __future__ import annotations
import sys
from typing import List, Dict

iota_counter = 0
def iota(reset = False):
    global iota_counter
    if reset:
        iota_counter = 0
    index = iota_counter
    iota_counter += 1
    return index

def error(message: str):
    print(f"ERROR: {message}")
    exit(-1)

TOK_INVALID = iota(True)
TOK_SYMBOL = iota()
TOK_INT  = iota()
TOK_POP  = iota()
TOK_DUP  = iota()
TOP_OVER = iota()
TOK_SWAP = iota()
TOK_PRINT = iota()
TOK_ADD  = iota()
TOK_SUB  = iota()
TOK_EQ   = iota()
TOK_NEQ  = iota()
TOK_GT   = iota()
TOK_LT   = iota()
TOK_OR   = iota()
TOK_AND  = iota()
TOK_WHILE = iota()
TOK_IF    = iota()
TOK_ELSE  = iota()
TOK_DO    = iota()
TOK_END   = iota()
TOK_ARRAY_GET = iota()
TOK_ARRAY_SET = iota()
TOK_DEF   = iota()
TOK_ARRAY = iota()
TOK_LOAD = iota()

TOK_DBGPRINT = iota()

keyword_map = {
    "dup": TOK_DUP,
    "pop": TOK_POP,
    "over": TOP_OVER,
    "swap": TOK_SWAP,
    "add": TOK_ADD,
    "sub": TOK_SUB, 
    "eq": TOK_EQ,
    "neq": TOK_NEQ,
    "gt": TOK_GT,
    "lt": TOK_LT,
    "or": TOK_OR,
    "and": TOK_AND,
    "while": TOK_WHILE,
    "if": TOK_IF,
    "else": TOK_ELSE,
    "do": TOK_DO,
    "end": TOK_END,
    "print": TOK_PRINT,

    "def": TOK_DEF,
    "array": TOK_ARRAY,
    "array_get": TOK_ARRAY_GET,
    "array_set": TOK_ARRAY_SET,

    "dbgprint": TOK_DBGPRINT,

}

class Token(object):
    kind: int
    text: str
    line_number: int

    def __init__(self, kind: int, text: str, line_number: int):
        self.kind = kind
        self.text = text
        self.line_number = line_number

    def __repr__(self):
        return f"Token({self.text}, {self.line_number})"

def is_name(word: str):
    if not word[0].isalpha() or word[0] == "_":
        return False
    for ch in word[1:]:
        if not (ch.isalnum() or ch == "_"):
            return False
    return True


def parse_tokens(source: str) -> List[Token]:
    result = []
    for line_number, line in enumerate(source.splitlines()):
        if line.strip().startswith(";"):
            continue

        for word in line.split():
            if word in keyword_map:
                result.append(Token(kind=keyword_map[word], text=word, line_number=line_number + 1))
            elif is_name(word):
                result.append(Token(kind=TOK_SYMBOL, text=word, line_number=line_number + 1))
            elif word[0] == "?" and is_name(word[1:]):
                result.append(Token(kind=TOK_ARRAY_GET, text=word[1:], line_number=line_number + 1))
            elif word[0] == "!" and is_name(word[1:]):
                result.append(Token(kind=TOK_ARRAY_SET, text=word[1:], line_number=line_number + 1))
            elif word.isdigit():
                result.append(Token(kind=TOK_INT, text=word, line_number=line_number + 1))
            else:
                result.append(Token(kind=TOK_INVALID, text=word, line_number=line_number + 1))
    return result

class Inst(object):
    pass

class Integer(Inst):
    value: int
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return f"Integer({self.value})"

class Intrinsic(Inst):
    kind: str
    def __init__(self, kind: str):
        self.kind = kind

    def __repr__(self):
        return self.kind

class ArrayOp(Inst):
    def __init__(self, name: str, is_get: bool):
        self.name = name
        self.is_get = is_get

class While(Inst):
    cond: List[Inst]
    body: List[Inst]
    line_number: int

    def __init__(self, cond: List[Inst], body: List[Inst], line_number: int):
        self.cond = cond
        self.body = body
        self.line_number = line_number

    def __repr__(self):
        return f"While(cond={self.cond}, body={self.body})"

class Branch(Inst):
    cond: List[Inst]
    if_body: List[Inst]
    else_body: List[Inst]
    line_number: int
    
    def __init__(self, cond: List[Inst], if_body: List[Inst], else_body: List[Inst], line_number: int):
        self.cond = cond
        self.if_body = if_body
        self.else_body = else_body
        self.line_number = line_number

    def __repr__(self):
        return f"Branch(cond={self.cond}, if={self.if_body}, else={self.else_body})"

class ArraySpec(object):
    def __init__(self, size: int, offset: int):
        self.size = size
        self.offset = offset

    def __repr__(self):
        return f"ArraySpec(size={self.size}, offset={self.offset})"

class Program(object):
    def __init__(self, body: List[Inst], macros: Dict[str, List[Inst]], arrays: Dict[str, ArraySpec]):
        self.body   = body
        self.macros = macros
        self.arrays = arrays
        self.offset = 0

    def __repr__(self):
        return f"Program(body={self.body}, macros={self.macros}, offset={self.offset})"

class Parser(object):
    def __init__(self, tokens: List[Token]):
        self.program = Program([], {}, {})
        self.blocks = [self.program.body]
        self.tokens = tokens
        self.i = 0

    def parse_once(self):
        if self.tokens[self.i].kind == TOK_WHILE:
            self.parse_while()
        elif self.tokens[self.i].kind == TOK_DEF:
            self.parse_macro()
        elif self.tokens[self.i].kind == TOK_ARRAY:
            self.parse_array()
        elif self.tokens[self.i].kind == TOK_SYMBOL:
            name = self.tokens[self.i]
            if name.text not in self.program.macros:
                error(f"Unknown macro {name.text} to expand")
            self.blocks[-1].extend(self.program.macros[name.text])
        elif self.tokens[self.i].kind == TOK_IF:
            self.parse_if()
        elif self.tokens[self.i].kind in [ TOK_DO, TOK_END, TOK_ELSE ]:
            error(f"invalid token '{self.tokens[self.i].text}' at line {self.tokens[self.i].line_number}. It has no context")
        elif self.tokens[self.i].kind == TOK_INT:
            self.blocks[-1].append(Integer(int(self.tokens[self.i].text)))
            self.i += 1
        elif self.tokens[self.i].text in keyword_map:
            self.blocks[-1].append(Intrinsic(self.tokens[self.i].text))
            self.i += 1
        elif self.tokens[self.i].kind == TOK_ARRAY_GET:
            self.blocks[-1].append(ArrayOp(self.tokens[self.i].text, True))
            self.i += 1
        elif self.tokens[self.i].kind == TOK_ARRAY_SET:
            self.blocks[-1].append(ArrayOp(self.tokens[self.i].text, False))
            self.i += 1
        else:
            error(f"invalid token '{self.tokens[self.i].text}' at line {self.tokens[self.i].line_number}")

    def parse_array(self):
        array_tok = self.tokens[self.i]
        self.i += 1
        name = self.tokens[self.i]
        if name.kind != TOK_SYMBOL:
            error(f"To define an array it must have the following pattern \"array <array-name> <array-size> end\"\n" +
                  f"At line {array_tok.line_number} expecting <array-name> to be a symbol token but found {name.kind} {name.text}")
        self.i += 1
        size = self.tokens[self.i]
        if size.kind != TOK_INT:
            error(f"To define an array it must have the following pattern \"array <array-name> <array-size> end\"\n" +
                  f"At line {array_tok.line_number} expecting <array-size> to be an integer token but found {size.kind} {size.text}")
        self.i += 1
        if self.tokens[self.i].kind != TOK_END:
            error(f"To define an array it must have the following pattern \"array <array-name> <array-size> end\"\n" +
                  f"At line {array_tok.line_number} expecting token end but found {size.kind} {size.text}")
        array = ArraySpec(int(size.text), self.program.offset)
        self.program.offset += array.size
        self.program.arrays[name.text] = array
        self.i += 1

    def parse_macro(self):
        # TODO(bagasjs): Make sure we can't add a while or if else block in macro
        #                because it can be expanded into illegal instruction at 
        #                something like i.e. while A_MACRO do end
        #                if A_MACRO => def A_MACRO while 1 1 eq do end end
        #                this wil be expanded into while while 1 1 eq do end do end
        #                Which for now will be illegal until further research done 
        #                (Although I don't want to research about this)
        macro_tok = self.tokens[self.i]
        self.i += 1
        name = self.tokens[self.i]
        if name.kind != TOK_SYMBOL:
            error(f"Expecting a symbol/name after 'def' in {macro_tok.line_number} found {name.text} {name.kind}")
        self.i += 1
        self.blocks.append([])
        while self.tokens[self.i].kind != TOK_END:
            if self.i + 1 >= len(self.tokens) and self.tokens[self.i].kind != TOK_END:
                error(f"invalid eof expecting 'end' for 'macro' in line {macro_tok.line_number}")
            self.parse_once()

        body = self.blocks[-1]
        self.blocks.pop()
        self.program.macros[name.text] = body
        self.i += 1
        pass

    def parse_if(self):
        if_tok = self.tokens[self.i]
        condition = []
        self.i += 1
        while self.tokens[self.i].kind != TOK_DO:
            if self.i + 1 >= len(self.tokens) and self.tokens[self.i].kind != TOK_DO:
                error(f"invalid eof expecting 'do' for 'if' in line {if_tok.line_number}")
            if self.tokens[self.i].kind in [ TOK_WHILE, TOK_IF, TOK_END, TOK_ELSE, TOK_DO ]:
                error(f"invalid token '{self.tokens[self.i].text}' in an if condition at line {self.tokens[self.i].line_number}")
            elif self.tokens[self.i].kind == TOK_INT:
                condition.append(Integer(int(self.tokens[self.i].text)))
            elif self.tokens[self.i].text in keyword_map:
                condition.append(Intrinsic(self.tokens[self.i].text))
            self.i += 1

        self.i += 1
        self.blocks.append([])
        while not (self.tokens[self.i].kind == TOK_END or self.tokens[self.i].kind == TOK_ELSE):
            if self.i + 1 >= len(self.tokens) and self.tokens[self.i].kind != TOK_END:
                error(f"invalid eof expecting 'end' for 'if' in line {if_tok.line_number}")
            self.parse_once()
        if_body = self.blocks[-1]
        self.blocks.pop()

        else_body = []
        if self.tokens[self.i].kind == TOK_ELSE:
            self.blocks.append(else_body)
            else_tok = self.tokens[self.i]
            self.i += 1
            while self.tokens[self.i].kind != TOK_END:
                if self.i + 1 >= len(self.tokens) and self.tokens[self.i].kind != TOK_END:
                    error(f"invalid eof expecting 'end' for 'else' in line {else_tok.line_number}")
                self.parse_once()
            self.blocks.pop()
        self.blocks[-1].append(Branch(condition, if_body, else_body, if_tok.line_number))
        self.i += 1

    def parse_while(self):
        while_tok = self.tokens[self.i]
        condition = []
        self.i += 1
        while self.tokens[self.i].kind != TOK_DO:
            if self.i + 1 >= len(self.tokens) and self.tokens[self.i].kind != TOK_DO:
                error(f"invalid eof expecting 'do' for 'while' in line {while_tok.line_number}")
            if self.tokens[self.i].kind in [ TOK_WHILE, TOK_IF, TOK_END, TOK_ELSE, TOK_DO ]:
                error(f"invalid token '{self.tokens[self.i].text}' in a while condition at line {self.tokens[self.i].line_number}")
            elif self.tokens[self.i].kind == TOK_INT:
                condition.append(Integer(int(self.tokens[self.i].text)))
            elif self.tokens[self.i].text in keyword_map:
                condition.append(Intrinsic(self.tokens[self.i].text))
            self.i += 1
        self.i += 1
        self.blocks.append([])
        while self.tokens[self.i].kind != TOK_END:
            if self.i + 1 >= len(self.tokens) and self.tokens[self.i].kind != TOK_END:
                error(f"invalid eof expecting 'end' for 'while' in line {while_tok.line_number}")
            self.parse_once()
        body = self.blocks[-1]
        self.blocks.pop()
        self.blocks[-1].append(While(condition, body, while_tok.line_number))
        self.i += 1

    def parse(self):
        while self.i < len(self.tokens):
            self.parse_once()

class Codegen(object):
    def __init__(self, program: Program):
        self.program = program
        self.result = []
        self.dp = 0

    def emit_intrinsic(self, inst: Inst):
        assert isinstance(inst, Intrinsic)
        match inst.kind:
            case "pop":
                if self.dp < 1:
                    raise IndexError("Not enough elements for `pop`")
                self.result.append("[-]<")
                self.dp -= 1

            case "dup":
                if self.dp < 1:
                    raise IndexError("Not enough elements for `dup`")
                self.result.append(
                        "[-]<" # Set Y to 0 then move to X
                        "[->+>+<<]" # Copy X to Y and Z
                        ">>[-<<+>>]" # Move Z to X
                        )
                self.dp += 1

            case "over":
                if self.dp < 2:
                    raise IndexError("Not enough elements for `over`")
                # [ ... X, FOO, Y, Z ]
                self.result.append(
                        "[-]<<" # Set Y to 0 then move to X
                        "[->>+>+<<<]" # Copy X to Y and Z
                        ">>>[-<<<+>>>]" # Move Z to X
                        )
                self.dp += 1

            case "swap":
                # [ ... X, Y ] -> [ ... Y, X ]
                if self.dp < 2:
                    raise IndexError("Not enough elements for `swap`")
                self.result.append(
                        "<[->+<]"
                        "<[->+<]"
                        ">>[-<<+>>]")

            case "add":
                if self.dp < 2:
                    raise IndexError(f"Not enough elements for `add` expecting 2 but {self.dp} found")
                self.result.append("<[-<+>]")
                self.dp -= 1

            case "sub":
                if self.dp < 2:
                    raise IndexError("Not enough elements for `sub`")
                self.result.append("<[-<->]")
                self.dp -= 1

            case "print":
                self.result.append("<. ; print")
                self.dp -= 1

            case "neq":
                # [ ..., Y, X ] = Y != X
                if self.dp < 2:
                    raise IndexError("Not enough elements for `neq`")
                self.result.append(
                        "[-]<" # move to X 
                        "[-<->]<" # subtract Y from X, X destroyed here
                        "[[-]>+<][-]" # Check for Y if it's not 0 then set it to 1 and then move to X
                        ">[-<+>]" # Check for Y if it's not 0 then set it to 1 and then move to X
                        )
                self.dp -= 1

            case "eq":
                # [ ..., Y, X ] Y == X
                if self.dp < 2:
                    raise IndexError("Not enough elements for `eq`")
                self.result.append(
                        "[-]<" # move to X 
                        "[-<->]<" # subtract Y from X, X destroyed here
                        "[[-]>+<]+" # If Y - X != 0 then set X=1. After that always set Y=1
                        ">[-<->]" # At this point X is either 1 or 0 but Y is always 1 thus Y-X will be the self.result
                        )
                self.dp -= 1

            case "gt":
                # NOTE(bagasjs): Y and X must not be 255. This is due to QUICK HACK
                #                If we disable QUICK HACK it will resulting on
                #                Weird behaviour if X or Y or both of them is 0
                # TODO(bagasjs): Find a way to not depends on the QUICK HACK
                # [ ..., Y, X, Z, W, A ] Y > X
                # [ ..., 21, 19, 0, 0, 1 ]
                if self.dp < 2:
                    raise IndexError("Not enough elements for `gt`")
                self.result.append(
                        "[-]>[-]>+<<<" # Clear Z and W and set A to 1 then move to X. This part ends in X
                        "[->+<]<[->+<]>" # Move X to Z and Move Y to X. We end in X
                        "+>+<" # QUICK HACK: Add 1 for X and Z
                        # If X > 0 decrease X then decrease Z.
                        # Looping move until 0 (which is always W) then move back to X
                        "[->-[>]<<]>>>[-<]<<" # Now we have if X > 0 then GT if Z > 0 then LT. Also we always in X
                        "[-<+>]" # We need to normalize the number if Y > 0 then set Y into 1
                        "<[[-]>+<][-]>[-<+>]"
                        )
                self.dp -= 1

            case "lt":
                # NOTE(bagasjs): Y and X must not be 255. This is due to QUICK HACK
                #                If we disable QUICK HACK it will resulting on
                #                Weird behaviour if X or Y or both of them is 0
                # TODO(bagasjs): Find a way to not depends on the QUICK HACK
                if self.dp < 2:
                    raise IndexError("Not enough elements for `lt`")
                # [ ..., Y, X, Z, W, A ] Y > X
                # [ ..., 21, 19, 0, 0, 1 ]
                if self.dp < 2:
                    raise IndexError("Not enough elements for `gt`")
                self.result.append(
                        "[-]>[-]>+<<<" # Clear Z and W then move to X
                        "[->+<]<[->+<]>" # Move X to Z and Move Y to X
                        "+>+<" # QUICK HACK: Add 1 for X and Z
                        "[->-[>]<<]>>>[-<]<" # Now we have if X > 0 then GT if Z > 0 then LT. Also we always in X
                        "[-<<+>>]<[-]" # We need to normalize the number if Y > 0 then set Y into 1
                        "<[[-]>+<][-]>[-<+>]"
                        )
                self.dp -= 1


            case "or":
                # TODO: This wont work for `0 0 or`
                # [ ..., Y, X ] => Y OR X
                if self.dp < 2:
                    raise IndexError("Not enough elements for `and`")
                self.result.append(
                        "[-]<" # Move to X,
                        "[-<+>]<" # Add X to Y
                        "[[-]>+<]>" # Set Y to 0 and X to 1 if Y > 0 
                        "[-<+>]"
                        )
                self.dp -= 1

            case "and":
                # [ ..., Y, X, Z ] => Y AND X
                if self.dp < 2:
                    raise IndexError("Not enough elements for `and`")
                self.result.append(
                        "[-]<<" # Move to X
                        "[[-]>[[-]>+<]<]" # If X != 0 set X to 0 if Y != 0 set Y to 0 and set Z = 1
                        ">>[-<<+>>]<" # Move the value of Z to Y
                        )
                self.dp -= 1

            # Helper intrinsic
            case "dbgprint":
                self.result.append("<? ; dbgprint")
                self.dp -= 1


    def emit_while(self, while_: Inst):
        assert isinstance(while_, While)
        start_sp = self.dp;
        self.result.append(";; Preamble condition")
        for inst in while_.cond:
            self.emit_once(inst)
        self.result.append(";; Start of the loop")
        self.result.append("<[")
        self.dp -= 1
        self.result.append(";; Loop Body")
        for inst in while_.body:
            self.emit_once(inst)
        self.result.append(";; Loop Condition Checking")
        for inst in while_.cond:
            self.emit_once(inst)
        self.result.append("<]")
        self.dp -= 1
        if self.dp != start_sp:
            error(f"While loop at line {while_.line_number} starts with SP={start_sp} but ends with SP={self.dp}")

    def emit_branch(self, branch: Inst):
        assert isinstance(branch, Branch)
        start_sp = self.dp
        self.result.append(";; Check for condition")
        for inst in branch.cond:
            self.emit_once(inst)
        # [ ... CONDITION_RESULT, A ]
        self.result.append(";; IF condition")
        self.result.append("[-]+<[") # If CONDITION_RESULT 
        self.result.append("[-]>[-]>")
        for inst in branch.if_body:
            self.emit_once(inst)
        self.result.append("<<]") # End of If
        if len(branch.else_body) > 0:
            self.result.append(";; ELSE")
            self.result.append(">[[-]>") # Start of else
            for inst in branch.else_body:
                self.emit_once(inst)
            self.result.append("<]<") # End of else
        else:
            self.dp -= 1
        self.result.append(";; ENDIF")
        if self.dp != start_sp:
            error(f"If statement at line {branch.line_number} starts with SP={start_sp} but ends with SP={self.dp}")

    def emit_array_op(self, inst: ArrayOp):
        if inst.is_get:
            print(f"Getting {inst.name}")
        else:
            # Set consume 2 DP which is [ ... index, value ] 
            print(f"Setting {inst.name}")
            self.dp -= 2

    def emit_once(self, inst: Inst):
        if isinstance(inst, Integer):
            self.result.append("[-]" + "+" * inst.value+ f"> ")
            self.dp += 1
        elif isinstance(inst, Intrinsic):
            self.emit_intrinsic(inst)
        elif isinstance(inst, While):
            self.emit_while(inst)
        elif isinstance(inst, ArrayOp):
            self.emit_array_op(inst)
        elif isinstance(inst, Branch):
            self.emit_branch(inst)

    def emit_all(self):
        if self.program.offset > 0:
            print("Program offset: ", self.program.offset)
            self.result.append(";; Aggregate Array Offset")
            self.result.append(">" * self.program.offset + "\n")
        for inst in self.program.body:
            self.emit_once(inst)
        return "\n".join(self.result)

def compile_to_brainfuck(source: str, debug_sym: bool = False) -> str:
    tokens = parse_tokens(source)
    parser = Parser(tokens)
    parser.parse()
    codegen = Codegen(parser.program)
    return codegen.emit_all()

def compile_file(input_file, output_file):
    with open(input_file, "r") as ifile:
        source = ifile.read()
        result = compile_to_brainfuck(source, debug_sym=True)
        with open(output_file, "w") as ofile:
            ofile.write(result)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("USAGE: bfcat <run|com> <source.bfcat> [output.bfcat]")
        exit(-1)

    outputfile = "a.bf"
    if len(sys.argv) == 4:
        outputfile = sys.argv[3]
    if sys.argv[1] == "com":
        compile_file(sys.argv[2], outputfile)
    elif sys.argv[1] == "run":
        import subprocess
        compile_file(sys.argv[2], outputfile)
        subprocess.run(["./build/bfpp.exe", outputfile])
