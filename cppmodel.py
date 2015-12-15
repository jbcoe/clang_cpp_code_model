import os
import sys
import clang.cindex
from clang.cindex import AccessSpecifier
from clang.cindex import CursorKind

def _get_annotations(node):
    return [c.displayname for c in node.get_children()
            if c.kind == CursorKind.ANNOTATE_ATTR]


class FunctionArgument:
    def __repr__(self):
        return str(self.type)+":\""+str(self.name)+"\""

    def __init__(self, type, name):
        self.type = type
        self.name = name


class Method(object):
    def __repr__(self):
        return "Function:"+str(self.name)

    def __init__(self, cursor):
        self.name = cursor.spelling
        arguments = [x.spelling for x in cursor.get_arguments()]
        argument_types = [x.spelling for x in cursor.type.argument_types()]

        if cursor.kind == CursorKind.CXX_METHOD:
            self.is_const = cursor.is_const_method()
            self.is_virtual = cursor.is_virtual_method()
            self.is_pure_virtual = cursor.is_pure_virtual_method()
            self.is_public = (cursor.access_specifier == AccessSpecifier.PUBLIC)
        self.type = cursor.type.spelling
        self.return_type = cursor.type.get_result().spelling
        self.arguments = []
        self.annotations = _get_annotations(cursor)

        for t,n in zip(argument_types,arguments):
            self.arguments.append(FunctionArgument(t,n))


class Class(object):
    def __repr__(self):
        return "Class:%s"%str(self.name)

    def __init__(self, cursor, namespaces):
        self.name = cursor.spelling
        self.namespace = '::'.join(namespaces)
        self.constructors = []
        self.methods = []
        self.fields = []
        self.annotations = _get_annotations(cursor)
        self.base_classes = []

        for c in cursor.get_children():
            if (c.kind == CursorKind.CXX_METHOD):
                f = Method(c)
                self.methods.append(f)
            elif (c.kind == CursorKind.CONSTRUCTOR):
                f = Method(c)
                self.constructors.append(f)
            elif (c.kind == CursorKind.CXX_BASE_SPECIFIER):
                self.base_classes.append(c.type.spelling)

class Model(object):
    def __repr__(self):
        return "Classes:[{}]".format(",".join(self.classes))

    def __init__(self, translation_unit):
       self.functions = []
       self.classes = []
       self.add_child_nodes(translation_unit.cursor, [])

    def add_child_nodes(self, cursor, namespaces=[]):
        for c in cursor.get_children():
            if c.kind == CursorKind.CLASS_DECL or c.kind == CursorKind.STRUCT_DECL:
                self.classes.append(Class(c,namespaces))
            elif c.kind == CursorKind.NAMESPACE:
                namespaces.append(c.spelling)
                self.add_child_nodes(c, namespaces)

