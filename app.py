import streamlit as st
from groq import Groq
import numpy as np
import math
import matplotlib.pyplot as plt

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(page_title="Engineering AI Suite", layout="wide")

st.title("🚀 Engineering AI Suite")

# -----------------------------
# SIDEBAR MENU
# -----------------------------
tool = st.sidebar.selectbox("Select Tool", [
    "🤖 Engineering Chatbot",
    "🔧 Spring Designer"
])

# =============================
# 🤖 CHATBOT SECTION
# =============================
if tool == "🤖 Engineering Chatbot":

    client = Groq(api_key=st.secrets["api_key"])

    def get_initial_message():
        return [
            {"role": "system", "content": "You are an Engineering Assistant helping in all engineering fields."},
            {"role": "assistant", "content": "👋 How may I assist you in your engineering work today?"}
        ]

    def get_response(messages):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages
        )
        return response.choices[0].message.content

    def update_chat(messages, role, content):
        messages.append({"role": role, "content": content})
        return messages

    if "messages" not in st.session_state:
        st.session_state.messages = get_initial_message()

    if "generated" not in st.session_state:
        st.session_state.generated = []

    if "past" not in st.session_state:
        st.session_state.past = []

    # Chat display
    for i in range(len(st.session_state.generated)):
        st.chat_message("user").write(st.session_state.past[i])
        st.chat_message("assistant").write(st.session_state.generated[i])

    # Input
    prompt = st.chat_input("Ask engineering question...")

    if prompt:
        messages = st.session_state.messages

        messages = update_chat(messages, "user", prompt)
        response = get_response(messages)
        messages = update_chat(messages, "assistant", response)

        st.session_state.past.append(prompt)
        st.session_state.generated.append(response)

        st.rerun()

# =============================
# 🔧 SPRING DESIGNER SECTION
# =============================
else:

    st.title("🔧 Spring Design Software")

    unit_system = st.selectbox("Unit System", ["US (lb, in)", "SI (N, mm)"])

    if unit_system == "US (lb, in)":
        F_conv, L_conv, stress_conv = 1, 1, 1
        force_unit, length_unit, stress_unit = "lb", "in", "psi"
    else:
        F_conv, L_conv, stress_conv = 4.44822, 25.4, 0.006895
        force_unit, length_unit, stress_unit = "N", "mm", "MPa"

    mode = st.selectbox("Problem Type", [
        "Two Forces & Lengths",
        "Known k + Max Force"
    ])

    st.sidebar.header("📥 Inputs")

    if mode == "Two Forces & Lengths":
        F1 = st.sidebar.number_input(f"F1 ({force_unit})", value=5.25)
        L1 = st.sidebar.number_input(f"L1 ({length_unit})", value=2.25)
        F2 = st.sidebar.number_input(f"F2 ({force_unit})", value=7.75)
        L2 = st.sidebar.number_input(f"L2 ({length_unit})", value=2.75)

        F1 /= F_conv; F2 /= F_conv
        L1 /= L_conv; L2 /= L_conv

        k = (F2 - F1) / (L2 - L1)
        Fmax = max(F1, F2)
        Fi = min(F1, F2) * 0.7

    else:
        k = st.sidebar.number_input(f"k ({force_unit}/{length_unit})", value=5.0)
        Fmax = st.sidebar.number_input(f"Fmax ({force_unit})", value=10.0)

        k /= (F_conv / L_conv)
        Fmax /= F_conv
        Fi = 0.3 * Fmax

    OD_max = st.sidebar.number_input(f"Max OD ({length_unit})", value=0.75)
    OD_max /= L_conv

    material = st.sidebar.selectbox("Material", ["Music Wire", "Stainless Steel"])
    service = st.sidebar.selectbox("Service", ["Average", "Severe"])

    if material == "Music Wire":
        G, Sut = 11.5e6, 230000
    else:
        G, Sut = 10e6, 180000

    tau_allow = 0.30*Sut if service == "Severe" else 0.45*Sut

    if st.button("Run Design"):

        solution = None

        for d in np.linspace(0.02, 0.2, 100):
            D = OD_max - d
            if D <= 0:
                continue

            Na = (G * d**4) / (8 * D**3 * k)

            if Na < 3 or Na > 100:
                continue

            C = D / d
            Kw = (4*C - 1)/(4*C - 4) + 0.615/C
            tau = (8 * Fmax * D * Kw) / (math.pi * d**3)

            if tau < tau_allow:
                solution = (d, D, Na, tau)
                break

        if solution:
            d, D, Na, tau = solution

            st.success("✅ Safe Design Found")

            st.write(f"Wire Diameter: {d*L_conv:.3f} {length_unit}")
            st.write(f"Mean Diameter: {D*L_conv:.3f} {length_unit}")
            st.write(f"Active Coils: {Na:.2f}")
            st.write(f"Stress: {tau*stress_conv:.2f} {stress_unit}")

            x = np.linspace(0, 2, 100)
            F = np.array([Fi if xi < 0.1 else Fi + k*(xi-0.1) for xi in x])

            fig, ax = plt.subplots()
            ax.plot(x*L_conv, F*F_conv)
            st.pyplot(fig)

        else:
            st.error("❌ No safe design found")