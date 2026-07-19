# ρ-collapse run report

_Generated 2026-07-19T02:57:03Z_

## Headline: ρ, N_eff, and saturation check

| Domain | Condition | N | Items | Mean acc | ρ (95% CI) | N_eff / N | Saturated? |
|---|---|---|---|---|---|---|---|
| law | D1_same_model | 5 | 250 | 0.230 | 0.557 (0.486, 0.624) | 1.55 / 5 | no |
| law | D2_cross_family_chinese | 5 | 250 | 0.206 | 0.302 (0.250, 0.351) | 2.27 / 5 | no |
| law | D3_cross_culture | 5 | 250 | 0.259 | 0.427 (0.368, 0.486) | 1.85 / 5 | no |
| medicine | D1_same_model | 5 | 250 | 0.602 | 0.415 (0.333, 0.486) | 1.88 / 5 | no |
| medicine | D2_cross_family_chinese | 5 | 250 | 0.566 | 0.276 (0.216, 0.334) | 2.38 / 5 | no |
| medicine | D3_cross_culture | 5 | 250 | 0.630 | 0.320 (0.250, 0.380) | 2.19 / 5 | no |
| science | D1_same_model | 5 | 250 | 0.678 | 0.488 (0.417, 0.556) | 1.69 / 5 | no |
| science | D2_cross_family_chinese | 5 | 250 | 0.677 | 0.320 (0.251, 0.383) | 2.19 / 5 | no |
| science | D3_cross_culture | 5 | 250 | 0.697 | 0.279 (0.210, 0.349) | 2.36 / 5 | no |

## Per-cell breakdown

### law × D1_same_model

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.230  |  **ρ:** 0.557 (95% CI 0.486, 0.624)  |  **N_eff:** 1.55  |  **C:** 9.3

**Per-agent accuracy**

- `deepseek_v4#1` — 0.260
- `deepseek_v4#2` — 0.224
- `deepseek_v4#3` — 0.204
- `deepseek_v4#4` — 0.232
- `deepseek_v4#5` — 0.232

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 34 | 0.529 | 0.230 | 0.141 | -0.299 |
| 2 | 21 | 0.524 | 0.418 | 0.177 | -0.106 |
| 3 | 22 | 0.636 | 0.632 | 0.220 | -0.004 |
| 4 | 34 | 0.853 | 0.804 | 0.269 | -0.049 |
| 5 | 18 | 0.833 | 0.908 | 0.326 | 0.075 |

### law × D2_cross_family_chinese

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.206  |  **ρ:** 0.302 (95% CI 0.250, 0.351)  |  **N_eff:** 2.27  |  **C:** 9.3

**Per-agent accuracy**

- `bytedance_seed#1` — 0.372
- `deepseek_v4#1` — 0.212
- `glm_46#1` — 0.084
- `kimi_k2#1` — 0.056
- `qwen_3#1` — 0.304

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 24 | 0.375 | 0.206 | 0.148 | -0.169 |
| 2 | 53 | 0.585 | 0.349 | 0.195 | -0.236 |
| 3 | 45 | 0.800 | 0.526 | 0.252 | -0.274 |
| 4 | 15 | 0.867 | 0.697 | 0.319 | -0.170 |

### law × D3_cross_culture

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.259  |  **ρ:** 0.427 (95% CI 0.368, 0.486)  |  **N_eff:** 1.85  |  **C:** 9.3

**Per-agent accuracy**

- `claude_sonnet#1` — 0.352
- `deepseek_v4#1` — 0.248
- `gemini_pro#1` — 0.384
- `gpt5_mini#1` — 0.256
- `kimi_k2#1` — 0.056

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 14 | 0.357 | 0.259 | 0.155 | -0.098 |
| 2 | 35 | 0.514 | 0.495 | 0.211 | -0.019 |
| 3 | 40 | 0.750 | 0.733 | 0.281 | -0.017 |
| 4 | 45 | 0.844 | 0.885 | 0.364 | 0.040 |
| 5 | 3 | 1.000 | 0.956 | 0.455 | -0.044 |

### medicine × D1_same_model

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.602  |  **ρ:** 0.415 (95% CI 0.333, 0.486)  |  **N_eff:** 1.88  |  **C:** 9.0

**Per-agent accuracy**

- `deepseek_v4#1` — 0.600
- `deepseek_v4#2` — 0.592
- `deepseek_v4#3` — 0.632
- `deepseek_v4#4` — 0.612
- `deepseek_v4#5` — 0.576

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 26 | 0.500 | 0.602 | 0.242 | 0.102 |
| 2 | 30 | 0.733 | 0.948 | 0.449 | 0.215 |
| 3 | 52 | 0.846 | 0.996 | 0.676 | 0.149 |
| 4 | 62 | 0.887 | 1.000 | 0.842 | 0.113 |
| 5 | 73 | 0.918 | 1.000 | 0.931 | 0.082 |

### medicine × D2_cross_family_chinese

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.566  |  **ρ:** 0.276 (95% CI 0.216, 0.334)  |  **N_eff:** 2.38  |  **C:** 9.0

**Per-agent accuracy**

- `bytedance_seed#1` — 0.808
- `deepseek_v4#1` — 0.616
- `glm_46#1` — 0.532
- `kimi_k2#1` — 0.120
- `qwen_3#1` — 0.752

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 13 | 0.154 | 0.566 | 0.276 | 0.412 |
| 2 | 42 | 0.667 | 0.931 | 0.537 | 0.265 |
| 3 | 92 | 0.891 | 0.993 | 0.779 | 0.102 |
| 4 | 85 | 0.918 | 0.999 | 0.915 | 0.082 |
| 5 | 18 | 0.833 | 1.000 | 0.970 | 0.167 |

### medicine × D3_cross_culture

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.630  |  **ρ:** 0.320 (95% CI 0.250, 0.380)  |  **N_eff:** 2.19  |  **C:** 9.0

**Per-agent accuracy**

- `claude_sonnet#1` — 0.832
- `deepseek_v4#1` — 0.588
- `gemini_pro#1` — 0.812
- `gpt5_mini#1` — 0.792
- `kimi_k2#1` — 0.124

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 4 | 0.250 | 0.630 | 0.282 | 0.380 |
| 2 | 29 | 0.586 | 0.959 | 0.552 | 0.372 |
| 3 | 70 | 0.886 | 0.997 | 0.795 | 0.111 |
| 4 | 127 | 0.906 | 1.000 | 0.924 | 0.094 |
| 5 | 20 | 0.900 | 1.000 | 0.974 | 0.100 |

### science × D1_same_model

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.678  |  **ρ:** 0.488 (95% CI 0.417, 0.556)  |  **N_eff:** 1.69  |  **C:** 9.8

**Per-agent accuracy**

- `deepseek_v4#1` — 0.692
- `deepseek_v4#2` — 0.672
- `deepseek_v4#3` — 0.656
- `deepseek_v4#4` — 0.700
- `deepseek_v4#5` — 0.668

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 30 | 0.667 | 0.678 | 0.231 | 0.011 |
| 2 | 28 | 0.821 | 0.975 | 0.449 | 0.154 |
| 3 | 29 | 0.931 | 0.999 | 0.688 | 0.068 |
| 4 | 41 | 0.976 | 1.000 | 0.856 | 0.024 |
| 5 | 109 | 0.982 | 1.000 | 0.942 | 0.018 |

### science × D2_cross_family_chinese

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.677  |  **ρ:** 0.320 (95% CI 0.251, 0.383)  |  **N_eff:** 2.19  |  **C:** 9.8

**Per-agent accuracy**

- `bytedance_seed#1` — 0.896
- `deepseek_v4#1` — 0.688
- `glm_46#1` — 0.528
- `kimi_k2#1` — 0.444
- `qwen_3#1` — 0.828

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 20 | 0.450 | 0.677 | 0.287 | 0.227 |
| 2 | 32 | 0.781 | 0.975 | 0.593 | 0.194 |
| 3 | 48 | 0.938 | 0.999 | 0.841 | 0.061 |
| 4 | 93 | 0.957 | 1.000 | 0.950 | 0.043 |
| 5 | 57 | 1.000 | 1.000 | 0.986 | -0.000 |

### science × D3_cross_culture

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.697  |  **ρ:** 0.279 (95% CI 0.210, 0.349)  |  **N_eff:** 2.36  |  **C:** 9.8

**Per-agent accuracy**

- `claude_sonnet#1` — 0.828
- `deepseek_v4#1` — 0.736
- `gemini_pro#1` — 0.792
- `gpt5_mini#1` — 0.704
- `kimi_k2#1` — 0.424

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 16 | 0.312 | 0.697 | 0.317 | 0.384 |
| 2 | 22 | 0.682 | 0.979 | 0.661 | 0.298 |
| 3 | 49 | 0.939 | 0.999 | 0.891 | 0.060 |
| 4 | 104 | 0.933 | 1.000 | 0.971 | 0.067 |
| 5 | 59 | 1.000 | 1.000 | 0.993 | -0.000 |
