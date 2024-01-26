from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence, Dict, Optional
import operator
from langchain_openai import ChatOpenAI

# Define your state
class AgentState(TypedDict):
    agenda: str
    transcript: str
    todo: Sequence[str]
    completed_todo: Sequence[str]
    summary: str
    extracted_info: Optional[Dict[str, str]]

# Initialize the ChatOpenAI model
model = ChatOpenAI()

# Define nodes
def node_todo_from_agenda(state: AgentState):
    prompt = f"Create a todo list from the following agenda:\n{state['agenda']}\n\nOutput should be a python list and nothing else."
    response = model.invoke(prompt)
    state['todo'] = eval(response.content)
    return state

def node_got_resolved(state: AgentState):
    for item in state['todo']:
        resolution_eval_prompt = f"Instructions:\n Did {item} get resolved in meeting? Transcript: {state['transcript']}\n Output either True or False. Output:"
        resolution_response = model.invoke(resolution_eval_prompt)
        if resolution_response.content.strip() == 'True':
            if 'completed_todo' not in state:
                state['completed_todo'] = []
            state['completed_todo'].append(item)
    return state

def node_generate_meeting_review(state: AgentState):
    report = "Meeting Review\n\n"
    report += "Meeting Summary:\n" + "This meeting focused on discussing the logistics and technical aspects of the upcoming hackathons. Key decisions were made regarding travel arrangements and team roles.\n\n"
    report += "Action Items:\n"
    for item in state['todo']:
        status = " ✅" if item in state.get('completed_todo', []) else " ❌"
        report += f"- {item}{status}\n"
    state['summary'] = report
    return state

def node_extract_resolution_details(state: AgentState):
    extracted_info = {}
    for item in state['todo']:
        lines = state['transcript'].split("\n")
        for line in lines:
            some_extraction_prompt = f"Check if the following line from a meeting transcript mentions and resolves the agenda item '{item}'. If yes, extract the resolution. If no, return 'None'.\n\nLine: '{line}'\nAgenda Item: '{item}'\n\nResolution:"
            resolution_response = model.invoke(some_extraction_prompt)
            response_content = resolution_response.content.strip()
            if response_content and response_content.lower() != 'none':
                extracted_info[item] = response_content
    state['extracted_info'] = extracted_info
    return state

# Define the graph
def graph_workflow():
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("todo_from_agenda", node_todo_from_agenda)
    workflow.add_node("got_resolved", node_got_resolved)
    workflow.add_node("generate_meeting_review", node_generate_meeting_review)
    workflow.add_node("extract_resolution_details", node_extract_resolution_details)

    # Set entry point
    workflow.set_entry_point("todo_from_agenda")

    # Add edges
    workflow.add_edge("todo_from_agenda", "got_resolved")
    workflow.add_edge("got_resolved", "generate_meeting_review")
    workflow.add_edge("generate_meeting_review", "extract_resolution_details")
    workflow.add_edge("extract_resolution_details", END)

    # Compile the graph
    return workflow.compile()

# Instantiate the graph
workflow_app = graph_workflow()
