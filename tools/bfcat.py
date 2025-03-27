# A simple stack based concatenative programming language compiled to bfpp

def tokenize_bfcat(source: str) -> list[str]:
    program = [ word 
               for line in source.strip().splitlines() 
               if not line.strip().startswith(";") and not len(line.strip()) == 0
               for word in line.strip().split(" ") ]
    return program

class Block(object):
    block_index: int
    label: str
    start: int
    end: int
    items: list[str]

    def __init__(self, label: str, block_index: int, start: int, end: int):
        self.block_index = block_index
        self.label = label
        self.start = start
        self.end = end
        self.items = []

    def __repr__(self):
        return f"{self.label} = {self.items}"
        # return f"Block(index={self.block_index}, label={self.label})"

def preprocess_program(program: list[str]) -> tuple[str, dict[str, Block]]:
    #  [ 50 @loop dup print 1 sub dup 0 eq ?end !loop @end ]
    #  [
    #      initlane: [ 50 @loop dup print 1 sub dup 0 eq ?end !loop ]
    #      !loop1_lane: [ dup print 1 sub 0 eq ?end ] 
    #      !end_lane: [  ] 
    #  ]

    blocks = {}
    block_counter = 1
    root_block_label = "start"
    prev_label = None
    for (i, word) in enumerate(program):
        if word[0] == "@":
            if len(blocks) == 0 and i != 0:
                start = Block("start", block_counter, 0, i)
                block_counter += 1
                start.items = program[start.start:start.end]
                blocks["start"] = start
                prev_label = "start"

            label = word[1:]
            if not prev_label:
                root_block_label = label

            if label in blocks:
                raise ValueError(f"Duplicate label {label}")
            block = Block(label, block_counter, i, len(program))
            block_counter += 1
            if prev_label is not None:
                blocks[prev_label].end = i
            blocks[label] = block
            prev_label = label


    for label, block in blocks.items():
        if len(block.items) == 0:
            block.items = program[block.start+1:block.end]

    if len(blocks) == 0:
        start = Block("start", block_counter, 0, len(program))
        block_counter += 1
        start.items = program[start.start:start.end]
        blocks["start"] = start

    return (root_block_label, blocks)

class Compiler(object):
    def __init__(self, source: str):
        self.program = tokenize_bfcat(source)
        root_block_label, self.blocks = preprocess_program(self.program)
        self.start = self.blocks[root_block_label]

    def compile_block_to_bf(self, block: Block) -> str:
        index = block.block_index
        compiled_block = []
        for i, inst in enumerate(block.items):
            match inst:
                case num if num.isdigit():
                    compiled_block.append("[-]" + "+" * int(inst) + f"> ")
                case jmp if jmp[0] == "!":
                    pass
                case jmp if jmp[0] == "?":
                    pass
                case "dup":
                    compiled_block.append(
                            "[-]<" # Set Y to 0 then move to X
                            "[->+>+<<]" # Copy X to Y and Z
                            ">>[-<<+>>]" # Move Z to X
                            )
                case "swap":
                    compiled_block.append(
                            "<[->+<]"
                            "<[->+<]"
                            ">>[-<<+>>]")
                    i += 1
                case "add":
                    compiled_block.append("<[-<+>]")
                case "sub":
                    compiled_block.append("<[-<->]")
                case "eq":
                    # Y == X
                    compiled_block.append(
                            "[-]<" # move to X 
                            "[-<->]<" # subtract Y from X, X destroyed here
                            "[[-]>+<]+" # If Y - X != 0 then set X=1. After that always set Y=1
                            ">[-<->]" # At this point X is either 1 or 0 but Y is always 1 thus Y-X will be the compiled_block
                            )
                case "print":
                    compiled_block.append("<?")
                case _:
                    raise ValueError(f"Unknown instruction `{inst}`")
        compiled = "\n".join(compiled_block)
        return compiled

    def compile_to_bf(self):
        compiled_program = []
        print(self.blocks)
        for _, block in self.blocks.items():
            compiled_program.append(self.compile_block_to_bf(block))
        compiled = "\n".join(compiled_program)
        compiled = f">\n{compiled}"
        return compiled


def main():
    import sys
    if len(sys.argv) < 2:
        print("USAGE: bfcat <source.bfcat> [output.bfcat]")
        exit(-1)
    with open(sys.argv[1], "r") as ifile:
        outputfile = "a.bf"
        if len(sys.argv) == 3:
            outputfile = sys.argv[2]
        output = Compiler(ifile.read()).compile_to_bf()
        with open(outputfile, "w") as ofile:
            ofile.write(output)

if __name__ == "__main__":
    main()
