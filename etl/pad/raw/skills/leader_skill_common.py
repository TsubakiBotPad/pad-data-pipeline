from enum import Enum


class ThresholdType(Enum):
    BELOW = '<'
    ABOVE = '>'


class Tag(Enum):
    NO_SKYFALL = '[No Skyfall]'
    BOARD_7X6 = '[Board becomes 7x6]'
    DISABLE_POISON = '[Disable Poison/Mortal Poison effects]'
    FIXED_4S = '[Fixed 4 second movetime]'
    FIXED_5S = '[Fixed 5 second movetime]'
    ERASE_4P = '[Unable to erase 3 orbs or less]'
    ERASE_5P = '[Unable to erase 4 orbs or less]'


class AttributeDict(dict):
    def __getattr__(self, key):
        if key not in self:
            raise AttributeError()
        return self[key]

    __setattr__ = dict.__setitem__
