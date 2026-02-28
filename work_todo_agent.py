import streamlit as st
import os
import json
import uuid
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ----------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Work To‑Do Agent",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------------------------------------------------
# CUSTOM CSS – light, modern design
# ----------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        font-family: 'Inter', sans-serif;
    }
    #MainMenu, footer, header {visibility: hidden;}
    .custom-nav {
        background: white;
        border-bottom: 1px solid #e2e8f0;
        padding: 0.8rem 2rem;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-radius: 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .logo {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0f172a;
    }
    .logo span { color: #7c3aed; }
    .nav-links { display: flex; gap: 2rem; color: #475569; font-weight: 500; }
    .nav-links a { color: inherit; text-decoration: none; transition: color 0.2s; }
    .nav-links a:hover { color: #7c3aed; }
    .status-badge {
        background: #7c3aed;
        color: white;
        padding: 0.4rem 1.2rem;
        border-radius: 30px;
        font-size: 0.9rem;
        font-weight: 600;
        box-shadow: 0 2px 10px rgba(124,58,237,0.2);
    }
    .sidebar-section {
        background: #f8fafc;
        border-radius: 20px;
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        border: 1px solid #e2e8f0;
    }
    /* Task cards */
    .task-card {
        background: white;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
        border: 1px solid #e2e8f0;
        transition: box-shadow 0.2s;
    }
    .task-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.04); }
    .task-title {
        font-weight: 600;
        font-size: 1.1rem;
        color: #0f172a;
    }
    .task-meta {
        display: flex;
        gap: 1rem;
        font-size: 0.85rem;
        color: #64748b;
        margin-top: 0.4rem;
    }
    .priority-high { border-left: 4px solid #ef4444; }
    .priority-medium { border-left: 4px solid #f59e0b; }
    .priority-low { border-left: 4px solid #10b981; }
    .completed {
        opacity: 0.6;
        text-decoration: line-through;
    }
    /* Message bubbles */
    .user-message {
        background: #7c3aed;
        color: white;
        border-radius: 22px 22px 4px 22px;
        padding: 12px 18px;
        margin: 10px 0;
        max-width: 70%;
        float: right;
        clear: both;
        box-shadow: 0 4px 12px rgba(124,58,237,0.15);
    }
    .assistant-message {
        background: white;
        color: #0f172a;
        border-radius: 22px 22px 22px 4px;
        padding: 15px 20px;
        margin: 10px 0;
        max-width: 70%;
        float: left;
        clear: both;
        box-shadow: 0 4px 12px rgba(0,0,0,0.02);
        border: 1px solid #e2e8f0;
        border-left: 4px solid #7c3aed;
    }
    .stChatInput textarea {
        background: white !important;
        border: 2px solid #e2e8f0 !important;
        border-radius: 30px !important;
        color: #0f172a !important;
    }
    .stChatInput textarea:focus {
        border-color: #7c3aed !important;
        box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important;
    }
    .custom-footer {
        margin-top: 4rem;
        border-top: 1px solid #e2e8f0;
        padding: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        color: #64748b;
        font-size: 0.9rem;
        background: white;
    }
    .custom-footer a { color: #64748b; text-decoration: none; margin: 0 1rem; }
    .custom-footer a:hover { color: #7c3aed; }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.image("https://img.icons8.com/fluency/96/todo-list.png", width=80)
    st.markdown("### ⚙️ Configuration")
    api_key = st.text_input(
        "OpenRouter API Key",
        type="password",
        value=os.getenv("OPENROUTER_API_KEY", ""),
        help="Get your free key at openrouter.ai/keys"
    )
    model = "z-ai/glm-4.5-air:free"
    st.info(f"🧠 Model: `{model}`")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 📋 How to Use")
    st.markdown("""
    Type natural language commands like:
    - *Add task: Prepare report by Friday high priority*
    - *Show my tasks*
    - *Mark task 1 as done*
    - *Delete task 2*
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# NAVIGATION
# ----------------------------------------------------------------------
st.markdown("""
<div class="custom-nav">
    <div class="logo">Work<span>To‑Do</span></div>
    <div class="nav-links"><a href="#">Tasks</a><a href="#">Calendar</a><a href="#">Settings</a></div>
    <div class="status-badge"><i class="fa-regular fa-circle-check"></i> Agent Ready</div>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# MAIN TITLE
# ----------------------------------------------------------------------
st.markdown("""
<div style="text-align: center; margin-bottom: 2rem;">
    <h1 style="font-size: 3rem; font-weight: 700; color: #0f172a;">✅ Work To‑Do Agent</h1>
    <p style="color: #475569;">Your AI‑powered task manager – just type naturally.</p>
</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------
# TASK STORAGE (in session state)
# ----------------------------------------------------------------------
if "tasks" not in st.session_state:
    st.session_state.tasks = []  # list of dicts: id, title, due_date, priority, completed

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "You are a helpful Work To-Do Agent. Your job is to manage tasks via natural language. "
            "You have access to the following functions:\n"
            "- add_task(title, due_date=None, priority='medium')\n"
            "- list_tasks(filter='all')\n"
            "- complete_task(task_id)\n"
            "- delete_task(task_id)\n"
            "Always call the appropriate function based on the user's request. "
            "After each operation, you should return a confirmation message and also show the updated task list. "
            "Keep responses concise and friendly."
        )}
    ]

if "openai_client" not in st.session_state:
    st.session_state.openai_client = None

# ----------------------------------------------------------------------
# HELPER: Convert message object to dict
# ----------------------------------------------------------------------
def message_to_dict(msg):
    if isinstance(msg, dict):
        return msg
    d = {"role": msg.role, "content": msg.content}
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        d["tool_calls"] = [tc.model_dump() for tc in msg.tool_calls]
    return d

# ----------------------------------------------------------------------
# TASK FUNCTIONS (tools)
# ----------------------------------------------------------------------
def add_task(title, due_date=None, priority="medium"):
    task = {
        "id": str(uuid.uuid4())[:8],
        "title": title,
        "due_date": due_date,
        "priority": priority,
        "completed": False,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    st.session_state.tasks.append(task)
    return {"success": True, "task": task}

def list_tasks(filter="all"):
    if filter == "completed":
        tasks = [t for t in st.session_state.tasks if t["completed"]]
    elif filter == "incomplete":
        tasks = [t for t in st.session_state.tasks if not t["completed"]]
    else:
        tasks = st.session_state.tasks
    return {"tasks": tasks}

def complete_task(task_id):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            t["completed"] = True
            return {"success": True, "task": t}
    return {"success": False, "error": "Task not found"}

def delete_task(task_id):
    for i, t in enumerate(st.session_state.tasks):
        if t["id"] == task_id:
            deleted = st.session_state.tasks.pop(i)
            return {"success": True, "task": deleted}
    return {"success": False, "error": "Task not found"}

# ----------------------------------------------------------------------
# DISPLAY TASKS (in a nice grid)
# ----------------------------------------------------------------------
def display_tasks():
    if not st.session_state.tasks:
        st.info("No tasks yet. Add one above!")
        return

    # Sort: incomplete first, then by priority
    incomplete = [t for t in st.session_state.tasks if not t["completed"]]
    complete = [t for t in st.session_state.tasks if t["completed"]]

    # Priority order: high > medium > low
    def priority_order(t):
        p = t.get("priority", "medium")
        return {"high": 0, "medium": 1, "low": 2}.get(p, 1)

    incomplete.sort(key=priority_order)
    complete.sort(key=lambda t: t.get("due_date", ""))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📝 To Do")
        for task in incomplete:
            priority_class = f"priority-{task.get('priority', 'medium')}"
            due = task.get("due_date", "No due date")
            st.markdown(f"""
            <div class="task-card {priority_class}">
                <div class="task-title">{task['title']}</div>
                <div class="task-meta">
                    <span>📅 {due}</span>
                    <span>⚡ {task['priority'].capitalize()}</span>
                    <span>🆔 {task['id']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col2:
        st.markdown("### ✅ Completed")
        for task in complete:
            st.markdown(f"""
            <div class="task-card completed priority-{task.get('priority', 'medium')}">
                <div class="task-title">{task['title']}</div>
                <div class="task-meta">
                    <span>📅 {task.get('due_date', 'No due date')}</span>
                    <span>🆔 {task['id']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ----------------------------------------------------------------------
# CORE AGENT FUNCTION (with tool calling)
# ----------------------------------------------------------------------
def call_agent(user_input):
    if not st.session_state.openai_client:
        if not api_key:
            return "**Status**: Error\n**Task Summary**: Missing API key.", st.session_state.messages
        st.session_state.openai_client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    client = st.session_state.openai_client

    st.session_state.messages.append({"role": "user", "content": user_input})

    # Define tools (functions)
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Add a new task",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Task title/description"},
                        "due_date": {"type": "string", "description": "Due date (optional)"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Priority level"}
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List tasks, optionally filtered",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filter": {"type": "string", "enum": ["all", "completed", "incomplete"], "description": "Filter tasks"}
                    }
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "complete_task",
                "description": "Mark a task as completed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "ID of the task to complete"}
                    },
                    "required": ["task_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "delete_task",
                "description": "Delete a task permanently",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string", "description": "ID of the task to delete"}
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]

    try:
        response = client.chat.completions.create(
            model=model,
            messages=st.session_state.messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2
        )
        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            assistant_dict = message_to_dict(assistant_message)
            st.session_state.messages.append(assistant_dict)

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                if func_name == "add_task":
                    result = add_task(args["title"], args.get("due_date"), args.get("priority", "medium"))
                elif func_name == "list_tasks":
                    result = list_tasks(args.get("filter", "all"))
                elif func_name == "complete_task":
                    result = complete_task(args["task_id"])
                elif func_name == "delete_task":
                    result = delete_task(args["task_id"])
                else:
                    result = {"error": f"Unknown function {func_name}"}

                # Append tool response
                st.session_state.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            # Second call to get final response
            second_response = client.chat.completions.create(
                model=model,
                messages=st.session_state.messages,
                temperature=0.2
            )
            final_message = second_response.choices[0].message
            final_dict = message_to_dict(final_message)
            st.session_state.messages.append(final_dict)
            return final_dict["content"], st.session_state.messages

        else:
            assistant_dict = message_to_dict(assistant_message)
            st.session_state.messages.append(assistant_dict)
            return assistant_dict["content"], st.session_state.messages

    except Exception as e:
        error_msg = f"**Status**: Error\n**Task Summary**: API call failed\n**Details**: {str(e)}"
        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        return error_msg, st.session_state.messages

# ----------------------------------------------------------------------
# UI LAYOUT
# ----------------------------------------------------------------------
# Display tasks at the top (so user can see current tasks)
display_tasks()

st.divider()

# Chat history display
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        if not isinstance(msg, dict):
            continue
        if msg["role"] == "user":
            st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
        elif msg["role"] == "assistant" and not msg.get("tool_calls"):
            st.markdown(f'<div class="assistant-message">{msg["content"]}</div>', unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Type a command... (e.g., 'Add task: Buy milk')"):
    st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)
    with st.spinner("🧠 Processing..."):
        response, _ = call_agent(prompt)
    st.rerun()

# ----------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------
st.markdown("""
<div class="custom-footer">
    <div>© 2025 Work To‑Do Agent · AI task management</div>
    <div><a href="#">index</a> · <a href="#">docs</a> · <a href="#">status</a></div>
    <div><i class="fa-brands fa-x-twitter"></i> <i class="fa-brands fa-github"></i> <i class="fa-brands fa-discord"></i></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">', unsafe_allow_html=True)