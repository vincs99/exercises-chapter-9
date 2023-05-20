"""Implement symbolic expressions."""
import numbers
from functools import singledispatch


class Expression:
    """The parent directory.

    Implements initialization and basic operations.
    """

    def __init__(self, *o):
        """Initialize epressions."""
        self.operands = o
        self.value = None

    def __add__(self, other):
        """Add two expressions."""
        if isinstance(other, Expression):
            return Add(self, other)
        elif isinstance(other, numbers.Number):
            numexp = Number(other)
            return Add(self, numexp)

    def __radd__(self, other):
        """Reverse the operation."""
        term = Number(other)
        return term + self

    def __mul__(self, other):
        """Add two expressions."""
        if isinstance(other, Expression):
            return Mul(self, other)
        elif isinstance(other, numbers.Number):
            numexp = Number(other)
            return Mul(self, numexp)

    def __rmul__(self, other):
        """Reverse the operation."""
        term = Number(other)
        return term*self

    def __sub__(self, other):
        """Substract two expressions."""
        if isinstance(other, Expression):
            return Sub(self, other)
        elif isinstance(other, numbers.Number):
            numexp = Number(other)
            return Sub(self, numexp)

    def __rsub__(self, other):
        """Reverse the operations."""
        numsub = Number(other)
        return (numsub - self)

    def __truediv__(self, other):
        """Add two expressions."""
        if isinstance(other, Expression):
            return Div(self, other)
        elif isinstance(other, numbers.Number):
            numexp = Number(other)
            return Div(self, numexp)

    def __rtruediv__(self, other):
        """Reverse the operations."""
        numdiv = Number(other)
        return numdiv/self

    def __pow__(self, other):
        """Add two expressions."""
        if isinstance(other, Expression):
            return Pow(self, other)
        elif isinstance(other, numbers.Number):
            numexp = Number(other)
            return Pow(self, numexp)

    def __rpow__(self, other):
        """Reverse power operation."""
        term = Number(other)
        return term**self


class Opearator(Expression):
    """Define special operator expreesion features."""

    def __repr__(self):
        """Return official string representation."""
        return type(self).__name__ + repr(self.operands)

    def __str__(self):
        """Return readable string representation."""
        if self.precedence > self.operands[0].precedence:
            r0 = "(" + str(self.operands[0]) + ")"
        else:
            r0 = str(self.operands[0])
        if self.precedence > self.operands[1].precedence:
            r1 = "(" + str(self.operands[1]) + ")"
        else:
            r1 = str(self.operands[1])

        return r0 + f" {self.symbol} " + r1


class Add(Opearator):
    """Special addition expression."""

    symbol = "+"
    precedence = 0


class Mul(Opearator):
    """Special multiplication expression."""

    symbol = "*"
    precedence = 1


class Div(Opearator):
    """Special division expression."""

    symbol = "/"
    precedence = 1


class Sub(Opearator):
    """Special substraction expression."""

    symbol = "-"
    precedence = 0


class Pow(Opearator):
    """Special multiplication expression."""

    symbol = "^"
    precedence = 2


class Terminal(Expression):
    """Umbrella class for terminal type objects."""

    precedence = 3

    def __init__(self, value):
        """Add value in initialization."""
        super().__init__()
        self.value = value

    def __repr__(self):
        """Define official representation."""
        return repr(self.value)

    def __str__(self):
        """Define readable string representation."""
        return str(self.value)


class Number(Terminal):
    """A number expression."""

    def __init__(self, value):
        """Check instance is a number."""
        if isinstance(value, numbers.Number):
            super().__init__(value)
        else:
            raise TypeError(
                "Numbers class expects a Number type, not a random type."
            )


class Symbol(Terminal):
    """A number expression."""

    def __init__(self, value):
        """Check instance is a string."""
        if isinstance(value, str):
            super().__init__(value)
        else:
            raise TypeError(
                "Numbers class expects a Number type, not a random type."
            )


def postvisitor(expr, fn, **kwargs):
    """Visit an Expression in postorder applying a function to every node.

    Parameters
    ----------
    expr: Expression
        The expression to be visited.
    fn: function(node, *o, **kwargs)
        A function to be applied at each node. The function should take
        the node to be visited as its first argument, and the results of
        visiting its operands as any further positional arguments. Any
        additional information that the visitor requires can be passed in
        as keyword arguments.
    **kwargs:
        Any additional keyword arguments to be passed to fn.
    """
    stack = []
    visited = {}
    stack.append(expr)
    while stack:
        e = stack.pop()
        unvisited_children = []
        for o in e.operands:
            if o not in visited:
                unvisited_children.append(o)
        if unvisited_children:
            stack.append(e)
            stack += unvisited_children
        else:
            # Any children of e have been visited, so we can visit it.
            visited[e] = fn(e, *(visited[o] for o in e.operands), **kwargs)
    return visited[expr]


@singledispatch
def differentiate(expr, *args, **kwargs):
    """Differentiate an expression."""
    raise NotImplementedError(
        f"Cannot evaluate a {type(expr).__name__}")


@differentiate.register(Number)
def _(expr, *o, **kwargs):
    return Number(0.0)


@differentiate.register(Symbol)
def _(expr, *o, var, **kwargs):
    return Number(float(var == expr.value))


@differentiate.register(Add)
def _(expr, *o, **kwargs):
    return o[0] + o[1]


@differentiate.register(Sub)
def _(expr, *o, **kwargs):
    return o[0] - o[1]


@differentiate.register(Mul)
def _(expr, *o, **kwargs):
    return o[0]*expr.operands[1] + o[1]*expr.operands[0]


@differentiate.register(Div)
def _(expr, *o, **kwargs):
    return (o[0]*expr.operands[1]-expr.operands[0]*o[1])/(expr.operands[1]**2)


@differentiate.register(Pow)
def _(expr, *o, **kwargs):
    return expr.operands[1]*(expr.operands[0]**(expr.operands[1]-1))*(o[0])
