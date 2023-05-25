from collections import defaultdict


class ResultSet:
    """
    A ResultSet contains:
        A list of variables
        A list of result lines corresponding to variables in order
    """
    def __init__(self):
        self.variables = []
        self.res = []

    def __str__(self):
        s = ""
        for v in self.variables:
            s += str(v) + "\t"
        s += "\n"
        for line in self.res:
            if isinstance(line, list):
                for value in line:
                    s += str(value) + "\t"
            else:
                s += str(line)
            s += "\n"
        return s


