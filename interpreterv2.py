from intbase import InterpreterBase, ErrorType
from brewparse import parse_program

def is_definition(statement_node):
  if statement_node.elem_type == 'vardef':
    return True
  return False

def is_assignment(statement_node):
  if statement_node.elem_type == '=':
    return True
  return False

def is_func_call(statement_node):
  if statement_node.elem_type == 'fcall':
    return True
  return False


class Interpreter(InterpreterBase):
  def __init__(self, console_output=True, inp=None, trace_output=False):
    super().__init__(console_output, inp)

  def run(self, program):
    ast = parse_program(program)
    self.variable_list = []
    self.variable_name_to_value = dict()  # dict to hold variables
    self.var_to_type = dict()
    functions = ast.dict['functions']
    exist_main = False
    for function in functions:
      if function.dict['name'] == 'main':
        exist_main = True
        main_func_node = function
        # TODO: What about functions other than main?
    if not exist_main:
      super().error(
        ErrorType.NAME_ERROR,
        "No main() function was found",
      )
    self.run_func(main_func_node)

  def run_func(self, func_node):
    statements = func_node.dict['statements']
    for statement_node in statements:
      
      self.run_statement(statement_node)

  def run_statement(self, statement_node):
    if is_definition(statement_node):
      var_name = statement_node.dict['name']
      # TODO: Type null ? 
      if statement_node.dict['name'] in self.variable_list:
        super().error(
          ErrorType.NAME_ERROR,
          f"Variable {var_name} defined more than once",
        )
        return
      else:
        self.variable_list.append(var_name)
        self.variable_name_to_value[var_name] = 0 # set the initial value to 0 by default
        self.var_to_type[var_name] = "int"
    elif is_assignment(statement_node):
      self.do_assignment(statement_node)
    elif is_func_call(statement_node):
      func_name = statement_node.dict['name']
      # TODO: inputi() as statement rather than expression in an assignment?
      if func_name != 'print' and func_name != 'inputi':
        super().error(
          ErrorType.NAME_ERROR,
          f"Function {func_name} has not been defined",
        )
      arg_list = statement_node.dict['args']
      output = ''
      for arg in arg_list:
        result = self.evaluate_expression(arg)[0]
        output+=str(result)
      super().output(output)



  def do_assignment(self, statement_node):
    var_name = statement_node.dict['name'] 
    if var_name not in self.variable_list:
      super().error(
        ErrorType.NAME_ERROR,
        f"Variable {var_name} has not been defined",
      )
      return
    source_node = statement_node.dict['expression']
    resulting_value = self.evaluate_expression(source_node)[0]
    resulting_type = self.evaluate_expression(source_node)[1]
    self.variable_name_to_value[var_name] = resulting_value
    self.var_to_type[var_name] = resulting_type

  def evaluate_expression(self, expression_node):
    node_type = expression_node.elem_type
    node_dict = expression_node.dict
    if node_type == 'int':
        return node_dict['val'], "int"
    elif node_type == 'string':
        return node_dict['val'], "string"
    elif node_type == 'var':
        var_name = node_dict['name']
        if var_name not in self.variable_list:
          super().error(
            ErrorType.NAME_ERROR,
            f"Variable {var_name} has not been defined",
          )
        # TODO: no value before? Here have a default init
        return self.variable_name_to_value[var_name], self.var_to_type[var_name]
    elif node_type == '+' or node_type == '-':
        # TODO: string concat
        if node_dict['op1'].elem_type == 'string' or node_dict['op2'].elem_type == 'string' \
        or (node_dict['op1'].elem_type == 'var' and self.var_to_type[node_dict['op1'].dict['name']] == "string") \
        or (node_dict['op2'].elem_type == 'var' and self.var_to_type[node_dict['op2'].dict['name']] == "string"):
          super().error(
            ErrorType.TYPE_ERROR,
            "Incompatible types for arithmetic operation",
          )
          return
        else:
          op1 = self.evaluate_expression(node_dict['op1'])[0]
          op2 = self.evaluate_expression(node_dict['op2'])[0]
          return (op1 + op2 if node_type == '+' else op1 - op2), "int"
    # TODO: expression node representing a function call
    elif node_type == 'fcall':
      func_name = node_dict['name']
      args_list = node_dict['args']
      if func_name == 'print':
        super().error(
        ErrorType.NAME_ERROR,
        "Unable to evaluate a print function call. Do you mean 'inputi()'?",
        ) 
        return
      if func_name != 'inputi':
        super().error(
          ErrorType.NAME_ERROR,
          f"Function {func_name} has not been defined",
        )
        return
      if len(args_list) == 0:
        user_input = super().get_input()
        user_input = int(user_input)
        return user_input, "int"
      elif len(args_list) == 1:
        super().output(args_list[0])
        user_input = super().get_input()
        user_input = int(user_input)
        # TODO: Can assume an integer input?
        return user_input, "int"
      else:
        super().error(
          ErrorType.NAME_ERROR,
          f"No inputi() function found that takes > 1 parameter",
        )
      





program = """ func main() {
  var b;
  b = 10+(2-3);
  print(b);  
}
"""

interpreter = Interpreter()
interpreter.run(program)   