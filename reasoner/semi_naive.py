import time
import warnings
from collections import defaultdict

from classes.atom import Atom
from classes.datastore import DataStore, IncrementalDataStore
from classes.term import Term
from reasoner.operators import evaluate
from util.parser import parse_data, parse_rules


def generate_idb(rules, data_store, last_idb = None, incremental_operation = None, incre_idb = None, neg_flushed_db = None, deleting_data = False, hn_edb = None, hn_idb = None, deleting_visited_triples = None):
    """
    One iteration of semi naive
    :param rules:
    :param data_store:
    :param incremental_operation:
    :param original_idb:
    :return:
    """

    if not incremental_operation:
        idb = DataStore()
        if not last_idb:
            for rule in rules:
                bs = evaluate(rule, data_store = data_store)
                predicate = rule.head.atom.predicate
                sv = rule.head.atom.subject if rule.head.atom.subject.type == "variable" else False
                ov = rule.head.atom.object if rule.head.atom.object.type == "variable" else False
                subject = rule.head.atom.subject
                object = rule.head.atom.object
                for i in range(len(bs)):
                    if sv:
                        subject = bs[sv][i]
                    if ov:
                        object = bs[ov][i]
                    idb.add(subject, predicate, object)

            return idb
        else:
            for rule in rules:
                for eatom in rule.positive_body:
                    if isinstance(eatom.atom, Atom):

                        bs = evaluate(rule, data_store=data_store, incre_eatom=eatom, incre_db=last_idb)
                        predicate = rule.head.atom.predicate
                        sv = rule.head.atom.subject if rule.head.atom.subject.type == "variable" else False
                        ov = rule.head.atom.object if rule.head.atom.object.type == "variable" else False
                        subject = rule.head.atom.subject
                        object = rule.head.atom.object
                        for i in range(len(bs)):
                            if sv:
                                subject = bs[sv][i]
                            if ov:
                                object = bs[ov][i]
                            """
                            if incre_neg_idb.query(subject, predicate, object):
                                incre_neg_idb.remove(subject, predicate, object)
                            else:
                                incre_pos_idb.add(subject, predicate, object)
                            """
                            idb.add(subject, predicate, object)

                        """
                        bs = evaluate(rule, data_store=data_store, incre_eatom=eatom, incre_db=incre_idb.negative_ds)
                        predicate = rule.head.atom.predicate
                        sv = rule.head.atom.subject if rule.head.atom.subject.type == "variable" else False
                        ov = rule.head.atom.object if rule.head.atom.object.type == "variable" else False
                        subject = rule.head.atom.subject
                        object = rule.head.atom.object
                        for i in range(len(bs)):
                            if sv:
                                subject = bs[sv][i]
                            if ov:
                                object = bs[ov][i]
                            incre_neg_idb.add(subject, predicate, object)
                        """
            return idb
    #In case of incremental operation
    else:
        incre_neg_idb = DataStore()
        incre_pos_idb = DataStore()
        new_incre_ds = IncrementalDataStore()
        verified_incre_neg_idb = DataStore()

        #not_verified_incre_neg_idb = DataStore()

        if not incre_idb:
            warnings.warn("An original IDB must be provided when doing incremental operation")
            return None
        """
        if isinstance(incre_idb, IncrementalDataStore) and incre_idb.not_verified_negative_ds:
            incre_neg_idb += incre_idb.not_verified_negative_ds
        """


        for rule in rules:
            if rule.aggregation:
                base_var_binding_set = set()

                for eatom in rule.positive_body:
                    if isinstance(eatom.atom, Atom):
                        # To be modified
                        bs = evaluate(rule, data_store=data_store, incre_eatom=eatom, incre_db=incre_idb.positive_ds)
                        for i in range(len(bs)):
                            base_var_binding_set.add(bs[rule.aggregation.base_var][i])

                        bs = evaluate(rule, data_store=data_store + incre_idb.negative_ds, incre_eatom=eatom, incre_db=incre_idb.negative_ds)
                        predicate = rule.head.atom.predicate
                        sv = rule.head.atom.subject if rule.head.atom.subject.type == "variable" else False
                        ov = rule.head.atom.object if rule.head.atom.object.type == "variable" else False
                        subject = rule.head.atom.subject
                        object = rule.head.atom.object
                        for i in range(len(bs)):
                            base_var_binding_set.add(bs[rule.aggregation.base_var][i])
                            if sv:
                                subject = bs[sv][i]
                            if ov:
                                object = bs[ov][i]
                            v_o = Term.getTerm("X", "variable")
                            rs = data_store.query(subject, predicate, v_o)
                            if rs:
                                verified_incre_neg_idb.add(subject, predicate, rs.res[0][0])
                                #incre_neg_idb.add(subject, predicate, rs.res[0][0])

                for eatom in rule.negative_body:
                    if isinstance(eatom.atom, Atom):
                        # Negation to positive when incremental
                        eatom.atom.negation = False

                        bs = evaluate(rule, data_store=data_store, incre_eatom=eatom, incre_db=incre_idb.negative_ds)
                        # Recover to original rule
                        eatom.atom.negation = True

                        for i in range(len(bs)):
                            base_var_binding_set.add(bs[rule.aggregation.base_var][i])


                        # Negation to positive when incremental
                        eatom.atom.negation = False



                        bs = evaluate(rule, data_store=data_store + incre_idb.negative_ds, incre_eatom=eatom, incre_db=incre_idb.positive_ds)

                        # Recover to original rule
                        eatom.atom.negation = True

                        predicate = rule.head.atom.predicate
                        sv = rule.head.atom.subject if rule.head.atom.subject.type == "variable" else False
                        ov = rule.head.atom.object if rule.head.atom.object.type == "variable" else False
                        subject = rule.head.atom.subject
                        object = rule.head.atom.object
                        for i in range(len(bs)):
                            base_var_binding_set.add(bs[rule.aggregation.base_var][i])
                            if sv:
                                subject = bs[sv][i]
                            if ov:
                                object = bs[ov][i]
                            v_o = Term.getTerm("X", "variable")
                            rs = data_store.query(subject, predicate, v_o)
                            if rs:
                                verified_incre_neg_idb.add(subject, predicate, rs.res[0][0])
                                #incre_neg_idb.add(subject, predicate, rs.res[0][0])

                bindings = defaultdict(bool)

                for value in base_var_binding_set:
                    bindings[rule.aggregation.base_var] = value
                    bs = evaluate(rule, data_store=neg_flushed_db, bindings = bindings)
                    predicate = rule.head.atom.predicate
                    sv = rule.head.atom.subject if rule.head.atom.subject.type == "variable" else False
                    ov = rule.head.atom.object if rule.head.atom.object.type == "variable" else False
                    subject = rule.head.atom.subject
                    object = rule.head.atom.object
                    for i in range(len(bs)):
                        if sv:
                            subject = bs[sv][i]
                        if ov:
                            object = bs[ov][i]
                        incre_pos_idb.add(subject, predicate, object)

                        v_o = Term.getTerm("X", "variable")
                        rs = neg_flushed_db.query(subject, predicate, v_o)
                        if rs:
                            if str(rs.res[0][0]) != str(object):
                                verified_incre_neg_idb.add(subject, predicate, rs.res[0][0])
                                #incre_neg_idb.add(subject, predicate, rs.res[0][0])
                            else:
                                verified_incre_neg_idb.remove(subject, predicate, rs.res[0][0])
                                #incre_neg_idb.remove(subject, predicate, rs.res[0][0])
                                incre_pos_idb.remove(subject, predicate, object)


                #A bug to be fixed
                """
                bs = evaluate(rule, data_store=data_store)
                predicate = rule.head.atom.predicate
                sv = rule.head.atom.subject if rule.head.atom.subject.type == "variable" else False
                ov = rule.head.atom.object if rule.head.atom.object.type == "variable" else False
                subject = rule.head.atom.subject
                object = rule.head.atom.object
                for i in range(len(bs)):
                    if sv:
                        subject = bs[sv][i]
                    if ov:
                        object = bs[ov][i]
                    incre_pos_idb.add(subject, predicate, object)
                    v_o = Term.getTerm("X", "variable")
                    rs = data_store.query(subject, predicate, v_o)
                    if rs and str(rs.res[0][0]) != str(object):
                        verified_incre_neg_idb.add(subject, predicate, rs.res[0][0])
                """
            else:
                for eatom in rule.positive_body:
                    if isinstance(eatom.atom, Atom):

                        bs = evaluate(rule, data_store=data_store, incre_eatom = eatom, incre_db = incre_idb.positive_ds)
                        predicate = rule.head.atom.predicate
                        sv = rule.head.atom.subject if rule.head.atom.subject.type == "variable" else False
                        ov = rule.head.atom.object if rule.head.atom.object.type == "variable" else False
                        subject = rule.head.atom.subject
                        object = rule.head.atom.object
                        for i in range(len(bs)):
                            if sv:
                                subject = bs[sv][i]
                            if ov:
                                object = bs[ov][i]
                            """
                            if incre_neg_idb.query(subject, predicate, object):
                                incre_neg_idb.remove(subject, predicate, object)
                            else:
                                incre_pos_idb.add(subject, predicate, object)
                            """
                            incre_pos_idb.add(subject, predicate, object)

                        bs = evaluate(rule, data_store=data_store, incre_eatom = eatom, incre_db = incre_idb.negative_ds)
                        predicate = rule.head.atom.predicate
                        sv = rule.head.atom.subject if rule.head.atom.subject.type == "variable" else False
                        ov = rule.head.atom.object if rule.head.atom.object.type == "variable" else False
                        subject = rule.head.atom.subject
                        object = rule.head.atom.object
                        for i in range(len(bs)):
                            if sv:
                                subject = bs[sv][i]
                            if ov:
                                object = bs[ov][i]
                            """
                            if isinstance(eatom.atom, Atom) and eatom.atom.predicate.aggregation_property:
                                if not incre_pos_idb.query(subject, predicate, object):
                                    incre_neg_idb.add(subject, predicate, object)
                            else:
                                incre_neg_idb.add(subject, predicate, object)
                            """
                            incre_neg_idb.add(subject, predicate, object)



                for eatom in rule.negative_body:
                    if isinstance(eatom.atom, Atom):
                        #Negation to positive when incremental
                        eatom.atom.negation = False


                        bs = evaluate(rule, data_store=data_store, incre_eatom=eatom, incre_db=incre_idb.negative_ds)

                        # Recover to original rule
                        eatom.atom.negation = True

                        predicate = rule.head.atom.predicate
                        sv = rule.head.atom.subject if rule.head.atom.subject.type == "variable" else False
                        ov = rule.head.atom.object if rule.head.atom.object.type == "variable" else False
                        subject = rule.head.atom.subject
                        object = rule.head.atom.object
                        for i in range(len(bs)):
                            if sv:
                                subject = bs[sv][i]
                            if ov:
                                object = bs[ov][i]
                            incre_pos_idb.add(subject, predicate, object)

                        # Negation to positive when incremental
                        eatom.atom.negation = False



                        bs = evaluate(rule, data_store=data_store, incre_eatom = eatom, incre_db = incre_idb.positive_ds)

                        # Recover to original rule
                        eatom.atom.negation = True

                        predicate = rule.head.atom.predicate
                        sv = rule.head.atom.subject if rule.head.atom.subject.type == "variable" else False
                        ov = rule.head.atom.object if rule.head.atom.object.type == "variable" else False
                        subject = rule.head.atom.subject
                        object = rule.head.atom.object
                        for i in range(len(bs)):
                            if sv:
                                subject = bs[sv][i]
                            if ov:
                                object = bs[ov][i]

                            incre_neg_idb.add(subject, predicate, object)


                # Backward verification of incre_neg_idb
                if deleting_visited_triples != None:
                    if incre_neg_idb and len(incre_neg_idb) > 0:
                        predicate = rule.head.atom.predicate
                        if predicate in incre_neg_idb.predicate_tuples:
                            #bindings = defaultdict(bool)
                            for subject, object in incre_neg_idb.predicate_tuples[predicate]:
                                if not backward_verification(subject, predicate, object, hn_edb, hn_idb, rules, deleting_visited_triples, neg_flushed_db):
                                    # if True:
                                    verified_incre_neg_idb.add(subject, predicate, object)
                else:
                    if incre_neg_idb and len(incre_neg_idb) > 0:
                        predicate = rule.head.atom.predicate
                        if predicate in incre_neg_idb.predicate_tuples:
                            bindings = defaultdict(bool)
                            for subject, object in incre_neg_idb.predicate_tuples[predicate]:
                                if rule.head.atom.subject.type == "variable":
                                    bindings[rule.head.atom.subject] = subject
                                if rule.head.atom.object.type == "variable":
                                    bindings[rule.head.atom.object] = object
                                bs = evaluate(rule, data_store = neg_flushed_db, bindings = bindings)

                                if not bs:
                                #if True:
                                    verified_incre_neg_idb.add(subject, predicate, object)

                                #else:
                                #    not_verified_incre_neg_idb.add(subject, predicate, object)


        new_incre_ds.positive_ds = incre_pos_idb
        new_incre_ds.negative_ds = verified_incre_neg_idb
        #new_incre_ds.negative_ds = incre_neg_idb

        #if not_verified_incre_neg_idb and len(not_verified_incre_neg_idb) > 0:
        #   new_incre_ds.not_verified_negative_ds = not_verified_incre_neg_idb


        return new_incre_ds

def backward_verification(subject, predicate, object, edb, idb, rules, visited_triples, neg_flushed_db):
    """

    :param subject:
    :param predicate:
    :param object:
    :param edb:
    :param idb:
    :param rules:
    :param visited_triples: A map (s,p,o) -> bool to tell if (s,p,o) can be verified recursively from hn.edb
    :param neg_flushed_db:
    :return:
    """
    if (subject, predicate, object) not in visited_triples:
        if edb.query(subject, predicate, object):
            visited_triples[(subject, predicate, object)] = True
            return True
        else:
            visited_triples[(subject, predicate, object)] = False

    for rule in rules:
        if rule.head.atom.predicate == predicate:
            bindings = defaultdict(bool)
            bindings[rule.head.atom.subject] = subject
            bindings[rule.head.atom.object] = object
            """
            bs = evaluate(rule, data_store=edb, bindings=bindings)
            if bs:
                visited_triples[(subject, predicate, object)] = True
                return True
            """


            bs = evaluate(rule, data_store=neg_flushed_db, bindings=bindings)
            if bs:
                rule_flag = True
                for i in range(len(bs)):
                    eatom_flag = True
                    for eatom in rule.positive_body:
                        if isinstance(eatom.atom, Atom):
                            triple = (bs[eatom.atom.subject][i] if eatom.atom.subject.type == "variable" else eatom.atom.subject, eatom.atom.predicate, bs[eatom.atom.object][i] if eatom.atom.object.type == "variable" else eatom.atom.object)
                            if triple not in visited_triples:
                                if not backward_verification(triple[0], triple[1], triple[2], edb, idb, rules, visited_triples, neg_flushed_db):
                                    eatom_flag = False
                                    break
                            else:
                                if not visited_triples[triple]:
                                    eatom_flag = False
                                    break
                    if not eatom_flag:
                        rule_flag = False
                        break
                    if rule_flag:
                        visited_triples[(subject, predicate, object)] = True
                        return True

    return False


def recursive(rule):
    head_predicate = rule.head.atom.predicate
    if head_predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and rule.head.atom.object.type == "constant":
        head_concept = rule.head.atom.object
        for ele in rule.positive_body:
            if isinstance(ele.atom, Atom) and ele.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and head_concept == ele.atom.object.name:
                return True
        return False
    else:
        for ele in rule.positive_body:
            if isinstance(ele.atom, Atom) and head_predicate == ele.atom.predicate:
                return True
        return False


def semi_naive_evaluate(rules, edb, incremental_operation = False, original_idb = None, incre_hn = False, incre_deleting = False, MAX_ITER = 50):
    idb = DataStore()
    idb_temp = None
    incre_idb_temp = None
    incre_idb = IncrementalDataStore()
    deleting_visited_triples = None



    if original_idb != None:
        idb = original_idb

    if incremental_operation:
        if edb.isdirty():
            edb.flush()

    if edb.incremental_store and edb.incremental_store.negative_ds:
        deleting_visited_triples = {}
        #idb -= edb.incremental_store.negative_ds

    fix_point = False
    iter = 0

    if len(rules) == 1 and not recursive(list(rules)[0]):
        if not incremental_operation:
            idb = generate_idb(rules, edb)
        else:
            incre_idb = generate_idb(rules, edb + idb + edb.incremental_store.negative_ds, incremental_operation=incremental_operation, incre_idb=edb.incremental_store, neg_flushed_db = edb + idb, hn_edb=edb, hn_idb=idb, deleting_visited_triples = deleting_visited_triples)
            idb.flush_with_IDS(incre_idb)
    else:
        #not_verified_neg_ds = DataStore()
        while not fix_point:
            if iter > MAX_ITER:
                raise RuntimeError("Reach Max Iteration! Rules may be undecidable!")

            if not incremental_operation:
                if iter == 0:
                    idb_temp = generate_idb(rules, edb)
                else:
                    idb_temp = generate_idb(rules, edb + idb, last_idb = idb_temp)
                idb_temp -= idb
                if len(idb_temp) == 0:
                    fix_point = True
                    #print("Iteration: " + str(iter))
                idb += idb_temp
                if original_idb:
                    incre_idb += idb_temp
                iter += 1
            else:
                if iter == 0:
                    if incre_deleting:
                        #start_time = time.time()
                        incre_idb_temp = generate_idb(rules, edb + idb + edb.incremental_store.negative_ds,
                                                      incremental_operation=incremental_operation,
                                                      incre_idb=edb.incremental_store, neg_flushed_db=edb + idb, deleting_data = True, hn_edb = edb, hn_idb = idb, deleting_visited_triples = deleting_visited_triples)
                        #print("Iter: " + str(iter) + " execution time: " + str(time.time() - start_time))
                    else:
                        incre_idb_temp = generate_idb(rules, edb + idb + edb.incremental_store.negative_ds, incremental_operation=incremental_operation, incre_idb = edb.incremental_store, neg_flushed_db = edb + idb, hn_edb=edb, hn_idb=idb, deleting_visited_triples = deleting_visited_triples)
                else:
                    if incre_deleting:
                        #start_time = time.time()
                        incre_idb_temp = generate_idb(rules, edb + idb + incre_idb_temp.negative_ds,
                                                      incremental_operation=incremental_operation,
                                                      incre_idb=incre_idb_temp, neg_flushed_db=edb + idb, deleting_data=True, hn_edb=edb, hn_idb=idb, deleting_visited_triples = deleting_visited_triples)
                        #print("Iter: " + str(iter) + " execution time: " + str(time.time() - start_time))
                    else:
                        #start_time = time.time()
                        incre_idb_temp = generate_idb(rules, edb + idb + incre_idb_temp.negative_ds, incremental_operation=incremental_operation, incre_idb = incre_idb_temp, neg_flushed_db = edb + idb, hn_edb=edb, hn_idb=idb, deleting_visited_triples = deleting_visited_triples)
                        #print("Iter: " + str(iter) + " execution time: " + str(time.time()-start_time))

                incre_idb_temp.positive_ds -= idb
                incre_idb_temp.negative_ds -= incre_idb.negative_ds
                if len(incre_idb_temp) == 0:
                    fix_point = True
                    # print("Iteration: " + str(iter))
                incre_idb += incre_idb_temp
                idb.flush_with_IDS(incre_idb_temp)
                iter += 1
        """

            if incre_idb_temp and incre_idb_temp.not_verified_negative_ds:
                incre_idb_temp.not_verified_negative_ds.print_content()
                print("------------------------------------")
                not_verified_neg_ds += incre_idb_temp.not_verified_negative_ds

        if not_verified_neg_ds:
            not_verified_neg_ds.print_content()
            print(str(len(not_verified_neg_ds)))
            print("******************************")
            incre_idb.negative_ds.print_content()
            print(str(len(incre_idb.negative_ds)))
            print("******************************")
        """

    if original_idb and len(incre_idb) > 0:
        if idb.incremental_store:
            idb.incremental_store += incre_idb
        else:
            idb.incremental_store = incre_idb
    elif incre_hn:
        idb.incremental_store = IncrementalDataStore()
        idb.incremental_store.positive_ds = idb

    return idb


def main():
    f = open("/testData/testData2.nt", "r")
    f_rules = open("/testData/testData_rules.rules", "r")
    f_add = open("/testData/testData2_add.nt", "r")

    edb = parse_data(f)
    rules = parse_rules(f_rules)
    extra_edb = parse_data(f_add)
    incre_db = IncrementalDataStore()
    incre_db.positive_ds = extra_edb

    start_time = time.time()
    idb = semi_naive_evaluate(rules, edb)
    idb.print_content()
    print("Compuation time: " + str(time.time() - start_time))
    print(len(idb))

    edb.set_incre_store(incre_db)


    start_time = time.time()
    idb = semi_naive_evaluate(rules, edb, incremental_operation = True, original_idb = idb)
    idb.print_content()
    print("Compuation time: " + str(time.time() - start_time))
    print(len(idb))

    print("end")


if __name__ == "__main__":
    main()