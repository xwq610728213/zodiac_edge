"""
Named as Stratify, on reality Hyper-node ;)
"""

import warnings

from classes.atom import Atom
from util.parser import parse_rules

#def rule_dependancy_dfs(strata_index, visited_rules, rule):

def build_dependancy_graph(rules):
    positive_dependancy_graph = {}
    negative_dependancy_graph = {}
    for rule1 in rules:
        for rule2 in rules:
            flag = False
            for ea in rule2.positive_body:
                if not isinstance(ea.atom, Atom):
                    continue
                if ea.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and rule1.head.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    if ea.atom.object.type == "constant" and ea.atom.object == rule1.head.atom.object:
                        flag = True
                elif ea.atom.predicate == rule1.head.atom.predicate:
                    flag = True
            if rule1 not in positive_dependancy_graph:
                positive_dependancy_graph[rule1] = {}

            positive_dependancy_graph[rule1][rule2] = flag

            flag = False
            for ea in rule2.negative_body:
                if ea.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and rule1.head.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    if ea.atom.object.type == "constant" and ea.atom.object == rule1.head.atom.object:
                        flag = True
                elif ea.atom.predicate == rule1.head.atom.predicate:
                    flag = True
            if rule1 not in negative_dependancy_graph:
                negative_dependancy_graph[rule1] = {}
            negative_dependancy_graph[rule1][rule2] = flag


    return (positive_dependancy_graph, negative_dependancy_graph)

def update_dependancy_graph(rules, positive_dependancy_graph, negative_dependancy_graph, old_rules):
    """
    new_rules = set()
    for rule in rules:
        if rule not in old_rules:
            new_rules.add(rule)

    rules = new_rules
    """
    for rule1 in old_rules:
        for rule2 in rules:
            flag = False
            for ea in rule2.positive_body:
                if isinstance(ea.atom, Atom):
                    if ea.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and rule1.head.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                        if ea.atom.object.type == "constant" and ea.atom.object == rule1.head.atom.object:
                            flag = True
                    elif ea.atom.predicate == rule1.head.atom.predicate:
                        flag = True
            positive_dependancy_graph[rule1][rule2] = flag

            flag = False
            for ea in rule2.negative_body:
                if isinstance(ea.atom, Atom):
                    if ea.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and rule1.head.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                        if ea.atom.object.type == "constant" and ea.atom.object == rule1.head.atom.object:
                            flag = True
                    elif ea.atom.predicate == rule1.head.atom.predicate:
                        flag = True
            negative_dependancy_graph[rule1][rule2] = flag

            flag = False
            for ea in rule1.positive_body:
                if not isinstance(ea.atom, Atom):
                    continue
                if ea.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and rule2.head.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                    if ea.atom.object.type == "constant" and ea.atom.object == rule2.head.atom.object:
                        flag = True
                elif ea.atom.predicate == rule2.head.atom.predicate:
                    flag = True
            if rule2 not in positive_dependancy_graph:
                positive_dependancy_graph[rule2] = {}

            positive_dependancy_graph[rule2][rule1] = flag

            flag = False
            for ea in rule1.negative_body:
                if isinstance(ea.atom, Atom):
                    if ea.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and rule2.head.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                        if ea.atom.object.type == "constant" and ea.atom.object == rule2.head.atom.object:
                            flag = True
                    elif ea.atom.predicate == rule2.head.atom.predicate:
                        flag = True
            if rule2 not in negative_dependancy_graph:
                negative_dependancy_graph[rule2] = {}
            negative_dependancy_graph[rule2][rule1] = flag

    for rule1 in rules:
        for rule2 in rules:
            flag = False
            for ea in rule2.positive_body:
                if isinstance(ea.atom, Atom):
                    if ea.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and rule1.head.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                        if ea.atom.object.type == "constant" and ea.atom.object == rule1.head.atom.object:
                            flag = True
                    elif ea.atom.predicate == rule1.head.atom.predicate:
                        flag = True
            if rule1 not in positive_dependancy_graph:
                positive_dependancy_graph[rule1] = {}

            positive_dependancy_graph[rule1][rule2] = flag

            flag = False
            for ea in rule2.negative_body:
                if isinstance(ea.atom, Atom):
                    if ea.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type" and rule1.head.atom.predicate.name == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
                        if ea.atom.object.type == "constant" and ea.atom.object == rule1.head.atom.object:
                            flag = True
                    elif ea.atom.predicate == rule1.head.atom.predicate:
                        flag = True
            if rule1 not in negative_dependancy_graph:
                negative_dependancy_graph[rule1] = {}
            negative_dependancy_graph[rule1][rule2] = flag

    return positive_dependancy_graph, negative_dependancy_graph, old_rules | rules


def compute_strongly_connected_components(vertex, pgraph, ngraph):
    visited = {}
    for node in vertex:
        visited[node] = False

    s = []
    colored = {}
    for node in vertex:
        colored[node] = False

    def dfs1(u, pgraph, ngraph, visited, s):
        visited[u] = True
        for v in pgraph[u].keys():
            if (pgraph[u][v] or ngraph[u][v]) and visited[v] == False:
                dfs1(v, pgraph, ngraph, visited, s)
        s.append(u)

    def dfs2(u, colored, inversed_pgraph, inversed_ngraph, num):
        colored[u] = num
        for v in inversed_pgraph[u].keys():
            if (inversed_pgraph[u][v] or inversed_ngraph[u][v]) and colored[v] == False:
                dfs2(v, colored, inversed_pgraph, inversed_ngraph, num)

    num = 0
    for v in vertex:
        if visited[v] == False:
            dfs1(v, pgraph, ngraph, visited, s)

    inversed_pgraph = {}
    inversed_ngraph = {}
    for v1 in vertex:
        for v2 in vertex:
            if v2 not in inversed_pgraph:
                inversed_pgraph[v2] = {}
                inversed_ngraph[v2] = {}
            inversed_pgraph[v2][v1] = pgraph[v1][v2]
            inversed_ngraph[v2][v1] = ngraph[v1][v2]

    for v in reversed(s):
        if colored[v] == False:
            num = num + 1
            dfs2(v, colored, inversed_pgraph, inversed_ngraph, num)

    return colored

def create_hyper_nodes(rules, positive_dependancy_graph, negative_dependancy_graph):
    rule_to_hyper_node_map = compute_strongly_connected_components(rules, positive_dependancy_graph, negative_dependancy_graph)
    hyper_nodes_to_rules_map = {}
    hyper_nodes = set()
    for k,v in rule_to_hyper_node_map.items():
        if v not in hyper_nodes_to_rules_map:
            hyper_nodes_to_rules_map[v] = set()
            hyper_nodes.add(v)
        hyper_nodes_to_rules_map[v].add(k)

    return rule_to_hyper_node_map, hyper_nodes_to_rules_map, hyper_nodes

def build_hyper_nodes_dependancy(rules, rule_to_hyper_node_map, hyper_nodes_to_rules_map, positive_dependancy_graph, negative_dependancy_graph):
    hyper_positive_dependancy_graph = {}
    hyper_negative_dependancy_graph = {}

    for rule1 in rules:
        for rule2 in rules:
            if rule_to_hyper_node_map[rule1] not in hyper_positive_dependancy_graph:
                hyper_positive_dependancy_graph[rule_to_hyper_node_map[rule1]] = {}
            if rule_to_hyper_node_map[rule2] not in hyper_positive_dependancy_graph[rule_to_hyper_node_map[rule1]]:
                hyper_positive_dependancy_graph[rule_to_hyper_node_map[rule1]][rule_to_hyper_node_map[rule2]] = False
            if rule_to_hyper_node_map[rule1] != rule_to_hyper_node_map[rule2]:
                hyper_positive_dependancy_graph[rule_to_hyper_node_map[rule1]][rule_to_hyper_node_map[rule2]] = hyper_positive_dependancy_graph[rule_to_hyper_node_map[rule1]][rule_to_hyper_node_map[rule2]] or positive_dependancy_graph[rule1][rule2]

            if rule_to_hyper_node_map[rule1] not in hyper_negative_dependancy_graph:
                hyper_negative_dependancy_graph[rule_to_hyper_node_map[rule1]] = {}
            if rule_to_hyper_node_map[rule2] not in hyper_negative_dependancy_graph[rule_to_hyper_node_map[rule1]]:
                hyper_negative_dependancy_graph[rule_to_hyper_node_map[rule1]][rule_to_hyper_node_map[rule2]] = False
            hyper_negative_dependancy_graph[rule_to_hyper_node_map[rule1]][rule_to_hyper_node_map[rule2]] = hyper_negative_dependancy_graph[rule_to_hyper_node_map[rule1]][rule_to_hyper_node_map[rule2]] or negative_dependancy_graph[rule1][rule2]

    if not has_circle(hyper_negative_dependancy_graph):
        return hyper_positive_dependancy_graph, hyper_negative_dependancy_graph
    else:
        warnings.warn("A circle is detected in negative hyper graph!")
        return None, None

def has_circle(graph):
    in_degree = {}
    not_visited = set()
    for node1 in graph.keys():
        in_degree[node1] = 0
        not_visited.add(node1)
        for node2 in graph.keys():
            if graph[node2][node1]:
                in_degree[node1] += 1

    next_targets = set()
    for node in graph.keys():
        if in_degree[node] == 0:
            next_targets.add(node)

    while len(next_targets) > 0:
        new_next_targets = set()
        for n in next_targets:
            not_visited.discard(n)
            for v in not_visited:
                if graph[n][v]:
                    in_degree[v] -= 1
                if in_degree[v] == 0:
                    new_next_targets.add(v)
        next_targets = new_next_targets

    if len(not_visited) > 0:
        return True
    else:
        return False



def stratify(rules):
    """
    :param rules: Rules to be stratified(Hyper-noded)
    :param positive_dependancy_graph: positive dependancy graph between rules
    :param negative_dependancy_graph: negative dependancy graph between rules
    :return:
    """

    positive_dependancy_graph, negative_dependancy_graph = build_dependancy_graph(rules)


    rule_to_hyper_node_map, hyper_nodes_to_rules_map, hyper_nodes = create_hyper_nodes(rules, positive_dependancy_graph, negative_dependancy_graph)
    hyper_positive_dependancy_graph, hyper_negative_dependancy_graph = build_hyper_nodes_dependancy(rules, rule_to_hyper_node_map, hyper_nodes_to_rules_map, positive_dependancy_graph, negative_dependancy_graph)

    hyper_nodes_in_degree = {}
    for hyper_node in hyper_nodes:
        hyper_nodes_in_degree[hyper_node] = 0

    for hn1 in hyper_nodes:
        for hn2 in hyper_nodes:
            if hyper_positive_dependancy_graph[hn2][hn1] or hyper_negative_dependancy_graph[hn2][hn1]:
                hyper_nodes_in_degree[hn1] += 1


    return positive_dependancy_graph, negative_dependancy_graph, hyper_nodes_in_degree, rule_to_hyper_node_map, hyper_nodes_to_rules_map, hyper_nodes, hyper_positive_dependancy_graph, hyper_negative_dependancy_graph

def re_stratify_plus(new_rules, positive_dependancy_graph, negative_dependancy_graph, old_rules, rule_to_hyper_node_map, hyper_nodes_to_rules_map, hyper_nodes, hyper_positive_dependancy_graph, hyper_negative_dependancy_graph, hyper_nodes_dbs):
    positive_dependancy_graph, negative_dependancy_graph, all_rules = update_dependancy_graph(new_rules, positive_dependancy_graph, negative_dependancy_graph, old_rules)
    """
    new_rules = set()

    for rule in rules:
        if rule not in rule_to_hyper_node_map:
            new_rules.add(rule)

    rules = new_rules
    """
    index_hyper_node = len(hyper_nodes) + 1

    for rule in new_rules:
        rule_to_hyper_node_map[rule] = index_hyper_node
        hyper_nodes_to_rules_map[index_hyper_node] = {rule}
        hyper_nodes.add(index_hyper_node)
        index_hyper_node += 1

    for rule in new_rules:
        for hn in hyper_nodes:
            if hn not in hyper_positive_dependancy_graph:
                hyper_positive_dependancy_graph[hn] = {}
            hyper_positive_dependancy_graph[hn][rule_to_hyper_node_map[rule]] = False
            if rule_to_hyper_node_map[rule] not in hyper_positive_dependancy_graph:
                hyper_positive_dependancy_graph[rule_to_hyper_node_map[rule]] = {}
            hyper_positive_dependancy_graph[rule_to_hyper_node_map[rule]][hn] = False

            if hn not in hyper_negative_dependancy_graph:
                hyper_negative_dependancy_graph[hn] = {}
            hyper_negative_dependancy_graph[hn][rule_to_hyper_node_map[rule]] = False
            if rule_to_hyper_node_map[rule] not in hyper_negative_dependancy_graph:
                hyper_negative_dependancy_graph[rule_to_hyper_node_map[rule]] = {}
            hyper_negative_dependancy_graph[rule_to_hyper_node_map[rule]][hn] = False

            for rule2 in hyper_nodes_to_rules_map[hn]:
                hyper_positive_dependancy_graph[hn][rule_to_hyper_node_map[rule]] = hyper_positive_dependancy_graph[hn][rule_to_hyper_node_map[rule]] or positive_dependancy_graph[rule2][rule]
                hyper_positive_dependancy_graph[rule_to_hyper_node_map[rule]][hn] = hyper_positive_dependancy_graph[rule_to_hyper_node_map[rule]][hn] or positive_dependancy_graph[rule][rule2]
                hyper_negative_dependancy_graph[hn][rule_to_hyper_node_map[rule]] = hyper_negative_dependancy_graph[hn][rule_to_hyper_node_map[rule]] or negative_dependancy_graph[rule2][rule]
                hyper_negative_dependancy_graph[rule_to_hyper_node_map[rule]][hn] = hyper_negative_dependancy_graph[rule_to_hyper_node_map[rule]][hn] or negative_dependancy_graph[rule][rule2]

    #modified
    hn_to_newhn_node_map, newhn_nodes_to_hn_map, new_hns = create_hyper_nodes(hyper_nodes, hyper_positive_dependancy_graph, hyper_negative_dependancy_graph)

    updated_hyper_nodes = set()
    for rule in new_rules:
        updated_hyper_nodes.add(hn_to_newhn_node_map[rule_to_hyper_node_map[rule]])

    new_hyper_positive_dependancy_graph, new_hyper_negative_dependancy_graph = build_hyper_nodes_dependancy(hyper_nodes, hn_to_newhn_node_map, newhn_nodes_to_hn_map, hyper_positive_dependancy_graph, hyper_negative_dependancy_graph)

    # Merge hyper nodes
    new_rule_to_hyper_node_map = {}
    new_hyper_nodes_to_rules_map = {}
    new_hyper_nodes_dbs = {}
    visited_hyper_nodes = set()
    visited_new_hyper_nodes = set()
    for rule in rule_to_hyper_node_map.keys():
        new_rule_to_hyper_node_map[rule] = hn_to_newhn_node_map[rule_to_hyper_node_map[rule]]
        if hn_to_newhn_node_map[rule_to_hyper_node_map[rule]] not in new_hyper_nodes_to_rules_map:
            new_hyper_nodes_to_rules_map[hn_to_newhn_node_map[rule_to_hyper_node_map[rule]]] = set()
        new_hyper_nodes_to_rules_map[hn_to_newhn_node_map[rule_to_hyper_node_map[rule]]].add(rule)

        #Merge hyper_nodes_dbs
        if rule_to_hyper_node_map[rule] not in visited_hyper_nodes:
            visited_hyper_nodes.add(rule_to_hyper_node_map[rule])
            if rule_to_hyper_node_map[rule] in hyper_nodes_dbs:
                if hn_to_newhn_node_map[rule_to_hyper_node_map[rule]] not in visited_new_hyper_nodes:
                    visited_new_hyper_nodes.add(hn_to_newhn_node_map[rule_to_hyper_node_map[rule]])
                    new_hyper_nodes_dbs[hn_to_newhn_node_map[rule_to_hyper_node_map[rule]]] = hyper_nodes_dbs[rule_to_hyper_node_map[rule]]
                else:
                    new_hyper_nodes_dbs[hn_to_newhn_node_map[rule_to_hyper_node_map[rule]]] += hyper_nodes_dbs[rule_to_hyper_node_map[rule]]

    return positive_dependancy_graph, negative_dependancy_graph, all_rules, updated_hyper_nodes, new_rule_to_hyper_node_map, new_hyper_nodes_to_rules_map, new_hns, new_hyper_positive_dependancy_graph, new_hyper_negative_dependancy_graph, new_hyper_nodes_dbs


def re_stratify_minus(deleting_rules, positive_dependancy_graph, negative_dependancy_graph, old_rules, rule_to_hyper_node_map, hyper_nodes_to_rules_map, hyper_nodes, hyper_positive_dependancy_graph, hyper_negative_dependancy_graph, hyper_nodes_dbs):

    influenced_hyper_nodes = set()

    rest_rules = old_rules - deleting_rules

    new_positive_dependancy_graph = {}
    new_negative_dependancy_graph = {}

    for rule1 in rest_rules:
        if rule1 not in new_positive_dependancy_graph:
            new_positive_dependancy_graph[rule1] = {}
            new_negative_dependancy_graph[rule1] = {}
        for rule2 in rest_rules:
            new_positive_dependancy_graph[rule1][rule2] = positive_dependancy_graph[rule1][rule2]
            new_negative_dependancy_graph[rule1][rule2] = negative_dependancy_graph[rule1][rule2]


    new_rule_to_hyper_node_map, new_hyper_nodes_to_rules_map, new_hyper_nodes = create_hyper_nodes(rest_rules, new_positive_dependancy_graph, new_negative_dependancy_graph)
    new_hyper_positive_dependancy_graph, new_hyper_negative_dependancy_graph = build_hyper_nodes_dependancy(rest_rules,
                                                                                                    new_rule_to_hyper_node_map,
                                                                                                    new_hyper_nodes_to_rules_map,
                                                                                                    new_positive_dependancy_graph,
                                                                                                    new_negative_dependancy_graph)
    new_hyper_nodes_dbs = {}

    for nhn in new_hyper_nodes:
        for ohn in hyper_nodes:
            if new_hyper_nodes_to_rules_map[nhn] == hyper_nodes_to_rules_map[ohn]:
                new_hyper_nodes_dbs[nhn] = hyper_nodes_dbs[ohn]

    for dr in deleting_rules:
        for rule2 in rest_rules:
            if positive_dependancy_graph[dr][rule2] or negative_dependancy_graph[dr][rule2] or rule_to_hyper_node_map[dr] == rule_to_hyper_node_map[rule2]:
                influenced_hyper_nodes.add(new_rule_to_hyper_node_map[rule2])



    return new_positive_dependancy_graph, new_negative_dependancy_graph, rest_rules, influenced_hyper_nodes, new_rule_to_hyper_node_map, new_hyper_nodes_to_rules_map, new_hyper_nodes, new_hyper_positive_dependancy_graph, new_hyper_negative_dependancy_graph, new_hyper_nodes_dbs



def compute_topological_order(vertex, p_graph, n_graph, start_points = None):
    visited = set()
    q = []

    def dfs(u, p_graph, n_graph, visited, q):
        visited.add(u)
        for v in p_graph[u].keys():
            if (p_graph[u][v] or n_graph[u][v]) and (v not in visited):
                dfs(v, p_graph, n_graph, visited, q)
        q.append(u)


    if start_points:
        for u in start_points:
            if u not in visited:
                dfs(u, p_graph, n_graph, visited, q)
    else:
        for u in vertex:
            if u not in visited:
                dfs(u, p_graph, n_graph, visited, q)

    q.reverse()
    return q







if __name__ == "__main__":
    R = set()
    with open("/testData/testRules.rules") as f:
        R = parse_rules(f)

    with open("/testData/addRules.rules") as f:
        R2 = parse_rules(f)


    positive_dependancy_graph, negative_dependancy_graph, hyper_nodes_in_degree, rule_to_hyper_node_map, hyper_nodes_to_rules_map, hyper_nodes, hyper_positive_dependancy_graph, hyper_negative_dependancy_graph = stratify(R)

    print(hyper_nodes_to_rules_map)

    positive_dependancy_graph, negative_dependancy_graph, all_rules, updated_hyper_nodes, rule_to_hyper_node_map, hyper_nodes_to_rules_map, hyper_nodes, hyper_positive_dependancy_graph, hyper_negative_dependancy_graph = re_stratify_plus(R2, positive_dependancy_graph, negative_dependancy_graph, R, rule_to_hyper_node_map, hyper_nodes_to_rules_map, hyper_nodes, hyper_positive_dependancy_graph, hyper_negative_dependancy_graph)


    for hn in updated_hyper_nodes:
        print(hn)
        rules =  hyper_nodes_to_rules_map[hn]

    print(rule_to_hyper_node_map)

    print(hyper_negative_dependancy_graph)


