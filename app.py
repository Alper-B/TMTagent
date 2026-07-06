import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
from TMTagent.enviromentTMT import TMTTaskProvider
from TMTagent.agent import CognitiveAgent

st.set_page_config(page_title="TMT Spatial Simulator", layout="wide")
st.title("TMT Cognitive Architecture Engine: Spatial Simulation")
st.divider()

# --- Sidebar Inputs ---
st.sidebar.header("Cognitive Parameters")
visual_capacity = st.sidebar.slider("Visual Search Capacity (Items per fixation)", 1, 7, 3)
search_speed = st.sidebar.slider("Visual Search Base Time (ms)", 50, 800, 300, 50)
shift_speed = st.sidebar.slider("Set Shifting Time (ms)", 100, 1500, 500, 50)
motor_speed = st.sidebar.slider("Motor Execution Time (ms)", 100, 1000, 250, 50)
memory_speed = st.sidebar.slider("Working Memory Time (ms)", 50, 500, 150, 25)
planning_speed = st.sidebar.slider("Visuomotor Planning (ms)", 50, 500, 200, 25)

col1, col2 = st.columns(2)
run_a = col1.button("Run TMT-A (1-25)", type="primary", use_container_width=True)
run_b = col2.button("Run TMT-B (1-13, A-L)", type="primary", use_container_width=True)

if run_a or run_b:
    task_type = "A" if run_a else "B"
    env = TMTTaskProvider(task_type=task_type)
    agent = CognitiveAgent(search_speed, shift_speed, motor_speed, memory_speed, planning_speed, visual_capacity)
    
    # Layout for Animation
    st.markdown(f"### Live Execution: TMT-{task_type}")
    status_text = st.empty()
    plot_spot = st.empty()
    
    total_time = 0
    
    # Simulation Loop
    for frame in agent.run_simulation(env):
        total_time += frame['time_cost']
        status_text.markdown(f"**Target:** {frame['current_target']} | **Active Step:** `{frame['step']}` | **Clock:** {total_time} ms")
        
        # --- Matplotlib Rendering ---
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis('off')
        
        # Draw Visual Field (Eye)
        ex, ey = frame['eye_pos']
        visual_field = plt.Circle((ex, ey), 15 + (visual_capacity * 2), color='yellow', alpha=0.3)
        ax.add_patch(visual_field)
        
        # Draw Nodes
        for idx, target in enumerate(env.targets):
            nx, ny = env.get_target_coords(target)
            is_completed = idx < frame['completed_index']
            color = 'lightgreen' if is_completed else 'white'
            edge = 'green' if is_completed else 'black'
            
            circle = plt.Circle((nx, ny), 3, facecolor=color, edgecolor=edge, linewidth=2, zorder=3)
            ax.add_patch(circle)
            ax.text(nx, ny, target, ha='center', va='center', fontweight='bold', zorder=4)

        # Draw Completed Path
        path_x, path_y = [], []
        for i in range(frame['completed_index']):
            tx, ty = env.get_target_coords(env.targets[i])
            path_x.append(tx)
            path_y.append(ty)
        if path_x: # Add current pen pos to path
            path_x.append(frame['pen_pos'][0])
            path_y.append(frame['pen_pos'][1])
            ax.plot(path_x, path_y, color='blue', linewidth=2, zorder=2)
            
        # Draw Pen Position
        px, py = frame['pen_pos']
        ax.plot(px, py, marker='o', markersize=8, color='red', zorder=5)

        plot_spot.pyplot(fig)
        plt.close(fig)
        
        # Artificial delay so the human eye can watch the animation
        time.sleep(0.05)

    st.success(f"Simulation Complete! Total Latency: {total_time} ms")