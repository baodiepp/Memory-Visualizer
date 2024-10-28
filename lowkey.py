def solve(x, y):
    """

    >>> solve(20,2)
    10
    """
    try:
        if x > 50:
            raise ValueError


        a = x / y
        solution = 2 * a
        print(solution)
    except ZeroDivisionError:
        print('Cannot divide by zero')
    except NameError:
        print('Name not defined inside')
    except:
        print('Something is wrong')
    else:
        print('Yay')
    finally:
        print('End of program')


doctest.testmod()
