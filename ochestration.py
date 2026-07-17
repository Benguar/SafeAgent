from typing import TypedDict, Annotated
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
import time 
from datetime import datetime,timezone
llm = ChatOllama(model="llama3.2", temperature=0)

class ChatState(TypedDict):
    user: str
    messages: Annotated[list, add_messages]
initial_state = [{'role': 'system','content': 
    "You are a helpful assistant. Every user message you receive will be prefixed with a timestamp "
    "indicating the current date and time. Use this timestamp as your absolute temporal anchor for "
    "all calculations, context, and references. Do not repeat the timestamp back to the user; "
    "simply use it to understand when the conversation is happening."
    "Use previous prompts for context only when relating or necessary with the latest prompt'"
}]
def prompt_input(state: ChatState) -> ChatState:
    prompt = input("You:   ")
    print(prompt)
    message = {'role':'user','content': f'[Context - Current Time: {datetime.now(timezone.utc)} \n user prompt {prompt}]'}
    initial_state.append(message)
    state['messages'] = initial_state
    print(state)
    return state
def chatbot(state: ChatState):
    assistant = llm.invoke(state['messages'])
    message = {'role':'assistant','content': assistant.content}
    initial_state.append(message)
    print(assistant.content)
    return state
builder = StateGraph(ChatState)

builder.add_node("prompt_input", prompt_input)
builder.add_node("chatbot", chatbot)

#edges
builder.add_edge(START,'chatbot')
builder.add_edge('chatbot', END)
graph = builder.compile()
while True:
    prompt = input("You:   ")
    message = {'role':'user','content': prompt}
    initial_state.append(message)
    response = graph.invoke({'messages': initial_state})
    # print(response)
    clock = time.time()
    # print(f'{response} \n\n {datetime.now(timezone.utc)}')
