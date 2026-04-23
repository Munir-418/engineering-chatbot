import streamlit as st
from groq import Groq
import os
from dotenv import load_dotenv, find_dotenv

# load env
load_dotenv(find_dotenv())

# client
client = Groq(api_key=os.getenv("api_key"))

st.title("🤖 EngineerGPT")
st.subheader("Your Smart Engineering Assistant")

# -----------------------------
# INITIAL MESSAGE
# -----------------------------
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


# -----------------------------
# RESPONSE
# -----------------------------
def get_response(messages):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

# -----------------------------
# SESSION
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = get_initial_message()

# -----------------------------
# DISPLAY CHAT
# -----------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    elif msg["role"] == "assistant":
        st.chat_message("assistant").write(msg["content"])

# -----------------------------
# INPUT
# -----------------------------
prompt = st.chat_input("👋 How may I assist you today?")

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = get_response(st.session_state.messages)

    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})