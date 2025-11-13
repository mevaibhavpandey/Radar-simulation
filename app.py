import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import time

# Simulation settings
dt = 0.01  # Smaller dt for smoother simulation
total_time = 20
hit_distance = 5.0  # Distance threshold for collision
N = 3.0  # Navigation constant
angle_step = 50.0  # Increased for faster radar sweep rotation

# Session state initialization
if 'threats' not in st.session_state:
    st.session_state.threats = []

if 'neutralized' not in st.session_state:
    st.session_state.neutralized = pd.DataFrame(columns=['ID', 'Hit Position', 'Hit Time'])

# Dashboard title
st.title("Radar-style Air Defense Missile Simulation")

# User inputs for adding a new threat
st.header("Add New Threat")
col1, col2, col3, col4 = st.columns(4)
pos_x = col1.number_input('Target Pos X', value=0.0)
pos_y = col2.number_input('Target Pos Y', value=0.0)
vel_x = col3.number_input('Target Vel X', value=0.0)
vel_y = col4.number_input('Target Vel Y', value=0.0)

if st.button('Add Threat'):
    new_id = len(st.session_state.threats) + 1
    new_threat = {
        'id': new_id,
        'pos': np.array([pos_x, pos_y]),
        'vel': np.array([vel_x, vel_y]),
        'status': 'active',
        'missile_pos': np.array([0.0, 0.0]),
        'missile_vel': np.array([0.0, 80.0]),  # High missile speed
        'hit_time': None,
        'hit_pos': None
    }
    st.session_state.threats.append(new_threat)
    st.success(f"Threat ID {new_id} added!")

# Display current threats
st.header("Current Threats")
for threat in st.session_state.threats:
    st.write(f"ID {threat['id']}: Pos {threat['pos']}, Vel {threat['vel']}, Status {threat['status']}")

# Zoom slider
st.header("Simulation Controls")
zoom_factor = st.slider('Zoom Factor', 0.5, 2.0, 1.0)
st.write("Higher zoom factor shows a wider view (zoomed out).")

# Start simulation button
if st.button('Start Simulation'):
    if not st.session_state.threats:
        st.warning("No threats added!")
    else:
        # Initialize traces and hit flags
        missile_traces = {threat['id']: [] for threat in st.session_state.threats}
        target_traces = {threat['id']: [] for threat in st.session_state.threats}
        hit_detected = {threat['id']: False for threat in st.session_state.threats}

        # Placeholders for plot and table
        plot_placeholder = st.empty()
        table_placeholder = st.empty()

        for frame in range(int(total_time / dt)):
            for threat in st.session_state.threats:
                id = threat['id']
                # Append current positions to traces
                missile_traces[id].append(threat['missile_pos'].copy())
                target_traces[id].append(threat['pos'].copy())

                if hit_detected[id]:
                    continue

                # Relative position and velocity
                rel_pos = threat['pos'] - threat['missile_pos']
                rel_vel = threat['vel'] - threat['missile_vel']
                distance = np.linalg.norm(rel_pos)

                if distance < hit_distance:
                    hit_detected[id] = True
                    threat['status'] = 'neutralized'
                    threat['hit_time'] = frame * dt
                    threat['hit_pos'] = threat['missile_pos'].copy()  # Record missile pos at hit
                    threat['pos'] = np.array([np.nan, np.nan])  # Hide target
                    threat['missile_vel'] = np.array([0.0, 0.0])  # Stop missile
                    new_row = pd.DataFrame({
                        'ID': [id],
                        'Hit Position': [str(threat['hit_pos'])],
                        'Hit Time': [threat['hit_time']]
                    })
                    st.session_state.neutralized = pd.concat([st.session_state.neutralized, new_row], ignore_index=True)
                else:
                    # Line-of-sight rate
                    norm_rel_pos = np.linalg.norm(rel_pos)
                    los_rate = 0
                    if norm_rel_pos > 0:
                        los_rate = (rel_pos[0] * rel_vel[1] - rel_pos[1] * rel_vel[0]) / (norm_rel_pos ** 2)

                    # Acceleration for proportional navigation
                    accel = N * np.linalg.norm(threat['missile_vel']) * los_rate

                    # Update missile heading and velocity
                    missile_heading = np.arctan2(threat['missile_vel'][1], threat['missile_vel'][0])
                    if np.linalg.norm(threat['missile_vel']) > 0:
                        missile_heading += accel * dt / np.linalg.norm(threat['missile_vel'])
                    speed = np.linalg.norm(threat['missile_vel'])
                    threat['missile_vel'] = speed * np.array([np.cos(missile_heading), np.sin(missile_heading)])

                    # Update positions
                    threat['missile_pos'] += threat['missile_vel'] * dt
                    threat['pos'] += threat['vel'] * dt

            # Create the plot
            fig, ax = plt.subplots(figsize=(7, 7))
            ax.set_facecolor('black')
            ax.set_xlim(-600 * zoom_factor, 600 * zoom_factor)
            ax.set_ylim(-600 * zoom_factor, 600 * zoom_factor)
            ax.set_aspect('equal')
            ax.grid(False)

            # Radar grid (simplified for performance)
            for radius in range(200, int(601 * zoom_factor), int(200 * zoom_factor)):  # Fewer rings
                circle = plt.Circle((0, 0), radius, color='green', fill=False, linestyle='--', linewidth=0.7)
                ax.add_patch(circle)

            for angle in range(0, 360, 45):  # Fewer crosslines (every 45 degrees)
                x = np.cos(np.radians(angle)) * 600 * zoom_factor
                y = np.sin(np.radians(angle)) * 600 * zoom_factor
                ax.plot([0, x], [0, y], color='green', linewidth=0.4)

            # Plot missiles and targets
            for threat in st.session_state.threats:
                id = threat['id']
                # Missile
                ax.plot(threat['missile_pos'][0], threat['missile_pos'][1], 'ro', label="Missile" if id == st.session_state.threats[0]['id'] else "", markersize=6)
                ax.plot([p[0] for p in missile_traces[id]], [p[1] for p in missile_traces[id]], 'r-', linewidth=0.5)
                # Target (if not hidden)
                if not np.isnan(threat['pos'][0]):
                    ax.plot(threat['pos'][0], threat['pos'][1], 'bo', label="Target" if id == st.session_state.threats[0]['id'] else "", markersize=6)
                ax.plot([p[0] for p in target_traces[id]], [p[1] for p in target_traces[id]], 'b-', linewidth=0.5)

            # Radar Sweep (rotating line)
            sweep_angle = (frame * angle_step) % 360  # Fast rotation
            sweep_x = np.cos(np.radians(sweep_angle)) * 600 * zoom_factor
            sweep_y = np.sin(np.radians(sweep_angle)) * 600 * zoom_factor
            ax.plot([0, sweep_x], [0, sweep_y], color='lime', linewidth=1.5, alpha=0.8)

            # Legend and styling
            ax.legend(loc='upper right', facecolor='black', labelcolor='white')
            plt.title("Radar-style Missile Guidance Simulation", color='white')
            plt.xlabel("X", color='white')
            plt.ylabel("Y", color='white')
            ax.tick_params(colors='white')

            # Update placeholders
            plot_placeholder.pyplot(fig)
            table_placeholder.dataframe(st.session_state.neutralized)

            # Close figure to free memory
            plt.close(fig)

            # Frame delay - very low for smooth and fast animation
            time.sleep(0.001)

# Display neutralized table outside simulation for reference
st.header("Neutralized Threats Table")
st.dataframe(st.session_state.neutralized)
