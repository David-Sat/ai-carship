"""Module for defining agents that interact with LLMs for conversational and UI responses."""
from typing import Callable, List
import traceback
from langchain.schema import StrOutputParser
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate, PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import ValidationError
from llm_utils.pydantic_models import Output, QuestionAnswer, PropertyRating
from llm_utils.config_loader import load_few_shot_examples, load_config
from llm_utils.stream_handler import DebugHandler


class Agent:
    """Base class for agents interacting with LLMs."""

    def __init__(self, model):
        self.model = model
        self.config = load_config()

        self.example_prompt = ChatPromptTemplate.from_messages(
            [
                ("human", "{input}"),
                ("ai", "{output}"),
            ]
        )

    def update_model(self, model):
        """Updates the agent's model."""
        self.model = model

    def get_model(self):
        """Returns the agent's model."""
        return self.model


class ConversationalAgent(Agent):
    """Agent for handling conversations."""

    def __init__(self, model):
        super().__init__(model)
        self.memory = []
        self.system_prompt = self.config["conversational_prompt"]

    def __call__(self, persona: str, cars: str, stream_handler: Callable) -> str:

        prompt = PromptTemplate(
            template="{system_prompt}\n{cars}\n{memory}",
            input_variables=["persona", "cars"],
            partial_variables={"system_prompt": self.system_prompt, "memory": '\n'.join([str(msg) for msg in self.memory])},
        )

        chain = (
            prompt
            | self.model
            | StrOutputParser()
        )

        config = {"callbacks": [stream_handler]}
        response = chain.invoke(input={"persona": persona, "cars": cars}, config=config)
        self.memory.append(AIMessage(role="assistant", content=response))
        return response


class QuestioningAgent(Agent):
    """Agent for generating responses based on a list of properties."""

    def __init__(self, model):
        super().__init__(model)
        self.system_prompt = self.config["questioning_prompt"]

    def __call__(self, properties: List[str], persona: str) -> str:
        properties = ", ".join(properties)
        parser = PydanticOutputParser(pydantic_object=QuestionAnswer)

        prompt = PromptTemplate(
            template="{system_prompt}\n{persona}\n{format_instructions}\nThe Properties you need to create a question for: {properties}",
            input_variables=["properties", "persona"],
            partial_variables={"system_prompt": self.system_prompt,
                               "format_instructions": parser.get_format_instructions()},
        )

        chain = (
            prompt
            | self.model
            | parser
        )

        handler = DebugHandler()
        config = {"callbacks": [handler]}

        retries = 3
        for attempt in range(retries):
            try:
                validated_data = chain.invoke(
                    input={"properties": properties, "persona": persona}, config=config)
                return validated_data.dict()

            except ValidationError as e:
                print(f"Validation error on attempt {attempt+1}: {e}")
                if attempt == retries - 1:
                    return None
                print("Retrying...")
            except Exception as e:
                print(f"Unexpected error: {traceback.format_exc()} - {e}")
                return None
            
class PropertyMatchingAgent(Agent):
    """Agent for generating responses based on a question and user's answer."""

    def __init__(self, model):
        super().__init__(model)
        self.system_prompt = self.config["property_matching_prompt"]

    def __call__(self, question: str, user_answer: str, properties: List[str]) -> PropertyRating:
        properties = ", ".join(properties)
        parser = PydanticOutputParser(pydantic_object=PropertyRating)

        prompt = PromptTemplate(
            template="{system_prompt}\nQuestion: {question}\nUser Answer: {user_answer}\nProperties: {properties}\n{format_instructions}",
            input_variables=["question", "user_answer"],
            partial_variables={"system_prompt": self.system_prompt,
                               "format_instructions": parser.get_format_instructions(),
                               "properties": properties
                               },
        )

        chain = (
            prompt
            | self.model
            | parser
        )

        handler = DebugHandler()
        config = {"callbacks": [handler]}

        retries = 3  # Number of retries
        for attempt in range(retries):
            try:
                validated_data = chain.invoke(
                    input={"question": question, "user_answer": user_answer}, config=config)
                return validated_data.dict()
            except ValidationError as e:
                print(f"Validation error on attempt {attempt+1}: {e}")
                if attempt == retries - 1:
                    return None
                print("Retrying...")
            except Exception as e:
                print(f"Unexpected error: {traceback.format_exc()} - {e}")
                return None
class UIAgent(Agent):
    """Agent for generating UI responses based on model outputs."""

    def __init__(self, model):
        super().__init__(model)
        self.system_prompt = self.config["ui_prompt"]

    def __call__(self, message) -> str:
        parser = PydanticOutputParser(pydantic_object=Output)

        prompt = PromptTemplate(
            template="{system_prompt}\n{format_instructions}\n{message}",
            input_variables=["message"],
            partial_variables={"system_prompt": self.system_prompt,
                               "format_instructions": parser.get_format_instructions()},
        )

        chain = (
            prompt
            | self.model
            | parser
        )

        handler = DebugHandler()
        config = {"callbacks": [handler]}

        retries = 3  # Number of retries
        for attempt in range(retries):
            try:
                validated_data = chain.invoke(
                    input={"message": message}, config=config)
                return validated_data.dict()
            except ValidationError as e:
                print(f"Validation error on attempt {attempt+1}: {e}")
                if attempt == retries - 1:
                    return None
                print("Retrying...")
            except Exception as e:
                print(f"Unexpected error: {traceback.format_exc()} - {e}")
                return None
