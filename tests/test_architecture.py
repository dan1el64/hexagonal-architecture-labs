import ast
from pathlib import Path
import unittest


class ArchitectureTests(unittest.TestCase):
    def test_core_never_imports_infrastructure_or_other_context(self):
        allowed = {"dataclasses", "typing"}
        for context in ("inventory", "evaluation"):
            for layer in ("domain", "ports", "application"):
                path = Path("labs") / context / f"{layer}.py"
                tree = ast.parse(path.read_text())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.assertIn(alias.name, allowed, str(path))
                    elif isinstance(node, ast.ImportFrom):
                        if node.level:
                            self.assertEqual(1, node.level, str(path))
                            self.assertIn(node.module, {"domain", "ports"}, str(path))
                        else:
                            self.assertIn(node.module, allowed, str(path))
