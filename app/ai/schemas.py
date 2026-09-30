from typing import Literal
from pydantic import BaseModel, Field, model_validator
class TestCase(BaseModel):
    stdin: str = Field(max_length=10000)
    expected: str = Field(max_length=10000)
    weight: int = Field(default=1, ge=1, le=10)
    visible: bool = False
class QuestionData(BaseModel):
    prompt: str = Field(min_length=10,max_length=5000)
    category: Literal['concept','error','output','code']
    difficulty: Literal['beginner','intermediate','advanced'] = 'beginner'
    code: str = Field(default='',max_length=10000)
    options: list[str] = Field(default_factory=list)
    correct: int | None = None
    explanation: str = Field(min_length=10,max_length=5000)
    tests: list[TestCase] = Field(default_factory=list,max_length=20)
    reference: str = Field(default='',max_length=10000)
    runtime: str = ''
    error_category: str = ''
    code_kind: Literal['short_code','complete_code','write_code'] = 'short_code'
    @model_validator(mode='after')
    def valid(self):
        if self.category != 'code':
            if len(self.options)!=4 or len(set(self.options))!=4 or self.correct not in range(4): raise ValueError('Four unique options and one correct index required')
        elif not self.tests or not self.reference or not self.runtime:
            raise ValueError('Coding questions require tests, reference solution, and runtime')
        return self
class Feedback(BaseModel):
    summary: str = Field(max_length=3000)
    strengths: list[str] = Field(max_length=10)
    improvements: list[str] = Field(max_length=10)

class GwenAnswer(BaseModel):
    answer: str = Field(min_length=1,max_length=3000)
    lesson_ids: list[int] = Field(default_factory=list,max_length=5)
