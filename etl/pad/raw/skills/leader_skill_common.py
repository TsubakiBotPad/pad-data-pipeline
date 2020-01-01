from enum import Enum


class ThresholdType(Enum):
    BELOW = '<'
    ABOVE = '>'


class Tag():
    NO_SKYFALL = '[No Skyfall]'
    BOARD_7X6 = '[Board becomes 7x6]'
    DISABLE_POISON = '[Disable Poison/Mortal Poison effects]'
    FIXED_TIME = '[Fixed {:d} second movetime]'
    ERASE_P = '[Unable to erase {:d} orbs or less]'

def sort_tags(tags):
    return sorted(tags, key=lambda x: x.value)


class AttributeDict(dict):
    def __getattr__(self, key):
        if key not in self:
            raise AttributeError()
        return self[key]

    __setattr__ = dict.__setitem__
