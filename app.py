import streamlit as st
import os
import json
import random
from manim import *

# Set up the page layout
st.set_page_config(page_title="Bin Packing Engine", layout="wide")

st.title("📦 Bin Packing Visualization Engine")
st.markdown("Click to watch a bunch of items go into bins")

# --- SIDEBAR: INPUTS ---
with st.sidebar:
    st.header("Configuration")
    
    algo_choice = st.selectbox(
        "Select Algorithm",
        ("First-Fit (FF)", "Best-Fit (BF)", "First-Fit Decreasing (FFD)", "Best-Fit Decreasing (BFD)")
    )
    
    # Extract short code
    algo_map = {
        "First-Fit (FF)": "FF",
        "Best-Fit (BF)": "BF",
        "First-Fit Decreasing (FFD)": "FFD",
        "Best-Fit Decreasing (BFD)": "BFD"
    }
    algo = algo_map[algo_choice]
    
    num_items = st.slider("Number of Items", 5, 20, 10)
    
    data_mode = st.radio("Data Source", ("Random", "Manual"))
    
    items = []
    if data_mode == "Random":
        if st.button("Regenerate Random Data"):
            st.session_state.random_seed = random.randint(0, 1000)
        
        # Use session state to keep random data stable across re-renders
        seed = st.session_state.get("random_seed", 42)
        random.seed(seed)
        items = [round(random.uniform(0.15, 0.7), 2) for _ in range(num_items)]
        st.write(f"Generated: {items}")
        
    else:
        st.subheader("Manual Input")
        cols = st.columns(3)
        for i in range(num_items):
            with cols[i % 3]:
                val = st.number_input(f"Item {i+1}", 0.1, 1.0, 0.5, key=f"item_{i}")
                items.append(val)

# --- THE MANIM LOGIC (Wrapped in a function) ---
def render_scene(config):
    # Save config to env for the script to pick up if we were running subprocess
    # But here we can just modify the class directly or pass params if we restructure.
    # For simplicity, we will write the config to a JSON file that the Scene reads,
    # or use the Environment Variable trick we already perfected.
    
    os.environ["BINPACK_DATA"] = json.dumps(config)
    
    # Define output file
    # Manim outputs to media/videos/...
    # We use a system call to run manim to ensure clean state
    cmd = "manim -pql -v WARNING --media_dir ./media packing_logic.py BinPackingScene"
    os.system(cmd)
    
    # Locate the file
    # Default path: media/videos/packing_logic/480p15/BinPackingScene.mp4
    # (Depends on quality settings)
    return "./media/videos/packing_logic/480p15/BinPackingScene.mp4"

# --- MAIN DISPLAY ---
if st.button("Render Animation", type="primary"):
    with st.spinner("The Animation is being created... (This may take 30s)"):
        
        # prepare config
        config = {
            "num_items": num_items,
            "algorithm": algo,
            "item_sizes": items
        }
        
        # We need the Manim Logic in a separate file for the os.system call to work cleanly
        # Let's assume you saved your previous 'packing.py' code as 'packing_logic.py'
        # AND removed the "if __name__ == main" block from it so it doesn't run on import.
        
        # actually, just writing the env var and running the command:
        os.environ["BINPACK_DATA"] = json.dumps(config)
        
        # Run Manim
        # We use your existing logic file. 
        # Make sure 'packing.py' is in the same folder and renamed to 'packing_logic.py'
        exit_code = os.system("manim -pql -v WARNING --media_dir ./media packing_logic.py BinPackingScene")
        
        video_path = "./media/videos/packing_logic/480p15/BinPackingScene.mp4"
        
        if exit_code == 0 and os.path.exists(video_path):
            st.success("Render Complete.")
            st.video(video_path)
        else:
            st.error("Render Failed. Check logs.")