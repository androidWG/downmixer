def remap(x: float, o_min: float, o_max: float, n_min: float, n_max: float) -> float:
    """Linearly map one range to another. For example, if the original range is 0 to 10 and the new range is 0 to 5, and
     `x` value of 5 will result in an output of 2.5.

     This function can handle negative values and inverted ranges. If the input is -10 to 0 and
     the new range is 5 to 10, the output will still be valid.

    :param x: The value inside the old range to be remapped.
    :param o_min: Minimum value of the old range.
    :param o_max: Maximum value of the old range.
    :param n_min: Minimum value of the new range.
    :param n_max: Maximum value of the new range.
    :return: `x` modified to be fit inside the new range.
    """
    # check reversed input range
    reverse_input = False
    old_min = min(o_min, o_max)
    old_max = max(o_min, o_max)
    if not old_min == o_min:
        reverse_input = True

    # check reversed output range
    reverse_output = False
    new_min = min(n_min, n_max)
    new_max = max(n_min, n_max)
    if not new_min == n_min:
        reverse_output = True

    portion = (x - old_min) * (new_max - new_min) / (old_max - old_min)
    if reverse_input:
        portion = (old_max - x) * (new_max - new_min) / (old_max - old_min)

    result = portion + new_min
    if reverse_output:
        result = new_max - portion

    return result


def ease(x: float) -> float:
    """Returns `y` according to this graph: https://www.desmos.com/calculator/3guvoyxg4z

    :param x: The value to be placed in the curve.
    :return: The value placed in the curve.
    """
    return 1 - (4 * x * x * x) if x < 0.5 else ((-2 * x + 2) ** 3) / 2


def match_length(len1: float, len2):
    x = remap(abs(len1 - len2), 0, 120, 0, 1)
    return ease(x) * 100
