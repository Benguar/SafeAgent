from typing import TypedDict, Annotated
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_ollama import ChatOllama
import time 
from datetime import datetime,timezone
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.checkpoint.memory import MemorySaver
import ddgs
import httpx
import asyncio

PROMPT_ENDPOINT_URL= "http://127.0.0.1:8000/v1/safeagent/prompt"
TOOL_OUTPUT_URL = "http://127.0.0.1:8000/v1/safeagent/tool_output"
FINAL_OUTPUT_URL = "http://127.0.0.1:8000/v1/safeagent/final_output"
memory = MemorySaver()
ddg_search = DuckDuckGoSearchRun()
llm = ChatOllama(model="llama3.2", temperature=0)

class ChatState(TypedDict):
    user: str
    block: bool
    messages: Annotated[list, add_messages]
    tool: list
    time: float

initial_state = [{'role': 'system','content': 
   """You are a helpful assistant. 

CRITICAL AND MANDATORY RULES:
1. Every user message contains a METADATA section at the top indicating the current time. Use this strictly as your anchor for tracking years, days, or time-sensitive calculations.
2. NEVER include, repeat, mimic, or print the timestamp, date, or time in your response unless the user explicitly asks you what time it is.
3. Maintain a natural, conversational response format. Do not prefix your message with brackets or dates.
4. ONLY use tool to answer questions you do not know
5. NEVER use tool when you are sure about an answer or for casual conversations,greetings or natural conversation
"""
}]

tools  = [ddg_search]
llm_with_tools = llm.bind_tools(tools)
def chatbot(state: ChatState):
    print(f'------------------------------CALLING LLM------------------------------')
    state["time"] = time.time()
    assistant = llm_with_tools.invoke(state['messages'])
    message = {'role':'assistant','content': assistant.content}
    print(f'⏰-----------------------------{state["time"]-time.time()}------------------------------')
    return {'messages': assistant}
async def prompt_guard_node(state: ChatState):
    print("------------------------------USING PROMPT GUARD------------------------------")
    state["time"] = time.time()
    prompt = state["messages"][-1]
    async with httpx.AsyncClient() as client:
        result = await client.post(
            PROMPT_ENDPOINT_URL,
            json={
                "user_id": "test_id",
                "chat_id": prompt.id,
                "role": "user",
                "prompt": prompt.content  
            }

        )
    output = result.json()
    state['block'] = output['block']
    prompt.content = output['prompt']
    print(f'⏰-----------------------------{state["time"]-time.time()}------------------------------')
    return state
def prompt_checker(state:ChatState):
    if state["block"] == True:
        return "block"
    else:
        return "allow"
async def tool_guard_node(state: ChatState):
    print("------------------------------USING TOOL GUARD------------------------------")
    state["time"] = time.time()
    tool_message =  state.get('messages')[-1]
    
    async with httpx.AsyncClient(timeout=None) as client:
        result = await client.post(
            TOOL_OUTPUT_URL,
            json={
                "role": "tool",
                "tool_call_id": tool_message.tool_call_id,
                "name": tool_message.name,
                "content": tool_message.content
            }

        )
    tool_message.content = result.text
    print(f'⏰-----------------------------{state["time"]-time.time()}------------------------------')
    return state
async def output_guard_node(state: ChatState):
    print("------------------------------USING OUTPUT GUARD------------------------------")
    state["time"] = time.time()
    output = state["messages"][-1]
    async with httpx.AsyncClient(timeout=None) as client:
        result = await client.post(
            FINAL_OUTPUT_URL,
            json={
                "output": output.content
            }
        )
    output.content = result.text
    print(f'⏰-----------------------------{state["time"]-time.time()}------------------------------')
    return state
builder = StateGraph(ChatState)

#nodes
builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))
builder.add_node("prompt_guard_node", prompt_guard_node)
builder.add_node("prompt_status_checker", prompt_checker)
builder.add_node("tool_guard_node", tool_guard_node)
builder.add_node("output_guard_node", output_guard_node)

#edges
builder.add_edge(START,"prompt_guard_node")
builder.add_conditional_edges(

    "prompt_guard_node",
    prompt_checker,
    {
        "block": END,
        "allow": "chatbot"
    }
)
builder.add_conditional_edges('chatbot'
                              ,tools_condition,
                              {
                                "tools": "tools", #if tools are needed call tools
                                END: "output_guard_node"
                              }) #this checks if the llm requests a tool if it does not it ends the graph
builder.add_edge('tools','tool_guard_node')
builder.add_edge('tool_guard_node', 'chatbot')
builder.add_edge('chatbot', 'output_guard_node')


graph = builder.compile(checkpointer=memory)


png_data = graph.get_graph().draw_mermaid_png()


with open("./orchestration/agent_workflow.png", "wb") as f:
    f.write(png_data)
async def main():
    time_done = time.time()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC+0")
    config = {"configurable": {"thread_id": "1"}}
    first_turn = True
    while True:
        prompt = input("You:   ")
        message = {'role':'user','content': f"METADATA\nTemporal Anchor: {timestamp}\n\nMessage: {prompt}"}
        if first_turn:
            initial_state.append(message)
            first_turn = False
            response = await graph.ainvoke({'messages': initial_state,"time": time_done}, config=config)
        else:
            response = await graph.ainvoke({'messages': message,"time": time_done}, config=config)
        print(f'\nassistant🤖:   {response['messages'][-1].content}\n')

asyncio.run(main())