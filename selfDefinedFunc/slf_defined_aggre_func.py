"""
Attention: Only upper letters and '_' are allowed in a SELF_DEFINED_FUNCTION's name
Input: a list of values
Attention: return object mush be hashable and string-able
"""
import numpy as np

def VARIANCE(lst):
    return np.var(lst)

def VECTORIZE(lst):
    class Vect:
        def __init__(self, vec):
            self.vector = vec
            self.hash_code = hash(str(vec))

        def __str__(self):
            return str(self.vector)

        def __hash__(self):
            return self.hash_code

        def get_content(self):
            return self.vector

    return Vect(np.array(lst))


