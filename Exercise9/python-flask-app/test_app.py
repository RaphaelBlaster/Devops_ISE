"""Tests for app.py.

Run from this directory:

    python -m unittest discover -s . -p "test_*.py"
"""

import unittest

from app import app


class FlaskAppTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_index_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_index_contains_heading(self):
        response = self.client.get("/")
        self.assertIn("Exercise 9 pipeline", response.get_data(as_text=True))

    def test_health_returns_ok(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_unknown_path_returns_404(self):
        response = self.client.get("/no-such-page")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
