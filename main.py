"""Streamlit app module for interactive chat management and display."""
from typing import Optional
import random
import json
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from streamlit_utils.ui_creator import display_question_answer, display_user_answer
from streamlit_utils.initialization import initialize_session
from streamlit_utils.status import display_progress
from llm_utils.stream_handler import StreamUntilSpecialTokenHandler
from llm_utils.conversation import Conversation
from llm_utils.questioning import Questioning
from llm_utils.analysing import Analysing
from llm_utils.prompt_assembly import prompt_assembly, get_non_zero_properties
from llm_utils.matching import match_car, get_full_name


def get_conversation() -> Optional[Conversation]:
    """Retrieve the current conversation instance from Streamlit's session state."""
    return st.session_state.get("conversation", None)

def get_questioning() -> Optional[Questioning]:
    """Retrieve the current questioning instance from Streamlit's session state."""
    return st.session_state.get("questioning", None)

def get_analysing() -> Optional[Analysing]:
    """Retrieve the current analysing instance from Streamlit's session state."""
    return st.session_state.get("analysing", None)

def handle_submission():
    """Process and submit user input, updating conversation history."""
    user_input = st.session_state.input_text
    user_prompt = prompt_assembly(st.session_state.user_inputs, user_input)
    user_message = HumanMessage(role="user", content=user_prompt)
    st.session_state.messages.append(user_message)
    st.session_state.conv_history.append(user_message)

    conversation_instance = get_conversation()

    with st.chat_message("assistant"):
        stream_handler = StreamUntilSpecialTokenHandler(st.empty())

        textual_response, json_response = conversation_instance(
            user_message, stream_handler)

        st.session_state.conv_history.append(AIMessage(
            role="assistant", content=textual_response))
        st.session_state.conv_history.append(
            AIMessage(role="assistant", content=json_response))
        st.session_state.messages.append(AIMessage(
            role="assistant", content=json_response))

    st.session_state.input_text = ""

    st.session_state.user_inputs = {}
    st.rerun()

def handle_questioning():
    properties = separate_and_select()
    st.session_state.last_properties = properties

    questioning_instance = get_questioning()
    persona = get_non_zero_properties(st.session_state.person)

    question_answer = questioning_instance(properties, persona)

    with st.chat_message("assistant"):
        st.session_state.conv_history.append(
            AIMessage(role="assistant", content=question_answer))
        st.session_state.messages.append(AIMessage(
            role="assistant", content=question_answer))

    st.session_state.user_inputs = {}
    st.rerun()

def separate_and_select():
    output = []
    zero_properties = []
    non_zero_properties = []

    for property, value in st.session_state.person.items():
        if value == 0:
            zero_properties.append(property)
        else:
            non_zero_properties.append(property)

    num_new_properties = random.choice([2, 3])
    selected_zero_properties = random.sample(zero_properties, min(num_new_properties, len(zero_properties)))

    selected_non_zero_property = None
    if len(selected_zero_properties) == 2 and non_zero_properties:
        selected_non_zero_property = random.choice(non_zero_properties)

    output.extend(selected_zero_properties)
    if selected_non_zero_property:
        output.append(selected_non_zero_property)
    return output

def analyze_response(response, chat_container):
    """Analyze the response and display the UI elements."""
    data = json.loads(response)
    analysing_instance = get_analysing()

    analysis = analysing_instance(data["question"], st.session_state.user_inputs[data["question"]], st.session_state.last_properties)

    st.session_state.conv_history.append(HumanMessage(role="user", content=analysis))
    st.session_state.messages.append(HumanMessage(role="user", content=analysis))
    
    update_person(analysis)
    if all(value != 0 for value in st.session_state.person.values()):
        calculate_match(chat_container)

def update_person(analysis):
    data = json.loads(analysis)
    for property in data["properties"]:
        if st.session_state.person[property["property_name"]] != 0:
            st.session_state.person[property["property_name"]] = (st.session_state.person[property["property_name"]] + property["property_value"]) / 2
        else:
            st.session_state.person[property["property_name"]] = property["property_value"]


def calculate_match(chat_container):
    conversation_instance = get_conversation()
    person_values = list(st.session_state.person.values())
    matches = match_car(person_values)

    car_string = ""

    for i in range(min(3, len(matches))):
        car_code = matches[i][1]
        car_full_name = get_full_name(car_code)
        car_string += f"{i+1}. {car_full_name}\n"

    with chat_container.chat_message("ai"):
        stream_handler = StreamUntilSpecialTokenHandler(st.empty())

        persona_string = get_non_zero_properties(st.session_state.person)

        textual_response = conversation_instance(persona_string, car_string, stream_handler)

        st.session_state.conv_history.append(AIMessage(
            role="ai", content=textual_response))
        st.session_state.messages.append(AIMessage(
            role="ai", content=textual_response))


def handle_sidebar():
    """Manage sidebar interactions for model selection and updates in the Streamlit app."""
    with st.sidebar:
        st.subheader("Conversation Agent")
        conv_selection = model_selection("Conversation")
        st.subheader("UI Agent")
        ui_selection = model_selection("UI")

        if st.button("Update Agents"):
            update_conversation(conv_selection, ui_selection)


def update_conversation(conv_selection, ui_selection):
    """Update the conversation instance with new models for conversation and UI agents."""
    conversation_instance = get_conversation()
    conversation_instance.update_agents(conv_selection, ui_selection)


def model_selection(agent):
    """Display and handle model selection radio button."""
    label = f"{agent} Model"
    options = st.session_state[f"supp_models_{agent.lower()}"]
    index = options.index(st.session_state[f"sel_model_{agent.lower()}"])

    selection = st.radio(label, options, index)
    st.session_state[f"sel_model_{agent.lower()}"] = selection

    return selection

def clear_cache():
    keys = list(st.session_state.keys())
    for key in keys:
        st.session_state.pop(key)


def main():
    """Main function to initialize and run the Streamlit application."""
    st.set_page_config(page_title="Carship", page_icon="❤️", initial_sidebar_state="collapsed", menu_items=None)
    initialize_session()
    #handle_sidebar()

    with st.expander("Debug Info"):
        st.write(st.session_state)

    st.title("Carship")
    st.subheader("Every 3 minutes an electric mercedes finds a new owner on carship.")

    if st.session_state.messages:
        st.divider()

    chat_container = st.container()

    for index, msg in enumerate(st.session_state.messages):
        if msg.role == "assistant":
            with chat_container.chat_message("assistant"):
                display_question_answer(
                    msg.content, index, len(st.session_state.messages)-1)
        elif msg.role == "ai":
            with chat_container.chat_message("ai"):
                st.markdown(msg.content)
        else:
            #display_user_answer(msg.content)
            #chat_container.chat_message(msg.role).write(msg.content)
            pass


    if st.session_state.messages:
        display_progress()
    st.divider()
    col1, col2 = st.columns(2)

    if col2.button("Restart Session"):
        clear_cache()
        st.rerun()


    button_text = "Submit"
    if len(st.session_state.messages) == 0:
        button_text = "Start the Journey"

    if col1.button(button_text, type="primary"):
        if len(st.session_state.messages) > 0:
            analyze_response(st.session_state.messages[-1].content, chat_container)
        handle_questioning()


if __name__ == "__main__":
    main()
