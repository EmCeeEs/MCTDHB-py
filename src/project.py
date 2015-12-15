#python3.5
#marcustheisen@web.de

"""MCTDHB project"""
from mctdhb import MCTDHB

class Project(object):
    def __init__(self, name):
        if is_valid(name):
            self.name = name
        else:
            raise TypeError('Name must be of type str!')
        MCTDHB.restore()
    
    @classmethod
    def from_template(cls, temp):
        pass
    
    def save(self):
        pass
    
    def relax(self):
        pass
    
    def propagate(self):
        pass
    
    def properties(self):
        # May be a good Idea to split this command into LR and rest
        pass

def load(name):
    # loads an exsisting net of states!
    pass

def is_valid(name):
    if type(name) is str:
        return True
    else:
        return False
