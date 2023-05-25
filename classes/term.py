import re


class Term:
    """
    A term contains a name and a type
    """
    individuals_map = {}
    variables_map = {}
    def __init__(self, name, type):
        """
        Args:
            name (a string or a digit):
            type ("constant" or "variable"):
        """

        self.name = name
        """
        #To be extended
        self.name_space = None
        self.local_name = None
        if (not name[0].isdigit()) and (name[0] != "\""):
            strs = name.split("#", 1)
            self.name_space = strs[0]
            self.local_name = strs[1]
        """
        self.type = type
        self.aggregation_property = False
        self.hash_code = hash(self.type + "$" + self.name)
        #self.hash_code = hash(self.type + "$" + str(self.name))

    @staticmethod
    def getTerm(value, type = None):
        if type == "constant":
            if value in Term.individuals_map:
                return Term.individuals_map[value]
            else:
                new_term = Term(value, type)
                Term.individuals_map[value] = new_term
                return new_term
        elif type == "variable":
            if value in Term.variables_map:
                return Term.variables_map[value]
            else:
                new_term = Term(value, type)
                Term.variables_map[value] = new_term
                return new_term
        else:
            return value

    @staticmethod
    def verify_type(ele, type):
        if isinstance(ele, Term) and ele.type == type:
            return True
        else:
            return False

    @staticmethod
    def setTerm(name, type, aggregation_property):
        if type == "constant":
            if name in Term.individuals_map:
                Term.individuals_map[name].aggregation_property = aggregation_property
            else:
                new_term = Term(name, type)
                new_term.aggregation_property = aggregation_property
                Term.individuals_map[name] = new_term


    def __eq__(self, other):
        try:
            if self.name == other.name:
            #if self.hash_code == other.hash_code:
                return True
            else:
                return False
        except:
            return False

    def __ne__(self, other):
        try:
            if self.name == other.name:
                # if self.hash_code == other.hash_code:
                return False
            else:
                return True
        except:
            return True

    def __str__(self):
        if self.type == "constant" and re.match(r'[^\"\d]',(self.name)[0]):
            return "<" + self.name + ">"
        else:
            return self.name

    def __hash__(self):
        return self.hash_code

