import unittest
import cppmodel as model
from util import get_tu

class TestClasses(unittest.TestCase):

    def test_class_name(self):
        source = 'class A{};'
        tu = get_tu(source, 'cpp')

        classes = model.build_classes(tu.cursor)

        assert(len(classes)==1)
        assert(classes[0].name == 'A')

    def test_class_methods(self):
        source = """
        class A{};
        class B{
            void foo();
            int bar();
        };"""
        tu = get_tu(source, 'cpp')

        classes = model.build_classes(tu.cursor)

        assert(len(classes[0].methods) == 0)
        assert(len(classes[1].methods) == 2)

    def test_class_method_return_types(self):
        source = """
        class B{
            void foo();
            int bar();
        };"""
        tu = get_tu(source, 'cpp')

        classes = model.build_classes(tu.cursor)

        assert(classes[0].methods[0].return_type == "void")
        assert(classes[0].methods[1].return_type == "int")

    def test_class_method_argument_types(self):
        source = """
        class A {
            int foo(int i, const char* p);
        };"""
        tu = get_tu(source, 'cpp')

        classes = model.build_classes(tu.cursor)
        args = classes[0].methods[0].arguments

        assert(args[0].type == "int")
        assert(args[0].name == "i")
        assert(args[1].type == "const char *") 
        # note the inserted whitespace    ^
        assert(args[1].name == "p")

    def test_class_method_const_qualifiers(self):
        source = """
        class A {
            int foo() const;
            int bar();
        };"""
        tu = get_tu(source, 'cpp')

        classes = model.build_classes(tu.cursor)
        methods = classes[0].methods

        assert( methods[0].is_const == True)
        assert( methods[1].is_const == False)

    def test_class_methods_are_virtual(self):
        source = """
        class A {
            virtual int foo();
            int bar();
            virtual int foobar() = 0;
        };"""
        tu = get_tu(source, 'cpp')

        classes = model.build_classes(tu.cursor)
        methods = classes[0].methods

        assert( methods[0].is_virtual == True)
        assert( methods[0].is_pure_virtual == False)
        assert( methods[1].is_virtual == False)
        assert( methods[2].is_pure_virtual == True)

    def test_namespaces(self):
        source = """
        class A{};
        namespace outer {
            class B{};
            namespace inner {
                class C{};
            } // end inner
        } // end outer"""
        tu = get_tu(source, 'cpp')

        classes = model.build_classes(tu.cursor)

        assert(classes[0].namespace == "");
        assert(classes[1].namespace == "outer");
        assert(classes[2].namespace == "outer::inner");

