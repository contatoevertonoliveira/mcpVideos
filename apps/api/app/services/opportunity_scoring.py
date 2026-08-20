"""Pure, agent-independent opportunity scoring (Documento 10 Fase 09:
"Opportunity Score: calculo final deve ocorrer em codigo").

The Opportunity Evaluator agent (Documento 05, secao 11) only proposes raw
0-100 component scores. Everything here - the weights, the weighted sum,
and the approve/reject threshold - is deterministic code, never trusted
from the LLM's own opinion. This is what lets the system genuinely
"reject an irrelevant trend" (Documento 10 F09 acceptance criterion)
instead of just repeating whatever the agent recommended.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.agents.schemas import OpportunityEvaluatorOutput
from app.models.enums import ScoreType

# Weights chosen so that how well an idea fits THIS channel and its
# audience (the two hardest things to fake with a generic idea) dominate
# the score, with strategic alignment and retention next; novelty, brand
# fit and raw competition are real but secondary signals. Sums to 1.0 -
# adjust deliberately, never silently, if rebalanced later.
SCORE_WEIGHTS: dict[ScoreType, float] = {
    ScoreType.CHANNEL_FIT: 0.18,
    ScoreType.AUDIENCE_FIT: 0.16,
    ScoreType.RETENTION_POTENTIAL: 0.14,
    ScoreType.STRATEGIC_FIT: 0.12,
    ScoreType.TREND: 0.10,
    ScoreType.SEARCH_POTENTIAL: 0.10,
    ScoreType.NOVELTY: 0.08,
    ScoreType.BRAND_FIT: 0.07,
    ScoreType.COMPETITION: 0.05,
}

assert abs(sum(SCORE_WEIGHTS.values()) - 1.0) < 1e-9

# An idea needs a majority-positive weighted score across the board to be
# worth a human's attention - below this, auto-reject rather than let a
# mediocre-everywhere idea clutter the Ideas screen.
RECOMMEND_THRESHOLD = 60.0

_RAW_SCORE_BY_TYPE: dict[ScoreType, str] = {
    ScoreType.CHANNEL_FIT: "channel_fit",
    ScoreType.AUDIENCE_FIT: "audience_fit",
    ScoreType.TREND: "trend",
    ScoreType.NOVELTY: "novelty",
    ScoreType.RETENTION_POTENTIAL: "retention_potential",
    ScoreType.SEARCH_POTENTIAL: "search_potential",
    ScoreType.COMPETITION: "competition",
    ScoreType.BRAND_FIT: "brand_fit",
    ScoreType.STRATEGIC_FIT: "strategic_fit",
}


@dataclass
class ScoredComponent:
    score_type: ScoreType
    score: float
    weight: float
    weighted_score: float


@dataclass
class OpportunityScoringResult:
    components: list[ScoredComponent]
    final_score: float
    recommended: bool


def score_opportunity(evaluation: OpportunityEvaluatorOutput) -> OpportunityScoringResult:
    components = []
    final_score = 0.0
    for score_type, attr_name in _RAW_SCORE_BY_TYPE.items():
        raw_score = getattr(evaluation, attr_name)
        weight = SCORE_WEIGHTS[score_type]
        weighted = raw_score * weight
        components.append(
            ScoredComponent(
                score_type=score_type, score=raw_score, weight=weight, weighted_score=weighted
            )
        )
        final_score += weighted

    return OpportunityScoringResult(
        components=components,
        final_score=round(final_score, 4),
        recommended=final_score >= RECOMMEND_THRESHOLD,
    )
