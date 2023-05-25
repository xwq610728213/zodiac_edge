import copy

from classes.bind import Bind, CustomizedBind
from classes.comp import Compare
from classes.extended_atom import EAtom
from classes.term import Term


def calculate_body_hash(body, v_appearance_order, v_join_position):
    hash_str = ""
    b_set = set(body)
    b_iter = 0
    for ea in b_set:
        hash_str += str(hash(ea))
        if isinstance(ea.atom, Bind):
            """
            for ele in ea.atom.reverse_polish_notation:
                if isinstance(ele, Term) and ele.type == "variable":
                    if ele not in v_appearance_order:
                        v_appearance_order.append(ele)
                    index_variable = v_appearance_order.index(ele)
                    if index_variable not in v_join_position:
                        v_join_position[index_variable] = ""
                    v_join_position[index_variable] += str(b_iter) + "|" + str(
                        ea.atom.reverse_polish_notation.index(ele)) + "$"
                if ea.atom.as_var not in v_appearance_order:
                    v_appearance_order.append(ea.atom.as_var)
                index_variable = v_appearance_order.index(ea.atom.as_var)
                if index_variable not in v_join_position:
                    v_join_position[index_variable] = ""
                v_join_position[index_variable] += "|as|" + str(b_iter)
                """
            for ele in ea.atom.var_lst:
                if ele not in v_appearance_order:
                    v_appearance_order.append(ele)
                index_variable = v_appearance_order.index(ele)
                if index_variable not in v_join_position:
                    v_join_position[index_variable] = ""
                v_join_position[index_variable] += str(b_iter) + "|" + str(
                    ea.atom.var_lst.index(ele)) + "$"
                if ea.atom.as_var not in v_appearance_order:
                    v_appearance_order.append(ea.atom.as_var)
                index_variable = v_appearance_order.index(ea.atom.as_var)
                if index_variable not in v_join_position:
                    v_join_position[index_variable] = ""
                v_join_position[index_variable] += "|as|" + str(b_iter)
        elif isinstance(ea.atom, CustomizedBind):
            for ele in ea.atom.func_vars:
                if ele not in v_appearance_order:
                    v_appearance_order.append(ele)
                index_variable = v_appearance_order.index(ele)
                if index_variable not in v_join_position:
                    v_join_position[index_variable] = ""
                v_join_position[index_variable] += str(b_iter) + "|" + str(
                    ea.atom.func_vars.index(ele)) + "$"
                if ea.atom.as_var not in v_appearance_order:
                    v_appearance_order.append(ea.atom.as_var)
                index_variable = v_appearance_order.index(ea.atom.as_var)
                if index_variable not in v_join_position:
                    v_join_position[index_variable] = ""
                v_join_position[index_variable] += "|as|" + str(b_iter)
        elif isinstance(ea.atom, Compare):
            if isinstance(ea.atom.subject,Term) and ea.atom.subject.type == "variable":
                if ea.atom.subject not in v_appearance_order:
                    v_appearance_order.append(ea.atom.subject)
                index_variable = v_appearance_order.index(ea.atom.subject)
                if index_variable not in v_join_position.keys():
                    v_join_position[index_variable] = ""
                v_join_position[index_variable] += str(b_iter) + "s"
            if isinstance(ea.atom.object,Term) and ea.atom.object.type == "variable":
                if ea.atom.object not in v_appearance_order:
                    v_appearance_order.append(ea.atom.object)
                index_variable = v_appearance_order.index(ea.atom.object)
                if index_variable not in v_join_position.keys():
                    v_join_position[index_variable] = ""
                v_join_position[index_variable] += str(b_iter) + "o"
        else:
            if ea.atom.subject.type == "variable":
                if ea.atom.subject not in v_appearance_order:
                    v_appearance_order.append(ea.atom.subject)
                index_variable = v_appearance_order.index(ea.atom.subject)
                if index_variable not in v_join_position.keys():
                    v_join_position[index_variable] = ""
                v_join_position[index_variable] += str(b_iter) + "s"
            if ea.atom.object.type == "variable":
                if ea.atom.object not in v_appearance_order:
                    v_appearance_order.append(ea.atom.object)
                index_variable = v_appearance_order.index(ea.atom.object)
                if index_variable not in v_join_position.keys():
                    v_join_position[index_variable] = ""
                v_join_position[index_variable] += str(b_iter) + "o"

        b_iter += 1
    for index in range(len(v_appearance_order)):
        hash_str += v_join_position[index]
    return hash_str

def calculate_rule_hash(head, positive_body, negative_body, aggregation):


    def reorder_list(list):
        new_list = copy.copy(list)
        for i in range(len(new_list) - 1):
            for j in range(i + 1, len(new_list), 1):
                if hash(new_list[i]) > hash(new_list[j]):
                    new_list[i], new_list[j] = new_list[j], new_list[i]
        return new_list


    positive_body = reorder_list(positive_body)
    negative_body = reorder_list(negative_body)
    v_appearance_order = []
    v_join_position = {}
    hash_str = ""
    hash_str += calculate_body_hash([head], v_appearance_order, v_join_position) + ":-"
    hash_str += calculate_body_hash(positive_body, v_appearance_order, v_join_position)
    hash_str += "||" + calculate_body_hash(negative_body, v_appearance_order, v_join_position)

    if aggregation:
        hash_str += "%%AGGRE(" + str(v_appearance_order.index(aggregation.base_var)) + "," + str(v_appearance_order.index(aggregation.target_var)) + "," + str(v_appearance_order.index(aggregation.as_var)) + "," + aggregation.function + ")"
    return hash(hash_str)


class Rule:
    """
    A rule instance consists of two part: a head (a Positive Atom instance),
    a positive_body (a list of Extended Atom Instances) and a negative_body (a list of Extended Atom Instances)
    """
    def __init__(self, head, positive_body=[], negative_body=[], aggregation = None):
        """
        Args:
            head (an Extended Atom instance): no Window Operator and positive
            positive_body (a list of Extended Atom Instances):
            negative_body (a list of Extended Atom Instances):
            aggregation (An aggregation instance)
        """
        self.head = head
        self.positive_body = positive_body  # a list of Extended Atom Instances
        self.negative_body = negative_body  # a list of Extended Atom Instances
        self.aggregation = aggregation # An Aggregation
        self.hash_code = calculate_rule_hash(self.head, self.positive_body, self.negative_body, self.aggregation)



    def __eq__(self, other):
        if isinstance(other, Rule) and self.hash_code == other.hash_code:
            return True
        else:
            return False

    def __hash__(self):
        return self.hash_code


    def __str__(self):
        return str(self.head) + " :- " + ("AGGREGATE(" if self.aggregation else "") + " and ".join([str(ea) for ea in self.positive_body]) + (" and " if len(self.negative_body) > 0 else "") + " and ".join([str(ea) for ea in self.negative_body]) + ((") ON " + str(self.aggregation.base_var) + " WITH " + self.aggregation.function + "(" + str(self.aggregation.target_var) + ") AS " + str(self.aggregation.as_var)) if self.aggregation else "") + " ."


if __name__ == '__main__':
    list = []
    print("test " + ",".join([str(ea) for ea in list]))
