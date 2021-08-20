import microtest

int_list_id = None
int_list_squared_id = None


@microtest.test
def test_resources(int_list, int_list_squared, foo):
    global int_list_id, int_list_squared_id
    int_list_id = id(int_list)
    int_list_squared_id = id(int_list_squared)

    assert int_list == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert int_list_squared == [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]
    assert foo == 'bar'


@microtest.test
def test_resource_creation(int_list, int_list_squared):
    assert id(int_list) == int_list_id
    assert id(int_list_squared) == int_list_squared_id
