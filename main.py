from typing import Annotated, TypedDict
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model


load_dotenv()


llm = init_chat_model("google_genai:gemini-2.0-flash")


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


graph_builder = StateGraph(State)
graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream(
            {"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant: ", value["messages"][-1].content)


if __name__ == "__main__":
    while True:
        try:
            user_input = input("> ")
            if user_input.lower() in ["quit", "q", "exit"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input)
        except Exception:
            user_input = "What do you know about AI?"
            print("User", user_input)
            stream_graph_updates(user_input)
            break
