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
