#!/usr/bin/python3

class TestModule(object):
    '''
    Custom Ansible Jinja2 test plugin that contains
    various test helper functions.
    '''

    def tests(self):
        return {
            'startswith': self.startswith,
            'contains': self.contains,
            'isrange': self.isrange,
            'inlist': self.inlist,
        }

    '''
    Jinja2 test that checks if a given input string starts with another string,
    basically making Python's str.startswith() function available
    to the Jinja2 templating engine.

    Parameters:
    - input: the string that is to be checked if it starts with a given value
    - value: the string that input will be checked against
    '''
    def startswith(self, input, value):
        try:
            return input.startswith(value)
        except TypeError:
            return False

    '''
    Jinja2 test that checks if a given input string contains another string,
    basically making Python's '(str) in (str)' function available
    to the Jinja2 templating engine.

    Parameters:
    - input: the string that is to be checked if it contains a given value
    - value: the string that input will be checked against
    '''
    def contains(self, input, value):
        try:
            return value in input
        except TypeError:
            return False

    '''
    Jinja2 test that checks if a given input list of integer values
    is a consecutive range starting with the given start value.

    Parameters:
    - input: the list of integers that is to be checked if it is a consecutive range of integers
    - start: the start index of the range, defaults to 0
    '''
    def isrange(self, input, start=0):
        try:
            return sorted(input) == list(range(start, max(input) + 1))
        except TypeError:
            return False

    '''
    Jinja2 test that checks if a given input string is member of a given list of values.

    Parameters:
    - input: the string that is to be checked if it is a member of a list of values
    - values: the list of values that input will be checked against
    '''
    def inlist(self, input, values):
        try:
            return input in values
        except TypeError:
            return False
