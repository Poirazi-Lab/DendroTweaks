import pyparsing as pp

pp.ParserElement.enablePackrat()

from pyparsing import (alphas, alphanums, nums)
from pyparsing import (Char, Word, Empty, Literal, Regex, Keyword)
from pyparsing import (infix_notation, opAssoc)

from pyparsing import (Group, Combine, Dict, Suppress, delimitedList, Optional)
from pyparsing import (ZeroOrMore, OneOrMore, oneOf)
from pyparsing import Forward
from pyparsing import (restOfLine, SkipTo)
from pyparsing import pyparsing_common
from pyparsing import LineEnd
from pyparsing import infixNotation, opAssoc, And
from pyparsing import NotAny

# Symbols
LBRACE, RBRACE, LPAREN, RPAREN, EQUAL, COLON = map(Suppress, "{}()=:")

# Keywords

## Block keywords
TITLE = Suppress(Keyword('TITLE', caseless=False))
COMMENT = Suppress(Keyword('COMMENT', caseless=False))
ENDCOMMENT = Suppress(Keyword('ENDCOMMENT', caseless=False))
NEURON = Suppress(Keyword('NEURON', caseless=False))
UNITS = Suppress(Keyword('UNITS', caseless=False))
PARAMETER = Suppress(Keyword('PARAMETER', caseless=False))
ASSIGNED = Suppress(Keyword('ASSIGNED', caseless=False))
STATE = Suppress(Keyword('STATE', caseless=False))
BREAKPOINT = Suppress(Keyword('BREAKPOINT', caseless=False))
INITIAL = Suppress(Keyword('INITIAL', caseless=False))
DERIVATIVE = Suppress(Keyword('DERIVATIVE', caseless=False))
FUNCTION = Suppress(Keyword('FUNCTION', caseless=False))
PROCEDURE = Suppress(Keyword('PROCEDURE', caseless=False))
INDEPENDENT = Suppress(Keyword('INDEPENDENT', caseless=False))
FROM = Suppress(Keyword('FROM', caseless=False))
TO = Suppress(Keyword('TO', caseless=False))
KINETIC = Suppress(Keyword('KINETIC', caseless=False))
STEADYSTATE = Suppress(Keyword('STEADYSTATE', caseless=False))

block_to_keep = TITLE | COMMENT | NEURON | UNITS | PARAMETER | ASSIGNED | STATE | BREAKPOINT | INITIAL | DERIVATIVE | FUNCTION | PROCEDURE

## Misc keywords
VERBATIM = Suppress(Keyword('VERBATIM', caseless=False))
ENDVERBATIM = Suppress(Keyword('ENDVERBATIM', caseless=False))



# TITLE

title = Combine(TITLE + restOfLine('block'))

comment = Combine(COLON + restOfLine)("comment")


comment_block = Combine(COMMENT + SkipTo(ENDCOMMENT) + ENDCOMMENT)('block')

# VERBATIM
verbatim = VERBATIM + SkipTo(ENDVERBATIM) + ENDVERBATIM

## Block keywords
FARADAY = Keyword('FARADAY', caseless=False)
R = Keyword('R', caseless=False)

number = pyparsing_common.number
identifier = Word(alphas, alphanums + "_") 
# unit = Combine(LPAREN + Word(alphas + nums + "/") + RPAREN)
unit = Combine(LPAREN
               + ( Combine(Word(alphas + "23") + "/" + Word(alphas + "23"))
                  | Combine("/" + Word(alphas + "23") + "/" + Word(alphas + "23"))
                  | Combine("/" + Word(alphas + "23"))
                  | Combine(Word(nums) + "/" + Word(alphas + "23"))
                  | Word(alphas + "23"))
               + RPAREN)
dimensionless = LPAREN + Literal("1") + RPAREN

faraday_constant = Dict(Group(FARADAY + EQUAL + LPAREN + Suppress(Literal('faraday')) + RPAREN + Optional(unit)))
gas_constant = Dict(Group(R + EQUAL + LPAREN + Suppress(Literal('k-mole')) + RPAREN + Optional(unit)))

constant = faraday_constant | gas_constant

quantity = And([number + Suppress(unit)])

value_range = Suppress(Literal('<')) + Suppress(number) + Suppress(Literal(',')) + Suppress(number) + Suppress(Literal('>'))

from_to = FROM + number("from") + TO + number("to")

# NEURON block

## Block keywords
SUFFIX = Suppress(Keyword('SUFFIX', caseless=False))
NONSPECIFIC_CURRENT = Suppress(Keyword('NONSPECIFIC_CURRENT', caseless=False))
USEION = Suppress(Keyword('USEION', caseless=False))
READ = Suppress(Keyword('READ', caseless=False))
WRITE = Suppress(Keyword('WRITE', caseless=False))
VALENCE = Suppress(Keyword('VALENCE', caseless=False))
RANGE = Suppress(Keyword('RANGE', caseless=False))
GLOBAL = Suppress(Keyword('GLOBAL', caseless=False))

## Block statements
suffix_stmt = SUFFIX + identifier("suffix")
nonspecific_current_stmt = NONSPECIFIC_CURRENT + identifier("nonspecific_current")
useion_stmt = (Group(
    USEION
    + identifier('ion')
    + Group(READ + delimitedList(identifier))("read")
    + Optional(Group(WRITE + delimitedList(identifier))("write"))
    + Optional(VALENCE + number("valence"))
))("useion*")
range_stmt = Group(RANGE + delimitedList(identifier))("range")
global_stmt = Group(GLOBAL + delimitedList(identifier))("global")

neuron_stmt = suffix_stmt | nonspecific_current_stmt | useion_stmt | range_stmt | global_stmt

## Block definition
neuron_block = Group(
    NEURON
    + LBRACE
    + OneOrMore(neuron_stmt)
    + RBRACE
)("block")


# UNITS block



## Block statements
unit_definition = Dict(Group(unit + EQUAL + unit)) | constant

## Block definition
units_block = Group(
    UNITS 
    + LBRACE 
    + OneOrMore(unit_definition) 
    + RBRACE
)("block")

# units_blocks = ZeroOrMore(units_block)("units_block")

# PARAMETER block

## Block statements
parameter_stmt = Group(
    identifier('name')
    + EQUAL 
    + number('value') 
    + Optional(unit | dimensionless)('unit') 
    + Optional(value_range('value_range'))
)

## Block definition
parameter_block = Group(
    PARAMETER 
    + LBRACE 
    + OneOrMore(parameter_stmt)
    + RBRACE
)("block")

parameter_block = parameter_block.ignore(comment)



# ASSIGNED block


## Block statements
assigned_stmt = Group(
    identifier('name')
    + Optional(unit | dimensionless)('unit') 
    )

## Block definition
assigned_block = Group(
    ASSIGNED 
    + LBRACE 
    + OneOrMore(assigned_stmt)
    + RBRACE
)("block")

assigned_block = assigned_block.ignore(comment)


# STATE block

## Block definition
state_var = Word(alphas) + Suppress(Optional(unit | dimensionless)) + Suppress(Optional(from_to))
# state_var = Group(identifier('name') + Optional(unit | dimensionless)('unit') + Optional(comment))
state_block = Group(
    STATE 
    + LBRACE 
    + OneOrMore(state_var) 
    + RBRACE
)('block')




# breakpoint_block = BREAKPOINT + SkipTo(block_to_keep)
# breakpoint_block = Suppress(breakpoint_block)

# DERIVATIVE block (not used)
# derivative_block = DERIVATIVE + SkipTo(block_to_keep)
# derivative_block = Suppress(derivative_block)

# INDEPENDENT block (not used)
independent_block = INDEPENDENT + SkipTo(block_to_keep)
independent_block = Suppress(independent_block)

kinetic_block = KINETIC + SkipTo(block_to_keep)
kinetic_block = Suppress(kinetic_block)

derivative_block = DERIVATIVE + SkipTo(block_to_keep)
derivative_block = Suppress(kinetic_block)

# Functional blocks

## Signature

param = Group(identifier('name') + Optional(unit('unit') | dimensionless('unit')))
param_list = delimitedList(param)('params')
signature = Group(
    identifier('name') 
    + LPAREN 
    + Optional(param_list) 
    + RPAREN 
    + Optional(unit)('returned_unit')
)('signature')

## Local 
LOCAL = Keyword("LOCAL", caseless=False)
LOCAL = Suppress(LOCAL)
local_stmt = LOCAL + delimitedList(identifier)

# Expression
expr = Forward()
parenth_expr = LPAREN + expr + RPAREN

## Function call with arguments
arg = expr | identifier | number
arg_list = delimitedList(arg)('args')
func_call_with_args = Group(identifier + LPAREN + Optional(arg_list) + RPAREN)
def func_call_with_args_action(tokens):
    function_name = tokens[0][0]
    function_args = tokens[0][1:]
    return {function_name: function_args}
func_call_with_args.setParseAction(func_call_with_args_action)

## Function call with expression
func_call_with_expr = Group(identifier('name') + LPAREN + expr + RPAREN)
def func_call_with_expr_action(tokens):
    function_name = tokens[0][0]
    function_expr = tokens[0][1]
    return {function_name: function_expr}
func_call_with_expr.setParseAction(func_call_with_expr_action)

## Operands
func_operand = func_call_with_args | func_call_with_expr
operand = func_operand | quantity | number | identifier # the order is important!
operand = operand | LPAREN + operand + RPAREN

## Operators
signop = Literal('-')
plusop = oneOf('+ -')
mulop = oneOf('* /')
orderop = oneOf('< > <= >= ==')
powop = Literal('^')

# def sign_action(tokens):
#     tokens = tokens[0]
#     return {tokens[0]: tokens[1]}

# def op_action(tokens):
#     tokens = tokens[0]
#     return {tokens[1]: [tokens[0], tokens[2]]}

def sign_action(tokens):
    tokens = tokens[0]
    return {tokens[0]: [tokens[1]]}

def op_action(tokens):
    tokens = tokens[0]
    while len(tokens) > 3:
        tokens = [{tokens[1]: [tokens[0], tokens[2]]}] + tokens[3:]
    return {tokens[1]: [tokens[0], tokens[2]]}

## Expression
expr <<= infix_notation(
 operand,
 [
  (signop, 1, opAssoc.RIGHT, sign_action),
  (powop, 2, opAssoc.RIGHT, op_action),
  (mulop, 2, opAssoc.LEFT, op_action),
  (plusop, 2, opAssoc.LEFT, op_action),
  (orderop, 2, opAssoc.LEFT, op_action),
 ]
)


# expr = expr | LPAREN + expr + RPAREN


## Assignment
assignment_stmt = Group(
    identifier('assigned_var')
    + EQUAL 
    + expr('expression')
)

# BREAKPOINT block (not used)
SOLVE = Suppress(Keyword('SOLVE', caseless=False))
METHOD = Suppress(Keyword('METHOD', caseless=False))
STEADYSTATE = Suppress(Keyword('STEADYSTATE', caseless=False))

solve_stmt = Group(
    SOLVE
    + identifier("solve")
    + (METHOD | STEADYSTATE)
    + identifier("method")
)("solve_stmt")

breakpoint_block = Group(
    BREAKPOINT 
    + LBRACE 
    + solve_stmt
    + ZeroOrMore(assignment_stmt)("statements")
    + RBRACE
)("block")

initial_stmt = (solve_stmt | assignment_stmt | func_call_with_args )

initial_block = Group(
    INITIAL
    + LBRACE
    # + OneOrMore(func_call_with_args)("func_calls")
    # + OneOrMore(assignment_stmt)("statements")
    + OneOrMore(initial_stmt)("statements")
    + RBRACE
)("block")

derivative_assignment_stmt = Group(
    identifier('assigned_var') 
    + "'"
    + EQUAL 
    + expr('expression')
)

derivative_block = Group(
    DERIVATIVE
    + Word(alphas)("name")
    + LBRACE
    + OneOrMore(func_call_with_args)("func_calls")
    + OneOrMore(derivative_assignment_stmt)("statements")
    + RBRACE
)("block")

# FUNCTION block

## IF-ELSE statement
IF = Keyword("if", caseless=False)
IF = Suppress(IF)
ELSE = Keyword("else", caseless=False)
ELSE = Suppress(ELSE)

if_else_stmt = Group(
    IF + LPAREN + expr('condition') + RPAREN 
    + LBRACE 
    + OneOrMore(assignment_stmt)('if_statements')
    + RBRACE
    + Optional(ELSE + LBRACE + OneOrMore(assignment_stmt)('else_statements') + RBRACE)
)


# if_else_stmt = if_else_stmt('if_else_statements*')
# assignment_stmt = assignment_stmt('assignment_statements*')

stmt = (assignment_stmt | if_else_stmt)

## Block definition
function_block = Group(
    FUNCTION 
    + signature('signature') 
    + LBRACE 
    + ZeroOrMore(local_stmt)('locals')
    # + ZeroOrMore(if_else_stmt)('if_else_statements')
    # + ZeroOrMore(assignment_stmt)('statements')
    + OneOrMore(stmt)("statements")
    + RBRACE)("block")

function_blocks = OneOrMore(function_block)("function_blocks")


# PROCEDURE block

# stmt = (if_else_stmt('if_else_statements*') | assignment_stmt('statements*'))



## Block definition
procedure_block = Group(
    PROCEDURE 
    + signature('signature') 
    + LBRACE 
    + ZeroOrMore(local_stmt)('locals')
    # + ZeroOrMore(if_else_stmt)('if_else_statements')
    # + OneOrMore(assignment_stmt)('statements')
    + OneOrMore(stmt)('statements')
    + RBRACE)("block")

procedure_blocks = OneOrMore(procedure_block)("procedure_blocks")

# MOD file

block = kinetic_block | independent_block | breakpoint_block | initial_block | derivative_block | procedure_blocks | function_blocks | title | comment_block | neuron_block | units_block | parameter_block | assigned_block | state_block
grammar = Group(ZeroOrMore(block))('mod_file')