#
# A full fledge compiler of bfcat.
# If you simply want to look at 
# how bfcat compile core operations
# like add, greater_than, less_than
# look at bfcat.py not bfcat2.py
#

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
TOK_DUP  = iota()
TOP_OVER = iota()
TOK_SWAP = iota()
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
TOK_DBGPRINT = iota()

TOK_DEF   = iota()

keyword_map = {
    "dup": TOK_DUP,
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
    "dbgprint": TOK_DBGPRINT,

    "def": TOK_DEF,
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
        for word in line.split():
            if word in keyword_map:
                result.append(Token(kind=keyword_map[word], text=word, line_number=line_number + 1))
            elif is_name(word):
                result.append(Token(kind=TOK_SYMBOL, text=word, line_number=line_number + 1))
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

class While(Inst):
    cond: List[Inst]
    body: List[Inst]

    def __init__(self, cond: List[Inst], body: List[Inst]):
        self.cond = cond
        self.body = body

    def __repr__(self):
        return f"While(cond={self.cond}, body={self.body})"

class Branch(Inst):
    cond: List[Inst]
    if_body: List[Inst]
    else_body: List[Inst]
    
    def __init__(self, cond: List[Inst], if_body: List[Inst], else_body: List[Inst]):
        self.cond = cond
        self.if_body = if_body
        self.else_body = else_body

    def __repr__(self):
        return f"Branch(cond={self.cond}, if={self.if_body}, else={self.else_body})"

class Program(object):
    def __init__(self, body: List[Inst], macros: Dict[str, List[Inst]]):
        self.body   = body
        self.macros = macros

    def __repr__(self):
        return f"Program(body={self.body}, macros={self.macros})"

class Parser(object):
    def __init__(self, tokens: List[Token]):
        self.program = Program([], {})
        self.blocks = [self.program.body]
        self.tokens = tokens
        self.i = 0

    def parse_once(self):
        if self.tokens[self.i].kind == TOK_WHILE:
            self.parse_while()
        elif self.tokens[self.i].kind == TOK_DEF:
            self.parse_macro()
        elif self.tokens[self.i].kind == TOK_SYMBOL:
            name = self.tokens[self.i]
            if name.text not in self.program.macros:
                error(f"Unknown macro {name.text} to expand")
            self.blocks[-1].extend(self.program.macros[name.text])
        elif self.tokens[self.i].kind == TOK_IF:
            self.parse_if()
        elif self.tokens[self.i].kind in [ TOK_DO, TOK_END, TOK_ELSE ]:
            print(self.blocks)
            error(f"invalid token '{self.tokens[self.i].text}' at line {self.tokens[self.i].line_number}. It has no context")
        elif self.tokens[self.i].kind == TOK_INT:
            self.blocks[-1].append(Integer(int(self.tokens[self.i].text)))
            self.i += 1
        elif self.tokens[self.i].text in keyword_map:
            self.blocks[-1].append(Intrinsic(self.tokens[self.i].text))
            self.i += 1
        else:
            error(f"invalid token '{self.tokens[self.i].text}' at line {self.tokens[self.i].line_number}")

    def parse_macro(self):
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
            while self.tokens[self.i].kind != TOK_END:
                if self.i + 1 >= len(self.tokens) and self.tokens[self.i].kind != TOK_END:
                    error(f"invalid eof expecting 'end' for 'else' in line {else_tok.line_number}")
                self.parse_once()
            self.blocks.pop()
        self.blocks[-1].append(Branch(condition, if_body, else_body))
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
        self.blocks[-1].append(While(condition, body))
        self.i += 1

    def parse(self):
        while self.i < len(self.tokens):
            self.parse_once()

class Codegen(object):
    def __init__(self, program: Program):
        self.program = program

    def generate_brainfuck(self):
        return ""

def compile_to_brainfuck(source: str, debug_sym: bool = False) -> str:
    tokens = parse_tokens(source)
    parser = Parser(tokens)
    parser.parse()
    codegen = Codegen(parser.program)
    print(parser.program)
    return codegen.generate_brainfuck()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: bfcat <source.bfcat> [output.bfcat]")
        exit(-1)
    with open(sys.argv[1], "r") as ifile:
        outputfile = "a.bf"
        if len(sys.argv) == 3:
            outputfile = sys.argv[2]
        source = ifile.read()
        result = compile_to_brainfuck(source, debug_sym=True)
        # with open(outputfile, "w") as ofile:
        #     source = ifile.read()
        #     ofile.write(compile_to_brainfuck(
        #         source,
        #         debug_sym=True,
        #         ))
