import copy
import time
import warnings
from collections import defaultdict
from functools import partial

from classes.resultset import ResultSet
from classes.term import Term

class DataStoreBag:
    def __init__(self, *args):
        self.data_store_bag = set()
        self.predicate_map = {}

        self.incremental_store = None


        for ele in args:
            if isinstance(ele, DataStore):
                #if len(ele) > 0:
                self.data_store_bag.add(ele)

                # Update predicate_map
                for p in ele.predicate_tuples.keys():
                    if p not in self.predicate_map:
                        self.predicate_map[p] = set()
                    self.predicate_map[p].add(ele)

            elif isinstance(ele, DataStoreBag):
                for d in ele.data_store_bag:
                    self.data_store_bag.add(d)

                    # Update predicate_map
                    for p in d.predicate_tuples.keys():
                        if p not in self.predicate_map:
                            self.predicate_map[p] = set()
                        self.predicate_map[p].add(d)

    def flush(self):
        #self += self.incremental_store.positive_ds
        #self -= self.incremental_store.negative_ds

        for ds in self.data_store_bag:
            pos_p, neg_p = ds.flush()
            if pos_p:
                for p in pos_p:
                    if p not in self.predicate_map:
                        self.predicate_map[p] = set()
                    self.predicate_map[p].add(ds)
            if neg_p:
                for p in neg_p:
                    self.predicate_map[p].discard(ds)
                    if not self.predicate_map[p]:
                        self.predicate_map.pop(p)

        return self

    def flush_positive(self):
        for ds in self.data_store_bag:
            ds.flush_positive()

        return self

    def flush_nagative(self):
        for ds in self.data_store_bag:
            ds.flush_negative()

        return self


    def isdirty(self):
        dirty_flag = False
        if not self.incremental_store:
            self.incremental_store = IncrementalDataStoreBag()
        else:
            dirty_flag = True
        for ds in self.data_store_bag:
            if ds.isdirty():
                self.incremental_store += ds.incremental_store
                dirty_flag = True
        return dirty_flag

    def clean_incremental_store(self):
        for ds in self.data_store_bag:
            if ds.isdirty():
                ds.clean_incremental_store()
        self.incremental_store = None
        return self

    def query(self, subject, predicate, object):
        rs = None
        if predicate not in self.predicate_map:
            return False

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
            #if len(other) > 0:
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

        return self

    def estimate_predicate(self, predicate):
        # Not exact but utile
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

    def print_content(self, max_number = -1, file = None):
        temp_pso = {}
        for ds in self.data_store_bag:
            for predicate in ds.predicate_tuples:
                if predicate not in temp_pso:
                    temp_pso[predicate] = set()
                temp_pso[predicate] |= ds.predicate_tuples[predicate]

        if file:
            for p in temp_pso:
                for s, o in temp_pso[p]:
                    file.write(str(s) + " " + str(p) + " " + str(o) + " .\n")
            return
        else:
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
        self.pso_index = defaultdict(partial(defaultdict, set))
        self.pos_index = defaultdict(partial(defaultdict, set))

        self.incremental_store = None
        self.incre_store_positve_signature = None
        self.flush_positive_signature = None
        self.incre_store_negative_signature = None
        self.flush_negative_signature = None

    def delete_incre_store(self):
        self.incremental_store = None

    def is_updated(self):
        if self.incre_store_signature != self.flush_signature:
            return False
        else:
            return True

    def isdirty(self):
        if self.incremental_store:
            return True
        else:
            return False

    def clean_incremental_store(self):
        self.incremental_store = None
        return self

    def add(self, subject, predicate, object):
        """
        :param subject: a Term
        :param predicate: a Term
        :param object: a Term
        :return:
        """


        self.predicate_tuples[predicate].add((subject, object))
        self.pso_index[predicate][subject].add(object)
        self.pos_index[predicate][object].add(subject)





    def remove(self, subject, predicate, object):

        if predicate in self.predicate_tuples and (subject, object) in self.predicate_tuples[predicate]:
            self.pso_index[predicate][subject].discard(object)
            self.predicate_tuples[predicate].discard((subject, object))
            if not self.pso_index[predicate][subject]:
                self.pso_index[predicate].pop(subject)
            if not self.pso_index[predicate]:
                self.pso_index.pop(predicate)
                self.predicate_tuples.pop(predicate)

            self.pos_index[predicate][object].discard(subject)
            if not self.pos_index[predicate][object]:
                self.pos_index[predicate].pop(object)
            if not self.pos_index[predicate]:
                self.pos_index.pop(predicate)



    def query(self, subject , predicate, object):
        """
        :param subject: A Term
        :param predicate: A Term
        :param object: A Term or others
        :return: A ResultSet
        """
        if predicate.type == "variable":
            raise ValueError("Predicate can't be variable")

        if subject.type == "variable" and object.type == "variable":
            rs = ResultSet()
            rs.variables.append(subject)
            rs.variables.append(object)
            if predicate in self.pso_index:
                for s in self.pso_index[predicate]:
                    for o in self.pso_index[predicate][s]:
                        rs.res.append([s, o])
            if len(rs.res) == 0:
                return None
            else:
                return rs
        elif subject.type == "variable":
            rs = ResultSet()
            rs.variables.append(subject)
            if predicate in self.pos_index and object in self.pos_index[predicate]:
                for s in self.pos_index[predicate][object]:
                    rs.res.append([s])
            if len(rs.res) == 0:
                return None
            else:
                return rs
        elif isinstance(object, Term) and object.type == "variable":
            rs = ResultSet()
            rs.variables.append(object)
            if predicate in self.pso_index and subject in self.pso_index[predicate]:
                for o in self.pso_index[predicate][subject]:
                    rs.res.append([o])
            if len(rs.res) == 0:
                return None
            else:
                return rs
        else:
            if predicate in self.pso_index and subject in self.pso_index[predicate] and object in self.pso_index[predicate][subject]:
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
            new_D.flush()
            new_D -= other
            new_D.flush()
            return new_D
        else:
            return False

    def __isub__(self, other):
        if isinstance(other, DataStore):
            for predicate in other.predicate_tuples.keys():
                if predicate in self.predicate_tuples:
                    self.predicate_tuples[predicate] -= other.predicate_tuples[predicate]
                if not self.predicate_tuples[predicate]:
                    self.predicate_tuples.pop(predicate)

                for s in other.pso_index[predicate].keys():
                    if self.pso_index[predicate][s]:
                        self.pso_index[predicate][s] -= other.pso_index[predicate][s]
                    if not self.pso_index[predicate][s]:
                        self.pso_index[predicate].pop(s)
                if not self.pso_index[predicate]:
                    self.pso_index.pop(predicate)

                for o in other.pos_index[predicate].keys():
                    if self.pos_index[predicate][o]:
                        self.pos_index[predicate][o] -= other.pos_index[predicate][o]
                    if not self.pos_index[predicate][o]:
                        self.pos_index[predicate].pop(o)
                if not self.pos_index[predicate]:
                    self.pos_index.pop(predicate)

            return self

        elif isinstance(other, DataStoreBag):
            for ds in other.data_store_bag:
                self -= ds
            return self
        else:
            if other:
                warnings.warn("Delete operation can only be done within two DataStore or DataStore and DataStoreBag")
            return self

    def __rshift__(self, other):
        if isinstance(other, DataStore):
            new_D = DataStore()
            new_D <<= other
            new_D <<= self
            return new_D
        else:
            return False

    def __lshift__(self, other):
        if isinstance(other, DataStore):
            new_D = DataStore()
            new_D <<= self
            new_D <<= other
            return new_D
        else:
            return False

    def __ilshift__(self, other):

        def deep_union(index1, index2):
            for key, value in index2.items():
                if isinstance(value, set):
                    index1[key] = index1[key] | index2[key]
                else:
                    deep_union(index1[key], index2[key])

        if isinstance(other, DataStore):
            for key in other.predicate_tuples.keys():
                if key in self.predicate_tuples:
                    del self.predicate_tuples[key]
                    del self.pso_index[key]
                    del self.pos_index[key]
                self.predicate_tuples[key] |= other.predicate_tuples[key]
                deep_union(self.pso_index[key], other.pso_index[key])
                deep_union(self.pos_index[key], other.pos_index[key])
            return self
        else:
            return self

    def __add__(self, other):
        if not ((isinstance(other, DataStore) or isinstance(other, DataStoreBag))):
            return self
        return DataStoreBag(self, other)

    def __iadd__(self, other):
        if isinstance(other, DataStoreBag):
            for ds in other.data_store_bag:
                self += ds
            return self
        elif not isinstance(other, DataStore):
            if other:
                warnings.warn("Add operation can only be done within two DataStore")
            return self

        """
        def deep_union(index1, index2):
            for key, value in index2.items():
                if isinstance(value, set):
                    index1[key] = index1[key] | index2[key]
                else:
                    deep_union(index1[key], index2[key])


        deep_union(self.pso_index, other.pso_index)

        deep_union(self.pos_index, other.pos_index)
        """

        for predicate in (set(self.predicate_tuples.keys()) | set(other.predicate_tuples.keys())):
            if not predicate.aggregation_property:
                self.predicate_tuples[predicate] = self.predicate_tuples[predicate] | other.predicate_tuples[predicate]
                for subject in (set(self.pso_index[predicate].keys()) | set(other.pso_index[predicate].keys())):
                    self.pso_index[predicate][subject] |= other.pso_index[predicate][subject]
                for object in (set(self.pos_index[predicate].keys()) | set(other.pos_index[predicate].keys())):
                    self.pos_index[predicate][object] |= other.pos_index[predicate][object]
            else:
                for subject in other.pso_index[predicate]:
                    if self.pso_index[predicate][subject]:
                        object = list(other.pso_index[predicate][subject])[0]
                        original_object = list(self.pso_index[predicate][subject])[0]

                        self.predicate_tuples[predicate].discard((subject, original_object))
                        self.predicate_tuples[predicate].add((subject, object))

                        self.pso_index[predicate][subject].discard(original_object)
                        self.pso_index[predicate][subject].add(object)

                        self.pos_index[predicate][original_object].discard(subject)
                        if not self.pos_index[predicate][original_object]:
                            self.pos_index[predicate].pop(original_object)
                        self.pos_index[predicate][object].add(subject)
                    else:
                        object = list(other.pso_index[predicate][subject])[0]
                        self.predicate_tuples[predicate].add((subject, object))
                        self.pso_index[predicate][subject].add(object)
                        self.pos_index[predicate][object].add(subject)

        return self

    def flush_with_IDS(self, ids):
        """
        :param ids: An Incremental DataStore
        :return:
        """

        if isinstance(ids, IncrementalDataStore):
            self.set_incre_store(ids)
            self.flush()

        return self

    def flush(self):
        p_set = set(self.predicate_tuples.keys())
        pos_p = None
        neg_p = None
        """
        if self.incremental_store and self.flush_positive_signature != self.incre_store_positve_signature:
            if self.incremental_store.positive_ds:
                self += self.incremental_store.positive_ds
                #pos_p = set(self.predicate_tuples.keys()) - p_set
                pos_p = set(self.incremental_store.positive_ds.predicate_tuples.keys())
        """


        """
        if self.incremental_store and self.flush_negative_signature != self.incre_store_negative_signature:
            if self.incremental_store.negative_ds:
                self -= self.incremental_store.negative_ds
                neg_p =  p_set - set(self.predicate_tuples.keys())
        """
        if self.incremental_store:
            if self.incremental_store.positive_ds:
                self += self.incremental_store.positive_ds
                # pos_p = set(self.predicate_tuples.keys()) - p_set
                pos_p = set(self.incremental_store.positive_ds.predicate_tuples.keys())
            self.flush_positive_signature = self.incre_store_positve_signature

            if self.incremental_store.negative_ds:
                self -= self.incremental_store.negative_ds
                neg_p = p_set - set(self.predicate_tuples.keys())

        self.flush_positive_signature = self.incre_store_positve_signature
        self.flush_negative_signature = self.incre_store_negative_signature

        return (pos_p, neg_p)

    def flush_positive(self):
        if self.incremental_store and self.flush_positive_signature != self.incre_store_positve_signature:
            if self.incremental_store.positive_ds:
                self += self.incremental_store.positive_ds
        self.flush_positive_signature = self.incre_store_positve_signature

        return self

    def flush_negative(self):
        if self.incremental_store and self.flush_negative_signature != self.incre_store_negative_signature:
            if self.incremental_store.negative_ds:
                self -= self.incremental_store.negative_ds
            self.flush_negative_signature = self.incre_store_negative_signature
        return self

    def set_incre_store(self, incre_store):
        if self.flush_negative_signature != self.incre_store_negative_signature or self.flush_positive_signature != self.incre_store_positve_signature:
            raise ValueError("Must flush before set incre store")
        self.incremental_store = incre_store
        self.incre_store_positve_signature = time.time()
        self.incre_store_negative_signature = time.time()
        return self

    def replace_by(self, other):
        if not isinstance(other, DataStore):
            return

        self.predicate_tuples = other.predicate_tuples
        self.pso_index = other.pso_index
        self.pos_index = other.pos_index

    def estimate_predicate(self, predicate):
        if predicate in self.predicate_tuples:
            return len(self.predicate_tuples[predicate])
        else:
            return 0


    def print_content(self, max_number = -1, file = None):
        if file:
            for p in self.predicate_tuples:
                for s, o in self.predicate_tuples[p]:
                    file.write(str(s) + " " + str(p) + " " + str(o) + " .\n")
            return
        else:
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

class IncrementalDataStoreBag:
    def __init__(self):
        self.positive_ds = DataStoreBag()
        self.negative_ds = DataStoreBag()

    def __len__(self):
        return len(self.positive_ds) + len(self.negative_ds)

    def __iadd__(self, other):
        if isinstance(other, DataStore) or isinstance(other, DataStoreBag):
            self.positive_ds += other
        elif isinstance(other, IncrementalDataStore) or isinstance(other, IncrementalDataStoreBag):
            self.positive_ds += other.positive_ds
            self.negative_ds += other.negative_ds

        return self

    def __isub__(self, other):
        if isinstance(other, DataStore) or isinstance(other, DataStoreBag):
            self.positive_ds += other

        elif isinstance(other, IncrementalDataStore) or isinstance(other, IncrementalDataStoreBag):
            self.positive_ds += other.positive_ds
            self.negative_ds += other.negative_ds

        return self



class IncrementalDataStore:
    def __init__(self):
        self.positive_ds = None
        self.negative_ds = None
        #self.not_verified_negative_ds = None
        #self.incremental_operation = None

    def __len__(self):
        return  (len(self.positive_ds) if self.positive_ds else 0) + (len(self.negative_ds) if self.negative_ds else 0)

    def __iadd__(self, other):
        if isinstance(other, DataStore):
            if self.positive_ds:
                self.positive_ds += other
            else:
                self.positive_ds = other
        elif isinstance(other, IncrementalDataStore):
            if self.positive_ds:
                self.positive_ds += other.positive_ds
            else:
                self.positive_ds = other.positive_ds

            if self.negative_ds:
                self.negative_ds += other.negative_ds
            else:
                self.negative_ds = other.negative_ds
        return self

    def __isub__(self, other):
        if isinstance(other, DataStore):
            if self.negative_ds:
                self.negative_ds += other
            else:
                self.negative_ds = other
        elif isinstance(other, IncrementalDataStore):
            if self.positive_ds:
                self.positive_ds -= other.positive_ds

            if self.negative_ds:
                self.negative_ds -= other.negative_ds

        return self


if __name__ == '__main__':
    D1 = DataStore()
    D2 = DataStore()

    D1.add(Term("Bob", "constant"), Term("love", "constant"), Term("Alice", "constant"))
    D1.add(Term("Bob", "constant"), Term("hate", "constant"), Term("Alice", "constant"))
    D1.add(Term("Bob", "constant"), Term("love", "constant"), Term("Amily", "constant"))
    #D2.add(Term("Bob", "constant"), Term("love", "constant"), Term("Amily", "constant"))
    D1 -= D2
    #D4 = D2 - D1
    #D1.remove(Term("Bob", "constant"), Term("love", "constant"), Term("Alice", "constant"))
    res = D1.query(Term("Bob", "constant"), Term("love", "constant"), Term("X", "variable"))
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

