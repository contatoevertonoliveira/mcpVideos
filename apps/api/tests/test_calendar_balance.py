from datetime import UTC, datetime

from app.models.content_pillar import ContentPillar
from app.models.content_strategy import ContentStrategy
from app.services.calendar_balance import (
    PlannedItem,
    build_format_balance,
    build_pillar_balance,
    detect_conflicts,
)


def _strategy(shorts_ratio=0.4, long_form_ratio=0.6) -> ContentStrategy:
    return ContentStrategy(shorts_ratio=shorts_ratio, long_form_ratio=long_form_ratio)


def test_format_balance_empty_batch():
    assert build_format_balance([], _strategy()) == {}


def test_format_balance_matches_manual_ratio():
    batch = [
        PlannedItem(content_type="short", planned_at=datetime.now(UTC)),
        PlannedItem(content_type="short", planned_at=datetime.now(UTC)),
        PlannedItem(content_type="long_form", planned_at=datetime.now(UTC)),
    ]

    report = build_format_balance(batch, _strategy(shorts_ratio=0.5, long_form_ratio=0.5))

    assert report["shorts_ratio_actual"] == round(2 / 3, 4)
    assert report["long_form_ratio_actual"] == round(1 / 3, 4)
    assert report["shorts_ratio_target"] == 0.5
    assert report["long_form_ratio_target"] == 0.5


def test_pillar_balance_empty_inputs():
    assert build_pillar_balance([], []) == {}
    assert (
        build_pillar_balance([PlannedItem(content_type="short", planned_at=datetime.now(UTC))], [])
        == {}
    )


def test_pillar_balance_matches_manual_ratio():
    pillar_a = ContentPillar(name="Reviews", target_ratio=0.4)
    pillar_b = ContentPillar(name="Comparativos", target_ratio=0.6)
    batch = [
        PlannedItem(content_type="short", planned_at=datetime.now(UTC), content_pillar="Reviews"),
        PlannedItem(
            content_type="long_form", planned_at=datetime.now(UTC), content_pillar="Comparativos"
        ),
        PlannedItem(
            content_type="long_form", planned_at=datetime.now(UTC), content_pillar="Comparativos"
        ),
    ]

    report = build_pillar_balance(batch, [pillar_a, pillar_b])

    assert report["Reviews"]["actual_ratio"] == round(1 / 3, 4)
    assert report["Reviews"]["target_ratio"] == 0.4
    assert report["Comparativos"]["actual_ratio"] == round(2 / 3, 4)
    assert report["Comparativos"]["target_ratio"] == 0.6


def test_detect_conflicts_no_overlap():
    batch = [PlannedItem(content_type="short", planned_at=datetime(2026, 9, 1, 10, tzinfo=UTC))]
    existing = [PlannedItem(content_type="short", planned_at=datetime(2026, 9, 2, 10, tzinfo=UTC))]

    assert detect_conflicts(batch, existing) == []


def test_detect_conflicts_same_day_as_existing_item():
    day = datetime(2026, 9, 1, 10, tzinfo=UTC)
    batch = [PlannedItem(content_type="short", planned_at=day)]
    existing = [
        PlannedItem(content_type="long_form", planned_at=datetime(2026, 9, 1, 18, tzinfo=UTC))
    ]

    conflicts = detect_conflicts(batch, existing)

    assert len(conflicts) == 1
    assert "2026-09-01" in conflicts[0]


def test_detect_conflicts_within_the_same_batch():
    day = datetime(2026, 9, 1, 10, tzinfo=UTC)
    batch = [
        PlannedItem(content_type="short", planned_at=day),
        PlannedItem(content_type="short", planned_at=datetime(2026, 9, 1, 20, tzinfo=UTC)),
    ]

    conflicts = detect_conflicts(batch, [])

    # First item on that day has no prior occupant; the second one does.
    assert len(conflicts) == 1
