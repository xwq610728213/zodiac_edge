(Users can import this project into pycharm to run the test. However, because of some network problem, the repo venv, which is necessary for importing a pycharm project, in this project will be ready after the 5 juin 2023)

To run de test, users can simply execute main.py. File path can be changed in main.py to test different dataset.
To generate dataset with different number of wind turbines, users can modify w_num in generate_data.py and execute the script to get new dataset.

# Paper Test Rule Set:

## Rule set 1

This rule set corresponds to an extract of the real-world Wind farm use case. Due to confidentiality reasons, we can not provide the complete rule set.

r1: hasNeighbour(X, Y) :- hasNeighbour(Y, X) .  
r2: hasNeighbour(X, Y) :- hasNeighbour(X, Z) and hasNeighbour(Z, Y) and COMP(X, !=, Y) .  
r3: hasNeighbourAirTemperatureMeasurementNumber(X, Z) :- aggregate( hasNeighbour(X, Y) and hasAirTemperatureMesurement(Y, T)) on X with count(T) as Z .

r4: hasMedianAirTemperatureMeasurementNearby(X, Z) :- aggregate( hasNeighbour(X, Y) and hasAirTemperatureMesurement(Y, T)) on X with Med(T) as Z .

r5: MoreThan3Neighbours(X) :- hasNeighbourAirTemperatureMeasurementNumber(X, N) and Comp(N, >=, 3) .

r6: SensorAnomalyWindTurbine(X) :- hasMedianAirTemperatureMeasurementNearby(X, M) $\wedge$ MoreThan3Neighbours(X) and hasAirTemperatureMesurement(X, T) and bind(abs(T-M) as D) and Comp(D, >, 5) .

# ZodiacEdge

ZodiacEdge is a prototype of RDF-Datalog-based engine for Hybird AI (Reasoning + ML/DL) written in Python, this system is typically for Edge Computing. Users are adviced to run ZodiacEdge in PyPy 3.11 environment.

ZodiacEdge supports incrementally insertion/deletion of rules/data, which makes the system fully configurable and adapted to dynamic graph-based representation of knowledge.

ZodiacEdge also supports an extension of RDF Datalog with **AGGREGATION**, **BIND**, **COMPARE** and **SELF DEFINED FUNCTIONS**, where **SELF DEFINED FUNCTIONS** can be indicated as functions trained by ML/DL. This means users can declare logical rules mixed with ML/DL in ZodiacEdge, thus we call this system a paradigm of Hybird AI.

## Usage

* Parse rules: &emsp; R = parse_rules(file)

* Parse data: &emsp; D = parse_data(file)

* Initialize ZodiacEdge: &emsp; program = Program() &emsp; \| &emsp; program = Program(data = D, rules = R)

* Data & rules manipulation:
  
  * program.add_data(D)
  
  * program.add_rules(R)
  
  * program.delete_data(D)
  
  * program.delete_rules(R)
* Check IDB size:
  * len(program.idb)
* Print IDB contents:
  * program.idb.print_content()
* Check EDB size:
  * len(program.edb)
* Print EDB contents:
  * program.edb.print_content()
* Query ZodiacEdge:
  * resultSet = program.query(<br>
                  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; subject=Term.getTerm("X", "variable"), <br>
                  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; predicate=Term.getTerm("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "constant"), <br>
                  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; object=Term.getTerm("HasPublicationDepartment", "constant") <br> 
                  &emsp; &emsp;&emsp;&emsp;&emsp;&emsp; ) <br>
  * print(resultSet)

### Data

* Data File Format: *.nt

* Syntax: 

  * \<subject\> \<predicate\> \<object\> .
  
  * \<subject\> \<predicate\> "string" .
  
  * \<subject\> \<predicate\> digit .
  
### Rule

* Rule File Format: *.rules

* Syntax: 

  * rule:&emsp; head :- body .
  
  * head:&emsp; atom
  
  * atom:&emsp; \<predicate\>(variable\|constant, variable\|constant)

  * body:&emsp; bodyElement &nbsp; and &nbsp; bodyElement &nbsp; and ... and &nbsp; bodyElement  &emsp; \| &emsp; AGGREGATE(bodyElement &nbsp; and &nbsp; bodyElement &nbsp; and ... and &nbsp; bodyElement) &nbsp; on &nbsp; variable &nbsp; with &nbsp; AGGRE_FUNCTION(variable) &nbsp; as &nbsp; variable


  * bodyElement:&emsp; not atom &emsp; \| &emsp; atom &emsp; \| &emsp; BIND(expression &nbsp; AS &nbsp; variable)  &emsp; \| &emsp; COMP(variable\|digit, >\|<\|=\|>=\|<=\|!=, variable\|digit)
  
  * expression:
    * Arithmetic with variables &emsp; &emsp; &emsp; example: (?x + ?y)/2
    * Self-defined-bind-function &emsp; &emsp; &emsp; example: func: neural_network(?x1, ?x2, ?x3)
      * Syntax: "func:" must be added before a function to indicate this is a self-defined-bind-function rather than an arithmetic
      * Can be customized in selfDefinedFunction.slf_defined_bind_func.py
      * Can be used as an interface between reasoning and ML/DL, put some variables' binding as the input of a function and get a classification or a confidential rate as the output of the function
      * Users can profit from other packages (e.g. Pytorch, Scikit-learn etc.) by importing them in selfDefinedFunction.slf_defined_bind_func.py
  
  * variable:&emsp; X\|?x
  
  * constant:&emsp; \<uri\>\|digit\|"string"
  
  
  * AGGRE_FUNCTION: COUNT\|MAX\|MIN\|AVG\|MED\|self-defined-aggregation-function
    * self-defined-aggregation-function correspondes to custimzed functions in selfDefinedFunction.slf_defined_aggre_func
  
  

### Attention: 
* All rules and data must be ended by "\<space\>."
* A "#" can be added to the beginning of a rule to make it a comment
* In rule files, ?x \<http://www.w3.org/1999/02/22-rdf-syntax-ns#type \> \<Concept\> can be written as \<Concept\>(?x) or \<http://www.w3.org/1999/02/22-rdf-syntax-ns#type \>(?x, \<Concept\>), while ?x \<http://www.w3.org/1999/02/22-rdf-syntax-ns#type \> ?y can only be written as \<http://www.w3.org/1999/02/22-rdf-syntax-ns#type \>(?x, ?y)
* Self defined aggregation functions can be customized in selfDefinedFunction.slf_defined_aggre_func.py
  * Only upper letters and '_' are allowed in a self-defined-aggregation-function's name
  * Functions accept a list of digital value as the input  &emsp; &emsp; &emsp; example: FUNC(lst)
* Self defined bind functions can be customized in selfDefinedFunction.slf_defined_bind_func.py
  * Only upper letters and '_' are allowed in a self-defined-bind-function's name
  * Functions accept some arguments as the input &emsp; &emsp; &emsp; example: FUNC(arg1, arg2, arg3)
* In ZodiacEdge, an RDF Datatype Object can be any thing (but it must be hashable and string-able, i.e. non-hashable or non-string-able object must be packed in an hashable and string-able object, e.g. numpy-array, pytorch-tensor, ...), while the parser only support traditional digits for now. Users can create other RDF Datatype Object by using **self-defined BIND** and **self-defined AGGREGATION**.
