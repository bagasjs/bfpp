# A simple stack based concatenative programming language compiled to bfpp

def compile_to_brainfuck(source: str, debug_sym = False) -> str:
    jumpables = {}
    # Tokenize
    program = [ word 
               for line in source.strip().splitlines() 
               if not line.lstrip().startswith(";")
               for word in line.strip().split(" ") ]
    print(program)

    # Pass 2: Convert to brainfuck
    result = []
    i = 0
    sp = 0
    while i < len(program):
        inst = program[i]

        if debug_sym:
            result.append(f";; {inst}")

        match inst:
            case num if num.isdigit():
                result.append("[-]" + "+" * int(inst) + f"> ")
                sp += 1
                i += 1

            case "dup":
                if sp < 1:
                    raise IndexError("Not enough elements for `dup`")
                result.append(
                        "[-]<" # Set Y to 0 then move to X
                        "[->+>+<<]" # Copy X to Y and Z
                        ">>[-<<+>>]" # Move Z to X
                        )
                sp += 1
                i += 1

            case "over":
                if sp < 2:
                    raise IndexError("Not enough elements for `over`")
                # [ ... X, FOO, Y, Z ]
                result.append(
                        "[-]<<" # Set Y to 0 then move to X
                        "[->>+>+<<<]" # Copy X to Y and Z
                        ">>>[-<<<+>>>]" # Move Z to X
                        )
                sp += 1
                i += 1

            case "swap":
                # [ ... X, Y ] -> [ ... Y, X ]
                if sp < 2:
                    raise IndexError("Not enough elements for `swap`")
                result.append(
                        "<[->+<]"
                        "<[->+<]"
                        ">>[-<<+>>]")
                i += 1

            case "add":
                if sp < 2:
                    raise IndexError("Not enough elements for `add`")
                result.append("<[-<+>]")
                sp -= 1
                i += 1

            case "sub":
                if sp < 2:
                    raise IndexError("Not enough elements for `sub`")
                result.append("<[-<->]")
                sp -= 1
                i += 1

            case "dbgprint":
                result.append("<? ; dbgprint")
                sp -= 1
                i += 1

            case "neq":
                # [ ..., Y, X ] = Y != X
                if sp < 2:
                    raise IndexError("Not enough elements for `neq`")
                result.append(
                        "[-]<" # move to X 
                        "[-<->]<" # subtract Y from X, X destroyed here
                        "[[-]>+<][-]" # Check for Y if it's not 0 then set it to 1 and then move to X
                        ">[-<+>]" # Check for Y if it's not 0 then set it to 1 and then move to X
                        )
                i += 1
                sp -= 1

            case "eq":
                # [ ..., Y, X ] Y == X
                if sp < 2:
                    raise IndexError("Not enough elements for `eq`")
                result.append(
                        "[-]<" # move to X 
                        "[-<->]<" # subtract Y from X, X destroyed here
                        "[[-]>+<]+" # If Y - X != 0 then set X=1. After that always set Y=1
                        ">[-<->]" # At this point X is either 1 or 0 but Y is always 1 thus Y-X will be the result
                        )
                sp -= 1
                i += 1

            case "gt":
                # [ ..., Y, X, Z, W, A ] Y > X
                # [ ..., 21, 19, 0, 0, 1 ]
                if sp < 2:
                    raise IndexError("Not enough elements for `gt`")
                result.append(
                        "[-]>[-]>+<<<" # Clear Z and W then move to X
                        "[->+<]<[->+<]>" # Move X to Z and Move Y to X
                        "[->-[>]<<]>>>[-<]<<" # Now we have if X > 0 then GT if Z > 0 then LT. Also we always in X
                        "[-<+>]" # We need to normalize the number if Y > 0 then set Y into 1
                        "<[[-]>+<][-]>[-<+>]"
                        )
                sp -= 1
                i += 1

            case "lt":
                if sp < 2:
                    raise IndexError("Not enough elements for `lt`")
                # [ ..., Y, X, Z, W, A ] Y > X
                # [ ..., 21, 19, 0, 0, 1 ]
                if sp < 2:
                    raise IndexError("Not enough elements for `gt`")
                result.append(
                        "[-]>[-]>+<<<" # Clear Z and W then move to X
                        "[->+<]<[->+<]>" # Move X to Z and Move Y to X
                        "[->-[>]<<]>>>[-<]<" # Now we have if X > 0 then GT if Z > 0 then LT. Also we always in X
                        "[-<<+>>]<[-]" # We need to normalize the number if Y > 0 then set Y into 1
                        "<[[-]>+<][-]>[-<+>]"
                        )
                i += 1
                sp -= 1


            # Unfinished

            case "and":
                # [ ..., Y, X, Z ] => Y AND X
                if sp < 2:
                    raise IndexError("Not enough elements for `and`")
                sp -= 1
                i += 1

            case "or":
                # TODO: This wont work for `0 0 or`
                # [ ..., Y, X ] => Y OR X
                if sp < 2:
                    raise IndexError("Not enough elements for `and`")
                result.append(
                        "[-]<<[->>+<<]>>" # Move Y to Z
                        "[[-]<<+>>]<" # If Z != 0, Increment Y and set Z to 0
                        "[[-]<+>]" # If X != 0, Increment Y and set X to 0
                        )
                sp -= 1
                i += 1

            case "while":
                pass

            case "end":
                pass

            case "do":
                pass

            case "if":
                pass
            case "else":
                pass

            case _:
                raise ValueError(f"Unknown instruction `{inst}`")

    
    concatenator = "\n" if debug_sym else ""
    return concatenator.join(result)

def main():
    import sys
    if len(sys.argv) < 2:
        print("USAGE: bfcat <source.bfcat> [output.bfcat]")
        exit(-1)
    with open(sys.argv[1], "r") as ifile:
        outputfile = "a.bf"
        if len(sys.argv) == 3:
            outputfile = sys.argv[2]
        with open(outputfile, "w") as ofile:
            ofile.write(compile_to_brainfuck(
                ifile.read(),
                debug_sym=True,
                ))

if __name__ == "__main__":
    main()
