from util import get_tu
import cppmodel

def test_function_name():
    source = """
    void foo();
    void bar();
    """
    tu = get_tu(source, 'cpp')

    model = cppmodel.Model(tu)
    functions = model.functions

    assert len(functions) == 2
    assert functions[0].name == 'foo'
    assert functions[1].name == 'bar'


def test_function_return_type():
    source = """
    int foo();
    double bar();
    """
    
    tu = get_tu(source, 'cpp')

    model = cppmodel.Model(tu)
    functions = model.functions
    
    assert functions[0].return_type == 'int'
    assert functions[1].return_type == 'double'


def test_function_arguments():
    source = """
    int foo();
    double bar(int x, char y);
    """
    
    tu = get_tu(source, 'cpp')

    model = cppmodel.Model(tu)
    functions = model.functions
    
    assert len(functions[0].arguments) == 0
    assert len(functions[1].arguments) == 2
    assert functions[1].arguments[0].type == 'int'
    assert functions[1].arguments[0].name == 'x'
    assert functions[1].arguments[1].type == 'char'
    assert functions[1].arguments[1].name == 'y'

