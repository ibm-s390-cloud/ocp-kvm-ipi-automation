#!/usr/bin/python3

class FilterModule(object):
    '''
    Custom Ansible Jinja2 filter plugin that contains
    various filter helper functions.
    '''

    def filters(self):
        return {
            'atindex': self.atindex,
            'avg': self.avg,
            'get_resources': self.get_resources,
            'all': self.all,
            'cexmode': self.cexmode,
            'parse_version': self.parse_version,
        }

    '''
    Jinja2 filter that returns a specific element from a given list.

    Parameters:
    - input: a list
    - index: the list index for the element that is to be extracted
    '''
    def atindex(self, input, index):
        try:
            return input[index]
        except (TypeError, IndexError):
            return None

    '''
    Jinja2 filter that calculates the average of a list of numbers.

    Parameters:
    - input: a list of numbers
    '''
    def avg(self, input):
        try:
            sum = 0
            for i in input:
                sum = sum + i
            return sum / len(input)
        except (TypeError, IndexError):
            return None

    '''
    Jinja2 filter that extracts the name of a k8s object from a list
    of k8s objects based on the state of that object.

    Parameters:
    - input: a k8s object (usually a dictionary)
    - state: the name of the state that is to be looked up (called 'type' in the k8s resource descriptor)
    - status: the value of the state that is to be looked up (can be multiple values, delimited by "|")
    '''
    def get_resources(self, input, state, status):
        try:
            if '|' in status:
                status = status.split('|')
            out = ""
            conditions = input.get("status").get("conditions")
            cn = [ input.get("metadata").get("name") for c in conditions if c.get("type") == state and c.get("status") in status ]
            if cn and len(cn) > 0:
                out = cn[0]
            return out
        except Exception:
            return ""

    '''
    Jinja2 filter that makes the Python all() function available to Ansible.
    Returns True if all elements of a given list are True (or if the list is empty).

    Parameters:
    - input: a list of boolean values
    '''
    def all(self, input):
        try:
            return all(input)
        except TypeError:
            return None

    '''
    Jinja2 filter that returns a k8s-compatible string of the given crypto resource mode
    of operation.

    Parameters:
    - input: a list of string values
    '''
    def cexmode(self, input):
        try:
            for i in input:
                if i.startswith("EP11"):
                    return "ep11"
                if i.startswith("CCA"):
                    return "cca"
                if i.startswith("Accel"):
                    return "accel"
            return ""
        except Exception:
            return ""

    '''
    Jinja2 filter that returns a dictionary containing the major, minor and micro
    (patch-level) version information parsed from the given input.

    Parameters:
    - input: either a list of string values or a single string value
    '''
    def parse_version(self, input):
        try:
            from packaging.version import parse
            if isinstance(input, list):
                parsed_version = parse(input[0])
            else:
                parsed_version = parse(input)
            out = {
              "major": parsed_version.major,
              "minor": parsed_version.minor,
              "micro": parsed_version.micro,
            }
            return out
        except Exception:
            return None
