import time
from abc import ABC, abstractmethod
import httpx
from flask import current_app
class SetupRequired(Exception): pass
def is_configured():
    """Check required settings, without claiming the provider is reachable."""
    c = current_app.config
    if not c['AI_MODEL'].strip():
        return False
    if c['AI_PROVIDER'] == 'gemini':
        return bool(c['GEMINI_API_KEY'].strip())
    if c['AI_PROVIDER'] == 'ollama':
        return bool(c['AI_ENDPOINT'].strip())
    return False

class Provider(ABC):
    @abstractmethod
    def generate(self,prompt,schema): pass
class Ollama(Provider):
    def generate(self,prompt,schema):
        c=current_app.config
        with httpx.Client(timeout=c['AI_TIMEOUT']) as client:
            r=client.post(c['AI_ENDPOINT'].rstrip('/')+'/api/generate',json={'model':c['AI_MODEL'],'prompt':prompt,'stream':False,'format':schema.model_json_schema(),'options':{'temperature':0.3,'num_predict':4096}})
            r.raise_for_status()
            return schema.model_validate_json(r.json()['response'])
class Gemini(Provider):
    def generate(self,prompt,schema):
        from google import genai
        from google.genai import types
        c=current_app.config
        if not c['GEMINI_API_KEY']: raise SetupRequired('Gemini API key is not configured')
        with genai.Client(api_key=c['GEMINI_API_KEY'],http_options=types.HttpOptions(timeout=c['AI_TIMEOUT']*1000)) as client:
            response=client.models.generate_content(model=c['AI_MODEL'],contents=prompt,config=types.GenerateContentConfig(response_mime_type='application/json',response_schema=schema,temperature=0.3,max_output_tokens=4096))
            return schema.model_validate_json(response.text)
def generate(prompt,schema):
    if not current_app.config['AI_MODEL']: raise SetupRequired('Set AI_MODEL and configure an AI provider first')
    provider={'gemini':Gemini,'ollama':Ollama}.get(current_app.config['AI_PROVIDER'])
    if not provider: raise SetupRequired('Unsupported AI provider')
    for retry in range(3):
        try: return provider().generate(prompt,schema)
        except SetupRequired: raise
        except Exception:
            if retry==2: raise SetupRequired('AI service unavailable or returned invalid structured content. Try again later.') from None
            time.sleep(0.5*(retry+1))
