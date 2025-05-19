# Brainfuck Compiler

An efficient Brainfuck-to-C compiler written in Python, featuring parsing, loop optimizations, dead-code elimination, and C code generation for fast execution.

## Features

* **Parsing & Tokenization:** Reads standard Brainfuck code (`+ - < > . , [ ]`) and ignores all other characters.
* **Instruction Simplification:** Merges consecutive increments/decrements and pointer moves.
* **Loop Optimization:** Detects common patterns (e.g., `[-]`) and replaces them with direct memory operations.
* **Dead Code Elimination:** Removes redundant assignments and combines operations on the same cell.
* **C Code Generation:** Translates optimized commands into readable, portable C code.
* **Customizable Tape:** Defaults to a 10,000‐cell tape with adjustable starting pointer offset.

## Prerequisites

* Python 3.6 or higher
* A C compiler (e.g., `gcc`, `clang`)

## Installation

1. Clone this repository:

   ```sh
   git clone https://github.com/yourusername/optimizing-brainfuck-compiler.git
   cd optimizing-brainfuck-compiler
   ```

2. (Optional) Create a virtual environment:

   ```sh
   python3 -m venv env
   source env/bin/activate
   ```

3. Install any required packages (none in this repository). All code uses standard library modules.

## Usage

Compile a Brainfuck file (`.bf`) to C:

```sh
python compiler.py path/to/program.bf path/to/output.c
```

Compile the generated C:

```sh
gcc -O2 -o program path/to/output.c
```

Run your program:

```sh
./program
```

## Example

Given a Brainfuck file `hello.bf`:

```bf
++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>--.<<+.>++.
------.--------.>+.>.
```

Generate and build:

```sh
python compiler.py hello.bf hello.c
gcc -O2 -o hello hello.c
./hello
# Output: Hello World!
```

## How It Works

1. **Parsing:** Removes non‐command characters and builds a command stream.
2. **Optimization Pass:**

   * **Linear Merging:** Combines successive `+`/`-` and `<`/`>` into single operations.
   * **Loop Simplification:** Transforms patterns like `[-]` into direct cell assignment `cell = 0`.
   * **Multiply‐Add Detection:** Converts nested loops that transfer values into `tape[dest] += tape[src] * factor` operations.
   * **Dead Code Elimination:** Removes overwritten assignments and redundant adds.
3. **Code Generation:** Walks the optimized command list to emit clean C, using `while (*ptr)` for loops and direct pointer arithmetic.

## Contributing

Contributions, issues, and feature requests are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
