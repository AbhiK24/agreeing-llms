# ρ-collapse run report

_Generated 2026-07-19T06:40:08Z_

## Headline: ρ, N_eff, and saturation check

| Domain | Condition | N | Items | Mean acc | ρ (95% CI) | N_eff / N | Saturated? |
|---|---|---|---|---|---|---|---|
| law | D1_same_model | 5 | 94 | 0.764 | 0.755 (0.635, 0.860) | 1.24 / 5 | no |
| law | D2_cross_family_chinese | 5 | 80 | 0.693 | 0.488 (0.350, 0.600) | 1.69 / 5 | no |
| law | D3_cross_culture | 5 | 129 | 0.743 | 0.554 (0.448, 0.654) | 1.56 / 5 | no |
| medicine | D1_same_model | 5 | 194 | 0.882 | 0.733 (0.625, 0.825) | 1.27 / 5 | no |
| medicine | D2_cross_family_chinese | 5 | 140 | 0.861 | 0.693 (0.552, 0.799) | 1.33 / 5 | no |
| medicine | D3_cross_culture | 5 | 192 | 0.863 | 0.630 (0.509, 0.733) | 1.42 / 5 | no |
| science | D1_same_model | 5 | 149 | 0.974 | 0.660 (0.167, 0.921) | 1.37 / 5 | ⚠ yes |
| science | D2_cross_family_chinese | 5 | 139 | 0.937 | 0.613 (0.356, 0.797) | 1.45 / 5 | no |
| science | D3_cross_culture | 5 | 168 | 0.929 | 0.458 (0.261, 0.606) | 1.77 / 5 | no |

> **⚠ Saturation warning.** One or more cells has mean per-agent accuracy > 0.95. In these cells `ρ ≈ 0` may indicate 'not enough errors to correlate' rather than genuine agent independence. Rerun those cells on a harder subset before publishing.

## Per-cell breakdown

### law × D1_same_model

- **Items scored:** 94  |  **Agents:** 5  |  **Mean per-agent acc:** 0.764  |  **ρ:** 0.755 (95% CI 0.635, 0.860)  |  **N_eff:** 1.24  |  **C:** 9.1

**Per-agent accuracy**

- `deepseek_v4#1` — 0.745
- `deepseek_v4#2` — 0.755
- `deepseek_v4#3` — 0.798
- `deepseek_v4#4` — 0.766
- `deepseek_v4#5` — 0.755

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 44 | 0.432 | 0.764 | 0.219 | 0.332 |
| 2 | 38 | 0.395 | 0.988 | 0.387 | 0.593 |
| 3 | 42 | 0.524 | 1.000 | 0.586 | 0.476 |
| 4 | 37 | 0.730 | 1.000 | 0.761 | 0.270 |
| 5 | 72 | 0.861 | 1.000 | 0.877 | 0.139 |

### law × D2_cross_family_chinese

- **Items scored:** 80  |  **Agents:** 5  |  **Mean per-agent acc:** 0.693  |  **ρ:** 0.488 (95% CI 0.350, 0.600)  |  **N_eff:** 1.69  |  **C:** 9.2

**Per-agent accuracy**

- `bytedance_seed#1` — 0.787
- `deepseek_v4#1` — 0.688
- `glm_46#1` — 0.525
- `kimi_k2#1` — 0.725
- `qwen_3#1` — 0.738

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 10 | 0.300 | 0.693 | 0.250 | 0.393 |
| 2 | 67 | 0.478 | 0.976 | 0.470 | 0.498 |
| 3 | 77 | 0.649 | 0.999 | 0.702 | 0.349 |
| 4 | 61 | 0.787 | 1.000 | 0.863 | 0.213 |
| 5 | 35 | 0.914 | 1.000 | 0.944 | 0.086 |

### law × D3_cross_culture

- **Items scored:** 129  |  **Agents:** 5  |  **Mean per-agent acc:** 0.743  |  **ρ:** 0.554 (95% CI 0.448, 0.654)  |  **N_eff:** 1.56  |  **C:** 9.2

**Per-agent accuracy**

- `claude_sonnet#1` — 0.767
- `deepseek_v4#1` — 0.698
- `gemini_pro#1` — 0.775
- `gpt5_mini#1` — 0.713
- `kimi_k2#1` — 0.760

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 13 | 0.077 | 0.743 | 0.249 | 0.666 |
| 2 | 52 | 0.404 | 0.985 | 0.468 | 0.581 |
| 3 | 52 | 0.615 | 0.999 | 0.701 | 0.384 |
| 4 | 55 | 0.764 | 1.000 | 0.861 | 0.236 |
| 5 | 78 | 0.897 | 1.000 | 0.943 | 0.103 |

### medicine × D1_same_model

- **Items scored:** 194  |  **Agents:** 5  |  **Mean per-agent acc:** 0.882  |  **ρ:** 0.733 (95% CI 0.625, 0.825)  |  **N_eff:** 1.27  |  **C:** 8.9

**Per-agent accuracy**

- `deepseek_v4#1` — 0.892
- `deepseek_v4#2` — 0.881
- `deepseek_v4#3` — 0.887
- `deepseek_v4#4` — 0.876
- `deepseek_v4#5` — 0.876

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 15 | 0.200 | 0.882 | 0.262 | 0.682 |
| 2 | 17 | 0.765 | 0.998 | 0.501 | 0.233 |
| 3 | 16 | 0.625 | 1.000 | 0.740 | 0.375 |
| 4 | 32 | 0.719 | 1.000 | 0.890 | 0.281 |
| 5 | 168 | 0.929 | 1.000 | 0.958 | 0.071 |

### medicine × D2_cross_family_chinese

- **Items scored:** 140  |  **Agents:** 5  |  **Mean per-agent acc:** 0.861  |  **ρ:** 0.693 (95% CI 0.552, 0.799)  |  **N_eff:** 1.33  |  **C:** 8.9

**Per-agent accuracy**

- `bytedance_seed#1` — 0.864
- `deepseek_v4#1` — 0.850
- `glm_46#1` — 0.850
- `kimi_k2#1` — 0.886
- `qwen_3#1` — 0.857

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 5 | 0.400 | 0.861 | 0.261 | 0.461 |
| 2 | 19 | 0.368 | 0.997 | 0.498 | 0.628 |
| 3 | 36 | 0.806 | 1.000 | 0.737 | 0.194 |
| 4 | 75 | 0.907 | 1.000 | 0.887 | 0.093 |
| 5 | 115 | 0.913 | 1.000 | 0.957 | 0.087 |

### medicine × D3_cross_culture

- **Items scored:** 192  |  **Agents:** 5  |  **Mean per-agent acc:** 0.863  |  **ρ:** 0.630 (95% CI 0.509, 0.733)  |  **N_eff:** 1.42  |  **C:** 9.0

**Per-agent accuracy**

- `claude_sonnet#1` — 0.870
- `deepseek_v4#1` — 0.865
- `gemini_pro#1` — 0.870
- `gpt5_mini#1` — 0.870
- `kimi_k2#1` — 0.839

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 2 | 0.000 | 0.863 | 0.275 | 0.863 |
| 2 | 12 | 0.250 | 0.997 | 0.536 | 0.747 |
| 3 | 23 | 0.609 | 1.000 | 0.779 | 0.391 |
| 4 | 59 | 0.881 | 1.000 | 0.914 | 0.119 |
| 5 | 154 | 0.922 | 1.000 | 0.970 | 0.078 |

### science × D1_same_model

- **Items scored:** 149  |  **Agents:** 5  |  **Mean per-agent acc:** 0.974  |  **ρ:** 0.660 (95% CI 0.167, 0.921)  |  **N_eff:** 1.37  |  **C:** 9.8

**Per-agent accuracy**

- `deepseek_v4#1` — 0.966
- `deepseek_v4#2` — 0.973
- `deepseek_v4#3` — 0.980
- `deepseek_v4#4` — 0.980
- `deepseek_v4#5` — 0.973

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 30 | 0.700 | 0.974 | 0.356 | 0.274 |
| 2 | 27 | 0.667 | 1.000 | 0.733 | 0.333 |
| 3 | 18 | 0.833 | 1.000 | 0.932 | 0.167 |
| 4 | 23 | 0.957 | 1.000 | 0.986 | 0.043 |
| 5 | 144 | 0.986 | 1.000 | 0.997 | 0.014 |

### science × D2_cross_family_chinese

- **Items scored:** 139  |  **Agents:** 5  |  **Mean per-agent acc:** 0.937  |  **ρ:** 0.613 (95% CI 0.356, 0.797)  |  **N_eff:** 1.45  |  **C:** 9.8

**Per-agent accuracy**

- `bytedance_seed#1` — 0.950
- `deepseek_v4#1` — 0.935
- `glm_46#1` — 0.914
- `kimi_k2#1` — 0.935
- `qwen_3#1` — 0.950

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 11 | 0.636 | 0.937 | 0.314 | 0.300 |
| 2 | 24 | 0.583 | 0.999 | 0.654 | 0.416 |
| 3 | 31 | 0.871 | 1.000 | 0.886 | 0.129 |
| 4 | 62 | 0.952 | 1.000 | 0.970 | 0.048 |
| 5 | 122 | 0.992 | 1.000 | 0.993 | 0.008 |

### science × D3_cross_culture

- **Items scored:** 168  |  **Agents:** 5  |  **Mean per-agent acc:** 0.929  |  **ρ:** 0.458 (95% CI 0.261, 0.606)  |  **N_eff:** 1.77  |  **C:** 9.8

**Per-agent accuracy**

- `claude_sonnet#1` — 0.923
- `deepseek_v4#1` — 0.958
- `gemini_pro#1` — 0.881
- `gpt5_mini#1` — 0.940
- `kimi_k2#1` — 0.940

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 10 | 0.100 | 0.929 | 0.374 | 0.829 |
| 2 | 16 | 0.688 | 0.999 | 0.763 | 0.312 |
| 3 | 30 | 0.767 | 1.000 | 0.945 | 0.233 |
| 4 | 57 | 0.912 | 1.000 | 0.989 | 0.088 |
| 5 | 137 | 0.985 | 1.000 | 0.998 | 0.015 |
