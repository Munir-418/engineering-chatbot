import streamlit as st
import numpy as np
import math
import matplotlib.pyplot as plt

st.set_page_config(page_title="Advanced Spring Designer", layout="wide")

st.title("🔧 Universal Spring Design Software")

# -----------------------------
# UNIT SYSTEM
# -----------------------------
unit_system = st.selectbox("Select Unit System", ["US (lb, in)", "SI (N, mm)"])

if unit_system == "US (lb, in)":
    force_unit = "lb"
    length_unit = "in"
    stress_unit = "psi"
    F_conv = 1
    L_conv = 1
    stress_conv = 1
else:
    force_unit = "N"
    length_unit = "mm"
    stress_unit = "MPa"
    F_conv = 4.44822       # lb → N
    L_conv = 25.4          # in → mm
    stress_conv = 0.006895 # psi → MPa

# -----------------------------
# MODE
# -----------------------------
mode = st.selectbox("Problem Type", [
    "Two Forces & Lengths",
    "Known k + Max Force",
    "Known k + Max Force + Length"
])

st.sidebar.header("📥 Inputs")

# -----------------------------
# INPUTS
# -----------------------------
if mode == "Two Forces & Lengths":
    F1 = st.sidebar.number_input(f"F1 ({force_unit})", value=5.25)
    L1 = st.sidebar.number_input(f"L1 ({length_unit})", value=2.25)
    F2 = st.sidebar.number_input(f"F2 ({force_unit})", value=7.75)
    L2 = st.sidebar.number_input(f"L2 ({length_unit})", value=2.75)

    # Convert to US internally
    F1 /= F_conv
    F2 /= F_conv
    L1 /= L_conv
    L2 /= L_conv

    k = (F2 - F1) / (L2 - L1)
    Fmax = max(F1, F2)
    Fi = min(F1, F2) * 0.7

elif mode == "Known k + Max Force":
    k = st.sidebar.number_input(f"k ({force_unit}/{length_unit})", value=5.0)
    Fmax = st.sidebar.number_input(f"Fmax ({force_unit})", value=10.0)

    k /= (F_conv / L_conv)
    Fmax /= F_conv
    Fi = 0.3 * Fmax

else:
    k = st.sidebar.number_input(f"k ({force_unit}/{length_unit})", value=5.0)
    Fmax = st.sidebar.number_input(f"Fmax ({force_unit})", value=10.0)
    Lmax = st.sidebar.number_input(f"Length ({length_unit})", value=5.0)

    k /= (F_conv / L_conv)
    Fmax /= F_conv
    Fi = 0.3 * Fmax

OD_max = st.sidebar.number_input(f"Max OD ({length_unit})", value=0.75)
OD_max /= L_conv

material = st.sidebar.selectbox("Material", ["Music Wire", "Stainless Steel"])
service = st.sidebar.selectbox("Service", ["Average", "Severe"])

# -----------------------------
# MATERIAL DATA
# -----------------------------
if material == "Music Wire":
    G = 11.5e6
    Sut = 230000
else:
    G = 10e6
    Sut = 180000

tau_allow = 0.30*Sut if service == "Severe" else 0.45*Sut

# -----------------------------
# SOLVER
# -----------------------------
if st.button("🔍 Run Design"):

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

        # Convert back to selected units
        k_out = k * (F_conv / L_conv)
        d_out = d * L_conv
        D_out = D * L_conv
        tau_out = tau * stress_conv
        Fi_out = Fi * F_conv

        col1, col2 = st.columns(2)

        col1.metric("Spring Rate", f"{k_out:.2f} {force_unit}/{length_unit}")
        col1.metric("Initial Tension", f"{Fi_out:.2f} {force_unit}")
        col1.metric("Wire Diameter", f"{d_out:.3f} {length_unit}")

        col2.metric("Mean Diameter", f"{D_out:.3f} {length_unit}")
        col2.metric("Active Coils", f"{Na:.2f}")
        col2.metric("Stress", f"{tau_out:.2f} {stress_unit}")

        # Graph
        st.subheader("📈 Real Force vs Extension")

        x = np.linspace(0, 2, 100)
        F = np.array([Fi if xi < 0.1 else Fi + k*(xi-0.1) for xi in x])

        x_out = x * L_conv
        F_out = F * F_conv

        fig, ax = plt.subplots()
        ax.plot(x_out, F_out)
        ax.set_xlabel(f"Extension ({length_unit})")
        ax.set_ylabel(f"Force ({force_unit})")

        st.pyplot(fig)

    else:
        st.error("❌ No safe design found")