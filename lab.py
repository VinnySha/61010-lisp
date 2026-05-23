"""
6.101 Lab:
LISP Interpreter Part 2
"""

#!/usr/bin/env python3
import sys

sys.setrecursionlimit(20_000)


#############################
# Scheme-related Exceptions #
#############################


class SchemeError(Exception):
    """
    A type of exception to be raised if there is an error with a Scheme
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class SchemeSyntaxError(SchemeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class SchemeNameError(SchemeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class SchemeEvaluationError(SchemeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SchemeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(value):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Scheme
                      expression
    """
    tokens = []
    current_token = []  # build this then add it to tokens when hit whitespace or ()
    in_comment = False

    for char in source:
        if char == ";":  # Start of a comment
            in_comment = True
        elif char.isspace():  # Whitespace separates tokens
            if char == "\n":
                in_comment = False
            if current_token:
                tokens.append("".join(current_token))
                current_token = []
        elif in_comment:  # Skip characters inside comments
            continue
        elif char in "()":  # Parentheses are separate tokens
            if current_token:
                tokens.append("".join(current_token))
                current_token = []
            tokens.append(char)

        else:  # Part of a token
            current_token.append(char)

    # Add the last token if any
    if current_token:
        tokens.append("".join(current_token))

    return tokens


def parse(inp):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    ['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')']
    ['+', 2, ['-', 5, 3], 7, 8]
    """

    def inner_parse(tokens):
        if len(tokens) == 0:
            raise SchemeSyntaxError("no input...")

        token = tokens.pop(0)

        if token == "(":  # ( marks start of S-expr
            expr = []
            while True:
                if len(tokens) == 0:  # We didn't find a close ).
                    raise SchemeSyntaxError("no closing paren found")
                if tokens[0] == ")":
                    tokens.pop(0)
                    return expr
                expr.append(inner_parse(tokens))

        elif token == ")":  # ) doesn't have a matching (
            raise SchemeSyntaxError("mismatched parens")

        # If first item is not a parentheses, it must be a single token.
        else:
            return number_or_symbol(token)

    result = inner_parse(inp)
    if len(inp) != 0:
        raise SchemeSyntaxError("random extra elements included")
    return result


######################
# Built-in Functions #
######################


def calc_sub(*args):
    """Function that subtracts all args from first"""
    if len(args) == 1:
        return -args[0]

    first_num, *rest_nums = args
    return first_num - scheme_builtins["+"](*rest_nums)


def calc_mult(*args):
    """Function that multiplies all args together"""
    if len(args) == 1:
        return args[0]

    first_num, *rest_nums = args
    return first_num * calc_mult(*rest_nums)


def calc_div(*args):
    """Function that divides all args from left to right"""
    if len(args) == 1:
        return args[0]

    first_num, *rest_nums = args
    result = first_num
    for num in rest_nums:
        result /= num
    return result


def equals(*args):
    """Function that checks if all args from left to right are equal"""
    for i in range(len(args) - 1):
        if args[i] != args[i + 1]:
            return False
    return True


def gt(*args):
    """Function that checks if args are strictly increasing"""
    for i in range(len(args) - 1):
        if args[i] <= args[i + 1]:
            return False
    return True


def gte(*args):
     """Function that checks if args are equal or increasing"""
    for i in range(len(args) - 1):
        if args[i] < args[i + 1]:
            return False
    return True


def lt(*args):
    """Function that checks if args are strictly decreasing"""
    for i in range(len(args) - 1):
        if args[i] >= args[i + 1]:
            return False
    return True


def lte(*args):
    """Function that checks if args are equal or decreasing"""
    for i in range(len(args) - 1):
        if args[i] > args[i + 1]:
            return False
    return True


def negation(*args):
    """Function that negates the truth value of the argument"""
    if len(args) > 1 or len(args) == 0:
        raise SchemeEvaluationError("not evaluated with 0 or >1 args")
    return not args[0]


def cons_car(*cons):
    """Function that returns the first element of a cons"""
    if len(cons) != 1 or not isinstance(cons[0], Pair):
        raise SchemeEvaluationError("car called on non-cons object or too many args")
    return cons[0].get_car()


def cons_cdr(*cons):
    """Function that returns the second element of a cons"""
    if len(cons) != 1 or not isinstance(cons[0], Pair):
        raise SchemeEvaluationError("cdr called on non-cons object or too many args")
    return cons[0].get_cdr()


def cons(*args):
    """Function that creates a new cons with the given args"""
    if len(args) != 2:
        raise SchemeEvaluationError("incorr. # args passed to cons")
    return Pair(args[0], args[1])


def make_list(*args):
    """Function that creates a new list with the given args"""
    if len(args) == 0:
        return []
    return Pair(args[0], make_list(*args[1:]))


def check_if_list(*args):
    """Function that checks if args is a list"""
    if len(args) != 1:
        raise SchemeEvaluationError("wrong # args for call to list?")
    
    if args[0] == [] or (isinstance(args[0], Pair) and args[0].get_cdr() == []):
        return True
    return isinstance(args[0], Pair) and check_if_list(args[0].get_cdr())

def length(*args):
    """Function that returns the length of a list"""
    if len(args) != 1 or not isinstance(args[0], (Pair, list)):
        raise SchemeEvaluationError("wrong # args for call to length")
    elif isinstance(args[0], list):
        return 0
    return 1 + length(args[0].get_cdr())


def index(*args):
    """Function that returns the element at the given index"""
    if len(args) != 2:
        raise SchemeEvaluationError("wrong # args passed to list-ref")
    input_list = args[0]
    ind = args[1]
    if not isinstance(ind, int) or not isinstance(input_list, (Pair, list)):
        raise SchemeEvaluationError("Index is not int or list is not list.")
    def loop(cons, index):
        if isinstance(cons, list):
            raise SchemeEvaluationError
        if index == 0:
            if not isinstance(cons, Pair):
                raise SchemeEvaluationError("item at correct index is not in Pair obj")
            return cons.get_car()
        return loop(cons.get_cdr(), index-1)
    return loop(input_list, ind)
            

def copy_list(lst):
    """Shallow copy of a linked list (new Pair nodes, same element values)."""
    if lst == []:
        return []
    return Pair(lst.get_car(), copy_list(lst.get_cdr()))


def append_two(a, b):
    """Append linked list b onto the end of a; both must be lists. Returns a new list."""
    if a == []:
        return copy_list(b)
    return Pair(a.get_car(), append_two(a.get_cdr(), b))


def list_append(*args):
    """Function that appends all args together"""
    # Check if any argument is not a list
    for arg in args:
        if not check_if_list(arg):
            raise SchemeEvaluationError("append can only be called with list arguments")
    
    # Base case: if no arguments, return the empty list (represented as an empty cons)
    if len(args) == 0:
        return []
    
    # Recursively append lists and build the cons structure
    result = []
    for lst in args:
        result = append_two(result, lst)
    return result


def do_begin(*args):
    return args[-1]


# Most super/parent frame
scheme_builtins = {
    "#t": True,
    "#f": False,
    "+": lambda *args: sum(args),
    "-": calc_sub,
    "*": calc_mult,
    "/": calc_div,
    "equal?": equals,
    ">": gt,
    ">=": gte,
    "<": lt,
    "<=": lte,
    "not": negation,
    "car": cons_car,
    "cdr": cons_cdr,
    "list": make_list,
    "cons": cons,
    "list?": check_if_list,
    "length": length,
    "list-ref":index,
    "append":list_append,
    "begin" : do_begin
}

special_forms = {"lambda", "define", "if", "and", "or"}


##############
# Evaluation #
##############


class Frame:
    """
    Class that establishes frames which includes object
    names and their mappings to the objects themselves.
    Attributes are the parent frame and the dictionary of mappings.
    """

    def __init__(self, parent, mapping):
        self.parent = parent
        self.mapping = mapping

    def __getitem__(self, var):
        if var in self.mapping:
            return self.mapping[var]
        elif self.parent:
            return self.parent[var]
        raise SchemeNameError(var, "does not exist")

    def __setitem__(self, var, value):
        self.mapping[var] = value

    def __str__(self):
        return str(self.mapping)


class Function:
    """
    Function class that establishes functions within frames.
    Attributes are the enclosing frame of the function (where
    it's defined), the parameters of the function, and the
    body of the function is a scheme tree.
    """

    def __init__(self, enclosing, params, body):
        self.enclosing = enclosing
        self.params = params if isinstance(params, list) else [params]
        self.body = body

    def call(self, args, frame):
        """
        Calls this function in the given frame with the given arguments.
        """
        if len(args) != len(self.params):
            raise SchemeEvaluationError(
                "Incorrect number of arguments passed to function"
            )

        # step 1, create new frame, parent is this func's enclosing frame
        new_frame = Frame(self.enclosing, {})

        # step 2, bind func's parameters to evaluated args in the new frame
        for param, arg in zip(self.params, args):
            new_frame[param] = arg

        # step 3, eval the func's body in the new frame
        return evaluate(self.body, new_frame)


class Pair:

    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def get_car(self):
        return self.car

    def get_cdr(self):
        return self.cdr
    
    def __str__(self):
        return f"(cons {self.car} {self.cdr})"


def make_initial_frame():
    init_frame = Frame(scheme_builtins, {})
    return init_frame


def evaluate(tree, frame=make_initial_frame()):
    """
    Evaluate the given syntax tree according to the rules of the Scheme
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """

    if isinstance(tree, str) and tree not in special_forms:
        if tree in {"#t", "#f"}:
            return scheme_builtins[tree]
        try:
            return frame[tree]
        except KeyError as excep:
            raise SchemeNameError(tree, "does not exist in frame") from excep

    elif isinstance(tree, (int, float)):
        return tree
    # At this point tree must be a list

    elif not tree:  # This is an empty list representation
        return []

    first = tree[0]

    if first == "define":
        # Must have (define NAME EXPR)
        if len(tree) != 3:
            raise SchemeEvaluationError("define called with wrong # of args")

        name = tree[1]

        # Short hand func definition
        if isinstance(name, list):
            subtree = name
            name = subtree[0]
            params = subtree[1:]
            body = tree[2]
            new_func = Function(frame, params, body)
            frame[name] = new_func
            return new_func

        elif not isinstance(name, str):
            raise SchemeEvaluationError("define NAME is not a string")

        value = evaluate(tree[2], frame)
        frame[name] = value
        return value

    elif first == "lambda":
        # Must have (lambda PARAMS BODY)
        if len(tree) != 3:
            raise SchemeEvaluationError("lambda called w wrong # of args")

        params = tree[1]
        body = tree[2]
        new_func = Function(frame, params, body)
        return new_func

    elif first == "if":
        pred = tree[1]
        true_exp = tree[2]
        false_exp = tree[3]
        return evaluate(true_exp if evaluate(pred, frame) else false_exp, frame)

    elif first == "and":
        args = tree[1:]
        if len(args) == 0:
            return True
        for arg in args:
            if not evaluate(arg, frame):
                return False
        return True

    elif first == "or":
        args = tree[1:]
        if len(args) == 0:
            return False
        for arg in args:
            if evaluate(arg, frame):
                return True
        return False

    func = evaluate(first, frame)

    if not callable(func) and not isinstance(func, Function):
        raise SchemeEvaluationError("first item in S-expr is not a function")

    evaluated = [evaluate(branch, frame) for branch in tree[1:]]

    if isinstance(func, Function):
        return func.call(evaluated, frame)

    return func(*evaluated)  # unpack list of args


if __name__ == "__main__":
    import os

    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    import schemerepl

    schemerepl.SchemeREPL(
        sys.modules[__name__], use_frames=True, verbose=False, repl_frame=None
    ).cmdloop()
