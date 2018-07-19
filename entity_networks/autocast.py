"""
This file contains functions that help perform automatic inference on the command
line parameter passed without calling eval. this is important as it helps avoid
quotes when passing strings as values.

Code modified from code taken from https://github.com/cgreer/cgAutoCast
"""


def boolify(s):

    if s == 'True' or s == 'true' or s == 'Yes' or s == 'yes':
        return True
    if s == 'False' or s == 'false' or s == 'No' or s == 'no':
        return False
    raise ValueError('Not Boolean Value!')


def noneify(s):
    ''' for None type'''
    if s == 'None':
        return None
    raise ValueError('Not None Value!')


def listify(s):
    '''will convert a string representation of a list
    into list of homogenous basic types.  type of elements in
    list is determined via first element and successive
    elements are casted to that type'''

    # this cover everything?
    if "," not in s:
        raise ValueError('Not a List')

    # derive the type of the variable
    loStrings = s.split(',')
    elementCaster = None
    for caster in (boolify, int, float, noneify, str):
        try:
            caster(loStrings[0])
            elementCaster = caster
            break
        except ValueError:
            pass

    # cast all elements
    try:
        castedList = [elementCaster(x) for x in loStrings]
    except ValueError:
        raise TypeError("Autocasted list must be all same type")

    return castedList


def estimateTypedValue(var):
    '''guesses the str representation of the variable's type'''

    # don't need to guess type if it is already un-str typed (not coming from CLI)
    if not isinstance(var, type('aString')):
        return var

    # guess string representation, will default to string if others dont pass
    for caster in (boolify, int, float, noneify, listify, str):
        try:
            return caster(var)
        except ValueError:
            pass
