import enum

# from RL/utils/logger.py
class Color(enum.Enum):
    ERROR = "\033[91m"
    WARNING = "\033[93m"
    INFO = "\033[96m"
    SUCCESS = "\033[92m"
    CLEAR = "\033[0m"


class Logger:

    def __init__(self, file=None, flags=[]):
        self.out_file = open(file, "a+") if file is not None else None
        self.flags = flags

    def __del__(self):
        if self.out_file is not None:
            self.out_file.close()

    def set_file_output(self, file):
        self.out_file = open(file, "a+")

    def set_flags(self, flags):
        self.flags = flags

    def _concat(*args):
        return " ".join(list(map(lambda x: repr(x)[1:-1], list(args))))

    def info(self, *args):
        if Color.INFO in self.flags:
            print(Color.INFO.value, *args, Color.CLEAR.value)
            if self.out_file is not None:
                self.out_file.write(Logger._concat("[INFO]", *args))
                self.out_file.write("\n")

    def success(self, *args):
        if Color.SUCCESS in self.flags:
            print(Color.SUCCESS.value, *args, Color.CLEAR.value)
            if self.out_file is not None:
                self.out_file.write(Logger._concat("[SUCCESS]", *args))
                self.out_file.write("\n")

    def warning(self, *args):
        if Color.WARNING in self.flags:
            print(Color.WARNING.value, *args, Color.CLEAR.value)
            if self.out_file is not None:
                self.out_file.write(Logger._concat("[WARNING]", *args))
                self.out_file.write("\n")

    def error(self, *args):
        if Color.ERROR in self.flags:
            print(Color.ERROR.value, *args, Color.CLEAR.value)
            if self.out_file is not None:
                self.out_file.write(Logger._concat("[ERROR]", *args))
                self.out_file.write("\n")

    def log(self, *args):
        if Color.CLEAR in self.flags:
            print(Color.CLEAR.value, *args)
            if self.out_file is not None:
                self.out_file.write(Logger._concat(*args))
                self.out_file.write("\n")


ALL_FLAGS = [Color.INFO, Color.SUCCESS, Color.WARNING, Color.ERROR]
INFO_FLAGS = [Color.INFO, Color.SUCCESS]
NON_CRITICAL_FLAGS = [Color.INFO, Color.SUCCESS, Color.WARNING]
NO_FLAGS = []

logger = Logger(flags=ALL_FLAGS)