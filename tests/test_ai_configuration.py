import pytest
from unittest.mock import MagicMock
from app.ai.providers import generate, is_configured, SetupRequired
from app.ai.schemas import GwenAnswer


def test_gemini_missing_key_is_not_ready(app, client):
    app.config.update(AI_PROVIDER='gemini', AI_MODEL='gemini-3.1-flash-lite', GEMINI_API_KEY='')
    with app.app_context():
        assert not is_configured()
        with pytest.raises(SetupRequired, match='API key'):
            generate('Explain loops', GwenAnswer)
    assert b'AI guidance needs a configured provider' in client.get('/').data


def test_gemini_sends_schema_and_validates_response(app, monkeypatch):
    from google import genai
    factory = MagicMock()
    client = factory.return_value.__enter__.return_value
    client.models.generate_content.return_value.text = '{"answer":"A loop repeats steps.","lesson_ids":[1]}'
    monkeypatch.setattr(genai, 'Client', factory)
    app.config.update(AI_PROVIDER='gemini', AI_MODEL='gemini-3.1-flash-lite', GEMINI_API_KEY='test-only-key')
    with app.app_context():
        assert is_configured()
        result = generate('Explain loops', GwenAnswer)
    assert result.lesson_ids == [1]
    call = client.models.generate_content.call_args.kwargs
    assert call['model'] == 'gemini-3.1-flash-lite'
    assert call['config'].response_schema is GwenAnswer
    assert call['config'].response_mime_type == 'application/json'
