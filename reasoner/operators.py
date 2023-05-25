import gc
import time
import warnings

import selfDefinedFunc.slf_defined_aggre_func as slf_defined_aggre_func
from collections import defaultdict

from classes.atom import Atom
from classes.bind import Bind, CustomizedBind
from classes.binding_set import BindingSet
from classes.comp import Compare
from classes.extended_atom import EAtom
from classes.rule import Rule
from classes.term import Term
from ruleBodyOptimiser import optimise
from util.parser import parse_data, parse_rules



def evaluate(operator, **kwargs):
    """
    All parameters should be transferred by explicitly indicating the names
    :param operator: an object
    :param kwargs:
    :return:
    """
    if isinstance(operator, Rule):
        return evaluate_rule(rule = operator, **kwargs)
    elif isinstance(operator, EAtom):
        return evaluate_eatom(**kwargs)
    elif isinstance(operator, Compare):
        return evaluate_compare(**kwargs)

def evaluate_compare(bindings, join_eatoms_list, index, data_store, binding_set, **kwargs):
    if not join_eatoms_list[index].w_operator:
        compare_atom = join_eatoms_list[index].atom
        num_s = 0.0
        num_o = 0.0
        str_s = ""
        str_o = ""
        result = False
        """
        try:
            str_s = str(bindings[compare_atom.subject] if compare_atom.subject.type == "variable" and bindings[compare_atom.subject] else compare_atom.subject)
            str_o = str(bindings[compare_atom.object] if compare_atom.object.type == "variable" and bindings[compare_atom.object] else compare_atom.object)
            num_s = float(str_s)
            num_o = float(str_o)
        except:
            if compare_atom.predicate == "=" and str_s == str_o:
                result = True
            elif compare_atom.predicate == "!=" and str_s != str_o:
                result = True
            else:
                return False
        """
        s = bindings[compare_atom.subject] if Term.verify_type(compare_atom.subject, "variable") and bindings[compare_atom.subject] else compare_atom.subject
        o = bindings[compare_atom.object] if Term.verify_type(compare_atom.object, "variable") and bindings[compare_atom.object] else compare_atom.object

        if compare_atom.predicate == ">" and s > o:
            result = True
        elif compare_atom.predicate == ">=" and s >= o:
            result = True
        elif compare_atom.predicate == "=" and s == o:
            result = True
        elif compare_atom.predicate == "!=" and s != o:
            result = True
        elif compare_atom.predicate == "<" and s < o:
            result = True
        elif compare_atom.predicate == "<=" and s <= o:
            result = True


        if result ^ compare_atom.negation:
            if index < len(join_eatoms_list) - 1:
                return evaluate(join_eatoms_list[index + 1], bindings=bindings, join_eatoms_list=join_eatoms_list, index=index + 1, data_store=data_store, binding_set=binding_set, **kwargs)
            else:
                binding_set.add_line(bindings)
                return True
        else:
            return False
    else:
        # To be completed with w_operator
        print("Time operators aren't supported yet!")

def evaluate_bind(bindings, join_eatoms_list, index, data_store, binding_set, **kwargs):
    if not join_eatoms_list[index].w_operator:
        bind_atom = join_eatoms_list[index].atom
        if bind_atom.as_var not in bindings or not bindings[bind_atom.as_var]:
            #Transform execution result to Term
            res = bind_atom.execute(bindings)
            if res:
                bindings[bind_atom.as_var] = Term.getTerm(bind_atom.execute(bindings),'digit')
            else:
                return False
        else:
            if bindings[bind_atom.as_var] != Term.getTerm(bind_atom.execute(bindings),'digit'):
                return False

        if not bindings[bind_atom.as_var]:
            return False
        if index < len(join_eatoms_list) - 1:
            evaluate(join_eatoms_list[index + 1], bindings=bindings, join_eatoms_list=join_eatoms_list, index=index + 1, data_store=data_store, binding_set=binding_set, **kwargs)
        else:
            binding_set.add_line(bindings)
        bindings[bind_atom.as_var] = False

    else:
        # To be completed with w_operator
        print("Time operators aren't supported yet!")

def evaluate_atom(bindings, join_eatoms_list, index, data_store, binding_set, **kwargs):
    query_atom = join_eatoms_list[index].atom

    tp_s = bindings[query_atom.subject] if Term.verify_type(query_atom.subject, "variable") and bindings[
        query_atom.subject] else query_atom.subject
    tp_p = query_atom.predicate
    tp_o = bindings[query_atom.object] if Term.verify_type(query_atom.object, "variable") and bindings[
        query_atom.object] else query_atom.object

    #If it is the incremental eatom, search in incre_db, otherwise search in data_store
    rs = None
    if "incre_eatom" not in kwargs or join_eatoms_list[index] != kwargs['incre_eatom']:
        rs = data_store.query(tp_s, tp_p, tp_o)
    else:
        if kwargs['incre_db']:
            rs = kwargs['incre_db'].query(tp_s, tp_p, tp_o)


    if bool(rs) ^ query_atom.negation:
        if index < len(join_eatoms_list) - 1:
            if isinstance(rs, bool) or (query_atom.negation and not rs):
                return evaluate(join_eatoms_list[index + 1], bindings=bindings, join_eatoms_list=join_eatoms_list,
                                index=index + 1, data_store=data_store, binding_set=binding_set, **kwargs)
            else:
                for temp_binding_line in rs.res:
                        for i in range(len(rs.variables)):
                            bindings[rs.variables[i]] = temp_binding_line[i]
                        evaluate(join_eatoms_list[index + 1], bindings=bindings, join_eatoms_list=join_eatoms_list,
                                 index=index + 1, data_store=data_store, binding_set=binding_set, **kwargs)

                for i in range(len(rs.variables)):
                    bindings[rs.variables[i]] = False
                return True
        else:
            if isinstance(rs, bool) or (query_atom.negation and not rs):
                binding_set.add_line(bindings)
            else:
                for temp_binding_line in rs.res:
                    for i in range(len(rs.variables)):
                        bindings[rs.variables[i]] = temp_binding_line[i]
                    binding_set.add_line(bindings)
                for i in range(len(rs.variables)):
                    bindings[rs.variables[i]] = False
            return True


def evaluate_rule(rule, data_store, **kwargs):
    join_eatoms_list = rule.positive_body + rule.negative_body
    #If incremental, set incre_eatom to first
    if "incre_eatom" in kwargs and kwargs["incre_eatom"]:
        incre_eatom = kwargs['incre_eatom']
        ind = None
        for i in range(len(join_eatoms_list)):
            if str(join_eatoms_list[i]) == str(incre_eatom):
                ind = i
                break
        join_eatoms_list.pop(ind)
        join_eatoms_list.insert(0, incre_eatom)
    #print("Rule order: " + " and ".join(str(ele) for ele in join_eatoms_list))
    if not rule.aggregation:
        binding_set = BindingSet(rule)
        if "bindings" not in kwargs:
            evaluate(operator = join_eatoms_list[0], bindings = defaultdict(bool), join_eatoms_list = join_eatoms_list, index = 0, data_store = data_store, binding_set = binding_set, **kwargs)
        else:
            evaluate(operator=join_eatoms_list[0], join_eatoms_list=join_eatoms_list, index=0, data_store=data_store, binding_set=binding_set, **kwargs)
        return binding_set
    else:
        binding_set = BindingSet(rule)
        func = None

        if not (rule.aggregation.function == "MAX" or rule.aggregation.function == "MIN" or rule.aggregation.function == "AVG" or rule.aggregation.function == "SUM" or rule.aggregation.function == "MED" or rule.aggregation.function == "COUNT"):
            try:
                func = getattr(slf_defined_aggre_func, rule.aggregation.function)
            except:
                warnings.warn("Function " + rule.aggregation.function + " not defined in selfDefinedFunc.slf_defined_aggre_func!")
                return binding_set


        bindings = None
        if "bindings" not in kwargs:
            evaluate(operator=join_eatoms_list[0], bindings=defaultdict(bool), join_eatoms_list=join_eatoms_list, index=0, data_store=data_store, binding_set=binding_set, **kwargs)
        else:
            evaluate(operator=join_eatoms_list[0], join_eatoms_list=join_eatoms_list, index=0, data_store=data_store, binding_set=binding_set, **kwargs)

        #binding_set.print_content()

        var_index_map = {}
        index_var_map = {}
        count = 0
        for var in binding_set.binding_table.keys():
            var_index_map[var] = count
            index_var_map[count] = var
            count += 1

        value_set = set()
        for index in range(len(binding_set)):
            line = []
            for var_index in range(count):
                line.append(binding_set[index_var_map[var_index]][index])
            value_set.add(tuple(line))

        base_target_map = defaultdict(list)
        for line in value_set:
            base_target_map[line[var_index_map[rule.aggregation.base_var]]].append(line[var_index_map[rule.aggregation.target_var]])
        aggre_binding_set = BindingSet(rule, aggre=True)

        def median(lst):
            n = len(lst)
            digit_lst = []
            for ele in lst:
                digit_lst.append(ele)
            s = sorted(digit_lst)
            return (s[n // 2 - 1] / 2.0 + s[n // 2] / 2.0, s[n // 2])[n % 2] if n else None

        for base in base_target_map.keys():
            aggre_binding_set[rule.aggregation.base_var].append(base)
            if rule.aggregation.function == "MAX":
                aggre_binding_set[rule.aggregation.as_var].append(max(base_target_map[base]))
            elif rule.aggregation.function == "MIN":
                aggre_binding_set[rule.aggregation.as_var].append(min(base_target_map[base]))
            elif rule.aggregation.function == "SUM":
                aggre_binding_set[rule.aggregation.as_var].append(sum(base_target_map[base]))
            elif rule.aggregation.function == "AVG":
                aggre_binding_set[rule.aggregation.as_var].append(sum(base_target_map[base])/len(base_target_map[base]))
            elif rule.aggregation.function == "MED":
                aggre_binding_set[rule.aggregation.as_var].append(median(base_target_map[base]))
            elif rule.aggregation.function == "COUNT":
                aggre_binding_set[rule.aggregation.as_var].append(len(base_target_map[base]))
            else:
                aggre_binding_set[rule.aggregation.as_var].append(func(base_target_map[base]))

        # To be modified, a bug here when head's variables are not base_variable// Fixed
        if rule.head.atom.subject != rule.aggregation.base_var and rule.head.atom.subject != rule.aggregation.as_var:
            aggre_map = defaultdict(bool)
            for i in range(len(aggre_binding_set[rule.aggregation.base_var])):
                aggre_map[aggre_binding_set[rule.aggregation.base_var][i]] = aggre_binding_set[rule.aggregation.as_var][i]

            binding_set.binding_table[rule.aggregation.as_var] = []
            for base_var_binding in binding_set.binding_table[rule.aggregation.base_var]:
                binding_set.binding_table[rule.aggregation.as_var].append(aggre_map[base_var_binding])

            return binding_set
        else:
            return aggre_binding_set



def evaluate_eatom(bindings, join_eatoms_list, index, data_store, binding_set, **kwargs):
    """
    :param bindings: A Defaultdict
    :param join_eatoms_list: A list of Extended Atoms
    :param index: current execution index of join_eatoms_list
    :param data_store: A DataStore
    :param binding_set: Final result BindingSet
    :return:
    """
    if not join_eatoms_list[index].w_operator:
        if isinstance(join_eatoms_list[index].atom, Atom):
            return evaluate_atom(bindings, join_eatoms_list, index, data_store, binding_set, **kwargs)
        elif isinstance(join_eatoms_list[index].atom, Compare):
            return evaluate_compare(bindings, join_eatoms_list, index, data_store, binding_set, **kwargs)
        elif isinstance(join_eatoms_list[index].atom, Bind) or isinstance(join_eatoms_list[index].atom, CustomizedBind):
            return evaluate_bind(bindings, join_eatoms_list, index, data_store, binding_set, **kwargs)
        """
        query_atom = join_eatoms_list[index].atom

        tp_s = bindings[query_atom.subject] if query_atom.subject.type == "variable" and bindings[query_atom.subject] else query_atom.subject
        tp_p = query_atom.predicate
        tp_o = bindings[query_atom.object] if query_atom.object.type == "variable" and bindings[query_atom.object] else query_atom.object

        rs = data_store.query(tp_s, tp_p, tp_o)

        if bool(rs) ^ query_atom.negation:
            if index < len(join_eatoms_list) - 1:
                if isinstance(rs, bool):
                    return evaluate(join_eatoms_list[index + 1], bindings=bindings, join_eatoms_list=join_eatoms_list, index=index + 1, data_store=data_store, binding_set=binding_set)
                else:
                    for temp_binding_line in rs.res:
                        for i in range(len(rs.variables)):
                            bindings[rs.variables[i]] = temp_binding_line[i]
                        evaluate(join_eatoms_list[index + 1], bindings=bindings, join_eatoms_list=join_eatoms_list, index=index + 1, data_store=data_store, binding_set=binding_set)

                    for i in range(len(rs.variables)):
                        bindings[rs.variables[i]] = False
                    return True
            else:
                for temp_binding_line in rs.res:
                    for i in range(len(rs.variables)):
                        bindings[rs.variables[i]] = temp_binding_line[i]
                    binding_set.add_line(bindings)
                for i in range(len(rs.variables)):
                    bindings[rs.variables[i]] = False
                return True
        """

    else:
        #To be completed with w_operator
        print("Time operators aren't supported yet!")


def main():

    f = open("/Users/RC5920/Documents/LUBM_generator/nt_data/univ0.nt", "r")
    rf = open("/testData/LUBM_rule.rules", "r")

    """
    f = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/testData.nt", "r")
    rf = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/testData_rules.rules", "r")
    """

    D = parse_data(f)
    R = parse_rules(rf)
    optimise(R, D)
    for r in R:
        binding_set = BindingSet(r)
        start_time = time.time()
        evaluate(r, data_store = D, binding_set = binding_set)
        print("Evaluate rule: " + str(r) + " time " + str(time.time() - start_time) + " size: " + str(len(binding_set)))
        s = str()
        for v in binding_set.binding_table.keys():
            s += str(v) + " "
        print(s)
        for i in range(min(10, len(binding_set))):
            s = str()
            for v in binding_set.binding_table.keys():
                s += str(binding_set[v][i]) + " "
            print(s)
        print("end")

    gc.collect()
    print("sqdf")


if __name__ == "__main__":
    main()