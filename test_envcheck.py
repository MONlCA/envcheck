import tempfile
import unittest
from pathlib import Path

from envcheck import check_environment, parse_spec, summarize


class EnvCheckTests(unittest.TestCase):
    def test_parse_required_and_optional(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ".env.example"
            path.write_text("API_KEY=\nDEBUG=false # optional\n", encoding="utf-8")
            variables = parse_spec(path)
        self.assertEqual(variables[0], {"name": "API_KEY", "required": True})
        self.assertEqual(variables[1], {"name": "DEBUG", "required": False})

    def test_values_are_never_returned(self):
        variables = [{"name": "SECRET_TOKEN", "required": True}]
        results = check_environment(variables, {"SECRET_TOKEN": "super-secret-value"})
        self.assertEqual(results[0]["state"], "SET")
        self.assertNotIn("value", results[0])
        self.assertNotIn("super-secret-value", str(results))

    def test_missing_required_variable(self):
        variables = [{"name": "DATABASE_URL", "required": True}]
        results = check_environment(variables, {})
        self.assertEqual(results[0]["state"], "MISSING")
        self.assertEqual(summarize(results)["missing"], 1)

    def test_optional_missing_does_not_count_as_required(self):
        variables = [{"name": "DEBUG", "required": False}]
        counts = summarize(check_environment(variables, {}))
        self.assertEqual(counts["missing"], 0)
        self.assertEqual(counts["optional_missing"], 1)


if __name__ == "__main__":
    unittest.main()
