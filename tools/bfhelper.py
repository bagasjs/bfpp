import math

def gen_bfnumber(n):
    if n == 0:
        return "[-]"

    # Find the best loop multiplier
    mul = 16
    rep = 1
    prevdiff = 256
    for i in range(16):
        diff = (mul * i) - n
        if diff < 0:
            diff *= -1

        if diff > prevdiff:
            break

        if diff < prevdiff:
            prevdiff = diff
            rep = i

    bf_code = f">{'+' * mul}[<{'+' * rep}>-]"
    adjust = n - (mul * rep)
    if adjust > 0:
        bf_code += "<" + "+" * adjust
    else:
        bf_code += "<" + "-" * (-adjust)
    return bf_code

def gen_bfstring(text: str) -> str:
    return "\n".join([ gen_bfnumber(ord(c)) + f";; {c} = {ord(c)}" for c in text ])

import sys
def usage():
    print("USAGE: bfhelper str|num|help <input>")

def shift(args: list[str], err: str) -> tuple[str, list[str]]:
    if len(args) <= 0:
        print(f"ERROR: {err}")
        sys.exit(-1)
    return args[0], args[1:]

if __name__ == "__main__":
    _, args = shift(sys.argv, "Unreachable")
    subcom, args = shift(args, "Please provide a subcommand")
    match subcom:
        case "str":
            input, args = shift(args, "Provide an input string")
            print(gen_bfstring(input))
        case "num":
            input, args = shift(args, "Provide an input number")
            print(gen_bfnumber(int(input)))
        case "help":
            usage()
        case _:
            usage()
