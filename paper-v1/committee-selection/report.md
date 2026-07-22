# Committee selection from the paper-v1 T=0 sweep

All numbers derive from `paper-v1/raw/responses.pre-final-filter.jsonl.bak`
(T=0 rows only; D2 row preferred over D3 for the two duplicated models).
Plurality accuracy uses abstention-tolerant voting over the full item
set, so every committee is scored on identical items.

## Per-model accuracy and cost (T=0 pool)

| Model | law | medicine | science | mean tokens_out |
|---|---|---|---|---|
| bytedance_seed | 0.682 | 0.818 | 0.900 | 1281 |
| claude_sonnet | 0.644 | 0.847 | 0.889 | 80 |
| deepseek_v4 | 0.611 | 0.847 | 0.907 | 770 |
| gemini_pro | 0.725 | 0.825 | 0.795 | 960 |
| glm_46 | 0.429 | 0.851 | 0.865 | 964 |
| gpt5_mini | 0.665 | 0.849 | 0.917 | 518 |
| kimi_k2 | 0.598 | 0.813 | 0.905 | 217 |
| qwen_3 | 0.632 | 0.789 | 0.905 | 3162 |

## Best size-5 committee per domain (plurality accuracy)

| Domain | Committee | Plurality acc | Mean acc | ρ̄ | N_eff |
|---|---|---|---|---|---|
| law | bytedance_seed, claude_sonnet, gemini_pro, kimi_k2, qwen_3 | 0.716 | 0.656 | 0.480 | 1.71 |
| medicine | claude_sonnet, deepseek_v4, gemini_pro, gpt5_mini, kimi_k2 | 0.861 | 0.836 | 0.636 | 1.41 |
| science | bytedance_seed, claude_sonnet, deepseek_v4, gpt5_mini, qwen_3 | 0.916 | 0.904 | 0.596 | 1.48 |

## Generalization regret (deploy row-domain's winner on column-domain)

Accuracy given up versus the column domain's own best committee:

| train \ test | law | medicine | science |
|---|---|---|---|
| law | 0.000 | 0.022 | 0.007 |
| medicine | 0.053 | 0.000 | 0.021 |
| science | 0.026 | 0.012 | 0.000 |

## Within-domain split-half (size 5, 20 splits)

Calibrate on half the items, deploy on the other half:

| Domain | rho_greedy | rho_exhaustive | top_acc | empirical | random |
|---|---|---|---|---|---|
| law | 0.680 ± 0.039 | 0.679 ± 0.037 | 0.694 ± 0.039 | 0.688 ± 0.037 | 0.669 ± 0.039 |
| medicine | 0.844 ± 0.018 | 0.845 ± 0.018 | 0.848 ± 0.020 | 0.842 ± 0.015 | 0.847 ± 0.020 |
| science | 0.889 ± 0.019 | 0.892 ± 0.017 | 0.900 ± 0.015 | 0.900 ± 0.014 | 0.898 ± 0.019 |

## Leave-one-domain-out (size 5)

Calibrate p and ρ on the other two domains, deploy on the held-out one:

| Held-out | rho_greedy | rho_exhaustive | top_acc | empirical | oracle | random E |
|---|---|---|---|---|---|---|
| law | 0.663 | 0.663 | 0.670 | 0.670 | 0.716 | 0.677 |
| medicine | 0.856 | 0.848 | 0.849 | 0.839 | 0.861 | 0.848 |
| science | 0.894 | 0.894 | 0.907 | 0.897 | 0.916 | 0.900 |

Committees chosen (LODO):

- **law / rho_greedy**: claude_sonnet, deepseek_v4, gemini_pro, gpt5_mini, kimi_k2
- **law / rho_exhaustive**: claude_sonnet, deepseek_v4, gemini_pro, gpt5_mini, kimi_k2
- **law / top_acc**: bytedance_seed, claude_sonnet, deepseek_v4, gpt5_mini, kimi_k2
- **law / empirical**: bytedance_seed, claude_sonnet, deepseek_v4, gpt5_mini, kimi_k2
- **medicine / rho_greedy**: bytedance_seed, claude_sonnet, deepseek_v4, gemini_pro, gpt5_mini
- **medicine / rho_exhaustive**: bytedance_seed, claude_sonnet, deepseek_v4, gemini_pro, glm_46
- **medicine / top_acc**: bytedance_seed, claude_sonnet, deepseek_v4, gpt5_mini, qwen_3
- **medicine / empirical**: bytedance_seed, claude_sonnet, gemini_pro, kimi_k2, qwen_3
- **science / rho_greedy**: claude_sonnet, deepseek_v4, gemini_pro, glm_46, qwen_3
- **science / rho_exhaustive**: claude_sonnet, deepseek_v4, gemini_pro, glm_46, qwen_3
- **science / top_acc**: bytedance_seed, claude_sonnet, deepseek_v4, gemini_pro, gpt5_mini
- **science / empirical**: claude_sonnet, deepseek_v4, gemini_pro, kimi_k2, qwen_3

## Head-to-head: the protocol vs current practice

`same_model_5seeds` is the D1 condition (5 seeds of DeepSeek V4 at
T=0.7) rescored with abstention voting over all items, so it is
directly comparable. Cost = mean output tokens per item.

| Domain | Strategy | Committee | Accuracy | Cost (tok/item) |
|---|---|---|---|---|
| law | protocol | claude_sonnet, gemini_pro, gpt5_mini | 0.667 | 1557 |
| law | same_model_5seeds | deepseek_v4 × 5 seeds | 0.585 | 4665 |
| law | top5_acc | bytedance_seed, claude_sonnet, gemini_pro, gpt5_mini, qwen_3 | 0.708 | 6000 |
| law | full_pool | bytedance_seed, claude_sonnet, deepseek_v4, gemini_pro, glm_46, gpt5_mini, kimi_k2, qwen_3 | 0.699 | 7951 |
| medicine | protocol | claude_sonnet, kimi_k2 | 0.832 | 297 |
| medicine | same_model_5seeds | deepseek_v4 × 5 seeds | 0.817 | 2759 |
| medicine | top5_acc | claude_sonnet, deepseek_v4, gemini_pro, glm_46, gpt5_mini | 0.859 | 3292 |
| medicine | full_pool | bytedance_seed, claude_sonnet, deepseek_v4, gemini_pro, glm_46, gpt5_mini, kimi_k2, qwen_3 | 0.851 | 7951 |
| science | protocol | claude_sonnet, gpt5_mini, kimi_k2 | 0.891 | 815 |
| science | same_model_5seeds | deepseek_v4 × 5 seeds | 0.867 | 3823 |
| science | top5_acc | bytedance_seed, deepseek_v4, gpt5_mini, kimi_k2, qwen_3 | 0.910 | 5947 |
| science | full_pool | bytedance_seed, claude_sonnet, deepseek_v4, gemini_pro, glm_46, gpt5_mini, kimi_k2, qwen_3 | 0.905 | 7951 |

## Rank transfer across domains (Spearman over size-5 committees)

Neither accuracy ranks nor ρ ranks transfer — committee choice is
domain-specific all the way down:

| Domain pair | plurality-acc rank corr | ρ̄ rank corr |
|---|---|---|
| law vs medicine | -0.231 | +0.193 |
| law vs science | +0.382 | -0.302 |
| medicine vs science | -0.455 | -0.541 |

## Constrained selection demo (cost budget)

Cost proxy: mean tokens_out per call. Budget = 3561 tokens across the committee.

- **law**: unconstrained → claude_sonnet, deepseek_v4, gemini_pro, glm_46, qwen_3 (cost 5936); budgeted → bytedance_seed, claude_sonnet, deepseek_v4, gemini_pro, kimi_k2 (cost 3308, plurality 0.706 vs 0.701)
- **medicine**: unconstrained → claude_sonnet, deepseek_v4, glm_46, kimi_k2, qwen_3 (cost 5193); budgeted → claude_sonnet, deepseek_v4, glm_46, gpt5_mini, kimi_k2 (cost 2549, plurality 0.857 vs 0.852)
- **science**: unconstrained → claude_sonnet, deepseek_v4, gemini_pro, gpt5_mini, kimi_k2 (cost 2545); budgeted → claude_sonnet, deepseek_v4, gemini_pro, gpt5_mini, kimi_k2 (cost 2545, plurality 0.895 vs 0.895)
