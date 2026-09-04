from evaluation.rag_evaluation import run_rag_evaluation


def test_rag_evaluation_distinguishes_retrieval_failure():
    manager = type("Rag", (), {"get_relevant_sources": lambda self, question, section: [{"document": "other.pdf", "score": 0.7}]})()
    records = run_rag_evaluation([{"id": "case", "question": "q", "section": "problems", "expected_document": "expected.pdf"}], manager)
    assert records[0]["retrieval_status"] == "RETRIEVAL_FAILURE"
    assert records[0]["generation_status"] == "NOT_EVALUABLE_RETRIEVAL_FAILURE"