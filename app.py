from fastapi import FastAPI
from graph import graph_workflow  # Replace 'your_module' with the actual module name
from typing import List, Dict

app = FastAPI()

# Import your LangGraph setup and other necessary components

# Global variables to hold state - this is a simplified example, consider a more robust state management for production
state = {
    "agenda": "",
    "transcript": "",
    "todo": [],
    "completed_todo": [],
    "summary": ""
}

@app.on_event("startup")
async def startup_event():
    # Initialize your LangGraph workflow here if needed
    pass

@app.get("/current_transcript")
async def get_current_transcript():
    return {"transcript": state["transcript"]}

@app.get("/summary")
async def get_summary():
    # Here, invoke the LangGraph app with the required state
    result = app.invoke(state)  # Assuming 'app' is your LangGraph compiled app
    state.update(result)  # Update the global state with the new result
    return {"summary": state["summary"]}

@app.get("/todo_items")
async def get_todo_items():
    return {"todo_items": state["todo"]}

@app.post("/update_transcript")
async def update_transcript(transcript: str):
    state["transcript"] = transcript
    # You may want to call LangGraph app here to update todo and summary based on the new transcript
    return {"success": True}

@app.post("/generate_action_items")
async def generate_action_items():
    # Here, invoke the LangGraph app to process the state
    result = app.invoke(state)  # Assuming 'app' is your LangGraph compiled app
    state.update(result)  # Update the global state with the new result
    return {"success": True}

# Example endpoint using the workflow
@app.post("/process")
async def process(state: dict):
    return graph_workflow.invoke(state)

# Add more endpoints as necessary

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)