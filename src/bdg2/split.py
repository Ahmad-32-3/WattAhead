"""Splits. The whole point: the test building_id is never in train."""


def lobo(df, test_id):
    """Leave-one-building-out. Train = every OTHER building, 2016. Test = held-out building, 2017."""
    if test_id not in set(df.building_id):
        raise ValueError(f"test_id {test_id!r} not in data")
    train = df[(df.building_id != test_id) & (df.year == 2016)]
    test = df[(df.building_id == test_id) & (df.year == 2017)]
    _assert_disjoint(train, test)
    return train, test


def same_building(df, debug_id):
    """Debug column: a DIFFERENT building than the lobo test, its own 2016 -> 2017. Same meter in train and test."""
    train = df[(df.building_id == debug_id) & (df.year == 2016)]
    test = df[(df.building_id == debug_id) & (df.year == 2017)]
    return train, test


def _assert_disjoint(train, test):
    leak = set(train.building_id) & set(test.building_id)
    if leak:
        raise ValueError(f"LEAK: building(s) in both train and test: {sorted(leak)}")
