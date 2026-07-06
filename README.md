# Trail Making Test (TMT) Cognitive Architecture Engine

An *in silico* experimental platform designed to simulate and evaluate cognitive processing latency, executive control, and motor execution during the Trail Making Test (Parts A and B). This application models a heuristic-driven virtual agent interacting with a spatial task provider to test cognitive modeling hypotheses.

## Features

- **Spatial Board Generation:** Dynamically maps 25 random nodes across an X/Y grid, matching standard clinical protocols (1-25 for Part A; 1-13 & A-L for Part B).
- **Heuristic Cognitive Agent:** Mimics human step-by-step processing without Reinforcement Learning (RL), following rigid cognitive flowchart sequences.
- **Configurable Latencies:** Real-time parameter sliders to alter processing speeds for visual search, set shifting, motor execution, planning, and memory updates.
- **Live Visual Search Simulation:** Includes a customizable **Visual Search Capacity** parameter representing human foveal/visual working memory limitations.
- **Real-Time Animation:** Features a dynamic live canvas displaying the agent's visual search field (gaze focus), manual trajectory (pen location), and path tracking.

## File Structure

```text
tmt_simulation_project/
│
├── app.py                   # Main Streamlit dashboard and UI rendering logic
├── agent.py                 # The CognitiveAgent execution architecture
├── environment.py           # The TMTTaskProvider and spatial environment data
└── requirements.txt         # Required Python packages
