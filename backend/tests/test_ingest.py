"""Tests for chunking logic. No external dependencies required —
these run with plain Python, so they're a fast, reliable CI check."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ingest import chunk_text, Chunk  # noqa: E402


class ChunkTextTests(unittest.TestCase):
    def test_empty_text_returns_no_chunks(self):
        self.assertEqual(chunk_text("", source="a.txt"), [])

    def test_short_text_returns_one_chunk(self):
        chunks = chunk_text("hello world", source="a.txt", chunk_size=800, chunk_overlap=150)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].text, "hello world")
        self.assertEqual(chunks[0].source, "a.txt")

    def test_long_text_splits_into_multiple_chunks(self):
        words = " ".join(f"word{i}" for i in range(1000))
        chunks = chunk_text(words, source="doc.pdf", chunk_size=300, chunk_overlap=50)
        self.assertGreater(len(chunks), 1)
        # every chunk index increments
        self.assertEqual([c.chunk_index for c in chunks], list(range(len(chunks))))

    def test_overlap_shares_words_between_consecutive_chunks(self):
        chunk_overlap = 50
        words = " ".join(f"w{i}" for i in range(500))
        chunks = chunk_text(words, source="doc.txt", chunk_size=200, chunk_overlap=chunk_overlap)
        # the overlap region is exactly `chunk_overlap` words wide: the
        # tail of chunk N equals the head of chunk N+1 there.
        first_tail = chunks[0].text.split()[-chunk_overlap:]
        second_head = chunks[1].text.split()[:chunk_overlap]
        self.assertEqual(first_tail, second_head)

    def test_overlap_must_be_smaller_than_chunk_size(self):
        with self.assertRaises(ValueError):
            chunk_text("some text here", source="a.txt", chunk_size=100, chunk_overlap=100)

    def test_no_word_is_split_in_half(self):
        words = " ".join(f"token{i}" for i in range(200))
        chunks = chunk_text(words, source="a.txt", chunk_size=50, chunk_overlap=10)
        all_words = set(words.split())
        for c in chunks:
            for w in c.text.split():
                self.assertIn(w, all_words)


if __name__ == "__main__":
    unittest.main()
