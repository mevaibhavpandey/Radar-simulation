# 🛰️ Radar-style Air Defense Missile Simulation

A real-time, interactive Streamlit application that simulates radar tracking and missile guidance using a simplified **proportional navigation** algorithm.  
Visualize missile and target trajectories on a radar-style display, add multiple threats, tune simulation parameters, and review neutralized targets.

---

## 🚀 Features

- **Interactive radar interface**
  - Real-time plotting of targets and missiles on a radar-style display.
  - Smooth animation with adjustable zoom and fast radar sweep.
- **Multiple threat handling**
  - Add multiple targets with user-defined positions and velocities.
  - Each missile autonomously intercepts its assigned target.
- **Proportional Navigation Guidance**
  - Simulates realistic missile pursuit using the navigation constant (N).
  - Dynamic update of missile heading and velocity.
- **Engagement reporting**
  - Automatically logs neutralized threats with hit time and coordinates.
  - Displays live and final results in a dynamic table.
- **Customizable parameters**
  - Adjustable radar sweep speed, missile velocity, detection radius, and zoom.
- **Lightweight & portable**
  - 100% Python, runs locally or on Streamlit Cloud.

---

## 🧩 How It Works

1. Add a threat with given position `(Pos X, Pos Y)` and velocity `(Vel X, Vel Y)`.
2. Each missile launches from origin `(0, 0)` toward its target.
3. The simulation updates every `dt` seconds:
   - Calculates **relative position** and **velocity**.
   - Computes **line-of-sight rate** and adjusts missile heading using **Proportional Navigation (PN)**.
   - If distance < `hit_distance`, the target is marked **neutralized**.
4. All trajectories and results are displayed in real time on the radar.

---

## ⚙️ Installation & Run

1. **Clone this repository**
   ```bash
   git clone https://github.com/<your-username>/radar-missile-simulation.git
   cd radar-missile-simulation
