import os


class __Config():
    DUMP_LOCATION = None
    BINARY_LOCATION = None

    def __init__(self):
        self.DUMP_LOCATION = os.environ.get("DUMPER_LOCATION", "backup")
        self.BINARY_LOCATION = os.environ.get("DUMPER_BINARY_LOCATION", "bin")


config = __Config()
