from task_Boriskin_Makary_indenter import Indenter


def test_indents_0(capsys):
    with Indenter(indent_str="--") as indent:
        indent.print("hi")
        with indent:
            indent.print("hello")
        with indent:
            indent.print("bonjour")
        indent.print("hey")

    outcome = capsys.readouterr()
    expected = "hi\n--hello\n----bonjour\nhey\n"
    assert expected == outcome.out, (
        f"Expected: {expected}. Get: {outcome.out}"
    )


def test_indents_1(capsys):
    with Indenter(indent_str="--", indent_level=1) as indent:
        indent.print("hi")
        with indent:
            indent.print("hello")
        with indent:
            indent.print("bonjour")
        indent.print("hey")

    outcome = capsys.readouterr()
    expected = "--hi\n----hello\n------bonjour\n--hey\n"
    assert expected == outcome.out, (
        f"Expected: {expected}. Get: {outcome.out}"
    )
