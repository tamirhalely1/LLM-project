def sort_array(arr):
    arr.sort()
    return arr

# Unit tests
def test_sort_array():
    # Test case 1
    input_arr = [4, 2, 8, 6, 5]
    expected_output = [2, 4, 5, 6, 8]
    assert sort_array(input_arr) == expected_output

    # Test case 2
    input_arr = [1, 5, 3, 2]
    expected_output = [1, 2, 3, 5]
    assert sort_array(input_arr) == expected_output

    # Test case 3
    input_arr = [9, 7, 2, 6, 1]
    expected_output = [1, 2, 6, 7, 9]
    assert sort_array(input_arr) == expected_output

    # Test case 4
    input_arr = [10, 3, 8, 6, 4]
    expected_output = [3, 4, 6, 8, 10]
    assert sort_array(input_arr) == expected_output

    # Test case 5
    input_arr = [7, 3, 1, 6, 9]
    expected_output = [1, 3, 6, 7, 9]
    assert sort_array(input_arr) == expected_output

    print("All test cases passed!")

# Run the unit tests
test_sort_array()
