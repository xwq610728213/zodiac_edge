class WOperator:
    def __init__(self, name, window_size):
        if name not in ["Boxminus", "Diamondminus"]:
            raise ValueError("Only support (Boxminus, Diamondminus) as time window operators!")

        self.name = name
        self.window_size = window_size

    def __eq__(self, other):
        if isinstance(other, WOperator) and other.name == self.name and other.window_size == self.window_size:
            return True
        else:
            return False

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        return self.name + "[" + self.window_size + "]"

class EAtom:
    def __init__(self, atom, w_operator = None):
        """
        :param atom: An Atom or A Compare or A Bind
        :param w_operator: A WOperator
        """
        self.w_operator = w_operator
        self.atom = atom

    def __str__(self):
        return ((str(self.w_operator) + "(") if self.w_operator else "") + str(self.atom) + (")" if self.w_operator else "")

    def __eq__(self, other):
        if isinstance(other, EAtom) and self.w_operator == other.w_operator and self.atom == other.atom:
            return True
        else:
            return False

    def __hash__(self):
        return hash(str(self.w_operator) + str(hash(self.atom)))
