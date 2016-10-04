import os
import sys
import clang.cindex
from clang.cindex import AccessSpecifier, CursorKind, TypeKind

def _get_annotations(node):
    return [c.displayname for c in node.get_children()
            if c.kind == CursorKind.ANNOTATE_ATTR]

class Type:
    def __init__(self, cindex_type):
        self.kind = cindex_type.kind
        self.name = cindex_type.spelling
        self.is_pointer = self.kind == TypeKind.POINTER
        self.is_reference = self.kind == TypeKind.LVALUEREFERENCE
        self.is_const = cindex_type.is_const_qualified()
        if self.is_pointer or self.is_reference:
            self.pointee = Type(cindex_type.get_pointee())
        else: self.pointee = None

    def __str__(self):
        return self.name

class Member:
    def __init__(self, cursor):
        self.type = Type(cursor.type)
        self.name = cursor.spelling

class FunctionArgument:
    def __str__(self):
        return str(self.type)+":\""+str(self.name)+"\""

    def __init__(self, type, name):
        self.type = type
        self.name = name


class _Function(object):
    def __str__(self):
        return str(self.name)

    def __init__(self, cursor):
        self.name = cursor.spelling
        arguments = [x.spelling for x in cursor.get_arguments()]
        argument_types = [Type(x) for x in cursor.type.argument_types()]

        self.return_type = Type(cursor.type.get_result())
        self.arguments = []
        self.annotations = _get_annotations(cursor)

        for t,n in zip(argument_types,arguments):
            self.arguments.append(FunctionArgument(t,n))


class Function(_Function):

    def __init__(self, cursor, namespaces=[]):
        _Function.__init__(self, cursor)
        self.namespace = '::'.join(namespaces)
        if self.namespace:
            self.qualified_name = '::'.join([self.namespace, self.name])
        else:
            self.qualified_name = self.name

    def __eq__(self, f):
        if self.name != f.name:
            return False
        if self.namespace != f.namespace:
            return False
        if len(self.arguments) != len(f.arguments):
            return False
        for x,fx in zip([arg.type for arg in self.arguments],[arg.type for arg in f.arguments]):
            if x.name != fx.name:
                return False
        return True

class Method(Function):

    def __init__(self, cursor):
        _Function.__init__(self, cursor)
        self.is_const = cursor.is_const_method()
        self.is_virtual = cursor.is_virtual_method()
        self.is_pure_virtual = cursor.is_pure_virtual_method()
        self.is_public = (cursor.access_specifier == AccessSpecifier.PUBLIC)


class Class(object):
    def __str__(self):
        return "Class:%s"%str(self.name)

    def __init__(self, model, cursor, namespaces):
        self.name = cursor.spelling
        self.namespace = '::'.join(namespaces)
        if self.namespace:
            self.qualified_name = '::'.join([self.namespace, self.name])
        else:
            self.qualified_name = self.name
        self.constructors = []
        self.methods = []
        self.members = []
        self.annotations = _get_annotations(cursor)
        self.base_classes = []
        # FIXME: populate these fields with AST info
        self.source_file = str(cursor.location.file)
        self.source_line = int(cursor.location.line)
        self.source_column = int(cursor.location.column)

        for c in cursor.get_children():
            if (c.kind == CursorKind.CXX_METHOD):
                f = Method(c)
                self.methods.append(f)
            elif (c.kind == CursorKind.CONSTRUCTOR):
                f = Method(c)
                self.constructors.append(f)
            elif (c.kind == CursorKind.FIELD_DECL):
                f = Member(c)
                self.members.append(f)
            elif (c.kind == CursorKind.FUNCTION_DECL):
                f = Function(c)
                model.functions.append(f)
            elif (c.kind == CursorKind.CXX_BASE_SPECIFIER):
                self.base_classes.append(c.type.spelling)

class Model(object):
    def __str__(self):
        return "Classes:[{}]".format(",".join(self.classes))

    def __init__(self, translation_unit=None):
       self.functions = []
       self.classes = []
       if translation_unit is not None:
           self.add_child_nodes(translation_unit.cursor, [])

    def extend(self, translation_unit):
        m = Model(translation_unit)
        # Check for duplicates and inconsistencies.
        for new_class in m.classes:
            is_new = True
            for old_class in self.classes:
                if new_class.qualified_name == old_class.qualified_name:
                    if new_class.source_file != old_class.source_file:
                        raise Exception("Class {} is defined in multiple locations: {} {}".format(
                            old_class.qualified_name, old_class.source_file, new_class.source_file))
                    # Move on as there can only be one match
                    is_new = False
                    break

            if is_new:
                self.classes.append(new_class)

        # We only look at declarations for functions so won't raise exceptions
        for new_function in m.functions:
            is_new = True
            for old_function in self.functions:
                if new_function == old_function:
                    is_new = False
                    break
            if is_new:
                self.functions.append(new_function)

    def add_child_nodes(self, cursor, namespaces=[]):
        for c in cursor.get_children():
            if c.kind == CursorKind.CLASS_DECL or c.kind == CursorKind.STRUCT_DECL:
                self.classes.append(Class(self,c,namespaces))
            if c.kind == CursorKind.FUNCTION_DECL:
                self.functions.append(Function(c,namespaces))
            elif c.kind == CursorKind.NAMESPACE:
                child_namespaces = list(namespaces)
                child_namespaces.append(c.spelling)
                self.add_child_nodes(c, child_namespaces)

