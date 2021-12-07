""" task_indenter

use with Indenter() as identifier:
"""


class Indenter:
    """Indenter class sample"""

    def __init__(self, indent_str: str = " " * 4, indent_level: int = 0):
        self.indent_str = indent_str
        self.indent_level = indent_level - 1
        self.initial_indent_level = indent_level - 1

    def __enter__(self):
        self.indent_level += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.indent_level == self.initial_indent_level + 3:
            self.indent_level = self.initial_indent_level + 1
        pass

    def print(self, message: str):
        indent = self.indent_str * self.indent_level
        print(
            f"{indent}{message}"
        )
