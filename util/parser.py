import os
import re
import string
import time
import warnings

#from memory_profiler import profile

from classes.aggregation import Aggregation
from classes.bind import Bind, CustomizedBind
from classes.comp import Compare
from classes.datastore import DataStore
from classes.term import Term
from classes.rule import Rule
from classes.extended_atom import EAtom
from classes.extended_atom import WOperator
from classes.atom import Atom

nt_line_pattern = re.compile(r"(?P<subj>[^\s]*)\s+(?P<pred>[^\s]*)\s+(?P<obj>(\".*\"[^\s]*|[^\"][^\s]*))\s*\.\s*$")

data_type_object_pattern = re.compile(r"(?P<value>\".*\")\^\^(?P<dtype>[^\s]*)")

extended_atom_pattern = re.compile(r"((?P<MTLOperator>[^\s]*)\[(?P<window_size>\d*)\]\()?(\s*(?P<negation>not)\s+)?((\s*(?P<bind>bind)\s*\(\s*(?P<expression>.*)\s+as\s+(?P<as_var>[^\s]*)\s*\)\s*)|((?P<predicate>[^\s]*)\(\s*(?P<subject>[^\s,]*)\s*,\s*(?P<object>[^\s,\)]*)\s*\))|((?P<concept>[^\s]*)\(\s*(?P<instance>[^\s,\)]*)\s*\))|((?P<comp>comp)\s*\(\s*(?P<ele1>[^\s]*)\s*,\s*(?P<comparator>[^\s]*)\s*,\s*(?P<ele2>[^\s]*)\s*\))\s*)\)?", re.I)

func_pattern = re.compile(r"\s*func:.*", re.I)

def parse_nt_line(line):
	#print(line)

	res = nt_line_pattern.match(line)
	if not res:
		return None
	subj = res.group("subj")
	pred = res.group("pred")
	obj = res.group("obj")
	#print(obj)
	datatype_obj_match = data_type_object_pattern.match(obj)
	if datatype_obj_match != None:
		#print(datatype_obj_match.group("dtype"))
		if datatype_obj_match.group("dtype") == "<http://www.w3.org/2001/XMLSchema#integer>" or datatype_obj_match.group("dtype") == "<http://www.w3.org/2001/XMLSchema#float>":
			#obj = datatype_obj_match.group("value").strip("\"")
			obj = datatype_obj_match.group("value").strip("\"")
	return subj.strip("<>"), pred.strip("<>"), obj.strip("<>")

def parse_extended_atom(str):

	"""
	extended_atom_pattern2 = re.compile(
		r"Diamondminus\[(?P<time_periode>\d*)\]\((?P<concept>[^\s]*)\(\s*(?P<instance>[^\s,]*)\s*\)\)")
	extended_atom_pattern3 = re.compile(
		r"Boxminus\[(?P<time_periode>\d*)\]\((?P<predicate>[^\s]*)\(\s*(?P<subject>[^\s,]*)\s*,\s*(?P<object>[^\s,]*)\s*\)\)")
	extended_atom_pattern4 = re.compile(
		r"Boxminus\[(?P<time_periode>\d*)\]\((?P<concept>[^\s]*)\(\s*(?P<instance>[^\s,]*)\s*\)\)")
	extended_atom_pattern5 = re.compile(
		r"(?P<predicate>[^\s]*)\(\s*(?P<subject>[^\s,]*)\s*,\s*(?P<object>[^\s,]*)\s*\)")
	extended_atom_pattern6 = re.compile(
		r"(?P<concept>[^\s]*)\(\s*(?P<instance>[^\s,]*)\s*\)")
	"""
	#print(extended_atom_pattern6.match("<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>(P, <https://w3id.org/bot#Zone>)").group("concept"))

	res = extended_atom_pattern.match(str)

	if not res:
		raise ValueError("Extendes atom syntax error:" + str)

	def construct_atom(res):
		if res.group("comp"):
			return Compare(
				Term.getTerm(res.group("ele1").strip("<>"), "variable") if res.group("ele1")[0].isupper() or res.group("ele1")[0] == "?" else (Term.getTerm(res.group("ele1").strip("<>"), "constant") if not res.group("ele1").isdigit() else string.atof(res.group("ele1"))),
				res.group("comparator"),
				Term.getTerm(res.group("ele2").strip("<>"), "variable") if res.group("ele2")[0].isupper() or res.group("ele2")[0] == "?" else (Term.getTerm(res.group("ele2").strip("<>"), "constant") if not res.group("ele2").isdigit() else string.atof(res.group("ele2"))),
				negation=True if res.group("negation") else False
			)
		elif res.group("predicate"):
			return Atom(
				Term.getTerm(res.group("predicate").strip("<>"), "constant"),
				Term.getTerm(res.group("subject").strip("<>"), "variable") if res.group("subject")[0].isupper() or res.group("subject")[0] == "?" else Term.getTerm(res.group("subject").strip("<>"), "constant"),
				Term.getTerm(res.group("object").strip("<>"), "variable") if res.group("object")[0].isupper() or res.group("object")[0] == "?" else Term.getTerm(res.group("object").strip("<>"), "constant"),
				negation = True if res.group("negation") else False
			)
		elif res.group("bind"):

			if func_pattern.match(res.group("expression")):
				return CustomizedBind(
					res.group("expression"),
					Term.getTerm(res.group("as_var").strip("<>"), "variable")
				)
			else:
				return Bind(
					res.group("expression"),
					Term.getTerm(res.group("as_var").strip("<>"), "variable")
				)
		else:
			return Atom(
				Term.getTerm("http://www.w3.org/1999/02/22-rdf-syntax-ns#type", "constant"),
				Term.getTerm(res.group("instance").strip("<>"), "variable") if res.group("instance")[0].isupper() or res.group("instance")[0] == "?" else Term.getTerm(res.group("instance").strip("<>"), "constant"),
				Term.getTerm(res.group("concept").strip("<>"), "constant"),
				negation = True if res.group("negation") else False
			)

	atom = construct_atom(res)

	if res.group("MTLOperator"):
		return EAtom(atom, WOperator(res.group("MTLOperator"), res.group("window_size")))
	else:
		return EAtom(atom)

rule_pattern = re.compile(r"\s*(?P<head>.*)\s*\:\-\s*(?P<body>.*)\s*\.\s*")
aggre_pattern = re.compile(r"\s*aggregate\s*\(\s*(?P<bodyNoAggre>.*)\s*\)\s+on\s+(?P<baseVar>[^\s]*)\s+with\s+(?P<func>[^\s\(]*)\((?P<targetVar>[^\s]*)\)\s+as\s+(?P<asVar>[^\s]*)\s*", re.I)

def parse_rule(line):


	res = rule_pattern.match(line)
	head_str = res.group("head")
	body_str = res.group("body")

	head = parse_extended_atom(head_str)


	res = aggre_pattern.match(body_str)
	aggregation = None
	if res:
		aggregation = Aggregation(Term.getTerm(res.group("baseVar"), "variable"), Term.getTerm(res.group("targetVar"), "variable"), Term.getTerm(res.group("asVar"), "variable"), res.group("func").upper())
		body_str = res.group("bodyNoAggre")
		Term.setTerm(head.atom.predicate.name, head.atom.predicate.type, True)

	body_str_list = re.split(r'\s+and\s+', body_str)
	body = []
	negative_body = []
	for str in body_str_list:
		ea = parse_extended_atom(str.strip())
		if ea.atom.negation:
			negative_body.append(ea)
		else:
			body.append(ea)

	return Rule(head, body, negative_body = negative_body, aggregation = aggregation)


def parse_data(f):
	"""
	:param f: A File Object
	:return: A DataStore
	"""
	D = DataStore()
	if f.name.endswith(".nt"):
		for line in f.readlines():
			triple = parse_nt_line(line)
			if not triple:
				continue
			subj, pred, obj = triple
			D.add(Term.getTerm(subj, "constant"), Term.getTerm(pred, "constant"), Term.getTerm(obj, "constant") if (not obj.isdigit() and obj[0] != "\"") else (Term.getTerm(obj, "literal") if not obj.isdigit() else Term.getTerm(float(obj), "digital")))

	return D

def parse_rules(f):
	R = set()
	if f.name.endswith(".rules"):
		rule_str = str()
		for line in f.readlines():
			if re.match(r'^\s*\#.*', line):
				continue
			rule_str += line
			if re.match(r'[^.]*\.\s*', line):
				try:
					rule = parse_rule(rule_str)
					R.add(rule)
				except:
					warnings.warn(rule_str + " doesn't satisfy the syntax!")
				rule_str = str()
	else:
		warnings.warn("Rules file must end with .rules!")

	return R


def main():
	"""
	f = open("/Users/RC5920/Documents/LUBM_generator/nt_data/univ0.nt", "r")
	f2 = open(
		"/Users/RC5920/Documents/LUBM_generator/nt_data/univ1.nt",
		"r")
	start = time.time()
	D = parse_data(f)
	print("Init data set time: " + str(time.time() - start))
	print("Length: " + str(len(D)))

	start = time.time()
	D2 = parse_data(f2)
	print("Init data set time: " + str(time.time() - start))
	print("Length: " + str(len(D2)))

	start = time.time()
	D3 = D + D2
	print("Merge two data stores time: " + str(time.time() - start))
	print("Length: " + str(len(D3)))


	start = time.time()
	D += D2
	print("Merge two data stores time: " + str(time.time() - start))
	print("Length: " + str(len(D)))

	qs = Term.getTerm("?X", "variable")
	qp = Term.getTerm("http://swat.cse.lehigh.edu/onto/univ-bench.owl#name", "constant")
	qo = Term.getTerm("?Y", "variable")
	start = time.time()
	rs = D3.query(qs, qp, qo)
	print("Query (" + qs.name + ", " + qp.name + ", " + qo.name +  ") and get " + str(len(rs.res)) + " results time: " + str(time.time() - start))
	"""


	"""
	for item in res:
		line = str()
		for ele in item:
			line = line + str(ele) + " "
		print(line)
	"""

	r = parse_rule("<neighbourMaxAirTemperatureMeasurementPlus1>(X, Y) :- <neighbourMaxAirTemperatureMeasurement>(X, G) and bind(func:bind_EXAMPLE(G) as Y) .")
	print(r)

	r1 = parse_rule("crowded(P) :- <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>(P, <https://w3id.org/bot#Zone>) and bind (2+P*(3-4) as Z) .")
	print(r1)
	r2 = parse_rule("crowded(E) :- <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>(E, <https://w3id.org/bot#Zone>) and bind (2+E*(3-4) as Q) .")
	print(r2)
	if r1 == r2:
		print("Equal!")
	#rule = parse_rule("crowded(P) :- not <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>(P, <https://w3id.org/bot#Zone>) and <https://w3id.org/platoon/hasOccupancy>(P, E) and <https://w3id.org/seas/evaluation>(E, O) and <https://w3id.org/seas/evaluatedSimpleValue>(O, N)")
	#print(parse_extended_atom("Boxminus[5](not <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>(P, <https://w3id.org/bot#Zone>))"))
	#print(parse_extended_atom("Boxminus[5](<https://w3id.org/bot#Zone>(P, Z))"))
	print("end")



	with open("/testData/testAggreRule.rules") as f:
		R = parse_rules(f)
		for rule in R:
			print(rule)

	print("end")




if __name__ == "__main__":
	main()