import os
import sys
import clang.cindex

def _get_annotations(node):
  return [c.displayname for c in node.get_children()
      if c.kind == clang.cindex.CursorKind.ANNOTATE_ATTR]


class Field:
  def __repr__(self):
    return str(self.type)+":\""+str(self.name)+"\""

  def __init__(self,cursor):
    self.name = cursor.spelling
    self.type = cursor.type.spelling


class FunctionArgument:
  def __repr__(self):
    return str(self.type)+":\""+str(self.name)+"\""

  def __init__(self, type, name):
    self.type = type
    self.name = name


class Function(object):
  def __repr__(self):
    return "Function:"+str(self.name)

  def __init__(self, cursor):
    self.function_cursor = cursor
    self.name = cursor.spelling
    arguments = [x.spelling for x in cursor.get_arguments()]
    argument_types = [x.spelling for x in cursor.type.argument_types()]
    
    if (cursor.kind == clang.cindex.CursorKind.CXX_METHOD):
        self.is_const = cursor.is_const_method()
        self.is_virtual = cursor.is_virtual_method()
        self.is_pure_virtual = cursor.is_pure_virtual_method()
    
    self.type = cursor.type.spelling
    self.return_type = cursor.type.get_result().spelling
    self.arguments = []
    self.annotations = _get_annotations(cursor)
    
    for t,n in zip(argument_types,arguments):
      self.arguments.append(FunctionArgument(t,n))


class Class(object):
  def __repr__(self):
    return "Class:%s"%str(self.name)

  def __init__(self, cursor):
    self.name = cursor.spelling
    self.functions = []
    self.fields = []
    self.annotations = _get_annotations(cursor)
    self.base_classes = []

    for c in cursor.get_children():
      if (c.kind == clang.cindex.CursorKind.FIELD_DECL):
        m = Field(c)
        self.fields.append(m)
      elif (c.kind == clang.cindex.CursorKind.CXX_METHOD):
        f = Function(c)
        self.functions.append(f)
      elif (c.kind == clang.cindex.CursorKind.CONSTRUCTOR):
        f = Function(c)
        self.functions.append(f)
      elif (c.kind == clang.cindex.CursorKind.CXX_BASE_SPECIFIER):
        self.base_classes.append(c.type.spelling)

    self.constructors = [x for x in self.functions if x.name == self.name]

def set_libclang_path_from_env():
    if clang.cindex.Config.loaded:
        return
    clang.cindex.Config.set_library_file(os.environ['LIBCLANG_PATH'])

def build_classes(cursor):
  result = []
  for c in cursor.get_children():
    if c.kind == clang.cindex.CursorKind.CLASS_DECL:
      a_class = Class(c)
      result.append(a_class)
    elif c.kind == clang.cindex.CursorKind.STRUCT_DECL:
      a_class = Class(c)
      result.append(a_class)
    elif c.kind == clang.cindex.CursorKind.NAMESPACE:
      child_classes = build_classes(c)
      result.extend(child_classes)

  return result


def parse_classes(class_file):
  set_libclang_path_from_env()
  index = clang.cindex.Index.create()
  translation_unit = index.parse(class_file, ['-x', 'c++', '-std=c++11'])
  classes = build_classes(translation_unit.cursor)
  return classes

