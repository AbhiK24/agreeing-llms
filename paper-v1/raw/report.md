# ρ-collapse run report

_Generated 2026-07-19T03:17:08Z_

## Headline: ρ, N_eff, and saturation check

| Domain | Condition | N | Items | Mean acc | ρ (95% CI) | N_eff / N | Saturated? |
|---|---|---|---|---|---|---|---|
| law | D1_same_model | 5 | 250 | 0.258 | 0.638 (0.566, 0.700) | 1.41 / 5 | no |
| law | D2_cross_family_chinese | 5 | 250 | 0.266 | 0.498 (0.434, 0.557) | 1.67 / 5 | no |
| law | D3_cross_culture | 5 | 250 | 0.316 | 0.660 (0.600, 0.719) | 1.37 / 5 | no |
| medicine | D1_same_model | 5 | 250 | 0.738 | 0.659 (0.576, 0.728) | 1.37 / 5 | no |
| medicine | D2_cross_family_chinese | 5 | 250 | 0.690 | 0.413 (0.337, 0.479) | 1.89 / 5 | no |
| medicine | D3_cross_culture | 5 | 250 | 0.755 | 0.473 (0.383, 0.548) | 1.73 / 5 | no |
| science | D1_same_model | 5 | 250 | 0.713 | 0.586 (0.520, 0.655) | 1.49 / 5 | no |
| science | D2_cross_family_chinese | 5 | 250 | 0.746 | 0.408 (0.330, 0.479) | 1.90 / 5 | no |
| science | D3_cross_culture | 5 | 250 | 0.778 | 0.395 (0.312, 0.476) | 1.94 / 5 | no |

## Per-cell breakdown

### law × D1_same_model

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.258  |  **ρ:** 0.638 (95% CI 0.566, 0.700)  |  **N_eff:** 1.41  |  **C:** 9.3

**Per-agent accuracy**

- `deepseek_v4#1` — 0.276
- `deepseek_v4#2` — 0.248
- `deepseek_v4#3` — 0.256
- `deepseek_v4#4` — 0.260
- `deepseek_v4#5` — 0.252

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 27 | 0.444 | 0.258 | 0.143 | -0.186 |
| 2 | 21 | 0.524 | 0.493 | 0.182 | -0.031 |
| 3 | 24 | 0.625 | 0.730 | 0.229 | 0.105 |
| 4 | 22 | 0.864 | 0.883 | 0.284 | 0.019 |
| 5 | 36 | 0.833 | 0.955 | 0.346 | 0.121 |

### law × D2_cross_family_chinese

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.266  |  **ρ:** 0.498 (95% CI 0.434, 0.557)  |  **N_eff:** 1.67  |  **C:** 9.3

**Per-agent accuracy**

- `bytedance_seed#1` — 0.372
- `deepseek_v4#1` — 0.244
- `glm_46#1` — 0.084
- `kimi_k2#1` — 0.292
- `qwen_3#1` — 0.340

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 5 | 0.400 | 0.266 | 0.151 | -0.134 |
| 2 | 41 | 0.488 | 0.513 | 0.203 | 0.026 |
| 3 | 39 | 0.692 | 0.754 | 0.267 | 0.062 |
| 4 | 39 | 0.769 | 0.899 | 0.342 | 0.130 |
| 5 | 13 | 0.923 | 0.963 | 0.426 | 0.040 |

### law × D3_cross_culture

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.316  |  **ρ:** 0.660 (95% CI 0.600, 0.719)  |  **N_eff:** 1.37  |  **C:** 9.3

**Per-agent accuracy**

- `claude_sonnet#1` — 0.352
- `deepseek_v4#1` — 0.284
- `gemini_pro#1` — 0.384
- `gpt5_mini#1` — 0.256
- `kimi_k2#1` — 0.304

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 9 | 0.222 | 0.316 | 0.152 | 0.094 |
| 2 | 26 | 0.385 | 0.631 | 0.204 | 0.246 |
| 3 | 27 | 0.556 | 0.863 | 0.269 | 0.308 |
| 4 | 30 | 0.767 | 0.959 | 0.345 | 0.192 |
| 5 | 45 | 0.889 | 0.989 | 0.430 | 0.100 |

### medicine × D1_same_model

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.738  |  **ρ:** 0.659 (95% CI 0.576, 0.728)  |  **N_eff:** 1.37  |  **C:** 9.0

**Per-agent accuracy**

- `deepseek_v4#1` — 0.752
- `deepseek_v4#2` — 0.712
- `deepseek_v4#3` — 0.748
- `deepseek_v4#4` — 0.740
- `deepseek_v4#5` — 0.740

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 15 | 0.200 | 0.738 | 0.228 | 0.538 |
| 2 | 18 | 0.778 | 0.985 | 0.410 | 0.207 |
| 3 | 21 | 0.619 | 0.999 | 0.620 | 0.380 |
| 4 | 40 | 0.775 | 1.000 | 0.794 | 0.225 |
| 5 | 154 | 0.935 | 1.000 | 0.901 | 0.065 |

### medicine × D2_cross_family_chinese

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.690  |  **ρ:** 0.413 (95% CI 0.337, 0.479)  |  **N_eff:** 1.89  |  **C:** 9.0

**Per-agent accuracy**

- `bytedance_seed#1` — 0.808
- `deepseek_v4#1` — 0.744
- `glm_46#1` — 0.532
- `kimi_k2#1` — 0.596
- `qwen_3#1` — 0.772

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 7 | 0.286 | 0.690 | 0.270 | 0.405 |
| 2 | 20 | 0.450 | 0.975 | 0.524 | 0.525 |
| 3 | 52 | 0.846 | 0.999 | 0.765 | 0.152 |
| 4 | 86 | 0.895 | 1.000 | 0.906 | 0.105 |
| 5 | 85 | 0.918 | 1.000 | 0.966 | 0.082 |

### medicine × D3_cross_culture

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.755  |  **ρ:** 0.473 (95% CI 0.383, 0.548)  |  **N_eff:** 1.73  |  **C:** 9.0

**Per-agent accuracy**

- `claude_sonnet#1` — 0.836
- `deepseek_v4#1` — 0.736
- `gemini_pro#1` — 0.812
- `gpt5_mini#1` — 0.792
- `kimi_k2#1` — 0.600

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 2 | 0.500 | 0.755 | 0.275 | 0.255 |
| 2 | 15 | 0.267 | 0.987 | 0.535 | 0.720 |
| 3 | 28 | 0.643 | 0.999 | 0.777 | 0.357 |
| 4 | 86 | 0.907 | 1.000 | 0.913 | 0.093 |
| 5 | 119 | 0.916 | 1.000 | 0.970 | 0.084 |

### science × D1_same_model

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.713  |  **ρ:** 0.586 (95% CI 0.520, 0.655)  |  **N_eff:** 1.49  |  **C:** 9.8

**Per-agent accuracy**

- `deepseek_v4#1` — 0.704
- `deepseek_v4#2` — 0.708
- `deepseek_v4#3` — 0.708
- `deepseek_v4#4` — 0.736
- `deepseek_v4#5` — 0.708

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 29 | 0.655 | 0.713 | 0.219 | 0.058 |
| 2 | 27 | 0.741 | 0.982 | 0.416 | 0.242 |
| 3 | 22 | 0.864 | 0.999 | 0.643 | 0.136 |
| 4 | 23 | 0.957 | 1.000 | 0.820 | 0.043 |
| 5 | 138 | 0.986 | 1.000 | 0.920 | 0.014 |

### science × D2_cross_family_chinese

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.746  |  **ρ:** 0.408 (95% CI 0.330, 0.479)  |  **N_eff:** 1.90  |  **C:** 9.8

**Per-agent accuracy**

- `bytedance_seed#1` — 0.896
- `deepseek_v4#1` — 0.724
- `glm_46#1` — 0.528
- `kimi_k2#1` — 0.756
- `qwen_3#1` — 0.828

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 14 | 0.500 | 0.746 | 0.279 | 0.246 |
| 2 | 31 | 0.677 | 0.987 | 0.573 | 0.310 |
| 3 | 27 | 0.852 | 1.000 | 0.823 | 0.148 |
| 4 | 73 | 0.959 | 1.000 | 0.942 | 0.041 |
| 5 | 105 | 0.990 | 1.000 | 0.983 | 0.010 |

### science × D3_cross_culture

- **Items scored:** 250  |  **Agents:** 5  |  **Mean per-agent acc:** 0.778  |  **ρ:** 0.395 (95% CI 0.312, 0.476)  |  **N_eff:** 1.94  |  **C:** 9.8

**Per-agent accuracy**

- `claude_sonnet#1` — 0.844
- `deepseek_v4#1` — 0.776
- `gemini_pro#1` — 0.792
- `gpt5_mini#1` — 0.704
- `kimi_k2#1` — 0.776

**Cluster analysis** — for each item, the largest cluster of agents that picked the same letter. `Observed` = how often that cluster was actually correct; `Naive` = Condorcet posterior assuming independence; `Corrected` = same with k rescaled by N_eff / N; `Gap` = Naive − Observed (positive = overconfidence).

| Largest cluster k | Items | Observed correct | Naive posterior | Corrected posterior | Overconfidence gap |
|---|---|---|---|---|---|
| 1 | 13 | 0.231 | 0.778 | 0.298 | 0.548 |
| 2 | 14 | 0.714 | 0.991 | 0.618 | 0.277 |
| 3 | 36 | 0.806 | 1.000 | 0.860 | 0.194 |
| 4 | 60 | 0.917 | 1.000 | 0.959 | 0.083 |
| 5 | 127 | 0.984 | 1.000 | 0.989 | 0.016 |
