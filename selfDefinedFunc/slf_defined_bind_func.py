"""
Attention: Only upper letters and '_' are allowed in a SELF_DEFINED_FUNCTION's name
Input: some digital args
Attention: return object mush be hashable and string-able
"""
import numpy as np

def BIND_EXAMPLE(ele1):
    return ele1 + 1

def BIND_EXAMPLE2(ele1, ele2):
    return ele1 + ele2

def BIND_VARIANCE(ele):
    return np.var(ele.get_content())