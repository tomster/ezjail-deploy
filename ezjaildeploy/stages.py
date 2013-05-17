from collections import OrderedDict


class NameDescription(object):

    name = u''
    description = u''

    def __init__(self, name=None, description=None):
        if name is not None:
            self.name = name
        if description is None:
            self.description = self.__doc__
        else:
            self.description = description

    def has_run(self):
        """ check for existence of ZFS snapsshot on host system """
        return False


class Step(NameDescription):

    command = None

    def __init__(self, command, name=None, description=None, args=[], kwargs=dict()):
        if name is None:
            name = command.func_name
        super(Step, self).__init__(name, description)
        self.command = command
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        self.command(*self.args, **self.kwargs)

    @property
    def _snapshot_name(self):
        return ''


class Stage(NameDescription):

    steps = OrderedDict()
    __jail__ = None

    def __init__(self, steps, name=None, description=None):
        super(Stage, self).__init__(name, description)
        for step in steps:
            self.steps[step.name] = step

    def __call__(self):
        if self.has_run():
            return
        for step in self.steps.itervalues():
            step()
