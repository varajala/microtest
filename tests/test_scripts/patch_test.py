import microtest


namespace = microtest.Namespace()
namespace.variable = 1
namespace.CONSTANT = 'string'


@microtest.test
def test_patching():
    with microtest.patch(namespace, variable = 2, CONSTANT = 'some_other_string'):
        assert namespace.variable == 2
        assert namespace.CONSTANT == 'some_other_string'

    assert namespace.variable == 1
    assert namespace.CONSTANT == 'string'
