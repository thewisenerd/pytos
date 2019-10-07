from pytos.models.context import Context


class RunCommand(object):
    def __init__(self):
        self.args = None

    # return 0 if no errors
    # set self.args to copy args formatted from cmdline
    def parse_args(self, args) -> int:
        return 0

    # only call this post parse_args is called
    def run(self, context: Context) -> int:
        raise NotImplementedError("not implemented")
