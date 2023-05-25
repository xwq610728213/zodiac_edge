import re
import string
import warnings

import selfDefinedFunc.slf_defined_bind_func as slf_defined_bind_func

from classes.term import Term


def parse_expression(expression):
    variable_map = {}
    temp_ele = str("")
    priority = {"(": 3, "*": 2, "/": 2, "+": 1, "-": 1, ")": 0}
    st_num = []
    st_symbol = []
    for char in expression:
        if char in priority:
            if len(temp_ele) > 0:
                if temp_ele.isdigit():
                    st_num.append(string.atof(temp_ele))
                else:
                    t = Term(temp_ele, "variable")
                    st_num.append(t)
                    variable_map[t] = len(st_num) - 1
                temp_ele = str("")
            if len(st_symbol) == 0:
                st_symbol.append(char)
            else:
                if char == "(":
                    st_symbol.append(char)
                elif char == ")":
                    while len(st_symbol) > 0 and st_symbol[-1] != "(":
                        st_num.append(st_symbol.pop())
                    if len(st_symbol) > 0:
                        st_symbol.pop()
                    else:
                        print("Expression syntax error!")
                        return False
                elif priority[st_symbol[-1]] < priority[char]:
                    st_symbol.append(char)
                else:
                    while len(st_symbol) != 0:
                        if st_symbol[-1] == "(":
                            break
                        st_num.append(st_symbol.pop())
                    st_symbol.append(char)
        elif char == " " or char == "\t":
            if len(temp_ele) > 0:
                if temp_ele.isdigit():
                    st_num.append(string.atof(temp_ele))
                else:
                    t = Term(temp_ele, "variable")
                    st_num.append(t)
                    variable_map[t] = len(st_num) - 1
                temp_ele = str("")
        else:
            temp_ele += char



    if len(temp_ele) > 0:
        st_num.append(string.atof(temp_ele))
        temp_ele = str("")

    while st_symbol:
        st_num.append(st_symbol.pop())

    return st_num, variable_map

class ExecEnv:
    def __init__(self, bindings):
        self.__dict__.update(bindings)

    def execute(self, expression):
        return eval(expression)

class Bind:
    def __init__(self, expression, as_var):
        self.original_expression = expression.replace(" ", "")
        self.as_var = as_var
        self.negation = False
        self.var_lst = []

        ele_lst = re.split("[()+\-*/]*", self.original_expression)

        pattern = re.compile(r"[A-Z][A-Z_0-9]*\s*$|\?[A-Za-z][A-Za-z_0-9]*\s*$")

        for ele in ele_lst:
            if pattern.match(ele):
                self.var_lst.append(Term.getTerm(ele, "variable"))

        var_map = {}

        var_count = 0
        for var in self.var_lst:
            if var not in var_map:
                var_map[var] = "var_" + str(var_count)
                var_count += 1

        hash_str = self.original_expression
        for var in var_map.keys():
            hash_str = hash_str.replace(str(var),var_map[var])

        if self.as_var not in var_map:
            var_map[self.as_var] = "var_" + str(var_count)
            var_count += 1
            #self.var_lst.append(self.as_var)
        hash_str = "Bind:(" + hash_str + " AS " + str(self.as_var) + ")"
        self.hash_code = hash(hash_str)

    def execute(self, bindings):
        try:
            b = {}
            for k in bindings.keys():
                if k in self.var_lst:
                    b[str(k)] = bindings[k]
            #env = ExecEnv(b)
            return eval(self.original_expression,globals(),b )

        except:
            warnings.warn("Execution error: " + self.original_expression)
            return False


    def __hash__(self):
        return self.hash_code

    def __eq__(self, other):
        if isinstance(other, Bind) and self.hash_code == other.hash_code:
            return True
        else:
            return False


    def __str__(self):
        return "BIND(" + self.original_expression + " AS " + str(self.as_var) + ")"

"""
class Bind:
    def __init__(self, expression, as_var):
        self.original_expression = expression.strip(" ")
        self.reverse_polish_notation, self.variables_index_map = parse_expression(expression)
        self.as_var = as_var
        self.negation = False
        hash_str = "Bind:("
        var_count_map = {}
        var_count = 0
        for ele in self.reverse_polish_notation:
            if isinstance(ele, Term) and ele.type == "variable":
                if ele not in var_count_map:
                    var_count_map[ele] = var_count
                    var_count += 1
                hash_str += "var_" + str(var_count_map[ele])
            else:
                hash_str += str(ele)
            hash_str += "%"
        hash_str += "as%"
        if as_var not in var_count_map:
            var_count_map[as_var] = var_count
            var_count += 1
        hash_str += "var_" + str(var_count_map[as_var])
        self.hash_code = hash(hash_str)

    def execute(self, bindings):
        exec_stack = []
        for ele in self.reverse_polish_notation:
            if isinstance(ele, float) or isinstance(ele, int):
                exec_stack.append(ele)
            elif isinstance(ele, Term) and ele.type == "variable":
                if ele in bindings:
                    exec_stack.append(string.atof(bindings[ele].name))
                else:
                    print("Can't find variable " + str(ele) + " in bindings!")
                    return False
            else:
                if ele == "+":
                    num_2 = exec_stack.pop()
                    num_1 = exec_stack.pop()
                    exec_stack.append(num_1 + num_2)
                elif ele == "-":
                    num_2 = exec_stack.pop()
                    num_1 = exec_stack.pop()
                    exec_stack.append(num_1 - num_2)
                elif ele == "*":
                    num_2 = exec_stack.pop()
                    num_1 = exec_stack.pop()
                    exec_stack.append(num_1 * num_2)
                elif ele == "/":
                    num_2 = exec_stack.pop()
                    num_1 = exec_stack.pop()
                    exec_stack.append(num_1 / num_2)

        return exec_stack[0]


    def __hash__(self):
        return self.hash_code

    def __eq__(self, other):
        if isinstance(other, Bind) and self.hash_code == other.hash_code:
            return True
        else:
            return False


    def __str__(self):
        return "BIND(" + self.original_expression + " AS " + str(self.as_var) + ")"
"""

class CustomizedBind:
    def __init__(self, expression, as_var):
        self.negation = False
        self.original_expression = expression
        self.as_var = as_var
        self.func = None

        pattern = re.compile(r"\s*func\s*:\s*(?P<func_name>[^\s]+)\s*\(\s*(?P<var_str>.+)\s*\)\s*", re.I)
        res = pattern.match(expression)
        if not res:
            warnings.warn("Self-defined-bind-function: " + expression + " syntax error!")

        try:
            func_name = res.group("func_name").upper()
            self.func = getattr(slf_defined_bind_func, func_name)
            self.func_vars = map(lambda x : Term.getTerm(x.strip(), "variable"), res.group("var_str").split(','))
        except:
            warnings.warn("Function: " + res.group("func_name") + " not defined in selfDefinedFunc.slf_defined_bind_func!")
            return

        hash_str = "Bind:("
        hash_str += "func:" + res.group("func_name") + ":"
        var_count_map = {}
        var_count = 0
        for var in self.func_vars:
            if var not in var_count_map:
                var_count_map[var] = var_count
                var_count += 1
            hash_str += "var_" + str(var_count_map[var])
            hash_str += "%"
        hash_str += "as%"
        if as_var not in var_count_map:
            var_count_map[as_var] = var_count
            var_count += 1
        hash_str += "var_" + str(var_count_map[as_var])
        self.hash_code = hash(hash_str)



    def execute(self, bindings):
        if self.func:
            args = tuple(bindings[var] for var in self.func_vars)
            try:
                return self.func(*args)
            except Exception as inst:
                warnings.warn(inst)
                return None
        else:
            return None

    def __hash__(self):
        return self.hash_code

    def __eq__(self, other):
        if isinstance(other, Bind) and self.hash_code == other.hash_code:
            return True
        else:
            return False

    def __str__(self):
        return "BIND(" + self.original_expression + " AS " + str(self.as_var) + ")"



def main():
    pattern = re.compile(r"(?P<bind>bind)\s*\(\s*(?P<expression>.*)\s+as\s+(?P<as_var>[^\s]*)\s*\)\s*", re.I)
    str = "bind(func:bind_EXAMPLE(G) as Y) "
    res = pattern.match(str)
    if res.group("bind"):
        print(res.group("expression"))

    s = "1- ?Y*( X_3 -Z1_3) +4"
    res, v_map = parse_expression(s)
    for ele in res:
        print(ele)
    print(v_map)

if __name__ == "__main__":
    main()