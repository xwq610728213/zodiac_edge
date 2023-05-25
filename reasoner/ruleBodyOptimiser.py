from classes.bind import Bind, CustomizedBind
from classes.comp import Compare
from classes.term import Term


def compare_priority(e_atom1, e_atom2, data_store):
    """
    :param e_atom1: A Extended Atom
    :param e_atom2: A Extended Atom
    :param data_store: A DataStore
    :return: True if e_atom1 is prior, False otherwise
    """

    def priority(atom, data_store):
        if isinstance(atom, Bind) or isinstance(atom, CustomizedBind):
            return -1
        if isinstance(atom, Compare):
            return -2
        elif data_store.estimate_predicate(atom.predicate) > 0:
            return 3 * (0 if atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" else 1) + (1 if atom.subject.type == "contant" else 0) + (1 if atom.object.type == "contant" else 0)
        else:
            return 0

    p1 = priority(e_atom1.atom, data_store)
    p2 = priority(e_atom2.atom, data_store)
    if p1 == p2:
        if data_store.estimate_predicate(e_atom1.atom.predicate) <= data_store.estimate_predicate(e_atom2.atom.predicate):
            return True
        else:
            return False
    else:
        return True if p1 > p2 else False




def optimise(rules, data_store):
    for rule in rules:
        existing_variables = set()
        for i in range(len(rule.positive_body)):
            if not existing_variables:
                for j in range(i + 1, len(rule.positive_body), 1):
                    if not compare_priority(rule.positive_body[i], rule.positive_body[j], data_store):
                        rule.positive_body[i], rule.positive_body[j] = rule.positive_body[j], rule.positive_body[i]
                if isinstance(rule.positive_body[i].atom, Bind):
                    existing_variables.add(rule.positive_body[i].atom.as_var)
                else:
                    if rule.positive_body[i].atom.subject.type == "variable":
                        existing_variables.add(rule.positive_body[i].atom.subject)
                    if rule.positive_body[i].atom.object.type == "variable":
                        existing_variables.add(rule.positive_body[i].atom.object)
            else:
                for j in range(i + 1, len(rule.positive_body), 1):
                    if (isinstance(rule.positive_body[j].atom, Bind) or isinstance(rule.positive_body[j].atom, CustomizedBind) or ((rule.positive_body[j].atom.subject in existing_variables) or (rule.positive_body[j].atom.object in existing_variables))):
                        if not isinstance(rule.positive_body[i].atom, Bind) and not isinstance(rule.positive_body[i].atom, CustomizedBind) and (rule.positive_body[i].atom.subject not in existing_variables) and (rule.positive_body[i].atom.object not in existing_variables):
                            rule.positive_body[i], rule.positive_body[j] = rule.positive_body[j], rule.positive_body[i]
                        elif not compare_priority(rule.positive_body[i], rule.positive_body[j], data_store):
                            rule.positive_body[i], rule.positive_body[j] = rule.positive_body[j], rule.positive_body[i]

                if isinstance(rule.positive_body[i].atom, Bind) or isinstance(rule.positive_body[i].atom, CustomizedBind):
                    existing_variables.add(rule.positive_body[i].atom.as_var)
                else:
                    if Term.verify_type(rule.positive_body[i].atom.subject, "variable"):
                        existing_variables.add(rule.positive_body[i].atom.subject)
                    if Term.verify_type(rule.positive_body[i].atom.object, "variable"):
                        existing_variables.add(rule.positive_body[i].atom.object)

        for i in range(len(rule.negative_body)):
            if not existing_variables:
                for j in range(i + 1, len(rule.negative_body), 1):
                    if not compare_priority(rule.negative_body[i], rule.negative_body[j], data_store):
                        rule.negative_body[i], rule.negative_body[j] = rule.negative_body[j], rule.negative_body[i]
                if isinstance(rule.positive_body[i].atom, Bind):
                    existing_variables.add(rule.positive_body[i].atom.as_var)
                else:
                    if rule.negative_body[i].atom.subject.type == "variable":
                        existing_variables.add(rule.negative_body[i].atom.subject)
                    if rule.negative_body[i].atom.object.type == "variable":
                        existing_variables.add(rule.negative_body[i].atom.object)
            else:
                for j in range(i + 1, len(rule.negative_body), 1):
                    if ((rule.negative_body[i].atom.subject in existing_variables) or (rule.negative_body[i].atom.object in existing_variables)) and not compare_priority(rule.negative_body[i], rule.negative_body[j], data_store):
                        rule.negative_body[i], rule.negative_body[j] = rule.negative_body[j], rule.negative_body[i]
                if isinstance(rule.positive_body[i].atom, Bind):
                    existing_variables.add(rule.positive_body[i].atom.as_var)
                else:
                    if rule.negative_body[i].atom.subject.type == "variable":
                        existing_variables.add(rule.negative_body[i].atom.subject)
                    if rule.negative_body[i].atom.object.type == "variable":
                        existing_variables.add(rule.negative_body[i].atom.object)


