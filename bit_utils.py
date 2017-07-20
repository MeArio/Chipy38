def wrap_around(value, max):
    """
        Wraps a number around if it's bigger or equal than the max value.
        I added the equal to be able to also use it in the draw function.
    """
    if value >= max:
        value %= max
    return value
