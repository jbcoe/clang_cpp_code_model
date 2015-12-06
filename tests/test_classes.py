import unittest
import cppmodel as model

class TestClasses(unittest.TestCase):

    def setUp(self):
        classes = model.parse_classes('test_file.cpp')
        self.class_a = classes[0]

    def test_className(self):
        assert(self.class_a.name == 'A')

    def test_classMethods(self):
        assert( len(self.class_a.methods) == 3)
        
    def test_classMethodReturnTypes(self):
        assert( self.class_a.methods[0].return_type == "int")
        assert( self.class_a.methods[1].return_type == "void")
    
    def test_classMethodArgumentTypes(self):
        args = self.class_a.methods[0].arguments
        assert( len(self.class_a.methods) == 2)
        
    def test_classMethodReturnTypes(self):
        assert( self.class_a.methods[0].return_type == "int")
        assert( self.class_a.methods[1].return_type == "void")
    
    def test_classMethodArgumentTypes(self):
        args = self.class_a.methods[0].arguments
        assert(args[0].type == "int")
        assert(args[0].name == "i")
        assert(args[1].type == "const char *") 
        # note the inserted whitespace    ^
        assert(args[1].name == "p")

    def test_classMethodConstQualifiers(self):
        assert( self.class_a.methods[0].is_const == True)
        assert( self.class_a.methods[1].is_const == False)
    
    def test_classMethodsAreVirtual(self):
        assert( self.class_a.methods[0].is_virtual == True)
        assert( self.class_a.methods[0].is_pure_virtual == False)
        assert( self.class_a.methods[1].is_virtual == False)
        assert( self.class_a.methods[2].is_pure_virtual == True)
