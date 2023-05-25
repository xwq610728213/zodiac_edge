

if __name__ == "__main__":

    w_num = 50
    w_add_rate = 0.5

    f = open("testData/windTurbineTest1000.nt","w")
    f2 = open("testData/windTurbinetest1000_additiveData.nt","w")
    for i in range(1, w_num, 1):
        f.write("<windTurbine" + str(i) + "> <hasNeighbour> <windTurbine" + str(i+1) + "> .\n")
        f.write("<windTurbine" + str(i) + "> <hasAirTemperatureMesurement> " + str(25) + " .\n")

    for i in range(w_num, w_num + int(w_num * w_add_rate),1):
        f2.write("<windTurbine" + str(i) + "> <hasNeighbour> <windTurbine" + str(i + 1) + "> .\n")
        f2.write("<windTurbine" + str(i) + "> <hasAirTemperatureMesurement> " + str(25) + " .\n")


    w_num = 50
    f = open("testData/windTurbineTest_complicate_case.nt", "w")
    #f2 = open("testData/windTurbinetest100_complicate_case_additiveData.nt", "w")
    for i in range(0, w_num, 1):
        f.write("<windTurbine" + str(i) + "> <p1> <windTurbine" + str(i + 1) + "> .\n")
        f.write("<windTurbine" + str(i + 1 * w_num) + "> <p2> <windTurbine" + str(i + 1 * w_num + 1) + "> .\n")
        f.write("<windTurbine" + str(i + 2 * w_num) + "> <p3> <windTurbine" + str(i + 2 * w_num + 1) + "> .\n")
        f.write("<windTurbine" + str(i + 3 * w_num) + "> <p4> <windTurbine" + str(i + 3 * w_num + 1) + "> .\n")

    #f.write("<windTurbine" + str(1200) + "> <p0> <windTurbine" + str(0) + "> .\n")

    f2 = open("testData/windTurbineTest_complicate_case_extra_data.nt", "w")
    f2.write("<windTurbine" + str(w_num) + "> <p5> <windTurbine" + str(w_num + 1) + "> .\n")

