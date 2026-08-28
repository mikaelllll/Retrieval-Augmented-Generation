from app.services.retrieval import is_overview_question


def test_detects_document_overview_questions() -> None:
    assert is_overview_question("What is this document about?")
    assert is_overview_question("Please give me a summary of this document.")
    assert is_overview_question("Give me an overview")


def test_does_not_treat_factual_question_as_overview() -> None:
    assert not is_overview_question("How many years of Python experience does the candidate have?")
