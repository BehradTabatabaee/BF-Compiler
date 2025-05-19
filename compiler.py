import pathlib, re, sys

# superclass
class Command:
    pass

# assignment
class Assign(Command):
    def __init__(self, offset, value):
        self.offset = offset
        self.value = value

# addition
class Add(Command):
    def __init__(self, offset, value):
        self.offset = offset
        self.value = value

# multiplication
class Multiply(Command):
    def __init__(self, offset, value):
        self.offset = offset
        self.value = value

# tape[destOffset] += tape[sourceOffset] * value
# this is needed for loop optimization (sigh)
class MultiplyAndAdd(Command):
    def __init__(self, sourceOffset, destinationOffset, value):
        self.sourceOffset = sourceOffset
        self.destinationOffset = destinationOffset
        self.value = value

# pointer movement
# a positive value indicates movement to the right, a negative value indicates movement to the left
class Right(Command):
    def __init__(self, offset):
        self.offset = offset

# input
class Input(Command):
    def __init__(self, offset):
        self.offset = offset

# output
class Output(Command):
    def __init__(self, offset):
        self.offset = offset

# if statement
class If(Command):
    def __init__(self, commands):
        self.commands = commands

# loop
class Loop(Command):
    def __init__(self, commands):
        self.commands = commands

def tokenize(characters, isMainCall: bool):
    result = []
    for c in characters:
        item = 0
        if c == "+":
            item = Add(0, +1)
        elif c == "-":
            item = Add(0, -1)
        elif c == "<":
            item = Right(-1)
        elif c == ">":
            item = Right(+1)
        elif c == ",":
            item = Input(0)
        elif c == ".":
            item = Output(0)
        elif c == "[":
            item = Loop(tokenize(characters, False))
        elif c == "]":
            if isMainCall:
                raise ValueError("Invalid Loop")
            else:
                return result
        else:
            raise AssertionError("Illegal Character")
        result.append(item)

    if isMainCall:
        return result
    else:
        raise ValueError("Invalid Loop")

def parse(codeString):
    codeString = re.sub(r"[^+\-<>.,\[\]]", "", codeString)
    return tokenize(iter(codeString), True)

def optimize_loop(commands):
    deltas = {}
    pointer_offset = 0

    for command in commands:
        if isinstance(command, Add):
            offset = command.offset + pointer_offset
            deltas[offset] = deltas.get(offset, 0) + command.value
        elif isinstance(command, Right):
            pointer_offset += command.offset
        else:
            return None

    if pointer_offset != 0 or deltas.get(0, 0) != -1:
        return None

    del deltas[0]

    result = []

    for offset in sorted(deltas.keys()):
        result.append(MultiplyAndAdd(0, offset, deltas[offset]))
    
    result.append(Assign(0, 0))

    return result

def optimize(commands):
    optimized = []
    pointer_shift = 0

    for command in commands:
        if isinstance(command, Assign):
            actual_offset = command.offset + pointer_shift
            prev_command = optimized[-1] if optimized else None

            if isinstance(prev_command, (Add, Assign)) and prev_command.offset == actual_offset:
                del optimized[-1]
            
            optimized.append(Assign(actual_offset, command.value))

        elif isinstance(command, Multiply):
            optimized.append(Multiply(command.offset + pointer_shift, command.value))

        elif isinstance(command, Add):
            actual_offset = command.offset + pointer_shift
            prev_command = optimized[-1] if optimized else None

            if isinstance(prev_command, Add) and prev_command.offset == actual_offset:
                prev_command.value = (prev_command.value + command.value) & 0xFF
            elif isinstance(prev_command, Assign) and prev_command.offset == actual_offset:
                prev_command.value = (prev_command.value + command.value) & 0xFF
            else:
                optimized.append(Add(actual_offset, command.value))

        elif isinstance(command, Right):
            pointer_shift += command.offset

        elif isinstance(command, Input):
            optimized.append(Input(command.offset + pointer_shift))

        elif isinstance(command, Output):
            optimized.append(Output(command.offset + pointer_shift))

        else:
            if pointer_shift != 0:
                optimized.append(Right(pointer_shift))
                pointer_shift = 0

            if isinstance(command, Loop):
                loop_optimized = optimize_loop(command.commands)
                if loop_optimized is not None:
                    optimized.extend(loop_optimized)
                else:
                    inner_optimized = optimize(command.commands)
                    optimized.append(Loop(inner_optimized))

            elif isinstance(command, If):
                inner_optimized = optimize(command.commands)
                optimized.append(If(inner_optimized))

            else:
                raise ValueError("Unknown command")

    if pointer_shift != 0:
        optimized.append(Right(pointer_shift))

    return optimized

def indent(line, level = 1) :
    return "\t" * level + line + "\n"

def plusOrMinus(val):
	return "+" if (val >= 0) else "-"

def translate(commands, name, isMainCall = True, indentlevel = 1):
	result = ""
	if isMainCall:
		result += indent("#include <stdio.h>", 0)
		result += indent("#include <stdlib.h>", 0)
		result += indent("", 0)
		result += indent("char read() {", 0)
		result += indent("int temp = getchar();", 1)
		result += indent("return (char)(temp != EOF ? temp : 0);", 1)
		result += indent("}", 0)
		result += indent("", 0)
		result += indent("int main(void) {", 0)
		result += indent("char tape[10000] = {0};")
		result += indent("char *tapePointer = &tape[1000];")
		result += indent("")
	
	for command in commands:
		if isinstance(command, Assign):
			result += indent(f"tapePointer[{command.offset}] = {command.value};")
               
		elif isinstance(command, Add):
			s = f"tapePointer[{command.offset}]"
			if command.value == 1:
				s += "++;"
			elif command.value == -1:
				s += "--;"
			else:
				s += f" {plusOrMinus(command.value)}= {abs(command.value)};"
			result += indent(s)
               
		elif isinstance(command, Multiply):
			if command.value == 1:
				result += indent(f"tapePointer[{command.offset}] = tapePointer[{command.value}];")
			else:
				result += indent(f"tapePointer[{command.offset}] *= tapePointer[{command.value}] & 0xFF;")
                    
		elif isinstance(command, Right):
			if command.offset == 1:
				result += indent("tapePointer++;")
			elif command.offset == -1:
				result += indent("tapePointer--;")
			else:
				result += indent(f"tapePointer {plusOrMinus(command.offset)}= {abs(command.offset)};")
                    
		elif isinstance(command, MultiplyAndAdd):
			if abs(command.value) == 1:
				result += indent(f"tapePointer[{command.destinationOffset}] {plusOrMinus(command.value)}= tapePointer[{command.sourceOffset}];")
			else:
				result += indent(f"tapePointer[{command.destinationOffset}] {plusOrMinus(command.value)}= tapePointer[{command.sourceOffset}] * {abs(command.value)};")        

		elif isinstance(command, Input):
			result += indent(f"tapePointer[{command.offset}] = read();")
               
		elif isinstance(command, Output):
			result += indent(f"putchar(tapePointer[{command.offset}]);")
               
		elif isinstance(command, If):
			result += indent("if (*tapePointer != 0) {")
			result += translate(command.commands, name, False, indentlevel + 1)
			result += indent("}")
               
		elif isinstance(command, Loop):
			result += indent("while (*tapePointer != 0) {")
			result += translate(command.commands, name, False, indentlevel + 1)
			result += indent("}")
               
		else:
			raise AssertionError("Unknown command")
	
	if isMainCall:
		result += indent("")
		result += indent("return 0;")
		result += indent("}", 0)
          
	return result

def main(args):
    if len(args) != 2:
        return "Usage: python compiler.py <infile> <outfile.c>"

    inpath = pathlib.Path(args[0])
    if not inpath.is_file():
        return f"{inpath}: Not a file"

    outpath = pathlib.Path(args[1])

    if outpath.suffix != ".c":
        return f"{outpath}: Unknown output type"

    incode = inpath.read_text()
    commands = parse(incode)
    commands = optimize(commands)

    outcode = translate(commands, outpath.stem, True)
    outpath.write_text(outcode)
    return None

if __name__ == "__main__":
    errmsg = main(sys.argv[1:])
    if errmsg is not None:
        sys.exit(errmsg)