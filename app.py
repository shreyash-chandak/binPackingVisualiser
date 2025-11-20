import streamlit as st
import os
import json
import random
import subprocess
from manim import *

# Set up the page layout
st.set_page_config(page_title="Bin Packing Engine", layout="wide")

st.title("Bin Packing Visualization Engine")
st.markdown("Click to watch a bunch of items go into bins")

# --- SIDEBAR: INPUTS ---
with st.sidebar:
    st.header("Configuration")
    
    algo_choice = st.selectbox(
        "Select Algorithm",
        ("First-Fit (FF)", "Best-Fit (BF)", "First-Fit Decreasing (FFD)", "Best-Fit Decreasing (BFD)")
    )
    
    # Map selection to short code
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

# --- MAIN RENDER LOGIC ---
if st.button("Render Animation", type="primary"):
    with st.spinner("The video is being generated... (This may take a while)"):
        
        # 1. Prepare Configuration
        config = {
            "num_items": num_items,
            "algorithm": algo,
            "item_sizes": items
        }
        
        # Pass config via Environment Variable
        os.environ["BINPACK_DATA"] = json.dumps(config)
        
        # 2. Construct Command
        # CRITICAL FIX: Removed '-p' (Preview). Used '-ql' (Quality Low).
        # Added '--format=mp4' to ensure compatibility.
        cmd = [
            "manim", 
            "-ql", 
            "--media_dir", "./media", 
            "packing_logic.py", 
            "BinPackingScene"
        ]
        
        # 3. Run with Error Capturing
        try:
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                check=False
            )
            
            # 4. Check Results
            video_path = "./media/videos/packing_logic/480p15/BinPackingScene.mp4"
            
            if result.returncode == 0 and os.path.exists(video_path):
                st.success("Render Complete.")
                st.video(video_path)
                
                # Optional: Show logs for curiosity
                with st.expander("View Render Logs"):
                    st.code(result.stderr)
            else:
                st.error("Render Failed.")
                st.subheader("Error Logs (Show this to the Developer):")
                st.text("Standard Output:")
                st.code(result.stdout)
                st.text("Standard Error:")
                st.code(result.stderr)
                
        except Exception as e:
            st.error(f"System Error: {e}")