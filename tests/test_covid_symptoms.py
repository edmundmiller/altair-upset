import json

from syrupy.extensions.image import PNGImageSnapshotExtension
from syrupy.extensions.json import JSONSnapshotExtension

from altair_upset import UpSetAltair
from tests.conftest import normalize_spec


def test_upset_by_frequency(covid_symptoms_data, output_dir, snapshot):
    """Test UpSet plot sorted by frequency"""
    chart = UpSetAltair(
        data=covid_symptoms_data.copy(),
        title="Symptoms Reported by Users of the COVID Symptom Tracker App",
        subtitle=[
            "Story & Data: https://www.nature.com/articles/d41586-020-00154-w",
            "Altair-based UpSet Plot: https://github.com/hms-dbmi/upset-altair-notebook",
        ],
        sets=[
            "Shortness of Breath",
            "Diarrhea",
            "Fever",
            "Cough",
            "Anosmia",
            "Fatigue",
        ],
        abbre=["B", "D", "Fe", "C", "A", "Fa"],
        sort_by="frequency",
        sort_order="ascending",
    )

    # Save generated spec for debugging
    with open(output_dir / "generated_frequency.vl.json", "w") as f:
        json.dump(chart.chart.to_dict(), f, indent=2)

    # Compare normalized spec with JSON snapshot
    assert normalize_spec(chart.chart.to_dict()) == snapshot(
        name="vega_spec", extension_class=JSONSnapshotExtension
    )

    # Save and compare image snapshot
    chart.save(str(output_dir / "frequency.png"))
    with open(output_dir / "frequency.png", "rb") as f:
        assert f.read() == snapshot(
            name="image", extension_class=PNGImageSnapshotExtension
        )


def test_upset_by_degree(covid_symptoms_data, output_dir, snapshot):
    """Test UpSet plot sorted by degree"""
    chart = UpSetAltair(
        data=covid_symptoms_data.copy(),
        title="Symptoms Reported by Users of the COVID Symptom Tracker App",
        subtitle=[
            "Story & Data: https://www.nature.com/articles/d41586-020-00154-w",
            "Altair-based UpSet Plot: https://github.com/hms-dbmi/upset-altair-notebook",
        ],
        sets=[
            "Shortness of Breath",
            "Diarrhea",
            "Fever",
            "Cough",
            "Anosmia",
            "Fatigue",
        ],
        abbre=["B", "D", "Fe", "C", "A", "Fa"],
        sort_by="degree",
        sort_order="ascending",
    )

    # Save generated spec for debugging
    with open(output_dir / "generated_degree.vl.json", "w") as f:
        json.dump(chart.chart.to_dict(), f, indent=2)

    # Compare normalized spec with JSON snapshot
    assert normalize_spec(chart.chart.to_dict()) == snapshot(
        name="vega_spec", extension_class=JSONSnapshotExtension
    )

    # Save and compare image snapshot
    chart.save(str(output_dir / "degree.png"))
    with open(output_dir / "degree.png", "rb") as f:
        assert f.read() == snapshot(
            name="image", extension_class=PNGImageSnapshotExtension
        )


def test_upset_by_degree_custom(covid_symptoms_data, output_dir, snapshot):
    """Test UpSet plot with custom styling options"""
    chart = UpSetAltair(
        data=covid_symptoms_data.copy(),
        title="Symptoms Reported by Users of the COVID Symptom Tracker App",
        subtitle=[
            "Story & Data: https://www.nature.com/articles/d41586-020-00154-w",
            "Altair-based UpSet Plot: https://github.com/hms-dbmi/upset-altair-notebook",
        ],
        sets=[
            "Shortness of Breath",
            "Diarrhea",
            "Fever",
            "Cough",
            "Anosmia",
            "Fatigue",
        ],
        abbre=["B", "D", "Fe", "C", "A", "Fa"],
        sort_by="degree",
        sort_order="ascending",
        # Custom options:
        width=900,
        height=500,
        height_ratio=0.65,
        color_range=["#F0E442", "#E69F00", "#D55E00", "#CC79A7", "#0072B2", "#56B4E9"],
        highlight_color="#777",
        horizontal_bar_chart_width=200,
        glyph_size=100,
        set_label_bg_size=650,
        line_connection_size=1,
        horizontal_bar_size=16,
        vertical_bar_label_size=12,
    )

    # Save generated spec for debugging
    with open(output_dir / "generated_degree_custom.vl.json", "w") as f:
        json.dump(chart.chart.to_dict(), f, indent=2)

    # Compare normalized spec with JSON snapshot
    assert normalize_spec(chart.chart.to_dict()) == snapshot(
        name="vega_spec", extension_class=JSONSnapshotExtension
    )

    # Save and compare image snapshot
    chart.save(str(output_dir / "degree_custom.png"))
    with open(output_dir / "degree_custom.png", "rb") as f:
        assert f.read() == snapshot(
            name="image", extension_class=PNGImageSnapshotExtension
        )
