# binPackingVisualiser

Visualiser for basic bin packing approximation algorithms - First Fit, Best Fit, First Fit Decreasing and Best Fit Decreasing.

---

## Core Features

### Dynamic Rendering  
Generates a **unique video on-demand** based on user-selected parameters including algorithm, dataset, and quality preset.

### Dual Quality Pipeline  
Automatically adapts rendering depending on complexity:
- **HD Mode (720p):** Crisp, publication-quality visuals  
- **Turbo Mode (480p):** Ultra-fast rendering for large datasets  

### Real-Time Visual Feedback  
Animations include **Green/Red pulse indicators** to highlight algorithmic decision-making:
- *Fit successful*  
- *Fit rejected*  

### Headless Execution  
Uses Manim’s powerful vector engine in **serverless environments**, without requiring a display backend.

---

## Supported Algorithms

| Acronym | Algorithm               | Type    | Strategy                                              |
|:-------:|--------------------------|---------|--------------------------------------------------------|
| **FF**  | First-Fit                | Online  | Place item in the **first** bin with available space. |
| **BF**  | Best-Fit                 | Online  | Place item in the bin with the **tightest** fit.      |
| **FFD** | First-Fit Decreasing     | Offline | Sort items (descending), then apply First-Fit.        |
| **BFD** | Best-Fit Decreasing      | Offline | Sort items (descending), then apply Best-Fit.         |

---

##  Aesthetic Protocols

### Color Map  
A **thermal gradient** visually expresses item weight:  
**Blue → Cyan → Purple → Red**

### Movement Rules  
- Manhattan-style traversal  
- Smooth deceleration on final placement  
- Confident, deterministic paths for clarity

### Anchoring  
- Gravity-based floor alignment  
- Subtle easing to simulate “settling into place”

---
