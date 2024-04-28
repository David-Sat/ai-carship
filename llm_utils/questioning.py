import json
from typing import Callable
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from llm_utils.agents import QuestioningAgent
from llm_utils.pydantic_models import QuestionAnswer
from typing import List

class Questioning:
    """Initializes questioning agent with specified models and API keys."""

    def __init__(
            self,
            api_keys: dict,
            model_name_qa="gpt-3.5-turbo-1106",
            ) -> None:
        """Initialize questioning agent using given API keys and model names."""
        self.api_keys = api_keys

        qa_model = self.create_model(model_name_qa, streaming=False)

        self.questioning_agent = QuestioningAgent(qa_model)


    def __call__(self, properties: List[str], persona: str) -> str:
        """Process a list of properties through the questioning agent and generate a QuestionAnswer response."""
        question_answer = self.questioning_agent(properties, persona)

        question_answer = json.dumps(question_answer)

        return question_answer

    def update_agent(self, model_name_qa: str):
        """Update questioning agent with new model."""
        print(f"Updating agent with model {model_name_qa}")
        qa_agent_model = self.create_model(model_name=model_name_qa, streaming=False)

        self.questioning_agent.update_model(qa_agent_model)

    def create_model(self, model_name: str, streaming=False):
        """Create a model instance based on model name and streaming capability."""
        if model_name in ("gpt-3.5-turbo-1106", "gpt-4-turbo-preview"):
            api_key = self.api_keys["openai"]
            return ChatOpenAI(openai_api_key=api_key, model_name=model_name, streaming=streaming)

        return None