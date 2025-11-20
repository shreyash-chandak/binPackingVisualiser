from manim import *
import random
import sys
import os
import json

# ==========================================
#   THE GRAND GEOMETRICIAN'S CONFIG
# ==========================================
USER_CONFIG = {
    "num_items": 10,
    "algorithm": "FF", 
    "item_sizes": []   
}

# (Input collection removed for Web Safety - Logic only)

class BinPackingScene(MovingCameraScene):
    def construct(self):
        # 1. INGESTION
        env_data = os.environ.get("BINPACK_DATA")
        if env_data:
            data = json.loads(env_data)
            items = data["item_sizes"]
            algo = data["algorithm"]
        else:
            items = [0.5, 0.4, 0.6, 0.2, 0.8, 0.3]
            algo = "FF"

        # 2. SCENE CONFIGURATION
        self.camera.frame.save_state()
        
        # --- GEOMETRY CONSTANTS (SCALED 0.75) ---
        SCALE_FACTOR = 0.75
        
        BIN_WIDTH = 1.4 * SCALE_FACTOR
        BIN_HEIGHT = 4.0 * SCALE_FACTOR
        BIN_CAPACITY = 1.0
        BIN_SPACING = 1.6 * SCALE_FACTOR
        
        # Anchors
        START_X = -5.0                       
        BIN_FLOOR = -3.4                     
        QUEUE_START_X = -6.0
        QUEUE_Y = 2.0                        
        
        # Header
        title = Text(f"Algorithm: {algo}", font_size=40, color=TEAL).to_edge(UP, buff=0.5)
        self.add(title)

        # 3. ITEM GENERATION
        item_mobjects = []
        for i, size in enumerate(items):
            color = interpolate_color(BLUE, RED, size)
            h = size * BIN_HEIGHT
            rect = Rectangle(width=BIN_WIDTH * 0.8, height=h, fill_color=color, fill_opacity=0.8, stroke_color=WHITE, stroke_width=1.5)
            label = Text(f"{size:.2f}", font_size=12).move_to(rect)
            group = VGroup(rect, label)
            group.size_val = size 
            item_mobjects.append(group)

        # Layout
        for i, item in enumerate(item_mobjects):
            if i == 0:
                item.move_to([QUEUE_START_X, QUEUE_Y, 0])
            else:
                item.next_to(item_mobjects[i-1], RIGHT, buff=0.15 * SCALE_FACTOR, aligned_edge=UP)

        self.play(
            LaggedStart(*[FadeIn(i, shift=DOWN) for i in item_mobjects], lag_ratio=0.05),
            run_time=1.2 
        )

        # 4. SORTING
        if algo in ["FFD", "BFD"]:
            self.play(title.animate.set_color(YELLOW))
            sort_text = Text("Sorting...", font_size=24).next_to(title, DOWN)
            self.play(Write(sort_text), run_time=0.6)
            
            item_mobjects.sort(key=lambda x: x.size_val, reverse=True)
            
            target_positions = []
            x_cursor = QUEUE_START_X
            for item in item_mobjects:
                pos = [x_cursor, QUEUE_Y, 0]
                target_positions.append(pos)
                x_cursor += (BIN_WIDTH * 0.8) + (0.15 * SCALE_FACTOR)

            self.play(
                *[item.animate.move_to(pos).align_to(pos, UP) for item, pos in zip(item_mobjects, target_positions)],
                run_time=1.8,
                rate_func=smooth
            )
            self.play(FadeOut(sort_text))

        # 5. BIN PACKING ENGINE
        bins_visual = [] 
        bin_fill_levels = [] 

        def create_new_bin():
            idx = len(bins_visual)
            b_rect = Rectangle(width=BIN_WIDTH, height=BIN_HEIGHT, color=WHITE, stroke_width=2)
            x_pos = START_X + idx * BIN_SPACING
            b_rect.move_to([x_pos, BIN_FLOOR + BIN_HEIGHT/2, 0])
            
            label = Text(f"B{idx+1}", font_size=16).next_to(b_rect, DOWN)
            b_group = VGroup(b_rect, label)
            
            self.play(FadeIn(b_group, shift=UP), run_time=0.6)
            
            bins_visual.append(b_group)
            bin_fill_levels.append(0.0)
            
            bin_right = b_rect.get_right()[0]
            cam_right = self.camera.frame.get_right()[0]
            if bin_right > cam_right - 1.5:
                self.play(self.camera.frame.animate.shift(RIGHT * 3), run_time=1.2)
            
            return idx

        # --- MAIN LOOP ---
        for item_obj in item_mobjects:
            size = item_obj.size_val
            
            # Highlight Active
            self.play(item_obj.animate.set_stroke(YELLOW, width=3), run_time=0.3)
            
            placed_idx = -1
            
            # ALGORITHM SEARCH
            if algo in ["FF", "FFD"]:
                for b_idx in range(len(bins_visual)):
                    b_group = bins_visual[b_idx]
                    bin_rect = b_group[0]
                    
                    target_x = bin_rect.get_center()[0]
                    hover_y = BIN_FLOOR + BIN_HEIGHT + 0.5
                    
                    # Slower Move to Inspection
                    self.play(item_obj.animate.move_to([target_x, hover_y, 0]), run_time=0.6)
                    
                    if bin_fill_levels[b_idx] + size <= BIN_CAPACITY + 0.0001:
                        self.play(bin_rect.animate.set_stroke(GREEN, width=6), run_time=0.15)
                        self.wait(0.15)
                        self.play(bin_rect.animate.set_stroke(WHITE, width=2), run_time=0.15)
                        placed_idx = b_idx
                        break 
                    else:
                        self.play(bin_rect.animate.set_stroke(RED, width=6), run_time=0.15)
                        self.wait(0.15)
                        self.play(bin_rect.animate.set_stroke(WHITE, width=2), run_time=0.15)
                
            elif algo in ["BF", "BFD"]:
                best_idx = -1
                min_residual = 1000.0
                
                for b_idx in range(len(bins_visual)):
                    b_group = bins_visual[b_idx]
                    bin_rect = b_group[0]
                    
                    target_x = bin_rect.get_center()[0]
                    hover_y = BIN_FLOOR + BIN_HEIGHT + 0.5
                    
                    # Slower Move
                    self.play(item_obj.animate.move_to([target_x, hover_y, 0]), run_time=0.4)
                    
                    residual = BIN_CAPACITY - bin_fill_levels[b_idx] - size
                    
                    if residual >= -0.0001:
                        self.play(bin_rect.animate.set_stroke(GREEN, width=6), run_time=0.15)
                        self.play(bin_rect.animate.set_stroke(WHITE, width=2), run_time=0.15)
                        if residual < min_residual:
                            min_residual = residual
                            best_idx = b_idx
                            self.play(Indicate(bin_rect, color=GOLD), run_time=0.3)
                    else:
                        self.play(bin_rect.animate.set_stroke(RED, width=6), run_time=0.15)
                        self.play(bin_rect.animate.set_stroke(WHITE, width=2), run_time=0.15)

                placed_idx = best_idx

            # DROP EXECUTION
            if placed_idx != -1:
                b_idx = placed_idx
                bin_rect = bins_visual[b_idx][0]
                
                current_fill_h = bin_fill_levels[b_idx] * BIN_HEIGHT
                drop_y = BIN_FLOOR + current_fill_h + (item_obj.height/2)
                drop_x = bin_rect.get_center()[0]
                
                # Slower Drop
                self.play(
                    item_obj.animate.move_to([drop_x, drop_y, 0]).set_stroke(WHITE, 1.5),
                    run_time=0.8,
                    rate_func=smooth
                )
                bin_fill_levels[b_idx] += size
                
            else:
                new_b_idx = create_new_bin()
                bin_rect = bins_visual[new_b_idx][0]
                
                target_x = bin_rect.get_center()[0]
                hover_y = BIN_FLOOR + BIN_HEIGHT + 0.5
                self.play(item_obj.animate.move_to([target_x, hover_y, 0]), run_time=0.8)
                
                drop_y = BIN_FLOOR + (item_obj.height/2)
                
                self.play(
                    item_obj.animate.move_to([target_x, drop_y, 0]).set_stroke(WHITE, 1.5),
                    run_time=0.8,
                    rate_func=smooth
                )
                bin_fill_levels[new_b_idx] += size

        self.wait(1)
        final_text = Text(f"Total Bins Used: {len(bins_visual)}", font_size=48, color=WHITE)
        center_cam = self.camera.frame.get_center()
        final_text.move_to(center_cam)
        bg = Rectangle(width=100, height=100, color=BLACK, fill_opacity=0.8).move_to(center_cam)
        self.play(FadeIn(bg), Write(final_text))
        self.wait(2)