import streamlit as st
import matplotlib.pyplot as plt
import time
from enviromentTMT import TMTTaskProvider
from agent import CognitiveAgent

st.set_page_config(page_title="TMT Spatial Simulator", layout="wide")
st.title("TMT Cognitive Architecture Engine: Spatial Simulation")
st.divider()

# --- Sidebar Inputs ---
st.sidebar.header("Cognitive Parameters")
visual_capacity = st.sidebar.slider("Visual Search Capacity (Items per fixation)", 1, 7, 3)
visual_skip = st.sidebar.slider("Visual Skip Probability", 0.0, 0.5, 0.1, 0.05)
search_speed = st.sidebar.slider("Visual Search Base Time (ms)", 50, 800, 300, 50)
shift_speed = st.sidebar.slider("Set Shifting Time (ms)", 100, 1500, 500, 50)
memory_speed = st.sidebar.slider("Working Memory Time (ms)", 50, 500, 150, 25)
click_overhead = st.sidebar.slider("Click Overhead (ms)", 20, 500, 120, 10)
mouse_speed = st.sidebar.slider("Mouse Velocity (pixels/ms)", 0.05, 1.0, 0.4, 0.05)

st.sidebar.header("Simulation Speed")
sim_delay = st.sidebar.slider("Frame delay (ms)", 0, 300, 60, 10)

col1, col2 = st.columns(2)
run_a = col1.button("Run TMT-A (1-25)", type="primary", use_container_width=True)
run_b = col2.button("Run TMT-B (1-13, A-L)", type="primary", use_container_width=True)

if run_a or run_b:
    task_type = "A" if run_a else "B"
    env = TMTTaskProvider(task_type=task_type)
    agent = CognitiveAgent(
        search_speed=search_speed,
        shift_speed=shift_speed,
        memory_speed=memory_speed,
        visual_capacity=visual_capacity,
        visual_skip=visual_skip,
        click_overhead=click_overhead,
        mouse_speed=mouse_speed,
    )
    
    st.markdown(f"### Live Execution: TMT-{task_type}")
    status_text = st.empty()
    metrics_text = st.empty()
    plot_spot = st.empty()
    
    total_time = 0
    correct_clicks = 0
    event_count = 0
    
    for frame in agent.run_simulation(env):
        total_time += frame['time_cost']
        event_count += 1
        if frame['step'] == 'Correct Click':
            correct_clicks += 1

        status_text.markdown(f"**Target:** {frame['current_target']} | **Step:** `{frame['step']}` | **Elapsed:** {total_time:.1f} ms")
        metrics_text.markdown(
            f"**Completed:** {frame['completed_index']} / {len(env.targets)}  |  "
            f"**Avg click time:** {total_time / max(correct_clicks, 1):.1f} ms  |  "
            f"**Frames:** {event_count}"
        )
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 100)
        ax.axis('off')
        
        ex, ey = frame['eye_pos']
        visual_field = plt.Circle((ex, ey), 15 + (visual_capacity * 2), color='yellow', alpha=0.3)
        ax.add_patch(visual_field)
        
        for idx, target in enumerate(env.targets):
            nx, ny = env.get_target_coords(target)
            is_completed = idx < frame['completed_index']
            color = 'lightgreen' if is_completed else 'white'
            edge = 'green' if is_completed else 'black'
            circle = plt.Circle((nx, ny), 3, facecolor=color, edgecolor=edge, linewidth=2, zorder=3)
            ax.add_patch(circle)
            ax.text(nx, ny, target, ha='center', va='center', fontweight='bold', zorder=4)

        path_x, path_y = [], []
        for i in range(frame['completed_index']):
            tx, ty = env.get_target_coords(env.targets[i])
            path_x.append(tx)
            path_y.append(ty)
        if path_x:
            path_x.append(frame['pen_pos'][0])
            path_y.append(frame['pen_pos'][1])
            ax.plot(path_x, path_y, color='blue', linewidth=2, zorder=2)
            
        px, py = frame['pen_pos']
        ax.plot(px, py, marker='o', markersize=8, color='red', zorder=5)

        plot_spot.pyplot(fig)
        plt.close(fig)
        
        time.sleep(sim_delay / 1000.0)

    st.success(f"Simulation Complete! Total Latency: {total_time:.1f} ms")
    st.balloons()