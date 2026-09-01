import pytest

from app.ai.llm_models.openai_llm import resolve_openai_model


def test_openai_model_requires_explicit_real_id():
    with pytest.raises(ValueError, match="OPENAI_MODEL"):
        resolve_openai_model("")


def test_openai_model_is_passed_through_without_alias_mapping():
    assert resolve_openai_model("provider-model-id") == "provider-model-id"