# Custom shell in python

&copy; Maxence Raballand 2021.

The goal of this program is to recreate a shell in python without using the [`cmd`](https://docs.python.org/3/library/cmd.html) module.

It has been achieved by creating searching for the process, waiting for its execution, and then reading its output.

## Usage

There are two modes for this program, the first one is the interactive mode, where the user can type commands and the program will execute them.

```bash
python3 mysh.py
```

The second mode is the batch mode, where the program will execute the commands in the file specified (for example `commands.txt`).

```bash
python3 mysh.py commands.txt
```

## Custom usage in python

By looking at the code, you can see that the program is very simple. It is just a loop that reads the input and executes the command.

The whole program is encapsulated in a class `Shell` which has a `run` method. To instantiate the class, you can use the `Shell` class. As parameter, you can pass the name of the file containing the commands and whether it is interactive or not (file not needed in interactive mode).

Thus we have something like this:

```py
from shell import Shell, ShellMode
import sys

if len(sys.argv) > 1:
    shell = Shell(ShellMode.BATCH, sys.argv[1])
else:
    shell = Shell()


shell.run()
```

## Credits

This program was created by Maxence Raballand for a course at ESILV Paris, La Défense.
