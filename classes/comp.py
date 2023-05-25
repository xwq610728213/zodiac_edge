from classes.term import Term


class Compare:
    def __init__(self, ele1, comparator, ele2, negation = False):
        """

        :param ele1: A Term or a number
        :param comparator: ">", "<", "<=", ">=" or "=",
        :param ele2: A Term or a number
        """
        self.subject = None
        self.predicate = None
        self.object = None
        if comparator == "<" or comparator == "<=":
            self.subject = ele2
            self.predicate = ">" if comparator == "<" else ">="
            self.object = ele1
        else:
            self.subject = ele1
            self.predicate = comparator
            self.object = ele2
        self.negation = negation
        self.hash_code = hash("COMP:" + ("" if (isinstance(self.subject, Term) and self.subject.type == "variable") else str(self.subject)) + ":" + self.predicate + ":" + ("" if (isinstance(self.object, Term) and self.object.type == "variable") else str(self.object)))

    def __eq__(self, other):
        if isinstance(other, Compare) and self.hash_code == other.hash_code:
            return True
        else:
            return False

    def __hash__(self):
        return self.hash_code

    def __str__(self):
        return "COMP(" + str(self.subject) + ", " + self.predicate + ", " + str(self.object) + ")"