from enum import Enum


class ThresholdType(Enum):
    BELOW = '<'
    ABOVE = '>'


class Tag(Enum):  
    NO_SKYFALL = 0
    BOARD_7X6 = 1
    DISABLE_POISON = 2
    FIXED_TIME = 3
    ERASE_P = 4

def sort_tags(tags):
    return sorted(tags, key=lambda x: x.value)


class AttributeDict(dict):
    def __getattr__(self, key):
        if key not in self:
            raise AttributeError()
        return self[key]

    __setattr__ = dict.__setitem__
