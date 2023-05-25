from classes.datastore import DataStore
#from classes.datastore_tuple_index import DataStoreBag


class HyperNodeDBs:
    def __init__(self, edb = None, idb = None):
        self.edb = edb
        self.idb = idb



    def __iadd__(self, other):
        if not isinstance(other, HyperNodeDBs):
            return self

        self.edb = self.edb + other.edb
        self.idb += other.idb

        return self


    def __add__(self, other):
        if not isinstance(other, HyperNodeDBs):
            return self

        new_edb = self.edb + other.edb
        new_idb = DataStore()
        new_idb += self.idb
        new_idb += other.idb
        return HyperNodeDBs(edb = new_edb, idb = new_idb)