from collections import defaultdict

from classes.bind import Bind, CustomizedBind
from classes.term import Term


def generate_binding_set(rule):
    return BindingSet(rule)


class BindingSet:
    def __init__(self, rule, aggre = False):
        self.binding_table = {}
        if not aggre:
            for eatom in rule.positive_body:
                if isinstance(eatom.atom, Bind) or isinstance(eatom.atom, CustomizedBind):
                    self.binding_table[eatom.atom.as_var] = []
                else:
                    if Term.verify_type(eatom.atom.subject, "variable"):
                        self.binding_table[eatom.atom.subject] = []
                    if Term.verify_type(eatom.atom.object, "variable"):
                        self.binding_table[eatom.atom.object] = []
        else:
            self.binding_table[rule.aggregation.base_var] = []
            self.binding_table[rule.aggregation.as_var] = []

    def add_line(self, binding):
        """
        :param binding: A Defaultdict
        :return:
        """
        for k in self.binding_table.keys():
            self.binding_table[k].append(binding[k])

    def __len__(self):
        return len(self.binding_table[list(self.binding_table.keys())[0]])

    def __getitem__(self, item):
        return self.binding_table[item]

    def __setitem__(self, key, value):
        self.binding_table[key] = value

    def __delitem__(self, key):
        del self.binding_table[key]

    def print_content(self):
        for var in self.binding_table.keys():
            print(str(var) + ":")
            print(" ".join(str(val) for val in self.binding_table[var]))

