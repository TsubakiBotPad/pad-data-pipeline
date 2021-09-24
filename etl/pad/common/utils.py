import unicodedata
from typing import List


def remove_diacritics(input: str) -> str:
    """
    Return the base character of char, by "removing" any
    diacritics like accents or curls and strokes and the like.
    """
    output = ''
    for c in input:
        try:
            desc = unicodedata.name(c)
            cutoff = desc.find(' WITH ')
            if cutoff != -1:
                desc = desc[:cutoff]
            output += unicodedata.lookup(desc)
        except:
            output += c
    return output


def format_int_list(values: List[int]) -> str:
    return ','.join(['({})'.format(x) for x in values])


class classproperty(property):
    def __get__(self, *args, **kwargs):
        return classmethod(self.fget).__get__(None, args[1])()
