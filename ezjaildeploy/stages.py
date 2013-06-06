from collections import OrderedDict
from operator import attrgetter


def counter():
    count = 0
    while True:
        yield count
        count += 1


class Step(object):

    __stage__ = None

    def __init__(self, **kwargs):
        self.name = None
        self.id = counter()
        self.kwargs = kwargs

    def command(self, **kwargs):
        NotImplemented

    def __call__(self):
        result = self.command(**self.kwargs)
        return result

    @property
    def _snapshot_name(self):
        step_index = self.__stage__.steps.keys().index(self.name) + 1
        return '{0}-{1:03}-{2}'.format(self.__stage__._snapshot_name, step_index, self.name)


class DecoratorStep(Step):

    def __init__(self, name, func):
        super(DecoratorStep, self).__init__()
        self.name = name
        self.command = func

    def __call__(self):
        result = self.command(self)
        return result


def step(func):
    return DecoratorStep(func.func_name, func)


class MetaStage(type):

    def __init__(cls, name, bases, attrs):
        steps = []
        for n, step in attrs.items():
            if isinstance(step, Step):
                step.name = n
                step.__stage__ = cls
                steps.append(step)
        cls.steps = OrderedDict((step.name, step) for step in sorted(steps, key=attrgetter('id')))
        super(MetaStage, cls).__init__(name, bases, attrs)


class Stage(object):

    __metaclass__ = MetaStage

    __jail__ = None

    def __init__(self, name=None):
        self.name = name

    def __call__(self):
        for step in self.steps.itervalues():
            step()

    @property
    def _snapshot_name(self):
        return '{0:03}-{1}'.format(self.__jail__.stages.keys().index(self.name) + 1, self.name)
