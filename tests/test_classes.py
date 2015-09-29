import unittest
import model

class TestClasses(unittest.TestCase):

    def setUp(self):
        classes = model.parse_classes('test_file.cpp')
        self.class_a = classes[0]

    def test_className(self):
        assert(self.class_a.name == 'A')

    def test_classMethods(self):
        assert( len(self.class_a.functions) == 2)
        
