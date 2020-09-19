from sys import version_info

if version_info.major == 3:
    Py3 = True
    Py2 = False
    
elif version_info.major == 2:
    Py3 = False
    Py2 = True
    
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]