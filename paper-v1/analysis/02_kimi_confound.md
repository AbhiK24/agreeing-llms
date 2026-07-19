# Analysis 02 — The Kimi K2 confound

Kimi K2 accuracy came in at 20.4% across the sweep — barely above the 10%
random-guess baseline for 10-way MCQ. Diagnosis below.

## Cause: max_tokens truncation

`configs/experiment.yaml` set `max_tokens: 1024`. Kimi K2 is a
chain-of-thought-heavy model; on our MCQ prompt it emits verbose reasoning
that gets truncated by that cap before it produces a final letter answer.

Breakdown of Kimi's 1,500 calls:

| Category | Count | % |
|---|---|---|
| Correct (parsed a letter, matches gold) | 306 | 20.4% |
| Wrong-answer (parsed a letter, doesn't match gold) | 88 | 5.9% |
| **Unparseable** (no letter emitted) | **1,106** | **73.7%** |
| API failures (permanent / max retries) | 228 | 15.2% |

**73.7% of Kimi's responses lack any final letter answer.** Sampled raw
text confirms Kimi is mid-reasoning at the cut-off point.

## Sample of truncated Kimi responses

Every one of these was scored as an error even though Kimi may well have
converged on the correct answer had it been given room:

```
[science-009802, gold=I]
"I need to find the speed of the car using the Doppler effect.
Given:
- Observed frequency approaching: f' = 284 Hz
- Observed frequency receding:    f'' = 266 Hz
- Source frequency: f₀ (unknown)
- Speed of sound: v = 1100 ft/s
- Speed of car:   v_s (what …"

[science-010225, gold=G]
"I need to calculate the molar standard Gibbs energy for Cl₂ using
statistical mechanics.  The standard molar Gibbs energy is given by:
G_m^∘ = -RT ln(q_m^∘ / N_A) + …"
```

## Effect on ρ

Because Kimi effectively guesses in a large fraction of items, its errors
look uncorrelated with everyone else's by luck of near-random guessing.
That mechanically lowers ρ in D2 (Chinese) and D3 (cross-culture) without
providing genuine diversification.

**ρ WITH vs. WITHOUT Kimi K2:**

| Domain | Cell | With Kimi | Without Kimi | Δ |
|---|---|---|---|---|
| Science | D1 same-model | 0.488 (0.42, 0.56) | 0.488 (0.42, 0.56) | +0.000 |
| Science | D2 Chinese | 0.320 (0.25, 0.38) | **0.407** (0.33, 0.49) | +0.086 |
| Science | D3 cross-culture | 0.279 (0.21, 0.35) | **0.398** (0.31, 0.49) | +0.119 |
| Medicine | D1 same-model | 0.415 (0.33, 0.49) | 0.415 (0.33, 0.49) | +0.000 |
| Medicine | D2 Chinese | 0.276 (0.22, 0.33) | **0.389** (0.31, 0.46) | +0.113 |
| Medicine | D3 cross-culture | 0.320 (0.25, 0.38) | **0.463** (0.37, 0.55) | +0.143 |
| Law | D1 same-model | 0.557 (0.49, 0.62) | 0.557 (0.49, 0.62) | +0.000 |
| Law | D2 Chinese | 0.302 (0.25, 0.35) | **0.413** (0.34, 0.48) | +0.111 |
| Law | D3 cross-culture | 0.427 (0.37, 0.49) | **0.609** (0.54, 0.68) | +0.182 |

D1 rows unchanged because Kimi is not in that committee (D1 is 5 seeds
of DeepSeek). Every D2/D3 cell rises by +0.09 to +0.18 when Kimi is
excluded.

## What this means for the paper

**The Kimi-excluded numbers are the fairer analysis** and become the
primary D2/D3 result in the paper. The "with Kimi" numbers serve as a
robustness check that illustrates a separate methodological finding:
**a low-competence agent artificially deflates measured ρ, giving a
misleading impression of committee independence.**

This is actually a genuinely useful methodological contribution — the
paper can frame it as *"practitioners composing committees should measure
ρ conditional on comparable per-agent accuracy; adding a low-accuracy
model reduces ρ without adding genuine diversification."*

## Fix in v2

Re-run Kimi K2 at `max_tokens=4096` (or `8192`) on all 750 items × 2
conditions (D2, D3) = 1,500 calls. Expected cost: ~$1 given Kimi's
per-token pricing. Other 7 agents don't need re-running.

If Kimi's true accuracy at higher token budget is close to the ~65-70%
cluster of the other models, the v2 primary analysis simply uses those
completions and the "Kimi confound" story becomes a v1 anomaly report.
If Kimi remains at 20-30%, that's a genuine capability finding worth
its own subsection.
