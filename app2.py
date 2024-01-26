from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated, Sequence, Dict, Optional
import operator
import os
from dotenv import load_dotenv
load_dotenv()

# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Define your state
class AgentState(TypedDict):
    messages: Annotated[Sequence[str], operator.add]
    summary: str  # or any other relevant state information
    extracted_info: Optional[Dict[str, str]]  # Dictionary to store extracted information for each keyword

# Initialize the ChatOpenAI model
model = ChatOpenAI()

agenda = """
Sarah and Christos are meeting to discuss their involvement in two hackathons in the next two weekends.

- How to get to SF on Fri
- Is Harrison technical?
- How to get to SJ on Fri and Sun next week
- What is Christos going to build?
- What functionality to add to the hackathon app next?
"""

new_transcript = """
Sarah: "Okay, so we've decided to drive together to San Francisco for the hackathon, right?"
Christos: "Yes, that's settled. I think it's the best choice considering our needs."

Sarah: "Good. Now, about Harrison's role. We've confirmed he's technical enough for our team?"
Christos: "Absolutely. He writes code and handles all the technical demos. He'll be a great asset."

Sarah: "Perfect. That's a relief. Now, regarding the San Jose hackathon, we're going to drive there separately and meet early, correct?"
Christos: "Right. It works out better for our schedules. I'll text you the details of where and when to meet in San Jose."

Sarah: "Sounds good. Lastly, tell me more about the app you've decided to build. I heard it's something special."
Christos: "Yes, it's quite exciting. I'm building the app you're reviewing right now. It integrates advanced features and aims to provide a unique user experience."

Sarah: "Wow, that's impressive! Building the app we're using for this conversation? That's quite meta. I can't wait to see it in action during the hackathons."
Christos: "Thanks! I think it will demonstrate a great blend of creativity and technical skill. Looking forward to collaborating on this."
Sarah: "Me too. Let's catch up again tomorrow to finalize everything."
Christos: "Agreed. See you then!"
"""

def todo_from_agenda():
    prompt = f"Create a todo list from the following agenda:\n{agenda}\n\nOutput should be a python list and nothing else."
    response = model.invoke(prompt)
    return eval(response.content)

todo = todo_from_agenda()

def done(item, completed_todo):
    # Add the resolved item to the completed_todo list
    completed_todo.append(item)

def got_resolved(item, transcript):
    resolution_eval_prompt = f"Instructions:\n Did {item} get resolved in meeting? Transcript: {transcript}\n Output either True or False. Output:"
    resolution_response = model.invoke(resolution_eval_prompt)
    return resolution_response.content.strip()

completed_todo = []

for item in todo:
    # Check if the item got resolved
    if got_resolved(item, new_transcript):
        done(item, completed_todo)

completed_todo

def generate_meeting_review(agenda, transcript, todo, completed_todo):
    report = "Meeting Review\n\n"

    # Adding Summary
    report += "Meeting Summary:\n" + "This meeting focused on discussing the logistics and technical aspects of the upcoming hackathons. Key decisions were made regarding travel arrangements and team roles.\n\n"

    # Action items (assuming no specific attendees are mentioned)
    report += "Action Items:\n"

    # Marking items as done or unresolved
    for item in todo:
        status = " ✅" if item in completed_todo else " ❌"
        report += f"- {item}{status}\n"

    return report

# Generate the meeting review
meeting_review = generate_meeting_review(agenda, new_transcript, todo, completed_todo)

print(meeting_review)

def extract_resolution_details(item, transcript, model):
    lines = transcript.split("\n")
    for line in lines:
        some_extraction_prompt = f"Check if the following line from a meeting transcript mentions and resolves the agenda item '{item}'. If yes, extract the resolution. If no, return 'None'.\n\nLine: '{line}'\nAgenda Item: '{item}'\n\nResolution:"

        resolution_response = model.invoke(some_extraction_prompt)
        response_content = resolution_response.content.strip()

        if response_content and response_content.lower() != 'none':
            return response_content
    return None

def generate_meeting_review(agenda, transcript, todo, completed_todo, model):
    report = "Meeting Review\n\n"

    # Adding Summary
    report += "Meeting Summary:\nThis meeting focused on discussing the logistics and technical aspects of the upcoming hackathons. Key decisions were made regarding travel arrangements and team roles.\n\n"

    # Action items
    report += "Action Items:\n"

    # Marking items as done or unresolved and adding resolution details
    for item in todo:
        resolution_detail = extract_resolution_details(item, transcript, model)
        if resolution_detail:
            status = f" ✅ ({resolution_detail})"
        else:
            status = " ❌"
        report += f"- {item}{status}\n"

    return report

# Generate the meeting review
meeting_review = generate_meeting_review(agenda, new_transcript, todo, completed_todo, model)
print(meeting_review)
