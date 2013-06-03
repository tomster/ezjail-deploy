from collections import OrderedDict


class NameDescription(object):

    name = u''
    description = u''
    _has_run = False

    def __init__(self, name=None, description=None):
        if name is not None:
            self.name = name
        if description is None:
            self.description = self.__doc__
        else:
            self.description = description

    def _mark_as_completed(self):
        """ create ZFS snapsshot on host"""
        self._has_run = True

    def has_run(self):
        """ check for existence of ZFS snapsshot on host system """
        return self._has_run


class Step(NameDescription):

    __stage__ = None

    def command(self):
        raise NotImplemented

    def __init__(self, command=None, name=None, description=None, **kwargs):
        if name is None and command is not None:
            name = command.func_name
        elif command is None:
            name = self.__class__.__name__
        super(Step, self).__init__(name, description)
        if command is not None:
            self.command = command
        self.kwargs = kwargs

    def __call__(self):
        self.command(**self.kwargs)
        self._mark_as_completed()

    @property
    def _snapshot_name(self):
        step_index = self.__stage__.steps.keys().index(self.name) + 1
        return '{0}-{1:03}-{2}'.format(self.__stage__._snapshot_name, step_index, self.name)


class Stage(NameDescription):

    __jail__ = None
    steps = None

    def __init__(self, steps, name=None, description=None):
        super(Stage, self).__init__(name, description)
        if self.steps is None:
            self.steps = OrderedDict()
        for step in steps:
            self.steps[step.name] = step
            self.steps[step.name].__stage__ = self

    def __call__(self):
        for step in self.steps.itervalues():
            if not step.has_run():
                step()
        self._mark_as_completed()

    @property
    def _snapshot_name(self):
        return '{0:03}-{1}'.format(self.__jail__.stages.keys().index(self.name) + 1, self.name)
