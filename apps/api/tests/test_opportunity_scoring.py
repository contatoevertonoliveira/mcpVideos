from app.agents.schemas import OpportunityEvaluatorOutput
from app.models.enums import ScoreType
from app.services.opportunity_scoring import RECOMMEND_THRESHOLD, SCORE_WEIGHTS, score_opportunity


def test_weights_sum_to_one():
    assert abs(sum(SCORE_WEIGHTS.values()) - 1.0) < 1e-9


def test_high_scores_across_the_board_are_recommended():
    evaluation = OpportunityEvaluatorOutput(
        channel_fit=85,
        audience_fit=80,
        trend=55,
        novelty=45,
        retention_potential=75,
        search_potential=60,
        competition=65,
        brand_fit=90,
        strategic_fit=80,
        confidence=0.7,
        reasoning_summary="strong fit",
    )

    result = score_opportunity(evaluation)

    assert result.recommended is True
    assert result.final_score >= RECOMMEND_THRESHOLD
    assert len(result.components) == len(SCORE_WEIGHTS)
    assert {c.score_type for c in result.components} == set(ScoreType)


def test_low_channel_and_audience_fit_is_rejected_even_with_high_trend():
    """The literal Documento 10 F09 acceptance criterion: a trend-chasing,
    off-niche idea must be rejectable by the system, not just given a
    lower (but still passing) score."""
    evaluation = OpportunityEvaluatorOutput(
        channel_fit=20,
        audience_fit=25,
        trend=70,
        novelty=85,
        retention_potential=30,
        search_potential=40,
        competition=35,
        brand_fit=30,
        strategic_fit=15,
        confidence=0.55,
        reasoning_summary="off-niche trend",
    )

    result = score_opportunity(evaluation)

    assert result.recommended is False
    assert result.final_score < RECOMMEND_THRESHOLD


def test_weighted_score_matches_manual_calculation():
    evaluation = OpportunityEvaluatorOutput(
        channel_fit=100,
        audience_fit=0,
        trend=0,
        novelty=0,
        retention_potential=0,
        search_potential=0,
        competition=0,
        brand_fit=0,
        strategic_fit=0,
        confidence=1.0,
        reasoning_summary="",
    )

    result = score_opportunity(evaluation)

    # Only channel_fit=100 contributes: 100 * its weight.
    assert result.final_score == 100 * SCORE_WEIGHTS[ScoreType.CHANNEL_FIT]
