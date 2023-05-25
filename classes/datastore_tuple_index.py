import copy
from collections import defaultdict
from functools import partial

from classes.resultset import ResultSet
from classes.term import Term


class DataStoreBag:
    def __init__(self, *args):
        self.data_store_bag = set()
        self.predicate_map = {}
        for ele in args:
            if isinstance(ele, DataStore):
                if len(ele) > 0:
                    self.data_store_bag.add(ele)

                    # Update predicate_map
                    for p in ele.predicate_tuples.keys():
                        if p not in self.predicate_map:
                            self.predicate_map[p] = set()
                        self.predicate_map[p].add(ele)

            elif isinstance(ele, DataStoreBag):
                for d in ele:
                    self.data_store_bag.add(d)

                    # Update predicate_map
                    for p in d.predicate_tuples.keys():
                        if p not in self.predicate_map:
                            self.predicate_map[p] = set()
                        self.predicate_map[p].add(d)

    def query(self, subject, predicate, object):
        rs = None
        for ds in self.predicate_map[predicate]:
            if rs == None:
                rs = ds.query(subject, predicate, object)
            else:
                temp_rs = ds.query(subject, predicate, object)
                if temp_rs:
                    if isinstance(rs, bool):
                        rs |= temp_rs
                    else:
                        check_v = True
                        for vi in range(len(rs.variables)):
                            if rs.variables[vi] != temp_rs.variables[vi]:
                                check_v = False
                        if check_v:
                            rs.res += temp_rs.res
                        else:
                            raise RuntimeError("Query data store bag variable order difference problem!")
        return rs

    def __add__(self, other):
        if not (isinstance(other, DataStore) or isinstance(other, DataStoreBag)):
            return self

        db = DataStoreBag()
        db += self
        db += other
        return db

    def __iadd__(self, other):
        if not (isinstance(other, DataStore) or isinstance(other, DataStoreBag)):
            return self

        if isinstance(other, DataStoreBag):
            self.data_store_bag |= other.data_store_bag

            # Update predicate_map
            for p in other.predicate_map:
                if p not in self.predicate_map:
                    self.predicate_map[p] = set()
                self.predicate_map[p] |= other.predicate_map[p]

        if isinstance(other, DataStore):
            if len(other) > 0:
                self.data_store_bag.add(other)

                # Update predicate_map
                for p in other.predicate_tuples:
                    if p not in self.predicate_map:
                        self.predicate_map[p] = set()
                    self.predicate_map[p].add(other)

        return self

    def __isub__(self, other):
        if isinstance(other, DataStore):
            self.data_store_bag.discard(other)
            for p in other.predicate_tuples:
                self.predicate_map[p].discard(other)
        elif isinstance(other, DataStoreBag):
            for d in other.data_store_bag:
                self.data_store_bag.discard(d)
                for p in d.predicate_tuples:
                    self.predicate_map[p].discard(d)
        else:
            return

    def estimate_predicate(self, predicate):
        # Not correct but utile
        l = 0
        for ds in self.data_store_bag:
            l += ds.estimate_predicate(predicate)

        return l

    def __len__(self):
        temp_pso = {}
        for ds in self.data_store_bag:
            for predicate in ds.predicate_tuples:
                if predicate not in temp_pso:
                    temp_pso[predicate] = set()
                temp_pso[predicate] |= ds.predicate_tuples[predicate]

        l = 0
        for p in temp_pso:
            l += len(temp_pso[p])

        return l

    def print_content(self, max_number = -1):
        temp_pso = {}
        for ds in self.data_store_bag:
            for predicate in ds.predicate_tuples:
                if predicate not in temp_pso:
                    temp_pso[predicate] = set()
                temp_pso[predicate] |= ds.predicate_tuples[predicate]

        if max_number < 0:
            for p in temp_pso:
                for s, o in temp_pso[p]:
                    print(str(s) + " " + str(p) + " " + str(o) + " .")
        else:
            print_count = 0
            for p in temp_pso:
                for s, o in temp_pso[p]:
                    print(str(s) + " " + str(p) + " " + str(o) + " .")
                    print_count += 1
                    if print_count >= max_number:
                        return




class DataStore:
    def __init__(self):
        self.predicate_tuples = defaultdict(set)
        self.pso_index = defaultdict(set)
        self.pos_index = defaultdict(set)

    def add(self, subject, predicate, object):
        """
        :param subject: a Term
        :param predicate: a Term
        :param object: a Term
        :return:
        """


        self.predicate_tuples[predicate].add((subject, object))
        self.pso_index[(predicate,subject)].add(object)
        self.pos_index[(predicate,object)].add(subject)




    def remove(self, subject, predicate, object):

        if object in self.pso_index[(predicate,subject)]:
            self.pso_index[(predicate,subject)].discard(object)
            self.predicate_tuples[predicate].discard((subject, object))
            if not self.pso_index[(predicate,subject)]:
                self.pso_index.pop((predicate,subject))
            if not self.predicate_tuples[predicate]:
                self.predicate_tuples.pop(predicate)

        if subject in self.pos_index[(predicate,object)]:
            self.pos_index[(predicate,object)].discard(subject)
            if not self.pos_index[(predicate,object)]:
                self.pos_index.pop((predicate,object))


    def query(self, subject, predicate, object):
        """
        :param subject: A Term
        :param predicate: A Term
        :param object: A Term
        :return: A ResultSet
        """
        if predicate.type == "variable":
            raise ValueError("Predicate can't be variable")

        if subject.type == "variable" and object.type == "variable":
            rs = ResultSet()
            rs.variables.append(subject)
            rs.variables.append(object)
            if predicate in self.predicate_tuples:
                for so_pair in self.predicate_tuples[predicate]:
                    rs.res.append(so_pair)
            if len(rs.res) == 0:
                return None
            else:
                return rs
        elif subject.type == "variable":
            rs = ResultSet()
            rs.variables.append(subject)
            if (predicate, object) in self.pos_index:
                for s in self.pos_index[(predicate,object)]:
                    rs.res.append((s,))
            if len(rs.res) == 0:
                return None
            else:
                return rs
        elif object.type == "variable":
            rs = ResultSet()
            rs.variables.append(object)
            if (predicate, subject) in self.pso_index:
                for o in self.pso_index[(predicate,subject)]:
                    rs.res.append((o,))
            if len(rs.res) == 0:
                return None
            else:
                return rs
        else:
            if predicate in self.predicate_tuples and (subject, object) in self.predicate_tuples[predicate]:
                return True
            else:
                return False


    def __len__(self):
        l = 0
        for predicate in self.predicate_tuples.keys():
            l += len(self.predicate_tuples[predicate])
        return l

    def __sub__(self, other):
        if isinstance(other, DataStore):
            new_D = DataStore()
            new_D += self
            new_D -= other
            return new_D
        else:
            return False

    def __isub__(self, other):
        if isinstance(other, DataStore):

            for predicate in other.predicate_tuples.keys():
                if predicate in self.predicate_tuples:
                    self.predicate_tuples[predicate] -= other.predicate_tuples[predicate]

            for ps in other.pso_index.keys():
                if ps in self.pso_index:
                    self.pso_index[ps] -= other.pso_index[ps]

            for po in other.pos_index.keys():
                if po in self.pos_index:
                    self.pos_index[po] -= other.pos_index[po]

            return self
        else:
            return self

    def __rshift__(self, other):
        if isinstance(other, DataStore):
            new_D = DataStore()
            new_D += other
            new_D <<= self
            return new_D
        else:
            return False

    def __lshift__(self, other):
        if isinstance(other, DataStore):
            new_D = DataStore()
            new_D += self
            new_D <<= other
            return new_D
        else:
            return False

    def __ilshift__(self, other):


        for predicate in other.predicate_tuples.keys():
            if predicate in self.predicate_tuples:
                self.predicate_tuples[predicate] = set()
                self.predicate_tuples[predicate] += other.predicate_tuples[predicate]

        for ps in other.pso_index.keys():
            if ps in self.pso_index:
                self.pso_index[ps] = set()
                self.pso_index[ps] += other.pso_index[ps]

        for po in other.pos_index.keys():
            if po in self.pos_index:
                self.pos_index[po] = set()
                self.pos_index[po] += other.pos_index[po]

            return self
        else:
            return self

    def __add__(self, other):
        if not ((isinstance(other, DataStore) or isinstance(other, DataStoreBag))):
            return self
        return DataStoreBag(self, other)

    def __iadd__(self, other):
        if not isinstance(other, DataStore):
            return self


        for predicate in other.predicate_tuples.keys():
            self.predicate_tuples[predicate] |= other.predicate_tuples[predicate]

        for ps in other.pso_index.keys():
            self.pso_index[ps] |= other.pso_index[ps]

        for po in other.pos_index.keys():
            self.pos_index[po] |= other.pos_index[po]

        return self

    def estimate_predicate(self, predicate):
        if predicate in self.predicate_tuples:
            return len(self.predicate_tuples[predicate])
        else:
            return 0

    def print_content(self, max_number = -1):
        if max_number < 0:
            for p in self.predicate_tuples:
                for s,o in self.predicate_tuples[p]:
                    print(str(s) + " " + str(p) + " " + str(o) + " .")
        else:
            print_count = 0
            for p in self.predicate_tuples:
                for s, o in self.predicate_tuples[p]:
                    print(str(s) + " " + str(p) + " " + str(o) + " .")
                    print_count += 1
                    if print_count >= max_number:
                        return



if __name__ == '__main__':
    D1 = DataStore()
    D2 = DataStore()

    D1.add(Term.getTerm("Bob", "constant"), Term.getTerm("love", "constant"), Term.getTerm("Alice", "constant"))
    D1.add(Term.getTerm("Bob", "constant"), Term.getTerm("hate", "constant"), Term.getTerm("Alice", "constant"))
    D2.add(Term.getTerm("Bob", "constant"), Term.getTerm("love", "constant"), Term.getTerm("Amily", "constant"))
    D3 = D1 - D2
    D4 = D2 - D1
    #D1.remove(Term("Bob", "constant"), Term("love", "constant"), Term("Alice", "constant"))
    res = D3.query(Term.getTerm("Bob", "constant"), Term.getTerm("love", "constant"), Term.getTerm("X", "variable"))
    print(res)
    """
    D1 = DataStore()
    D2 = DataStore()

    D1.add(Term("Bob", "constant"), Term("love", "constant"), Term("Alice", "constant"))
    D2.add(Term("Bob", "constant"), Term("love", "constant"), Term("Amily", "constant"))
    D3 = D1 + D2
    D1.remove(Term("Bob", "constant"), Term("love", "constant"), Term("Alice", "constant"))
    res = D3.query(Term("Bob", "constant"), Term("love", "constant"), Term("X", "variable"))
    print(res)
    """





