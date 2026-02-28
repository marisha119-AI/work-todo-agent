import streamlit as st
import os
import json
import uuid
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

# ── SECURE API KEY HANDLER ────────────────────────────────
def get_api_key():
    # First try Streamlit Secrets (cloud)
    try:
        key = st.secrets["OPENROUTER_API_KEY"]
        if key:
            return key
    except:
        pass
    # Then try .env (local)
    try:
        key = os.getenv("OPENROUTER_API_KEY", "")
        if key:
            return key
    except:
        pass
    return None

api_key = get_api_key()

# ── Page Config ───────────────────────────────────────────
st.set_page_config(
    page_title="Work To-Do Agent",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Block if no API key ───────────────────────────────────
if not api_key:
    st.markdown("""
    <div style="background:#1e2130; padding:40px;
                border-radius:15px; text-align:center; margin-top:50px;">
        <h2 style="color:#ff4444;">⚠️ Configuration Required</h2>
        <p style="color:#aaa;">Please contact the app administrator.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Custom CSS ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background: #0a0b0f;
}

#MainMenu, footer, header { visibility: hidden; }

/* ── Hero Header ── */
.hero-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border: 1px solid #1e3a5f;
    padding: 40px;
    border-radius: 20px;
    margin-bottom: 30px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(99,102,241,0.1) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-size: 3rem;
    font-weight: 800;
    color: white;
    margin: 0;
    letter-spacing: -1px;
}
.hero-title span { color: #818cf8; }
.hero-subtitle {
    color: #94a3b8;
    font-size: 1.1rem;
    margin: 10px 0 0 0;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,102,241,0.2);
    border: 1px solid rgba(99,102,241,0.4);
    color: #818cf8;
    padding: 6px 16px;
    border-radius: 30px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: 15px;
}

/* ── Stats Bar ── */
.stats-bar {
    display: flex;
    gap: 15px;
    margin-bottom: 25px;
}
.stat-card {
    flex: 1;
    background: #12131a;
    border: 1px solid #1e2d3d;
    border-radius: 14px;
    padding: 20px;
    text-align: center;
}
.stat-number {
    font-size: 2.2rem;
    font-weight: 800;
    color: white;
}
.stat-label {
    color: #64748b;
    font-size: 0.85rem;
    margin-top: 4px;
}

/* ── Task Cards ── */
.task-card {
    background: #12131a;
    border: 1px solid #1e2d3d;
    border-radius: 14px;
    padding: 16px 20px;
    margin-bottom: 12px;
    transition: all 0.2s ease;
    position: relative;
}
.task-card:hover {
    border-color: #6366f1;
    box-shadow: 0 0 20px rgba(99,102,241,0.1);
    transform: translateY(-1px);
}
.task-card-high   { border-left: 4px solid #ef4444; }
.task-card-medium { border-left: 4px solid #f59e0b; }
.task-card-low    { border-left: 4px solid #10b981; }
.task-card-done   { opacity: 0.5; border-left: 4px solid #334155; }

.task-title {
    font-weight: 600;
    font-size: 1rem;
    color: #f1f5f9;
    margin-bottom: 8px;
}
.task-title-done {
    text-decoration: line-through;
    color: #64748b;
}
.task-meta {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
}
.task-tag {
    background: #1e2d3d;
    color: #94a3b8;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 500;
}
.task-tag-high   { background: rgba(239,68,68,0.15);  color: #fca5a5; }
.task-tag-medium { background: rgba(245,158,11,0.15); color: #fcd34d; }
.task-tag-low    { background: rgba(16,185,129,0.15); color: #6ee7b7; }
.task-tag-done   { background: rgba(99,102,241,0.15); color: #a5b4fc; }
.task-id {
    background: #1e2d3d;
    color: #475569;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-family: monospace;
}

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 15px;
}
.section-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #f1f5f9;
}
.section-count {
    background: #1e2d3d;
    color: #818cf8;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}

/* ── Chat Messages ── */
.chat-wrapper {
    background: #12131a;
    border: 1px solid #1e2d3d;
    border-radius: 20px;
    padding: 20px;
    margin-bottom: 20px;
    min-height: 100px;
}
.user-msg {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    margin: 8px 0;
    max-width: 75%;
    float: right;
    clear: both;
    font-size: 0.95rem;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3);
}
.agent-msg {
    background: #1e2130;
    color: #e2e8f0;
    border-radius: 18px 18px 18px 4px;
    padding: 14px 18px;
    margin: 8px 0;
    max-width: 75%;
    float: left;
    clear: both;
    font-size: 0.95rem;
    border: 1px solid #2d3561;
    border-left: 3px solid #6366f1;
}
.clearfix { clear: both; }

/* ── Chat Input ── */
.stChatInput > div {
    background: #ffffff !important;
    border: 2px solid #1e2d3d !important;
    border-radius: 16px !important;
}
.stChatInput textarea {
    color: #0f172a !important;
    background: #ffffff !important;
    caret-color: #6366f1 !important;
}
.stChatInput textarea::placeholder {
    color: #94a3b8 !important;
}
.stChatInput textarea:focus {
    color: #0f172a !important;
    background: #ffffff !important;
}
/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0d0e14 !important;
    border-right: 1px solid #1e2d3d;
}
section[data-testid="stSidebar"] * {
    color: #94a3b8 !important;
}

/* ── Empty State ── */
.empty-state {
    text-align: center;
    padding: 40px 20px;
    color: #334155;
}
.empty-state-icon { font-size: 3rem; margin-bottom: 10px; }
.empty-state-text { font-size: 1rem; color: #475569; }

/* ── Footer ── */
.footer {
    text-align: center;
    padding: 20px;
    color: #334155;
    font-size: 0.85rem;
    margin-top: 30px;
    border-top: 1px solid #1e2d3d;
}
.footer a { color: #6366f1; text-decoration: none; }

/* ── Divider ── */
.custom-divider {
    border: none;
    border-top: 1px solid #1e2d3d;
    margin: 25px 0;
}

/* ── Command Examples ── */
.cmd-box {
    background: #0d0e14;
    border: 1px solid #1e2d3d;
    border-radius: 10px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 0.85rem;
    color: #818cf8;
    font-family: monospace;
}
</style>
""", unsafe_allow_html=True)

# ── Model ─────────────────────────────────────────────────
MODEL = "z-ai/glm-4.5-air:free"

# ── Session State ─────────────────────────────────────────
if "tasks" not in st.session_state:
    st.session_state.tasks = []

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": (
            "You are a professional Work To-Do Agent. "
            "Manage tasks via natural language using these functions: "
            "add_task(title, due_date, priority), "
            "list_tasks(filter), "
            "complete_task(task_id), "
            "delete_task(task_id). "
            "Always call the right function. "
            "Keep responses short, friendly and professional. "
            "After every action confirm what was done."
        )}
    ]

if "client" not in st.session_state:
    st.session_state.client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

# ── Task Functions ────────────────────────────────────────
def add_task(title, due_date=None, priority="medium"):
    task = {
        "id": str(uuid.uuid4())[:6],
        "title": title,
        "due_date": due_date or "No due date",
        "priority": priority.lower(),
        "completed": False,
        "created_at": datetime.now().strftime("%b %d, %Y")
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
    return {"tasks": tasks, "count": len(tasks)}

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

def message_to_dict(msg):
    if isinstance(msg, dict):
        return msg
    d = {"role": msg.role, "content": msg.content or ""}
    if hasattr(msg, "tool_calls") and msg.tool_calls:
        d["tool_calls"] = [tc.model_dump() for tc in msg.tool_calls]
    return d

# ── Agent Function ────────────────────────────────────────
def call_agent(user_input):
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Add a new task to the list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title":    {"type": "string"},
                        "due_date": {"type": "string"},
                        "priority": {"type": "string",
                                     "enum": ["low", "medium", "high"]}
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List all tasks",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filter": {"type": "string",
                                   "enum": ["all", "completed", "incomplete"]}
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
                        "task_id": {"type": "string"}
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
                        "task_id": {"type": "string"}
                    },
                    "required": ["task_id"]
                }
            }
        }
    ]

    try:
        response = st.session_state.client.chat.completions.create(
            model=MODEL,
            messages=st.session_state.messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.2
        )
        msg = response.choices[0].message

        if msg.tool_calls:
            msg_dict = message_to_dict(msg)
            st.session_state.messages.append(msg_dict)

            for tc in msg.tool_calls:
                fn   = tc.function.name
                args = json.loads(tc.function.arguments)

                if fn == "add_task":
                    result = add_task(
                        args["title"],
                        args.get("due_date"),
                        args.get("priority", "medium")
                    )
                elif fn == "list_tasks":
                    result = list_tasks(args.get("filter", "all"))
                elif fn == "complete_task":
                    result = complete_task(args["task_id"])
                elif fn == "delete_task":
                    result = delete_task(args["task_id"])
                else:
                    result = {"error": f"Unknown: {fn}"}

                st.session_state.messages.append({
                    "role":        "tool",
                    "tool_call_id": tc.id,
                    "content":     json.dumps(result)
                })

            final = st.session_state.client.chat.completions.create(
                model=MODEL,
                messages=st.session_state.messages,
                temperature=0.2
            )
            final_dict = message_to_dict(final.choices[0].message)
            st.session_state.messages.append(final_dict)
            return final_dict["content"]

        else:
            msg_dict = message_to_dict(msg)
            st.session_state.messages.append(msg_dict)
            return msg_dict["content"]

    except Exception as e:
        return f"❌ Error: {str(e)}"

# ── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 Work To-Do Agent")
    st.markdown("---")

    # Stats
    total     = len(st.session_state.tasks)
    done      = len([t for t in st.session_state.tasks if t["completed"]])
    pending   = total - done
    high_prio = len([t for t in st.session_state.tasks
                     if not t["completed"] and t.get("priority") == "high"])

    st.markdown(f"**📊 Task Overview**")
    st.markdown(f"• Total Tasks: **{total}**")
    st.markdown(f"• Pending: **{pending}**")
    st.markdown(f"• Completed: **{done}**")
    st.markdown(f"• 🔴 High Priority: **{high_prio}**")

    st.markdown("---")
    st.markdown("**💬 Example Commands**")
    commands = [
        "Add task: Write report by Friday high priority",
        "Show my tasks",
        "Show incomplete tasks",
        "Complete task [id]",
        "Delete task [id]",
        "Show completed tasks",
    ]
    for cmd in commands:
        st.markdown(f"""
        <div class="cmd-box">💬 {cmd}</div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**🔐 Security**")
    st.success("✅ API Key Secured")
    st.caption("Key loaded from encrypted secrets. Never visible to users.")

    st.markdown("---")
    st.markdown("**👩‍💻 Built by**")
    st.markdown("**Marisha Dwivedi**")
    st.markdown("AI Engineer | Prompt Engineering")
    st.markdown("🔗 [GitHub](https://github.com/marisha119-AI)")

# ── HERO HEADER ───────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-title">✅ Work<span>To-Do</span> Agent</div>
    <div class="hero-subtitle">
        Your AI-powered task manager — just type naturally in plain English
    </div>
    <div class="hero-badge">🤖 Powered by GLM-4.5 Air · Tool-Calling Agent</div>
</div>
""", unsafe_allow_html=True)

# ── STATS BAR ─────────────────────────────────────────────
total   = len(st.session_state.tasks)
done    = len([t for t in st.session_state.tasks if t["completed"]])
pending = total - done
high    = len([t for t in st.session_state.tasks
               if not t["completed"] and t.get("priority") == "high"])

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{total}</div>
        <div class="stat-label">📋 Total Tasks</div>
    </div>""", unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number" style="color:#f59e0b;">{pending}</div>
        <div class="stat-label">⏳ Pending</div>
    </div>""", unsafe_allow_html=True)
with col3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number" style="color:#10b981;">{done}</div>
        <div class="stat-label">✅ Completed</div>
    </div>""", unsafe_allow_html=True)
with col4:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number" style="color:#ef4444;">{high}</div>
        <div class="stat-label">🔴 High Priority</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

# ── TASK DISPLAY ──────────────────────────────────────────
incomplete = [t for t in st.session_state.tasks if not t["completed"]]
completed  = [t for t in st.session_state.tasks if t["completed"]]

priority_order = {"high": 0, "medium": 1, "low": 2}
incomplete.sort(key=lambda t: priority_order.get(t.get("priority", "medium"), 1))

col_left, col_right = st.columns(2)

with col_left:
    st.markdown(f"""
    <div class="section-header">
        <div class="section-title">📝 To Do</div>
        <div class="section-count">{len(incomplete)}</div>
    </div>""", unsafe_allow_html=True)

    if incomplete:
        for task in incomplete:
            p = task.get("priority", "medium")
            st.markdown(f"""
            <div class="task-card task-card-{p}">
                <div class="task-title">{task['title']}</div>
                <div class="task-meta">
                    <span class="task-tag">📅 {task['due_date']}</span>
                    <span class="task-tag task-tag-{p}">
                        {'🔴' if p=='high' else '🟡' if p=='medium' else '🟢'}
                        {p.capitalize()}
                    </span>
                    <span class="task-id">#{task['id']}</span>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">🎯</div>
            <div class="empty-state-text">No pending tasks!<br>Add one below.</div>
        </div>""", unsafe_allow_html=True)

with col_right:
    st.markdown(f"""
    <div class="section-header">
        <div class="section-title">✅ Completed</div>
        <div class="section-count">{len(completed)}</div>
    </div>""", unsafe_allow_html=True)

    if completed:
        for task in completed:
            st.markdown(f"""
            <div class="task-card task-card-done">
                <div class="task-title task-title-done">{task['title']}</div>
                <div class="task-meta">
                    <span class="task-tag">📅 {task['due_date']}</span>
                    <span class="task-tag task-tag-done">✅ Done</span>
                    <span class="task-id">#{task['id']}</span>
                </div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">⏳</div>
            <div class="empty-state-text">No completed tasks yet.<br>Complete one to see it here!</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

# ── CHAT SECTION ──────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <div class="section-title">💬 Chat with Your Agent</div>
</div>""", unsafe_allow_html=True)

# Show chat history
chat_html = '<div class="chat-wrapper">'
has_chat = False
for msg in st.session_state.messages:
    if not isinstance(msg, dict):
        continue
    if msg["role"] == "user":
        chat_html += f'<div class="user-msg">👤 {msg["content"]}</div>'
        has_chat = True
    elif msg["role"] == "assistant" and not msg.get("tool_calls"):
        if msg.get("content"):
            chat_html += f'<div class="agent-msg">🤖 {msg["content"]}</div>'
            has_chat = True

if not has_chat:
    chat_html += """
    <div style="text-align:center; padding:30px; color:#334155;">
        <div style="font-size:2rem;">💬</div>
        <div style="margin-top:8px; color:#475569;">
            Start by typing a command below!<br>
            <span style="font-size:0.85rem; color:#334155;">
                Try: "Add task: Prepare Q3 report by Friday high priority"
            </span>
        </div>
    </div>"""

chat_html += '<div class="clearfix"></div></div>'
st.markdown(chat_html, unsafe_allow_html=True)

# ── Chat Input ────────────────────────────────────────────
if prompt := st.chat_input("💬 Type a command... e.g. 'Add task: Buy groceries by tomorrow high priority'"):
    with st.spinner("🤖 Agent is thinking..."):
        call_agent(prompt)
    st.rerun()

# ── Footer ────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Built by <a href="https://github.com/marisha119-AI">Marisha Dwivedi</a> |
    AI Engineer Portfolio |
    Streamlit + OpenRouter + GLM-4.5 Air |
    Prompt Engineering Project #1
</div>
""", unsafe_allow_html=True)
