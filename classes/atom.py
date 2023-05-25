class Atom:
    def __init__(self, predicate, subject, object, negation = False):
        """
        :param predicate: A Term
        :param subject: A Term
        :param object: A Term
        :param negation: Boolean
        """
        self.predicate = predicate
        self.subject = subject
        self.object = object
        self.negation = negation
        self.hash_code = hash(str(self.predicate) + "*" + (str(self.subject) if self.subject.type == "constant" else "") + "*" + (str(self.object) if self.object.type == "constant" else "") + "*" + ("1" if self.negation == True else "0"))


    def __str__(self):
        return ("not " if self.negation else "") + str(self.predicate) + "(" + str(self.subject) + ", " + str(self.object) + ")"

    def __eq__(self, other):
        return isinstance(other, Atom) and (self.predicate == other.predicate) and (self.subject == other.subject or (self.subject.type == "variable" and other.subject.type == "variable")) and (self.object == other.object or (self.object.type == "variable" and other.object.type == "variable"))

    def __hash__(self):
        return self.hash_code