import gc
import os

#import psutil
import time

from classes.term import Term
from reasoner import program
from reasoner.program import Program
from util.parser import parse_data, parse_rules


def main():
    experiment_result = {}
    f2 = None

    f = open("testData/chamber.nt", "r")
    rf = open("testData/chamber.rules", "r")
    rf2 = open("testData/chamber_additional_rules.rules", "r")
    f2 = open("testData/chamber_extra_data.nt", "r")


    """
    f = open("testData/windTurbineTest_complicate_case.nt", "r")
    f2 = open("testData/windTurbineTest_complicate_case_extra_data.nt", "r")
    rf = open("testData/windTurbineTest_complicate_case_rules.rules", "r")
    rf2 = open("testData/windTurbineTest_complicate_case_extra_rules.rules", "r")
    
    """

    """

    f = open("testData/windTurbineTest1000.nt", "r")
    f2 = open("testData/windTurbinetest1000_additiveData.nt", "r")
    rf = open("testData/windTurbineTestRules.rules", "r")
    rf2 = open("testData/windTurbineTestRulesExtraRules.rules", "r")
    """

    D = parse_data(f)
    R = parse_rules(rf)
    R2 = parse_rules(rf2)
    start_time = time.time()
    program = Program(data=D, rules= R)
    experiment_result["Creat_program_time"] = time.time() - start_time
    print("Creat program time: " + str(experiment_result["Creat_program_time"]) + " s")
    print("IDB size: " + str(len(program.idb)))
    #program.edb.print_content()

    rs = program.query(subject= Term.getTerm("stateStation", "constant"), predicate= Term.getTerm("hasEnergyGenerationApartFromSolarFarm", "constant"), object= Term.getTerm("X", "variable"))
    print(rs)

    """
    info = p.memory_full_info()
    print("Mem: " + str(info.uss / 1024. / 1024. ) + " Mb")
    """

    gc.collect()
    start_time = time.time()
    program.add_rules(R2)
    experiment_result["Add_extra_rules_time"] = time.time() - start_time
    print("Add rules time: " + str(experiment_result["Add_extra_rules_time"]) + " s")
    print("IDB size: " + str(len(program.idb)))
    #program.idb.print_content()
    rs = program.query(subject=Term.getTerm("stateStation", "constant"),
                       predicate=Term.getTerm("hasEnergyGenerationApartFromSolarFarm", "constant"), object=Term.getTerm("X", "variable"))
    print(rs)
    """
    gc.collect()
    info = p.memory_full_info()
    print("Mem: " + str(info.uss / 1024. / 1024.) + " Mb")
    """

    # pf = open("persistData/persistData.nt", "w")
    # program.idb.print_content(file = pf)

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
        #program.idb.print_content()
        rs = program.query(subject=Term.getTerm("stateStation", "constant"),
                           predicate=Term.getTerm("hasEnergyGenerationApartFromSolarFarm", "constant"),
                           object=Term.getTerm("X", "variable"))
        print(rs)
        # print("EDB size: " + str(len(program.edb)))
        # program.edb.print_content()
        #program.idb.print_content()

        f2.seek(0, 0)
        D2 = parse_data(f2)
        start_time = time.time()
        program.delete_data(D2)
        experiment_result["Delete_extra_data_time"] = time.time() - start_time
        print("Delete data time: " + str(experiment_result["Delete_extra_data_time"]) + " s")
        print("IDB size: " + str(len(program.idb)))
        #program.idb.print_content()
        rs = program.query(subject=Term.getTerm("stateStation", "constant"),
                           predicate=Term.getTerm("hasEnergyGenerationApartFromSolarFarm", "constant"),
                           object=Term.getTerm("X", "variable"))
        print(rs)
        # program.idb.print_content()

    gc.collect()
    rf2.seek(0, 0)
    R2 = parse_rules(rf2)
    start_time = time.time()
    program.delete_rules(R2)
    experiment_result["Delete_extra_rules_time"] = time.time() - start_time
    print("Delete rules time: " + str(experiment_result["Delete_extra_rules_time"]) + " s")
    #print("IDB size: " + str(len(program.idb)))
    rs = program.query(subject=Term.getTerm("stateStation", "constant"),
                       predicate=Term.getTerm("hasEnergyGenerationApartFromSolarFarm", "constant"), object=Term.getTerm("X", "variable"))
    print(rs)
    # program.idb.print_content()

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

    # program.idb.print_content()
    gc.collect()
    print("end")

    return experiment_result


def ds_mem():
    pid = os.getpid()
    p = psutil.Process(pid)
    info = p.memory_full_info()
    print("Mem: " + str(info.uss / 1024. / 1024.) + " Mb")

    f = open("persistData/persistData.nt", "r")
    D = parse_data(f)
    program = Program(data=D)
    gc.collect()
    info = p.memory_full_info()
    print("Mem: " + str(info.uss / 1024. / 1024.) + " Mb")

if __name__ == "__main__":
    #main()
    main()
    """
    d_f = open("./testData/WindFarm/data.nt", "r")
    r_f = open("./testData/WindFarm/rules.rules", "r")
    D = parse_data(d_f)
    R = parse_rules(r_f)
    engine = Program(data=D, rules= R)
    res = engine.query(Term.getTerm("X", "variable"), Term.getTerm("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "constant"), Term.getTerm("TargetDeviceForModel2", "constant"))
    print(res)
    """
    """
    f = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/WindFarm/data.nt", "r")

    rf = open("/Users/RC5920/Documents/testAI/DatalogEngine/testData/WindFarm/rules.rules", "r")


    D = parse_data(f)

    D2 = parse_data(f)


    R = parse_rules(rf)
    R2 = parse_rules(rf)


    reasoner = Program(data=D, rules=R)

    reasoner.add_data(D2)
    reasoner.add_rules(R2)
    reasoner.delete_data(D2)
    reasoner.delete_rules(R2)

    reasoner.idb.print_content()


    result = reasoner.query(subject=Term.getTerm("X", "variable"), predicate=Term.getTerm("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "constant"), object= Term.getTerm("TargetDeviceForModel1", "constant"))


    print(result)
    """
    """
    res = defaultdict(list)
    for i in range(1):
        r = program.main()
        for k in r.keys():
            res[k].append(r[k])

    
    gc.collect()
    ds_mem()
    """
    """
    for k in res.keys():
        print("Average " + k + " time: " + str(np.mean(res[k])) + " s")
    """



