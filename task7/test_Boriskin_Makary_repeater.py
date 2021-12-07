from task_Boriskin_Makary_repeater import verbose, verbose_context, repeater


@verbose
def hello(name):
    """my hello docstring"""
    print(f"*** Hello {name}! ***")


def test_verbose(capsys):
    hello("Nokilay")
    outcome = capsys.readouterr()
    assert 'before function call\n*** Hello Nokilay! ***\nafter function call\n' == outcome.out, (
        f"Expected: decorator in use. Get: {outcome.out}"
    )


@verbose_context()
def hello_from(name):
    """my hello docstring"""
    print(f"*** Hello {name}! ***")


def test_verbose_context(capsys):
    hello_from("Albert")
    outcome = capsys.readouterr()
    assert 'class: before function call\n*** Hello Albert! ***\nclass: after function call\n' == outcome.out, (
        f"Expected: decorator in use. Get: {outcome.out}"
    )


@repeater(count=5)
def sum_and_repeat(arg_1, arg_2):
    """my repeat docstring"""
    print(f"{arg_1 + arg_2}")


def test_repeater(capsys):
    sum_and_repeat(2, 3)
    outcome = capsys.readouterr()
    assert "5\n5\n5\n5\n5\n" == outcome.out, (
        f"Expected: decorator in use. Get: {outcome.out}"
    )
