"""Tests for the RAG pipeline logic, using fakes instead of a real
vector database or a live Anthropic API call."""
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.rag import answer_question, build_context  # noqa: E402


class FakeStore:
    def __init__(self, results):
        self._results = results

    def query(self, question, top_k=None):
        return self._results


class FakeAIMessage:
    """Mimics the object LangChain chat models return from .invoke()."""

    def __init__(self, content):
        self.content = content


class RagTests(unittest.TestCase):
    def test_build_context_formats_sources(self):
        retrieved = [
            {"text": "Paris is the capital of France.", "source": "geo.pdf", "distance": 0.1},
        ]
        ctx = build_context(retrieved)
        self.assertIn("geo.pdf", ctx)
        self.assertIn("Paris is the capital of France.", ctx)

    def test_build_context_handles_empty_results(self):
        self.assertIn("no relevant context", build_context([]))

    def test_answer_question_uses_retrieved_sources(self):
        store = FakeStore(
            [
                {"text": "chunk A", "source": "report.pdf", "distance": 0.05},
                {"text": "chunk B", "source": "report.pdf", "distance": 0.08},
                {"text": "chunk C", "source": "notes.txt", "distance": 0.2},
            ]
        )

        fake_client = MagicMock()
        fake_client.invoke.return_value = FakeAIMessage("The answer is 42.")

        result = answer_question("What is the answer?", store, client=fake_client)

        self.assertEqual(result["answer"], "The answer is 42.")
        self.assertEqual(result["sources"], ["notes.txt", "report.pdf"])
        self.assertEqual(result["chunks_used"], 3)

        # confirm the prompt actually contains the retrieved context
        sent_messages = fake_client.invoke.call_args.args[0]
        human_role, human_content = sent_messages[1]
        self.assertEqual(human_role, "human")
        self.assertIn("chunk A", human_content)
        self.assertIn("report.pdf", human_content)

    def test_answer_question_with_no_matches(self):
        store = FakeStore([])
        fake_client = MagicMock()
        fake_client.invoke.return_value = FakeAIMessage("I don't have enough information.")

        result = answer_question("Unanswerable question", store, client=fake_client)
        self.assertEqual(result["sources"], [])
        self.assertEqual(result["chunks_used"], 0)


if __name__ == "__main__":
    unittest.main()
