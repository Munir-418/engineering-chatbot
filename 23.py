import streamlit as st
from streamlit_chat import message
from groq import Groq
import os
from dotenv import load_dotenv, find_dotenv

# load .env file
load_dotenv(find_dotenv())

# ✅ FIX 1: import os BEFORE using it
# (already imported above)

# Groq client
client = Groq(api_key=os.getenv("api_key"))

st.title("🤖 EngineerGPT")
st.subheader("Your Smart Engineering Assistant")

def get_initial_message():
    return [
        {"role": "system", "content": """
You are a Professional Engineering Assistant for ALL engineering fields, with strong focus on Mechanical Engineering.

You help students, engineers, and professionals in:

MAIN ENGINEERING AREAS:
- Mechanical Engineering
- Electrical Engineering (basic to intermediate)
- Civil Engineering (basic concepts)
- Industrial & Manufacturing Engineering
- Mechatronics basics
- Engineering Mathematics
- Physics related to engineering

MECHANICAL CORE TOPICS:
- Mechanics of Materials (stress, strain, bending, torsion)
- Strength of Materials
- Thermodynamics
- Fluid Mechanics
- Machine Design
- Manufacturing Processes
- Heat Transfer
- Engineering Mechanics (statics & dynamics)

HOW YOU SHOULD RESPOND:
1. Explain in simple, clear, student-friendly language.
2. Give step-by-step solutions for numerical problems.
3. Always show formulas when needed.
4. Use diagrams in text form if helpful.
5. Provide real-world engineering applications.
6. Keep answers exam-oriented when needed.
7. If question is theoretical → short and structured.
8. If question is numerical → step-by-step full solution.

IMPORTANT ENGINEERING FORMULAS:
- Stress = Force / Area
- Strain = ΔL / L
- Young’s Modulus = Stress / Strain
- PV = nRT (Ideal Gas Law)
- Q = mCpΔT (Heat Transfer)
- Bernoulli Equation: P + ½ρv² + ρgh = constant
- Continuity: A1V1 = A2V2
- Factor of Safety = Failure Stress / Working Stress
- Efficiency = Output/Input × 100%

BEHAVIOR:
- Act like a university engineering tutor
- Be practical, not overly theoretical
- Focus on understanding, not memorization
- Help in assignments, exams, and projects

If the question is unclear, ask a short clarification first.
"""},
        {"role": "user", "content": "assalam o alaikum"},
      {"role": "assistant", "content": "👋 Hello! I am EngineerGPT.\nHow can I help you today in engineering?"}
    ]

def get_response(messages):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

def update_chat(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages

# session state
if "messages" not in st.session_state:
    st.session_state.messages = get_initial_message()

if "generated" not in st.session_state:
    st.session_state.generated = []

if "past" not in st.session_state:
    st.session_state.past = []


# INPUT WITH AUTO CLEAR
with st.form(key="chat_form", clear_on_submit=True):
    prompt = st.text_input("👋 How may I assist you today?")
    submit = st.form_submit_button("Send")

if submit and prompt:
    messages = st.session_state.messages

    messages = update_chat(messages, "user", prompt)
    response = get_response(messages)
    messages = update_chat(messages, "assistant", response)

    st.session_state.past.append(prompt)
    st.session_state.generated.append(response)

# display chat
if st.session_state.generated:
    for i in range(len(st.session_state.generated) - 1, -1, -1):
        message(st.session_state.past[i], is_user=True, key=str(i) + "_u")
        message(st.session_state.generated[i], key=str(i))  