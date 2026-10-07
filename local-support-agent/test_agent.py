import unittest
from agent import run_support_agent

class TestSupportAgentGraph(unittest.TestCase):
    def test_triage_out_of_scope(self):
        result = run_support_agent("Write a refund for my subscription.")
        self.assertEqual(result["json_output"]["classification"], "out_of_scope")

    def test_verification_retry_path(self):
        result = run_support_agent("My scheduled exports stopped.", force_fail=True)
        self.assertIn("Revision Node Executed (Retry Path)", result["logs"])

    def test_graph_routing_trace(self):
        result = run_support_agent("Can a read-only user create API credentials?")
        self.assertIn("Triage Node Executed", result["logs"])
        self.assertIn("Retrieval Node Executed", result["logs"])

if __name__ == "__main__":
    unittest.main()