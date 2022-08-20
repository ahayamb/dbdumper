import os


class __Config():
    DUMP_LOCATION = None
    BINARY_LOCATION = None
    ENABLE_COMPRESSION = None

    def __init__(self):
        self.DUMP_LOCATION = os.environ.get("DUMPER_LOCATION", "backup")
        self.BINARY_LOCATION = os.environ.get("DUMPER_BINARY_LOCATION", "bin")
        self.ENABLE_COMPRESSION = os.environ.get(
            "DUMPER_ENABLE_COMPRESSION", True)


config = __Config()
