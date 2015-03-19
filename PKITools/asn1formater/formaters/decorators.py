# Decorator to assign a formater to a class
class UseFor(object):
    def __init__(self, understoodClass):
        self.understoodClass = understoodClass

    def __call__(self, f):
        if (getattr(f, "understoodClasses", None) == None):
            f.understoodClasses = []
        f.understoodClasses += [self.understoodClass]
        return f