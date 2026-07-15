import unittest

from services.rag_service import run_rag


class RAGServiceTest(unittest.TestCase):
    def test_returns_excerpt_for_matching_content(self):
        question = "What should I do when an incident happens?"
        sop_content = "When an incident happens, escalate immediately and follow the response checklist."

        answer, excerpt = run_rag(question, sop_content)

        self.assertIn("According to the SOP", answer)
        self.assertIn("incident", excerpt.lower())


if __name__ == '__main__':
    unittest.main()
