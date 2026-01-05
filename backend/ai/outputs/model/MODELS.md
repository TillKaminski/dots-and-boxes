# AI Model Documentation

This section documents the versions of the Dots and Boxes AI models.

---
---

## Feed-Forward Neural Network (FFN)

### Input/Output
* **Input**: `(1, 56)` Vector representing 40 edges (20 horizontal, 20 vertical) and 16 boxes.
* **Output**: `(1, 40)` Vector providing a probability distribution over all possible moves.

### Model Paramters

| Parameter | Value |
| :--- | :--- |
| **Input Size** | 56 |
| **Output Size** | 40 |
| **Hidden Layers** | `[128, 128, 64]` |
| **Activation Function** | `ReLU` (Hidden) / `Softmax` (Output) |
| **Optimizer** | `Adam` 
| **Loss Function** | `CrossEntropyLoss`

---

### Versions

---

> ---
>
> #### Version 1: "Basic Rules"
>
> **Filename:** `v1_rule_based_mix.pt`
>
> ---

---

#### Training-Data
**Total:** 10,000 Games
- **20%** Random vs. Random
- **20%** Rule vs. Random
- **60%** Rule vs. Rule

#### Training Progress
![Training Progess](..\img_training\v1_rule_based_mix.png)
*Figure 1: Loss and Accuracy over 100 epochs.*

> **Performance**:
>   - Wins Random, draws/loses against Rule-Bot.
>   - Draws (8:8) in Self-Play (deterministic).


#### Evaluation Benchmark (vs. Rule-Bot):


| RESULTS for Rule vs FFN | 1.000 Games |
| :--- | :--- |
| Wins (Rule) | 413 (41.3%) |
| Wins (FFN) | 429 (42.9%) |
| Draws | 158 |
| Avg Score (Rule) | 6.38 |
| Avg Score (FFN) | 6.58 |

---
---
