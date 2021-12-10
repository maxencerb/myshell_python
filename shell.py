import os
import sys
import subprocess

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ShellMode:
    INTERACTIVE = 0
    BATCH = 1

def interactive_output(command, color: bcolors, is_bold: bool = False):
    result = f"{color}{command}{bcolors.ENDC}"
    if is_bold:
        result = set_bold(result)
    return result

def set_bold(command, noend: bool = False):
    return f"{bcolors.BOLD}{command}{bcolors.ENDC if not noend else ''}"

class Shell:

    def __init__(self, shell_mode: ShellMode = ShellMode.INTERACTIVE, file_input: str = None):
        self.shell_mode = shell_mode
        self.current_directory = os.getcwd()
        self.current_user = os.getenv('USER')
        self.current_host = "pythonMysh"
        self.set_promp()
        if file_input is None and shell_mode == ShellMode.BATCH:
            raise ValueError("file_input cannot be None in batch mode")
        self.file_input = file_input
        self.default_output = sys.stdout
        self.default_error = sys.stderr
        self.current_output = self.default_output
        self.current_error = self.default_error

    def set_promp(self):
        self.prompt = interactive_output(f"{self.current_user}@{self.current_host}", bcolors.OKGREEN, True) + ':' + interactive_output(self.current_directory, bcolors.OKBLUE, True) + "$ "


    def run(self):
        if self.shell_mode == ShellMode.INTERACTIVE:
            self.__run_interactive()
        else:
            self.__run_batch()

    def __run_interactive(self):
        while True:
            command = input(self.prompt)
            result = self.__run_command(command)
            if result is not None:
                print(result, file=self.current_output)

    def __run_batch(self):
        with open(self.file_input, 'r') as file:
            stderr_fileno = sys.stderr.fileno()
            for line in file:
                os.write(stderr_fileno, line.encode())
                result = self.__run_command(line)
                if result is not None:
                    print(result, file=self.current_output)

    def __write_to_file(self, file):
        return open(file, 'w')

    def __run_command(self, command):
        parsed_command = self.__split_command(command)
        # Get all env variables
        for i in range(len(parsed_command)):
            if parsed_command[i][0] == '$':
                env_var = parsed_command[i][1:]
                tryget = os.getenv(env_var)
                parsed_command[i] = tryget if tryget is not None else parsed_command[i]
        if len(parsed_command) == 0:
            return None
        elif parsed_command[0] == 'exit':
            if len(parsed_command) == 1:
                exit(0)
            elif parsed_command[1] == '1':
                exit(1)
            else:
                exit(2)
        elif parsed_command[0] == "cd":
            return self.__run_cd(parsed_command)
        elif parsed_command[0] == "pwd":
            return os.getcwd()
        else:
            try:
                parsed_command[0] = self.__which(parsed_command[0])
                if parsed_command[0] is None:
                    raise FileNotFoundError()
                proc = subprocess.Popen(parsed_command, stdout=self.current_output, stderr=self.current_error, stdin=subprocess.PIPE)
                proc.communicate()
            except Exception as e:
                self.__run_error()

    def __split_command(self, command):
        output_to_file = command.split('>')
        # There is a redirection
        if len(output_to_file) == 2:
            outputs = self.__split_spaces(output_to_file[1])
            if len(outputs) == 1:
                self.current_output = self.__write_to_file(outputs[0])
                return self.__split_spaces(output_to_file[0])
            else:
                self.__run_error()
                return None, None
        # No redirection
        elif len(output_to_file) == 1:
            self.current_output = self.default_output
            return self.__split_spaces(output_to_file[0])
        # Incorrect redirection
        else:
            self.__run_error()
            return None

    def __split_spaces(self, command):
        return list(filter(lambda x: x != '', command.split(' ')))

    def __run_error(self):
        err = "An error has occurred\n"
        print(err, file=sys.stderr)

    def __which(self, command):

        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(command)

        if fpath:
            if is_exe(command):
                return command
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, command)
                if is_exe(exe_file):
                    return exe_file
        return None

    # Change directory

    def __run_cd(self, parsed_command):
        if len(parsed_command) == 1:
            return self.__run_cd_home()
        elif len(parsed_command) == 2:
            return self.__run_cd_path(parsed_command[1])
        else:
            self.__run_error()
            return None
    
    def __run_cd_home(self):
        self.current_directory = os.getenv('HOME')
        os.chdir(self.current_directory)
        self.set_promp()
        return None

    def __run_cd_path(self, path):
        if path[0] != '/' and path[0] != '~' and path[0] != '.':
            path = './' + path
        if os.path.exists(path):
            os.chdir(path)
            self.current_directory = os.getcwd()
            self.set_promp()
            return None
        else:
            self.__run_error()
            return None