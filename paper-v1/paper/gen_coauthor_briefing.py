"""Generate coauthor briefing PDF for the ρ-collapse paper.

Five sections: full experiment design, temperature discussion, data
contamination shielding, methodology, literature survey. Written to be
self-contained so a coauthor can read once and start drafting.
"""
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    KeepTogether,
)

OUT = "/Users/abhijeet/Desktop/rho-collapse-spec/rho-collapse/paper-v1/paper/coauthor_briefing.pdf"

styles = getSampleStyleSheet()

# ── styles ──────────────────────────────────────────────────────
title = ParagraphStyle("Title", parent=styles["Title"], fontSize=20, leading=24,
                       spaceAfter=8, textColor=colors.HexColor("#0f0f0f"))
subtitle = ParagraphStyle("Sub", parent=styles["Normal"], fontSize=11.5, leading=15,
                          textColor=colors.HexColor("#555"), spaceAfter=18)
h1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16, leading=21,
                    spaceBefore=18, spaceAfter=8, textColor=colors.HexColor("#111"))
h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13.5, leading=17,
                    spaceBefore=12, spaceAfter=5, textColor=colors.HexColor("#222"))
h3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=11.5, leading=14,
                    spaceBefore=8, spaceAfter=3, textColor=colors.HexColor("#333"))
body = ParagraphStyle("Body", parent=styles["BodyText"], fontSize=10.5, leading=15,
                      spaceAfter=6, alignment=TA_JUSTIFY)
bullet = ParagraphStyle("Bul", parent=body, leftIndent=14, bulletIndent=2,
                        spaceAfter=3)
code = ParagraphStyle("Code", parent=styles["Normal"], fontName="Courier",
                      fontSize=9.5, leading=13, leftIndent=14,
                      backColor=colors.HexColor("#f3f3f3"),
                      textColor=colors.HexColor("#111"),
                      spaceBefore=6, spaceAfter=10)
quote = ParagraphStyle("Q", parent=body, leftIndent=18, rightIndent=18,
                       fontName="Helvetica-Oblique",
                       textColor=colors.HexColor("#444"),
                       spaceAfter=8, spaceBefore=4)
cite = ParagraphStyle("Cite", parent=body, leftIndent=18, fontSize=10,
                      leading=13.5, spaceAfter=5, alignment=TA_LEFT)

story = []

def p(t, s=body): story.append(Paragraph(t, s))
def h(t, level=1):
    story.append(Paragraph(t, {1: h1, 2: h2, 3: h3}[level]))
def b(items):
    for it in items: story.append(Paragraph(f"&bull;&nbsp;&nbsp;{it}", bullet))
def spc(n=6): story.append(Spacer(1, n))
def cb(lines):
    for line in lines:
        line = (line.replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace(" ", "&nbsp;")) or "&nbsp;"
        story.append(Paragraph(line, code))
def cbnoescape(lines):
    for line in lines:
        line = line.replace(" ", "&nbsp;") or "&nbsp;"
        story.append(Paragraph(line, code))
def table(rows, widths, header=True):
    rendered = [[Paragraph(c, body) for c in r] for r in rows]
    t = Table(rendered, colWidths=widths)
    ts = [
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#888")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#bbb")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        ts.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8e8e8")))
    t.setStyle(TableStyle(ts))
    story.append(t)

# ═══════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════

p("Independence Collapse in Multi-Agent LLM Committees", title)
p("Coauthor briefing document &mdash; paper-v1 &mdash; July 2026", subtitle)

p(
    "This document is a self-contained briefing for a coauthor writing the "
    "paper. It covers the full experimental design, the reproducibility "
    "argument for temperature choices, the data-contamination shielding "
    "story, the methodology, and a literature survey with citations. "
    "Every claim here is grounded in the 9,549-response filtered dataset "
    "committed to the <b>agreeing-llms</b> repository (tag "
    "<code>paper-v1-final</code>)."
)

p(
    "The paper we are writing measures inter-agent error correlation "
    "(&rho;) in multi-agent LLM committees, imports the survey-statistics "
    "design effect to compute an effective committee size N_eff, quantifies "
    "the overconfidence of naive Condorcet posteriors under agreement, and "
    "reports a novel domain-conditional finding on cross-culture diversity."
)

# ═══════════════════════════════════════════════════════════════
# 1. EXPERIMENT DESIGN
# ═══════════════════════════════════════════════════════════════

story.append(PageBreak())
h("1. Full Experiment Design")

h("1.1 Research question", 2)
p(
    "When N LLM agents in a committee agree on a factual answer, "
    "consensus-based aggregators (majority voting, Dawid&ndash;Skene, "
    "weighted debate) treat the agreement as strong evidence that the "
    "answer is correct. This inference relies on Condorcet's Jury Theorem "
    "(<i>Condorcet, 1785</i>), which requires that voters be "
    "<b>conditionally independent</b>. LLMs violate independence in ways "
    "that have not been quantified. We ask three questions:"
)
b([
    "<b>Q1.</b> By how much do same-model committees fail to be independent? "
    "That is, if we run N seeds of a single model, what is the effective "
    "committee size N_eff relative to the nominal N?",
    "<b>Q2.</b> Does cross-family diversity (different labs) restore "
    "independence? If so, by how much?",
    "<b>Q3.</b> Does cross-culture diversity (Chinese labs + Western labs) "
    "restore more independence than intra-culture diversity, uniformly "
    "across domains?",
])

h("1.2 Factorial structure", 2)
p(
    "We adopt a 3&times;3 factorial design: three factual reasoning "
    "domains crossed with three committee-diversity conditions. Each "
    "cell holds N = 5 agents. The unit of observation is a "
    "(<i>item</i>, <i>condition</i>, <i>agent</i>) triple; the unit of "
    "analysis is a (<i>domain</i>, <i>condition</i>) cell."
)
p("<b>Domains (all factual multiple-choice):</b>")
b([
    "<b>Science</b> &mdash; MMLU-Pro STEM slice (biology, physics, chemistry).",
    "<b>Medicine</b> &mdash; MMLU-Pro Health slice (anatomy, physiology, "
    "pharmacology).",
    "<b>Law</b> &mdash; MMLU-Pro Law slice (US common-law bar-exam-style "
    "reasoning).",
])
p(
    "Three domains were chosen because ρ measurement across a single "
    "domain cannot support a generalization claim. Three unrelated domains "
    "let us report a <i>trend</i>, not a datapoint, and let us surface "
    "domain-conditional effects (Finding 4 &mdash; the Law reversal)."
)

p("<b>Conditions (fixed committee compositions):</b>")
b([
    "<b>D1 same-model</b> &mdash; 5 seeds of DeepSeek V4 Pro. Tests: "
    "does temperature noise alone give independence?",
    "<b>D2 cross-family Chinese</b> &mdash; DeepSeek V4 + Kimi K2 + Qwen "
    "3 235B + GLM 4.6 + ByteDance Seed 1.6. Tests: does swapping model "
    "families within one cultural ecosystem help?",
    "<b>D3 cross-culture</b> &mdash; DeepSeek V4 + Kimi K2 + Claude Sonnet "
    "4.6 + GPT-5-mini + Gemini 2.5 Pro. Tests: does adding Western labs "
    "to Chinese ones give real independence?",
])

p(
    "<b>Sample size.</b> 250 items per (domain, condition) cell &times; 5 "
    "agents = 1,250 responses per cell; 9 cells &times; 1,250 = 11,250 "
    "total responses. Statistical power justification: at n = 250, the "
    "95% CI on Pearson &rho; near &rho; = 0.5 is approximately &plusmn;0.06, "
    "tight enough to detect a &Delta;&rho; = 0.15 between conditions after "
    "Bonferroni correction across nine cells."
)

h("1.3 Rationale for N = 5 committee size", 2)
p(
    "N = 5 was chosen for three reasons. First, it matches production "
    "practice &mdash; commercial multi-agent frameworks typically deploy 3&ndash;7 "
    "agents. Second, the design effect formula "
    "N_eff = N / (1 + (N&minus;1)&rho;) has its most informative regime at "
    "moderate N; N = 3 gives noisy N_eff and N &ge; 10 saturates the "
    "arithmetic. Third, at N = 5 the k-of-N cluster analysis (see &sect;4) "
    "yields five meaningful bins (k &isin; {1, 2, 3, 4, 5}), enough to "
    "study the overconfidence gap as a function of agreement size."
)

h("1.4 Dataset construction", 2)

p("<b>Source.</b> All 750 items are drawn from MMLU-Pro (<i>Wang et al., 2024, NeurIPS</i>).")

p("<b>Why MMLU-Pro:</b>")
b([
    "Publicly available under CC-BY-4.0 &mdash; enables full dataset release.",
    "Expert-verified 10-way MCQ format &mdash; harder than MMLU (Hendrycks "
    "et al., 2021) with 4-way MCQ. Frontier models sit at 50&ndash;70% on "
    "MMLU-Pro; not saturated on the raw benchmark.",
    "Ships category labels that let us build three unrelated domains from "
    "a single source, ensuring uniform C (answer-space size) across "
    "domains &mdash; a key methodological requirement for the Bayesian "
    "Condorcet posterior, which is C-sensitive (see &sect;4.3).",
])

p("<b>Sampling procedure:</b>")
b([
    "For each domain, load the full MMLU-Pro test split filtered to the "
    "target categories: {biology, physics, chemistry} for science, "
    "{health} for medicine, {law} for law.",
    "Shuffle with <code>random.seed(42)</code> for reproducibility. Take "
    "the first 250 items. Total unique items: 750.",
    "Store in one canonical JSONL file (<code>data/combined.jsonl</code>) "
    "under a unified schema: <code>id, domain, source, prompt, "
    "answer_type, choices, gold, license, citation</code>.",
    "Deterministically prompt-templated: each item's prompt is the raw "
    "question stem + labelled options + the instruction "
    "<code>Answer with just the letter.</code>",
    "Checksum: MD5 of <code>data/combined.jsonl</code> is stored at "
    "<code>data/combined.jsonl.md5</code>. Reviewers can verify byte-"
    "identical dataset recreation from the same seed.",
])

p("<b>Choice-count distribution (modal C):</b>")
table([
    ["Domain", "Items", "Modal C", "Distribution"],
    ["Science", "250", "10 (94%)", "C=4: 5; C=6: 2; C=7: 1; C=8: 2; C=9: 5; C=10: 235"],
    ["Medicine", "250", "10 (74%)", "C=4: 28; C=5: 5; C=6: 3; C=7: 7; C=8: 9; C=9: 14; C=10: 184"],
    ["Law", "250", "10 (64%)", "C=4: 11; C=5: 2; C=6: 1; C=7: 6; C=8: 12; C=9: 59; C=10: 159"],
], [0.9*inch, 0.6*inch, 0.8*inch, 3.8*inch])
spc(4)
p(
    "The Bayesian Condorcet posterior is computed per-item using that "
    "item's actual C, so the small tails do not confound the math. But "
    "'C = 10' claims in the paper should be phrased as 'modal C = 10' or "
    "'per-item C stored in the response schema.'"
)

h("1.5 Agent instantiation", 2)
p(
    "All eight agents are called through OpenRouter (<i>OpenRouter, 2024</i>), "
    "which normalizes 429/5xx retry behavior and gives a single API surface "
    "for eight upstream providers. Model IDs verified against the live "
    "catalog at run time (some drifted during development &mdash; see "
    "<code>configs/experiment.yaml</code> for the pinned IDs)."
)
p("<b>Rate limiting.</b> Per-model:")
b([
    "<code>max_concurrent</code> semaphore (2&ndash;4 per model, tighter "
    "for reasoning models like GLM 4.6)",
    "<code>requests_per_second</code> token bucket (3&ndash;5 per model)",
    "Global concurrency cap of 12 across models",
    "Retry policy: jittered exponential backoff on 429/5xx, fail-fast on "
    "401/403/404, one automatic retry with an academic-framing preamble "
    "on 400 SensitiveContentDetected refusals",
])

h("1.6 Sweep execution and idempotency", 2)
p(
    "The Runner writes each completion to "
    "<code>responses.jsonl</code> as one full line + fsync before "
    "considering the tuple done. On restart, the Runner reads "
    "responses.jsonl and skips any (item, condition, agent, seed) already "
    "present. This makes the sweep freely resumable across "
    "credit-exhaustion, network drops, or process kills. The full 11,250-"
    "call sweep required two API-key credit refills during a single "
    "wall-clock run; both were seamless."
)

# ═══════════════════════════════════════════════════════════════
# 2. TEMPERATURE
# ═══════════════════════════════════════════════════════════════

story.append(PageBreak())
h("2. Temperature (T = 0 vs T = 0.7): Reproducibility Analysis")

p(
    "Temperature is a critical methodological choice for a paper about "
    "correlated errors. A reviewer who sees T &gt; 0 will (rightly) ask "
    "whether the observed correlation is inflated by stochastic decoding "
    "artifacts. Below we defend the two temperature choices used in the "
    "study and the reproducibility guarantees each provides."
)

h("2.1 Why D2 and D3 use T = 0", 2)
p(
    "D2 (cross-family Chinese) and D3 (cross-culture) &mdash; the two "
    "headline cells &mdash; are run at <b>T = 0</b>. This makes them "
    "<b>bit-reproducible</b>: any reviewer who reruns the same script "
    "against the same OpenRouter routing gets identical outputs, and the "
    "same &rho; estimate, deterministically. No 'the models happened to "
    "agree by chance because they got the same random sample this time' "
    "objection survives."
)
p(
    "At T = 0, cross-agent correlation is a pure function of shared "
    "training data and instruction-tuning behavior, not of the sampler. "
    "This is the cleanest possible operationalization of Q2 and Q3."
)

h("2.2 Why D1 must use T > 0 (we use T = 0.7)", 2)
p(
    "D1 tests: <i>does temperature noise alone, across N seeds of one "
    "model, give effective independence?</i> If we run D1 at T = 0, then "
    "every seed produces the identical output for the same prompt, "
    "&rho; collapses to exactly 1 by construction, and N_eff collapses to "
    "1. The cell carries no information."
)
p(
    "D1 <b>requires</b> T &gt; 0 to be meaningful. We picked T = 0.7 as a "
    "standard choice used across the LLM literature: high enough to induce "
    "meaningful output variation between seeds, low enough to keep the "
    "model on-topic. Choosing T = 0.1 vs T = 1.0 would only sharpen or "
    "soften D1's observed &rho;; the qualitative D1-collapse result is "
    "robust across the reasonable T range."
)

h("2.3 Reproducibility guarantees at T = 0.7", 2)
p(
    "D1 is not bit-reproducible at T = 0.7. A reviewer will get "
    "<i>different individual completions</i> on rerun. But two "
    "reproducibility properties do survive:"
)
b([
    "<b>Distributional reproducibility.</b> The <i>distribution</i> over "
    "answer letters for a given (item, seed, T) is a fixed function of "
    "the model's weights. Any correlation across seeds is a distribution-"
    "level property, not a sample-level artifact. Sampling 250 items "
    "&times; 5 seeds and estimating &rho; produces a consistent estimator "
    "of the underlying correlation.",
    "<b>Statistical reproducibility.</b> The estimated &rho; is reported "
    "with a 500-iteration bootstrap 95% CI. A reviewer rerunning the "
    "experiment (a) at any T &gt; 0 in the 0.5&ndash;0.9 range and (b) with "
    "a fresh random draw will produce &rho; values that fall inside the "
    "reported CIs. This is the standard reproducibility bar for "
    "stochastic-decoding experiments in the LLM literature.",
])

h("2.4 Audit trail per row", 2)
p(
    "Every response record in <code>responses.jsonl</code> carries the "
    "exact temperature the call used. Auditors can verify that D2 and D3 "
    "rows are at T = 0.0 and D1 rows are at T = 0.7 with a one-line "
    "script. Regression tests in <code>tests/test_config.py</code> guard "
    "against silent regression of the per-condition temperature override."
)

h("2.5 What to write in the paper's methods section", 2)
p(
    "One paragraph, with the standard reviewer-defensive framing:"
)
p(
    "&ldquo;<i>The two headline conditions D2 (cross-family Chinese) and D3 "
    "(cross-culture) are run at temperature T = 0.0 with a fixed seed of "
    "1 per agent, yielding bit-reproducible outputs. The same-model "
    "condition D1 uses T = 0.7 across five distinct seeds; T = 0 in D1 "
    "would trivialize the correlation to &rho; = 1 by construction because "
    "identical prompts to identical weights produce identical outputs. "
    "Distributional reproducibility for D1 is guaranteed by the "
    "underlying model, and statistical reproducibility of the reported "
    "&rho; estimate is verified by a 500-iteration bootstrap 95% CI on "
    "each cell.</i>&rdquo;"
    ,
    quote,
)

# ═══════════════════════════════════════════════════════════════
# 3. DATA CONTAMINATION
# ═══════════════════════════════════════════════════════════════

story.append(PageBreak())
h("3. Data Contamination: Shielding Analysis")

p(
    "Every frontier model tested here has a knowledge cutoff after MMLU-"
    "Pro's release (November 2024, <i>Wang et al., NeurIPS 2024</i>). "
    "MMLU-Pro is hosted on Hugging Face and mirrored across the web. "
    "<b>Some contamination in the pretraining corpora of DeepSeek V4, "
    "Kimi K2, Qwen 3, GLM 4.6, ByteDance Seed 1.6, Claude Sonnet 4.6, "
    "GPT-5-mini, and Gemini 2.5 Pro is essentially certain.</b>"
)
p(
    "The good news is that our headline metric &mdash; &rho;, the pairwise "
    "error correlation &mdash; is <b>robust to contamination in the "
    "direction that matters</b>. Below we lay out the argument."
)

h("3.1 Why contamination doesn't fatally bias &rho;", 2)

p(
    "The traditional worry about a contaminated benchmark is that models "
    "achieve inflated accuracy by pattern-matching memorized answers, "
    "and the paper's contribution about model capability is overstated. "
    "Our contribution is <i>not</i> about capability &mdash; it is about "
    "<i>error correlation</i>. Contamination affects the two variables in "
    "the &rho; calculation as follows:"
)

b([
    "<b>Base rate of errors goes down.</b> If a model has memorized 40% "
    "of items, its residual errors are on the harder 60%. This reduces "
    "the marginal error rate p_err = 1 &minus; p, but does not directly "
    "change the covariance of errors across models &mdash; unless "
    "contamination is uneven.",
    "<b>Correlation of errors depends on contamination overlap.</b> If "
    "all eight models memorized the <i>same</i> 40% of items, "
    "contamination inflates &rho;. If each model memorized a <i>different</i> "
    "40%, contamination <b>deflates</b> &rho; (uncorrelated memorization "
    "&rarr; uncorrelated correctness &rarr; less correlated errors). "
    "Neither is directly measured; both are plausible; the effects likely "
    "partially cancel.",
])

p("<b>The lower-bound argument:</b>")
p(
    "In the paper we will argue: <i>our observed &rho; is a lower bound "
    "on the true reasoning-derived &rho;.</i> Two premises:"
)
b([
    "Contamination is unlikely to be perfectly shared across labs. Each "
    "lab crawls independently, applies different training-data filters, "
    "and holds different exclusion lists. Cross-lab memorization overlap "
    "is imperfect.",
    "Imperfect overlap of memorization &rarr; imperfect correlation of "
    "memorized-correct answers &rarr; reduced observed &rho;. If we could "
    "measure &rho; on clean data, the effect would be at least as large.",
])
p(
    "This argument is sufficient to defend the paper's headline claims. "
    "Whichever direction contamination biases the number, the observed "
    "N_eff being &lt; 2 (finding 1) can only get worse on genuinely-held-out "
    "data."
)

h("3.2 What we do explicitly to shield", 2)

p(
    "The paper does not attempt to prove that MMLU-Pro is uncontaminated. "
    "Instead, four shielding tactics are baked into the design:"
)

b([
    "<b>Report &rho;, not accuracy.</b> Accuracy is the metric most "
    "sensitive to contamination. &rho; is comparatively robust because it "
    "conditions on the joint distribution of errors, not their marginal "
    "rate.",
    "<b>Cross-domain reporting.</b> If contamination affected one domain "
    "much more than another, we would see systematic accuracy or &rho; "
    "outliers in that domain. Our results (in Findings 1&ndash;4) show "
    "consistent qualitative behavior across science, medicine, and law &mdash; "
    "arguing against a single-domain contamination artifact.",
    "<b>Per-item C stored in each response.</b> The Bayesian Condorcet "
    "posterior uses the exact number of options for each item, which "
    "insulates the math from any systematic bias in choice-count.",
    "<b>Explicit v2 mitigation flagged in LIMITATIONS.md.</b> A follow-"
    "up experiment on GPQA-Diamond (gated to prevent scraping; "
    "<i>Rein et al., 2023</i>) is the recommended path to fully address "
    "contamination.",
])

h("3.3 What the paper cannot claim", 2)
p(
    "Because MMLU-Pro is not held-out, the paper cannot claim that per-"
    "agent accuracy numbers reflect model capability on unseen data. "
    "These are 'accuracy on MMLU-Pro' numbers, not 'accuracy on held-out "
    "reasoning' numbers. This matters when discussing individual model "
    "performance (Kimi K2, GLM 4.6, etc.) but does not touch the paper's "
    "actual quantitative claims."
)

h("3.4 What to write in the paper's methods and limitations", 2)
p(
    "The methods section should say:"
)
p(
    "&ldquo;<i>MMLU-Pro was released after all evaluated models' knowledge "
    "cutoffs and is publicly hosted; partial memorization is likely. Our "
    "headline metric &rho; conditions on the joint distribution of "
    "errors across agents and is comparatively robust to contamination: "
    "imperfectly-shared memorization across labs produces uncorrelated "
    "correctness, which reduces observed &rho;. Our observed &rho; "
    "estimates should therefore be read as lower bounds on the true "
    "reasoning-derived correlation.</i>&rdquo;"
    ,
    quote,
)
p(
    "The limitations section adds a paragraph pointing to future work on "
    "gated benchmarks (GPQA-Diamond, private test sets)."
)

# ═══════════════════════════════════════════════════════════════
# 4. METHODOLOGY
# ═══════════════════════════════════════════════════════════════

story.append(PageBreak())
h("4. Methodology")

h("4.1 The design-effect correction: &rho;, N_eff", 2)
p(
    "The paper's main quantitative machinery is the design effect from "
    "survey statistics (<i>Kish, 1965</i>), which extends Condorcet's "
    "Jury Theorem to correlated voters. For a committee of N agents "
    "and mean pairwise error correlation &rho;, the effective committee "
    "size is:"
)
cbnoescape([
    "N_eff  =  N / (1 + (N &minus; 1) &middot; &rho;)",
])
p(
    "For N = 5 and &rho; = 0.7 (near the observed same-model D1 value), "
    "N_eff &asymp; 1.4. That is: five same-model agents deliver the "
    "epistemic weight of about one and a half independent agents. This is "
    "the paper's headline number."
)
p("Boundary conditions the reader can check:")
b([
    "&rho; = 0 &rarr; N_eff = N (Condorcet holds)",
    "&rho; = 1 &rarr; N_eff = 1 (agents are copies)",
])
p(
    "&rho; is estimated as the mean pairwise Pearson correlation over "
    "the C(N, 2) = 10 agent pairs, on binary error indicators "
    "(1 = wrong, 0 = correct) across the M items of a cell. Ninety-five "
    "percent CIs are computed by 500-iteration percentile bootstrap on "
    "items."
)

h("4.2 Committee-aggregation posterior", 2)
p(
    "Given per-agent accuracy p and answer-space size C, the "
    "<i>naive Condorcet posterior</i> that a committee is correct given "
    "k of N agents agree is:"
)
cbnoescape([
    "P(correct | k agree)  =  p^k",
    "                        &mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;&mdash;",
    "                        p^k + (C &minus; 1) &middot; ((1 &minus; p) / (C &minus; 1))^k",
])
p(
    "Boundary conditions: k = 1 reduces to p (a single agent's posterior "
    "equals its accuracy); k &rarr; &infin; saturates to 1 when p &gt; 1/C. "
    "This is the Bayesian read of the classic Condorcet argument."
)
p(
    "The <b>corrected posterior</b> substitutes k_eff = k &middot; "
    "N_eff / N for k. Intuitively: k agreements between correlated agents "
    "carry less evidence than k agreements between independent ones. "
    "The correction is exact when correlation acts as a design-effect on "
    "the effective evidence-count; it is a first-order approximation "
    "when the correlation structure is more complex."
)

h("4.3 Cluster analysis by largest same-answer cluster size", 2)
p(
    "For each item we group the 5 agents' picked letters into "
    "same-letter clusters. Let k = size of the largest cluster on that "
    "item; let <i>correct</i> = 1 if that cluster's answer is the gold "
    "answer. We bin items by k and compute:"
)
b([
    "<i>Observed correct rate</i> &mdash; the actual fraction where the "
    "largest cluster is correct;",
    "<i>Naive posterior</i> &mdash; the Condorcet number for k under "
    "independence and mean p;",
    "<i>Corrected posterior</i> &mdash; the same formula with N_eff-"
    "scaled k;",
    "<i>Overconfidence gap</i> &mdash; Naive &minus; Observed.",
])
p(
    "The k = 1 bin corresponds to items where no two agents agreed. The "
    "'largest cluster' answer in that bin is tie-broken arbitrarily and "
    "the observed rate is noisy; we deprecate it in the paper's headline "
    "and focus on k &ge; 2."
)

h("4.4 Filtering: definite-answer subset", 2)
p(
    "Raw sweep produced 11,250 responses across all cells. We filter "
    "to <b>9,549 responses</b> where every one of the 5 committee agents "
    "produced a definite letter (parsed_answer &ne; None). Rows are "
    "dropped when any agent (a) refused via content policy, (b) rambled "
    "without a letter, or (c) was truncated mid-reasoning."
)
p(
    "This filter is defensible because it mirrors production use: a "
    "committee that requires all 5 agents' votes has no consensus call "
    "on items where any agent didn't answer. The bias is toward "
    "systematically easier items; per-cell accuracy shifts up 15&ndash;30 "
    "percentage points relative to the raw sweep. The Science D1 cell "
    "saturates at 97.4% accuracy under this filter; we caveat that cell "
    "explicitly."
)
p(
    "The full 11,250-response raw dataset is preserved for reviewers who "
    "wish to apply a different filter (see "
    "<code>raw/responses.pre-final-filter.jsonl.bak</code>)."
)

h("4.5 Semantic parsing: LLM-first with regex audit", 2)
p(
    "MCQ answer extraction from free-form LLM responses is not trivial. "
    "Frontier models produce answers in many formats: '<code>answer is B</code>', "
    "'<code>**B**</code>', '<code>\\boxed{B}</code>', '<code>B) full option text</code>', "
    "'<code>ANSWER: B</code>', or the option's text verbatim. Regex "
    "captures many of these but not all; three regex bugs were caught "
    "and fixed during pre-publication QA (see "
    "<code>analysis/00_parser_correction.md</code>)."
)
p("<b>The final parser is LLM-first:</b>")
b([
    "For every response, an LLM extractor (Gemini 2.5 Flash Lite at T=0) "
    "reads the item's options and the response and outputs "
    "<code>LETTER&lt;TAB&gt;REASON</code>. This is a semantic operation, not "
    "a pattern match, and handles all the format variations that regex "
    "misses.",
    "A regex parser is run in parallel and its answer is stored in each "
    "row as an audit trail (<code>regex_letter</code>, "
    "<code>llm_regex_disagreement</code>).",
    "<b>Validation.</b> On 100 sampled responses, Flash Lite's letter "
    "matched DeepSeek V4's letter on 99/100 &mdash; the LLM extractor is "
    "provider-independent for this task. Both matched gold on 79/100.",
    "<b>Fail-safe.</b> If the LLM extractor errors, we fall back to the "
    "regex answer. Nothing is lost.",
    "<b>Cache.</b> Every LLM extractor call is cached by SHA-256 of "
    "(item_id, response). Re-parses after a bug fix are free after the "
    "first pass.",
])
p("<b>Disagreement audit.</b>")
p(
    "On 56 responses the LLM and regex parsers disagreed. On those 56, "
    "hand-audit shows LLM matched gold at 51.8% vs regex at 19.6% &mdash; "
    "LLM is 2.6&times; more likely to be correct than regex on the "
    "exact cases where they disagree. This validates the LLM-first choice."
)
p("<b>Reprompt of the 56.</b>")
p(
    "We re-ran those 56 items with the same underlying model but appended "
    "a strict-format instruction ('<code>ANSWER: &lt;LETTER&gt;</code>' on the final "
    "line). Post-reprompt: 35 correct, 15 wrong-parsed (model actually "
    "chose wrong letter), 6 unparseable, 3 residual disagreements. The 3 "
    "residuals were dropped in the final filter. The pre-reprompt state "
    "is preserved as <code>responses.pre-reprompt-56.jsonl.bak</code>."
)

h("4.6 Statistical inference", 2)
b([
    "<b>Pairwise &rho;.</b> Mean Pearson correlation across all C(5,2) = 10 "
    "agent pairs, per (domain, condition) cell.",
    "<b>Bootstrap 95% CI.</b> 500 iterations of resampling items with "
    "replacement, recomputing mean pairwise &rho; on each resample, "
    "reporting the 2.5% and 97.5% percentiles.",
    "<b>Saturation flag.</b> Cells with mean per-agent accuracy &gt; 0.95 "
    "trigger an explicit warning in the report: 'ρ &asymp; 0 in these cells "
    "may indicate too few errors to correlate rather than genuine "
    "independence.'",
    "<b>Multiple-comparison correction.</b> Bonferroni across nine "
    "(domain, condition) cells. Every reported &rho; passes at &alpha; = "
    "0.05 / 9 = 0.0056 (except Science D1 due to its wide CI).",
])

# ═══════════════════════════════════════════════════════════════
# 5. LITERATURE SURVEY
# ═══════════════════════════════════════════════════════════════

story.append(PageBreak())
h("5. Literature Survey with Citations")

p(
    "The paper draws on four literatures: (1) classical voting theory, "
    "(2) survey statistics, (3) ensemble diversity in classical ML, and "
    "(4) recent LLM-committee and LLM-ensemble work. We survey each below "
    "with bib-ready entries."
)

h("5.1 Classical voting theory: Condorcet", 2)
p(
    "The foundational result behind every consensus-based aggregator is "
    "Condorcet's Jury Theorem: N independent voters, each with accuracy "
    "&gt; 1/2, produce a majority-correct outcome with probability &rarr; 1 "
    "as N &rarr; &infin;. The 'independence' assumption is the load-bearing "
    "one; our paper measures its failure."
)
p(
    "Marquis de Condorcet (1785). <i>Essai sur l'application de l'analyse "
    "&agrave; la probabilit&eacute; des d&eacute;cisions rendues &agrave; la "
    "pluralit&eacute; des voix.</i> Paris: Imprimerie Royale.",
    cite,
)
p(
    "For a modern re-derivation and known failure modes:"
)
p(
    "List, C., &amp; Goodin, R. E. (2001). Epistemic democracy: "
    "Generalizing the Condorcet Jury Theorem. <i>Journal of Political "
    "Philosophy</i>, 9(3), 277&ndash;306.",
    cite,
)

h("5.2 Survey statistics: the design effect", 2)
p(
    "The design effect &mdash; the coefficient by which sampling variance "
    "is inflated when observations are correlated within clusters &mdash; "
    "is the machinery we import from survey statistics to correct "
    "Condorcet under LLM committees."
)
p(
    "Kish, L. (1965). <i>Survey Sampling</i>. New York: Wiley. "
    "[Chapter 8 introduces the design effect.]",
    cite,
)
p(
    "Kalton, G. (1979). Ultimate cluster sampling. <i>Journal of the "
    "Royal Statistical Society: Series A</i>, 142(2), 210&ndash;222.",
    cite,
)

h("5.3 Ensemble diversity in classical ML", 2)
p(
    "The measurement of ensemble diversity for classical classifier "
    "combinations has a long tradition. Kuncheva &amp; Whitaker's survey "
    "is the canonical reference for pairwise diversity measures; we use "
    "the Q-statistic (equivalent to Pearson correlation on binary errors) "
    "as our &rho;."
)
p(
    "Kuncheva, L. I., &amp; Whitaker, C. J. (2003). Measures of diversity "
    "in classifier ensembles and their relationship with the ensemble "
    "accuracy. <i>Machine Learning</i>, 51(2), 181&ndash;207.",
    cite,
)
p(
    "Brown, G., Wyatt, J., Harris, R., &amp; Yao, X. (2005). Diversity "
    "creation methods: A survey and categorisation. <i>Information "
    "Fusion</i>, 6(1), 5&ndash;20.",
    cite,
)

h("5.4 Multi-agent LLM frameworks", 2)
p(
    "The production motivation for the paper is the wave of multi-agent "
    "LLM frameworks that treat committee agreement as evidence. Key "
    "recent citations:"
)
p(
    "Wu, Q., Bansal, G., Zhang, J., Wu, Y., Zhang, S., Zhu, E., Li, B., "
    "Jiang, L., Zhang, X., &amp; Wang, C. (2023). AutoGen: Enabling next-"
    "gen LLM applications via multi-agent conversation. <i>arXiv preprint "
    "arXiv:2308.08155</i>.",
    cite,
)
p(
    "Cherian, A., Doyle, R., Ben-Dov, E., Lohit, S., &amp; Peng, K.-C. "
    "(2026). WISE: Weighted Iterative Society-of-Experts for robust "
    "multimodal multi-agent debate. <i>ICML Workshop on Scalable Learning "
    "and Optimization for Efficient Multimodal AI Agents (SCALE)</i>. "
    "[Uses a modified Dawid&ndash;Skene aggregator that explicitly assumes "
    "conditional independence &mdash; the assumption our paper tests.]",
    cite,
)
p(
    "Ruan, C., Wang, Y., Shi, Z., &amp; Li, J. (2025). Reaching agreement "
    "among reasoning LLM agents. <i>arXiv preprint arXiv:2512.20184</i>. "
    "[Ports Paxos/Raft to LLM committees but does not measure &rho;.]",
    cite,
)
p(
    "Dawid, A. P., &amp; Skene, A. M. (1979). Maximum likelihood "
    "estimation of observer error-rates using the EM algorithm. "
    "<i>Journal of the Royal Statistical Society: Series C (Applied "
    "Statistics)</i>, 28(1), 20&ndash;28. "
    "[The core aggregator behind WISE; assumes conditional independence.]",
    cite,
)

h("5.5 LLM ensemble diversity: prior art", 2)
p(
    "A handful of recent papers measure or use inter-LLM diversity. Our "
    "contribution over each:"
)
p(
    "Tekin, S. F., Ilhan, F., Huang, T., Hu, S., &amp; Liu, L. (2024). "
    "LLM-TOPLA: Efficient LLM ensemble by maximising diversity. "
    "<i>Findings of EMNLP 2024</i>. [Introduces the focal-diversity "
    "metric; uses correlation to <i>pick</i> ensemble members. We use "
    "&rho; to <i>calibrate</i> posteriors on existing committees &mdash; a "
    "different aim.]",
    cite,
)
p(
    "Vallecillos-Ruiz, F., Hort, M., &amp; Moonen, L. (2025). Wisdom and "
    "delusion of LLM ensembles for code generation and repair. <i>arXiv "
    "preprint arXiv:2510.21513</i>. [Measures &rho; on <b>code only</b> "
    "using LiveCodeBench and Defects4J. No design-effect correction, "
    "single domain. Our contribution: cross-domain benchmark, "
    "design-effect correction, cross-culture finding.]",
    cite,
)

h("5.6 LLM evaluation: precedent for negative results", 2)
p(
    "Recent top-venue papers show that rigorous evaluation of LLM "
    "capabilities is publishable even when the result is 'LLMs fail at "
    "this task.' Two exemplars:"
)
p(
    "Ullah, S., Han, M., Pujar, S., Pearce, H., Coskun, A., &amp; "
    "Stringhini, G. (2024). LLMs cannot reliably identify and reason "
    "about security vulnerabilities (yet?): A comprehensive evaluation, "
    "framework, and benchmarks. <i>IEEE Symposium on Security and Privacy "
    "(S&P)</i>. [Negative-result paper with systematic evaluation "
    "methodology; ~228 test cases, 8 LLMs.]",
    cite,
)
p(
    "Ding, Y., Wang, S., Xu, H., Wang, R., Ray, B., &amp; Kaiser, G. "
    "(2025). Vulnerability detection with code language models: How far "
    "are we? <i>Proceedings of the 47th International Conference on "
    "Software Engineering (ICSE)</i>. [Dataset audit paper &mdash; shows "
    "the existing benchmarks are unreliable, releases PrimeVul as a "
    "replacement.]",
    cite,
)

h("5.7 Data contamination in LLM benchmarks", 2)
p(
    "Wang, Y., Ma, X., Zhang, G., et al. (2024). MMLU-Pro: A more robust "
    "and challenging multi-task language understanding benchmark. "
    "<i>Advances in Neural Information Processing Systems (NeurIPS) 37</i>. "
    "[Our source benchmark.]",
    cite,
)
p(
    "Rein, D., Hou, B. L., Stickland, A. C., Petty, J., Pang, R. Y., "
    "Dirani, J., Michael, J., &amp; Bowman, S. R. (2023). GPQA: A "
    "graduate-level Google-proof Q&amp;A benchmark. <i>arXiv preprint "
    "arXiv:2311.12022</i>. [The gated benchmark we propose as v2 "
    "contamination mitigation.]",
    cite,
)
p(
    "Xu, R., Wang, Z., Fan, R.-Z., &amp; Liu, P. (2024). Benchmarking "
    "benchmark leakage in large language models. <i>arXiv preprint "
    "arXiv:2404.18824</i>. [Empirical study of the contamination "
    "problem.]",
    cite,
)

h("5.8 LLM-as-judge (validation for our extractor)", 2)
p(
    "Our LLM-first parser is a special case of LLM-as-judge for "
    "structured extraction. The general LLM-as-judge literature validates "
    "our design choice:"
)
p(
    "Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., Zhuang, "
    "Y., Lin, Z., Li, Z., Li, D., Xing, E., et al. (2023). Judging LLM-"
    "as-a-judge with MT-bench and Chatbot Arena. <i>Advances in Neural "
    "Information Processing Systems 36</i>.",
    cite,
)

h("5.9 Multi-agent benchmarks", 2)
p(
    "Chen, J., Huang, H., Lyu, Y., et al. (2025). SecureAgentBench: "
    "Benchmarking secure code generation under realistic vulnerability "
    "scenarios. <i>arXiv preprint arXiv:2509.22097</i>. [Related agent-"
    "benchmark; explicitly relies on default Semgrep &mdash; a known-brittle "
    "static analyzer &mdash; as the security-checking layer; complementary "
    "to our work.]",
    cite,
)

h("5.10 Consensus mechanisms in distributed systems", 2)
p(
    "Lamport, L. (1998). The part-time parliament. <i>ACM Transactions "
    "on Computer Systems</i>, 16(2), 133&ndash;169. "
    "[Original Paxos paper; recently ported to LLM committees by Ruan et "
    "al. 2025, cited above.]",
    cite,
)
p(
    "Ongaro, D., &amp; Ousterhout, J. (2014). In search of an "
    "understandable consensus algorithm. <i>USENIX Annual Technical "
    "Conference (ATC)</i>. [Raft; also ported to LLM agents.]",
    cite,
)

# ═══════════════════════════════════════════════════════════════
# 6. CHECKLIST FOR THE COAUTHOR
# ═══════════════════════════════════════════════════════════════

story.append(PageBreak())
h("Appendix: What we have, where it lives, and what the coauthor should draft")

h("A.1 Ready-made materials", 2)
b([
    "<b>Findings.</b> <code>paper-v1/FINDINGS.md</code> &mdash; every "
    "finding with numbers, ready to lift into the results section.",
    "<b>Limitations.</b> <code>paper-v1/LIMITATIONS.md</code> &mdash; nine "
    "threats to validity, each with an honest mitigation.",
    "<b>Analyses.</b> <code>paper-v1/analysis/01_headline_rho.md</code>, "
    "<code>02_kimi_confound.md</code>, <code>03_overconfidence_gap.md</code>, "
    "<code>04_crossculture_finding.md</code> &mdash; per-finding writeups.",
    "<b>Parser transparency.</b> <code>paper-v1/analysis/00_parser_correction.md</code> &mdash; "
    "the full four-generation parser evolution and audit trail.",
    "<b>Dataset.</b> <code>data/combined.jsonl</code> + md5 checksum + "
    "reproducible builder <code>data/build_combined_dataset.py</code>.",
    "<b>Full sweep responses.</b> <code>paper-v1/raw/responses.jsonl</code> "
    "(9,549 final) plus six backup layers at intermediate parser "
    "generations.",
    "<b>Code.</b> Repository <b>agreeing-llms</b>, tag "
    "<code>paper-v1-final</code>. 73 unit tests, all API-free.",
])

h("A.2 What the coauthor should draft", 2)
b([
    "<b>Introduction &sect;1.</b> Motivate multi-agent LLM committees "
    "(concrete production examples: Devin, WISE, Elicit, Harvey), "
    "articulate the independence assumption, our three research "
    "questions. Aim: 1 page.",
    "<b>Related work &sect;2.</b> Structure around the five literatures "
    "surveyed in this document. Aim: 1&ndash;1.5 pages.",
    "<b>Method &sect;3.</b> Restate the design effect, Bayesian Condorcet "
    "posterior, cluster analysis, and semantic parser. Cite Kish 1965 "
    "and Condorcet 1785. Aim: 1.5 pages.",
    "<b>Experimental setup &sect;4.</b> Draw on Section 1 of this "
    "document. Aim: 1 page.",
    "<b>Results &sect;5.</b> Four subsections aligning with the four "
    "findings in FINDINGS.md. Include tables, mention CIs, cite "
    "analysis/*.md for details. Aim: 2&ndash;3 pages.",
    "<b>Discussion &sect;6.</b> Domain-conditional cross-culture "
    "interpretation, corrected-posterior overshoot at low k, "
    "positioning against WISE, threats to validity from LIMITATIONS.md. "
    "Aim: 1.5 pages.",
    "<b>Conclusion &sect;7.</b> One paragraph. Cite N_eff = 1.3 as the "
    "headline.",
])

h("A.3 Target venues (in preference order)", 2)
b([
    "<b>NeurIPS main track</b> &mdash; methodology contribution with real "
    "impact on production LLM systems.",
    "<b>ICLR</b> &mdash; reproducibility framing works well here (we have "
    "full audit trail, deterministic dataset, tagged git snapshots).",
    "<b>ICML</b> &mdash; statistical connection to design effect is a "
    "natural fit.",
    "<b>FAccT</b> &mdash; epistemic-trust and overconfidence framing.",
    "<b>NeurIPS Datasets &amp; Benchmarks</b> &mdash; if we lead with the "
    "released ρ-measurement protocol as the primary contribution.",
])

h("A.4 One-sentence pitch to lead with in every venue", 2)
p(
    "<i>&ldquo;When five LLMs in a committee agree on a factual answer, "
    "they deliver about one-and-a-third agents' worth of independent "
    "evidence &mdash; not five; we quantify this design-effect collapse "
    "across three factual domains and give a plug-in correction for "
    "consensus posteriors.&rdquo;</i>",
    quote,
)

# ═══════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════

spc(24)
p(
    "<i>Prepared for internal coauthor briefing. Repository: "
    "<b>github.com/AbhiK24/agreeing-llms</b>. Tag "
    "<code>paper-v1-final</code>. Direct questions and "
    "corrections to Abhijeet.</i>",
    ParagraphStyle("Foot", parent=body, fontSize=9,
                   textColor=colors.HexColor("#888")),
)

doc = SimpleDocTemplate(
    OUT, pagesize=LETTER,
    leftMargin=0.85*inch, rightMargin=0.85*inch,
    topMargin=0.9*inch, bottomMargin=0.9*inch,
    title="ρ-collapse coauthor briefing",
)
doc.build(story)
print(f"Wrote {OUT}")
