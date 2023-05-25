class Aggregation:
    def __init__(self, base_var, target_var, as_var, function):
        self.base_var = base_var
        self.target_var = target_var
        self.as_var = as_var
        self.function = function