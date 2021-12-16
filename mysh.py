from shell import Shell, ShellMode
import sys

if len(sys.argv) > 1:
    shell = Shell(ShellMode.BATCH, sys.argv[1])
else:
    shell = Shell()


shell.run()

# shell = Shell(ShellMode.INTERACTIVE)
# shell.run() 