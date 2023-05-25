import gc
import time

#from memory_profiler import profile

from classes.atom import Atom
from classes.hyper_node_dbs import HyperNodeDBs
from ruleBodyOptimiser import optimise
from semi_naive import semi_naive_evaluate
from classes.datastore import DataStore, IncrementalDataStore, DataStoreBag, IncrementalDataStoreBag
import stratify as stratify
from util.parser import parse_data, parse_rules
#import psutil


class Program:
    def __init__(self, data = None, rules = None, local_namespace = None):
        """
        :param local_namespace: The namespace of this device
        :param data: A DataStore object
        :param rules: A set of Rules
        """
        self.local_namespace = local_namespace
        if data:
            self.edb = data
        else:
            self.edb = DataStore()
        self.idb = DataStore()
        if rules:
            self.rules = rules
        else:
            self.rules = set()
        self.initialize_rules()

    def initialize_rules(self):
        self.positive_dependancy_graph, self.negative_dependancy_graph, self.hyper_nodes_in_degree, self.rule_to_hyper_node_map, self.hyper_nodes_to_rules_map, self.hyper_nodes, self.hyper_positive_dependancy_graph, self.hyper_negative_dependancy_graph = stratify.stratify(self.rules)
        self.hyper_nodes_dbs = {}
        reasoning_plan = stratify.compute_topological_order(self.hyper_nodes, self.hyper_positive_dependancy_graph, self.hyper_negative_dependancy_graph)

        for hyper_node in reasoning_plan:

            self.hyper_nodes_dbs[hyper_node] = HyperNodeDBs(edb = self.edb)
            for hn in self.hyper_nodes:
                if self.hyper_positive_dependancy_graph[hn][hyper_node] or self.hyper_negative_dependancy_graph[hn][hyper_node]:
                    self.hyper_nodes_dbs[hyper_node].edb = self.hyper_nodes_dbs[hyper_node].edb + self.hyper_nodes_dbs[hn].idb

            optimise(self.hyper_nodes_to_rules_map[hyper_node], self.edb)
            new_idb = semi_naive_evaluate(self.hyper_nodes_to_rules_map[hyper_node],  self.hyper_nodes_dbs[hyper_node].edb)
            self.hyper_nodes_dbs[hyper_node].idb = new_idb
            # Attention: DataStore1 + DataStore2 will create a DataStoreBag while DataStore1 += DataStore2 will merge DataStore2 into DataStore1
            self.idb = self.idb + new_idb

    def query(self, subject, predicate, object):
        return (self.edb + self.idb).query(subject, predicate, object)

    def add_data(self, new_edb):
        concerned_hyper_nodes = set()
        incre_store = IncrementalDataStore()
        incre_store.positive_ds = new_edb
        self.edb.set_incre_store(incre_store)

        for p in new_edb.predicate_tuples:
            for rule in self.rules:
                for eatom in rule.positive_body:
                    if isinstance(eatom.atom, Atom) and eatom.atom.predicate == p:
                        concerned_hyper_nodes.add(self.rule_to_hyper_node_map[rule])
                for eatom in rule.negative_body:
                    if isinstance(eatom.atom, Atom) and eatom.atom.predicate == p:
                        concerned_hyper_nodes.add(self.rule_to_hyper_node_map[rule])

        reasoning_plan = stratify.compute_topological_order(self.hyper_nodes, self.hyper_positive_dependancy_graph,
                                                            self.hyper_negative_dependancy_graph, concerned_hyper_nodes)

        for hyper_node in reasoning_plan:
            optimise(self.hyper_nodes_to_rules_map[hyper_node], self.edb)

            #start_time = time.time()
            if self.hyper_nodes_dbs[hyper_node].edb.isdirty():
                if self.hyper_nodes_dbs[hyper_node].idb:
                    semi_naive_evaluate(self.hyper_nodes_to_rules_map[hyper_node],  self.hyper_nodes_dbs[hyper_node].edb, incremental_operation = True, original_idb = self.hyper_nodes_dbs[hyper_node].idb)
                else:
                    self.hyper_nodes_dbs[hyper_node].idb = semi_naive_evaluate(self.hyper_nodes_to_rules_map[hyper_node],  self.hyper_nodes_dbs[hyper_node].edb, incremental_operation = True, original_idb = self.hyper_nodes_dbs[hyper_node].idb)
                    self.idb = self.idb + self.hyper_nodes_dbs[hyper_node].idb
                    for hn in self.hyper_positive_dependancy_graph[hyper_node]:
                        if self.hyper_positive_dependancy_graph[hyper_node][hn]:
                            self.hyper_nodes_dbs[hn].edb = self.hyper_nodes_dbs[hn].edb + self.hyper_nodes_dbs[hyper_node].idb
                        if self.hyper_negative_dependancy_graph[hyper_node][hn]:
                            self.hyper_nodes_dbs[hn].edb = self.hyper_nodes_dbs[hn].edb + self.hyper_nodes_dbs[hyper_node].idb

            #print("Hyper_node: " + str(hyper_node) + " execution time: " + str(time.time()-start_time))

        for hyper_node in reasoning_plan:
            self.hyper_nodes_dbs[hyper_node].idb.flush()
            self.hyper_nodes_dbs[hyper_node].idb.clean_incremental_store()
            self.hyper_nodes_dbs[hyper_node].edb.clean_incremental_store()

        self.edb.flush()
        self.edb.clean_incremental_store()


    def add_data_reserved(self, new_edb):


        concerned_hyper_nodes = set()

        temp_data_store = DataStore()
        for p in new_edb.predicate_tuples:
            replaceable_flag = True
            for rule in self.rules:
                appearing_count = 0
                for eatom in rule.positive_body:
                    if isinstance(eatom.atom, Atom) and eatom.atom.predicate == p:
                        appearing_count += 1
                for eatom in rule.negative_body:
                    if isinstance(eatom.atom, Atom) and eatom.atom.predicate == p:
                        appearing_count += 1
                if appearing_count > 0:
                    concerned_hyper_nodes.add(self.rule_to_hyper_node_map[rule])
                    if len(self.hyper_nodes_to_rules_map[self.rule_to_hyper_node_map[rule]]) > 1 or appearing_count > 1 or rule.head.atom.predicate == p or rule.aggregation:
                        replaceable_flag = False

            if replaceable_flag:
                temp_data_store.predicate_tuples[p] = self.edb.predicate_tuples[p]
                temp_data_store.pso_index[p] = self.edb.pso_index[p]
                temp_data_store.pos_index[p] = self.edb.pos_index[p]

                self.edb.predicate_tuples[p] = new_edb.predicate_tuples[p]
                self.edb.pso_index[p] = new_edb.pso_index[p]
                self.edb.pos_index[p] = new_edb.pos_index[p]
            else:
                """
                for s, o in new_edb.predicate_tuples[p]:
                    self.edb.predicate_tuples[p].add((s,o))
                    self.edb.pso_index[(p, s)].add(o)
                    self.edb.pos_index[(p, o)].add(s)
                """
                self.edb.predicate_tuples[p] |= new_edb.predicate_tuples[p]
                for s in new_edb.pso_index[p]:
                    self.edb.pso_index[p][s] |= new_edb.pso_index[p][s]
                for o in new_edb.pos_index[p]:
                    self.edb.pos_index[p][o] |= new_edb.pos_index[p][o]


        reasoning_plan = stratify.compute_topological_order(self.hyper_nodes, self.hyper_positive_dependancy_graph, self.hyper_negative_dependancy_graph, concerned_hyper_nodes)

        for hyper_node in reasoning_plan:
            optimise(self.hyper_nodes_to_rules_map[hyper_node], self.edb)
            new_idb = semi_naive_evaluate(self.hyper_nodes_to_rules_map[hyper_node],  self.hyper_nodes_dbs[hyper_node].edb)
            if hyper_node in concerned_hyper_nodes:
                self.hyper_nodes_dbs[hyper_node].idb += new_idb
            else:
                self.hyper_nodes_dbs[hyper_node].idb.replace_by(new_idb)

        for p in temp_data_store.predicate_tuples:
            if len(self.edb.predicate_tuples[p]) > len(temp_data_store.predicate_tuples[p]):
                """
                for s, o in temp_data_store.predicate_tuples[p]:
                    self.edb.predicate_tuples[p].add((s, o))
                    self.edb.pso_index[(p, s)].add(o)
                    self.edb.pos_index[(p, o)].add(s)
                """
                self.edb.predicate_tuples[p] |= temp_data_store.predicate_tuples[p]
                for s in temp_data_store.pso_index[p]:
                    self.edb.pso_index[p][s] |= temp_data_store.pso_index[p][s]
                for o in temp_data_store.pos_index[p]:
                    self.edb.pos_index[p][o] |= temp_data_store.pos_index[p][o]
            else:
                """
                for s, o in self.edb.predicate_tuples[p]:
                    temp_data_store.predicate_tuples[p].add((s, o))
                    temp_data_store.pso_index[(p, s)].add(o)
                    temp_data_store.pos_index[(p, o)].add(s)
                """
                temp_data_store.predicate_tuples[p] |= self.edb.predicate_tuples[p]
                for s in self.edb.pso_index[p]:
                    temp_data_store.pso_index[p][s] |= self.edb.pso_index[p][s]
                for o in self.edb.pos_index[p]:
                    temp_data_store.pos_index[p][o] |= self.edb.pos_index[p][o]

                self.edb.predicate_tuples[p] = temp_data_store.predicate_tuples[p]
                self.edb.pso_index[p] = temp_data_store.pso_index[p]
                self.edb.pos_index[p] = temp_data_store.pos_index[p]



    def delete_data(self, deleting_edb):
        concerned_hyper_nodes = set()
        incre_store = IncrementalDataStore()
        incre_store.negative_ds = deleting_edb
        self.edb.set_incre_store(incre_store)

        for p in deleting_edb.predicate_tuples:
            for rule in self.rules:
                appearing_count = 0
                for eatom in rule.positive_body:
                    if isinstance(eatom.atom, Atom) and eatom.atom.predicate == p:
                        appearing_count += 1
                for eatom in rule.negative_body:
                    if isinstance(eatom.atom, Atom) and eatom.atom.predicate == p:
                        appearing_count += 1
                if appearing_count > 0:
                    concerned_hyper_nodes.add(self.rule_to_hyper_node_map[rule])

        if not concerned_hyper_nodes:
            return

        reasoning_plan = stratify.compute_topological_order(self.hyper_nodes, self.hyper_positive_dependancy_graph, self.hyper_negative_dependancy_graph, concerned_hyper_nodes)

        for hyper_node in reasoning_plan:
            optimise(self.hyper_nodes_to_rules_map[hyper_node], self.edb)
            if self.hyper_nodes_dbs[hyper_node].edb.isdirty():
                semi_naive_evaluate(self.hyper_nodes_to_rules_map[hyper_node],  self.hyper_nodes_dbs[hyper_node].edb, incremental_operation = True, original_idb = self.hyper_nodes_dbs[hyper_node].idb, incre_deleting = True)

        for hyper_node in reasoning_plan:
            self.hyper_nodes_dbs[hyper_node].idb.flush()
            self.hyper_nodes_dbs[hyper_node].idb.clean_incremental_store()
            self.hyper_nodes_dbs[hyper_node].edb.clean_incremental_store()

        self.edb.flush()
        self.edb.clean_incremental_store()


    def add_rules(self, new_rules):
        if len(self.rules) == 0:
            self.rules = new_rules
            self.initialize_rules()
            return

        adding_rules = set()
        for rule in new_rules:
            if rule not in self.rules:
                adding_rules.add(rule)
        new_rules = adding_rules
        if len(new_rules) == 0:
            return


        self.positive_dependancy_graph, self.negative_dependancy_graph, self.rules, updated_hyper_nodes, self.rule_to_hyper_node_map, self.hyper_nodes_to_rules_map, self.hyper_nodes, self.hyper_positive_dependancy_graph, self.hyper_negative_dependancy_graph, self.hyper_nodes_dbs = stratify.re_stratify_plus(
            new_rules, self.positive_dependancy_graph, self.negative_dependancy_graph, self.rules, self.rule_to_hyper_node_map,
            self.hyper_nodes_to_rules_map, self.hyper_nodes, self.hyper_positive_dependancy_graph, self.hyper_negative_dependancy_graph, self.hyper_nodes_dbs)

        reasoning_plan = stratify.compute_topological_order(self.hyper_nodes, self.hyper_positive_dependancy_graph, self.hyper_negative_dependancy_graph, updated_hyper_nodes)
        for hyper_node in reasoning_plan:

            if hyper_node not in self.hyper_nodes_dbs:
                self.hyper_nodes_dbs[hyper_node] = HyperNodeDBs(edb=self.edb)
                for hn in self.hyper_nodes:
                    if self.hyper_positive_dependancy_graph[hn][hyper_node] or self.hyper_negative_dependancy_graph[hn][hyper_node]:
                        self.hyper_nodes_dbs[hyper_node].edb = self.hyper_nodes_dbs[hyper_node].edb + self.hyper_nodes_dbs[hn].idb

                optimise(self.hyper_nodes_to_rules_map[hyper_node], self.edb)
                new_idb = semi_naive_evaluate(self.hyper_nodes_to_rules_map[hyper_node], self.hyper_nodes_dbs[hyper_node].edb, incre_hn=True)
                self.hyper_nodes_dbs[hyper_node].idb = new_idb
                #Attention: DataStore1 + DataStore2 will create a DataStoreBag while DataStore1 += DataStore2 will merge DataStore2 into DataStore1
                self.idb = self.idb + new_idb
            else:
                for hn in self.hyper_nodes:
                    if (self.hyper_positive_dependancy_graph[hn][hyper_node] or self.hyper_negative_dependancy_graph[hn][hyper_node]) and (isinstance(self.hyper_nodes_dbs[hyper_node].edb, DataStore) or (isinstance(self.hyper_nodes_dbs[hyper_node].edb, DataStoreBag) and self.hyper_nodes_dbs[hn].idb not in self.hyper_nodes_dbs[hyper_node].edb.data_store_bag)):
                        if isinstance(self.hyper_nodes_dbs[hyper_node].edb, DataStore):
                            self.hyper_nodes_dbs[hyper_node].edb = self.hyper_nodes_dbs[hyper_node].edb + self.hyper_nodes_dbs[hn].idb
                            self.hyper_nodes_dbs[hyper_node].edb.incremental_store = IncrementalDataStoreBag()
                            self.hyper_nodes_dbs[hyper_node].edb.incremental_store.positive_ds += self.hyper_nodes_dbs[hn].idb
                        elif isinstance(self.hyper_nodes_dbs[hyper_node].edb, DataStoreBag):
                            if not self.hyper_nodes_dbs[hyper_node].edb.incremental_store:
                                self.hyper_nodes_dbs[hyper_node].edb.incremental_store = IncrementalDataStoreBag()
                            #Modified
                            self.hyper_nodes_dbs[hyper_node].edb += self.hyper_nodes_dbs[hn].idb

                optimise(self.hyper_nodes_to_rules_map[hyper_node], self.edb)
                # Mb a bug here, if new rules appear in an existing hyper node, deletion also? fixed!

                if self.hyper_nodes_to_rules_map[hyper_node] & new_rules:
                    semi_naive_evaluate(self.hyper_nodes_to_rules_map[hyper_node], self.hyper_nodes_dbs[hyper_node].edb + self.hyper_nodes_dbs[hyper_node].idb, original_idb=self.hyper_nodes_dbs[hyper_node].idb)
                if self.hyper_nodes_dbs[hyper_node].edb.isdirty():
                    semi_naive_evaluate(self.hyper_nodes_to_rules_map[hyper_node], self.hyper_nodes_dbs[hyper_node].edb,
                                        incremental_operation=True, original_idb=self.hyper_nodes_dbs[hyper_node].idb)

                if isinstance(self.idb, DataStore):
                    self.idb = self.idb + self.hyper_nodes_dbs[hyper_node].idb
                else:
                    self.idb += self.hyper_nodes_dbs[hyper_node].idb

        for hyper_node in reasoning_plan:
            self.hyper_nodes_dbs[hyper_node].idb.flush()
            self.hyper_nodes_dbs[hyper_node].idb.clean_incremental_store()
            self.hyper_nodes_dbs[hyper_node].edb.clean_incremental_store()

        self.edb.flush()
        self.edb.clean_incremental_store()

        return self




    def delete_rules(self, deleting_rules):
        if len(self.rules) == 0:
            return

        actual_deleting_rules = set()
        for rule in deleting_rules:
            if rule in self.rules:
                actual_deleting_rules.add(rule)
        deleting_rules = actual_deleting_rules

        if len(deleting_rules) == 0:
            return



        self.positive_dependancy_graph, self.negative_dependancy_graph, self.rules, influenced_hyper_nodes, self.rule_to_hyper_node_map, self.hyper_nodes_to_rules_map, self.hyper_nodes, self.hyper_positive_dependancy_graph, self.hyper_negative_dependancy_graph, self.hyper_nodes_dbs = stratify.re_stratify_minus(
            deleting_rules, self.positive_dependancy_graph, self.negative_dependancy_graph, self.rules,
            self.rule_to_hyper_node_map,
            self.hyper_nodes_to_rules_map, self.hyper_nodes, self.hyper_positive_dependancy_graph,
            self.hyper_negative_dependancy_graph, self.hyper_nodes_dbs)

        reasoning_plan = []
        if influenced_hyper_nodes:
            reasoning_plan = stratify.compute_topological_order(self.hyper_nodes, self.hyper_positive_dependancy_graph, self.hyper_negative_dependancy_graph, influenced_hyper_nodes)

        self.idb = DataStore()

        for hn in self.hyper_nodes:
            if hn not in reasoning_plan:
                self.idb = self.idb + self.hyper_nodes_dbs[hn].idb



        for hyper_node in reasoning_plan:

            self.hyper_nodes_dbs[hyper_node] = HyperNodeDBs(edb=self.edb)
            for hn in self.hyper_nodes:
                if self.hyper_positive_dependancy_graph[hn][hyper_node] or self.hyper_negative_dependancy_graph[hn][hyper_node]:
                    self.hyper_nodes_dbs[hyper_node].edb = self.hyper_nodes_dbs[hyper_node].edb + self.hyper_nodes_dbs[hn].idb


            optimise(self.hyper_nodes_to_rules_map[hyper_node], self.edb)
            new_idb = semi_naive_evaluate(self.hyper_nodes_to_rules_map[hyper_node],
                                          self.hyper_nodes_dbs[hyper_node].edb)
            self.hyper_nodes_dbs[hyper_node].idb = new_idb
            # Attention: DataStore1 + DataStore2 will create a DataStoreBag while DataStore1 += DataStore2 will merge DataStore2 into DataStore1
            self.idb = self.idb + new_idb

        for hyper_node in reasoning_plan:
            self.hyper_nodes_dbs[hyper_node].idb.flush()
            self.hyper_nodes_dbs[hyper_node].idb.clean_incremental_store()
            self.hyper_nodes_dbs[hyper_node].edb.clean_incremental_store()

        self.edb.flush()
        self.edb.clean_incremental_store()

        return self




def main():
    experiment_result = {}
    f2 = None
    """
    pid = os.getpid()
    p = psutil.Process(pid)
    info = p.memory_full_info()
    print("Mem: " + str(info.uss / 1024. / 1024.) + " Mb")
    """
    """
    f = open("/Users/RC5920/Documents/LUBM_generator/nt_data/univ0.nt", "r")
    rf = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/LUBM_rule.rules", "r")
    rf2 = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/additive_LUBM_rules.rules", "r")
    f2 = open("/Users/RC5920/Documents/LUBM_generator/nt_data/univ1.nt", "r")
    """

    """
    f = open("testData/windTurbineTest.nt", "r")
    f2 = open("testData/windTurbinetestAdditiveData.nt", "r")
    rf = open("testData/windTurbineTestRules.rules", "r")
    rf2 = open("testData/windTurbineTestRulesExtraRules.rules", "r")
    """
    """
    f = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/AggreTest/data.nt", "r")
    f2 = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/AggreTest/data.nt", "r")
    rf = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/AggreTest/rules.rules", "r")
    rf2 = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/AggreTest/rules.rules", "r")
    """
    """
    f = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/windTurbineTest_complicate_case.nt", "r")
    f2 = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/windTurbineTest_complicate_case_extra_data.nt", "r")
    rf = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/windTurbineTest_complicate_case_rules.rules", "r")
    rf2 = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/windTurbineTest_complicate_case_extra_rules.rules", "r")
    """

    f = open("./testData/windTurbineTest1000.nt", "r")
    #f2 = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/windTurbinetest100_additiveData.nt", "r")
    rf = open("./testData/windTurbineTestRules.rules", "r")
    rf2 = open("./testData/windTurbineTestRulesExtraRules.rules", "r")




    """
    f = open("testData/testData2.nt", "r")
    f2 = open("testData/testData2_add.nt", "r")
    rf = open("testData/testData_rules.rules", "r")
    rf2 = open("testData/testData_rules.rules", "r")
    """


    """
    f = open("/Users/RC5920/Documents/projects/Occupancy/occupancyNTTestSamples/engieStainsOccupancy_202105031345_29e8b33b-6e3e-44f2-b652-5de302154828.nt", "r")
    rf = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/windTurbineRules.rules", "r")
    rf2 = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/windTurbineRules.rules", "r")
    """



    D = parse_data(f)
    R = parse_rules(rf)
    R2 = parse_rules(rf2)
    start_time = time.time()
    program = Program(data=D)
    experiment_result["Creat_program_time"] = time.time() - start_time
    print("Creat program time: " + str(experiment_result["Creat_program_time"]) + " s")
    print("IDB size: " + str(len(program.idb)))
    """
    info = p.memory_full_info()
    print("Mem: " + str(info.uss / 1024. / 1024. ) + " Mb")
    """
    start_time = time.time()
    program.add_rules(R)
    experiment_result["Add_extra_rules_time"] = time.time() - start_time
    print("Add rules time: " + str(experiment_result["Add_extra_rules_time"]) + " s")
    print("IDB size: " + str(len(program.idb)))
    """
    info = p.memory_full_info()
    print("Mem: " + str(info.uss / 1024. / 1024. ) + " Mb")
    """
    #program.idb.print_content()

    gc.collect()
    start_time = time.time()
    program.add_rules(R2)
    experiment_result["Add_extra_rules_time"] = time.time() - start_time
    print("Add rules time: " + str(experiment_result["Add_extra_rules_time"]) + " s")
    print("IDB size: " + str(len(program.idb)))
    """
    gc.collect()
    info = p.memory_full_info()
    print("Mem: " + str(info.uss / 1024. / 1024.) + " Mb")
    """

    #pf = open("persistData/persistData.nt", "w")
    #program.idb.print_content(file = pf)

    if f2:
        start_time = time.time()
        D2 = parse_data(f2)
        print("Parse data time: " + str(time.time() - start_time) + " s")
        print("Parsed data size: " + str(len(D2)))
        gc.collect()

        start_time = time.time()
        program.add_data(D2)
        experiment_result["Add_extra_data_time"] = time.time() - start_time
        print("Add data time: " + str(experiment_result["Add_extra_data_time"]) + " s")
        print("IDB size: " + str(len(program.idb)))
        #print("EDB size: " + str(len(program.edb)))
        #program.edb.print_content()
        program.idb.print_content()

        f2.seek(0, 0)
        D2 = parse_data(f2)
        start_time = time.time()
        program.delete_data(D2)
        experiment_result["Delete_extra_data_time"] = time.time() - start_time
        print("Delete data time: " + str(experiment_result["Delete_extra_data_time"]) + " s")
        print("IDB size: " + str(len(program.idb)))
        #program.idb.print_content()

    gc.collect()
    rf2.seek(0,0)
    R2 = parse_rules(rf2)
    start_time = time.time()
    program.delete_rules(R2)
    experiment_result["Delete_extra_rules_time"] = time.time() - start_time
    print("Delete rules time: " + str(experiment_result["Delete_extra_rules_time"]) + " s")
    print("IDB size: " + str(len(program.idb)))
    #program.idb.print_content()


    """
    
    
    D = parse_data(f)
    R = parse_rules(rf)
    R2 = parse_rules(rf2)
    start_time = time.time()
    program = Program(data=D)
    print("Creat program time: " + str(time.time() - start_time) + " s")
    print("IDB size: " + str(len(program.idb)))

    start_time = time.time()
    program.add_rules(R)
    print("Add rules time: " + str(time.time() - start_time) + " s")
    print("IDB size: " + str(len(program.idb)))

    gc.collect()
    start_time = time.time()
    program.add_rules(R2)
    print("Add rules time: " + str(time.time() - start_time) + " s")
    print("IDB size: " + str(len(program.idb)))
    #program.idb.print_content()

    if f2:
        start_time = time.time()
        D2 = parse_data(f2)
        print("Parse data time: " + str(time.time() - start_time) + " s")
        print("Parsed data size: " + str(len(D2)))
        gc.collect()

        start_time = time.time()
        program.add_data(D2)
        print("Add data time: " + str(time.time() - start_time) + " s")
        print("IDB size: " + str(len(program.idb)))
        print("EDB size: " + str(len(program.edb)))
        #program.idb.print_content()
        rs = program.query(subject=Term.getTerm("X", "variable"),
                           predicate=Term.getTerm("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "constant"),
                           object=Term.getTerm("HasPublicationDepartment", "constant"))

        print(rs)

        f2.seek(0, 0)
        D2 = parse_data(f2)
        start_time = time.time()
        program.delete_data(D2)
        print("Delete data time: " + str(time.time() - start_time) + " s")
        print("IDB size: " + str(len(program.idb)))

    gc.collect()
    start_time = time.time()
    program.delete_rules(R2)
    print("Delete rules time: " + str(time.time() - start_time) + " s")
    print("IDB size: " + str(len(program.idb)))

    gc.collect()
    start_time = time.time()
    program.delete_rules(R)
    print("Delete rules time: " + str(time.time() - start_time) + " s")
    print("IDB size: " + str(len(program.idb)))

    rs = program.query(subject= Term.getTerm("X", "variable"), predicate= Term.getTerm("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "constant"), object= Term.getTerm("HasPublicationDepartment", "constant"))

    print(rs)
    """

    #program.idb.print_content()
    gc.collect()
    print("end")

    return experiment_result



if __name__ == "__main__":
    main()


