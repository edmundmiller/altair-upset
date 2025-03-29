"""Tests for advanced UpSet plot features."""

import pytest
import pandas as pd
import numpy as np
import altair as alt
import altair_upset as au


@pytest.fixture
def sample_data():
    """Create sample dataset for testing."""
    np.random.seed(42)
    n_samples = 100

    # Create set membership data
    data = pd.DataFrame(
        {
            "A": np.random.choice([0, 1], size=n_samples, p=[0.3, 0.7]),
            "B": np.random.choice([0, 1], size=n_samples, p=[0.4, 0.6]),
            "C": np.random.choice([0, 1], size=n_samples, p=[0.5, 0.5]),
        }
    )

    # Add set-specific attributes
    data["set_size"] = data.sum(axis=1)  # Number of sets each element belongs to

    return data


@pytest.fixture
def basic_chart(sample_data):
    """Create basic UpSet chart for testing."""
    return au.UpSetAltair(data=sample_data, sets=["A", "B", "C"], title="Test Chart")


def test_basic_chart_structure(basic_chart):
    """Test that the basic chart has all required components."""
    # The chart should be a VConcatChart (vertical concatenation)
    assert isinstance(basic_chart.chart, alt.VConcatChart)

    # Should have intersection matrix and bar charts
    assert len(basic_chart.chart.vconcat) == 2  # Vertical components
    assert isinstance(
        basic_chart.chart.vconcat[1], alt.HConcatChart
    )  # Horizontal components


def test_set_size_encoding(basic_chart):
    """Test that set sizes are correctly encoded."""
    # Get the horizontal bar chart component
    hconcat = basic_chart.chart.vconcat[1]
    horizontal_bar = hconcat.hconcat[-1]

    # Check encoding - need to convert to dict to access field values
    encoding_dict = horizontal_bar.encoding.to_dict()
    assert encoding_dict["x"]["field"] == "count"
    assert encoding_dict["y"]["field"] == "set_order"


def test_intersection_encoding(basic_chart):
    """Test that intersections are correctly encoded."""
    # Get the matrix view component
    hconcat = basic_chart.chart.vconcat[1]
    matrix = hconcat.hconcat[0]

    # Convert encodings to dict for checking
    encoding_dict = matrix.layer[
        0
    ].encoding.to_dict()  # Use first layer for matrix encodings
    assert encoding_dict["x"]["field"] == "intersection_id"
    assert encoding_dict["y"]["field"] == "set_order"


def test_interactive_legend(basic_chart):
    """Test that the chart has interactive legend selection."""
    # Check for legend selection parameter
    params = basic_chart.chart.params
    assert any("legend" in str(p) for p in params)


def test_hover_interaction(basic_chart):
    """Test that the chart has hover interactions."""
    # Get the matrix view component
    hconcat = basic_chart.chart.vconcat[1]
    matrix = hconcat.hconcat[0]

    # Check for tooltips in any layer of the matrix
    has_tooltip = False
    for layer in matrix.layer:
        if hasattr(layer, "encoding"):
            encoding_dict = layer.encoding.to_dict()
            if "tooltip" in encoding_dict:
                has_tooltip = True
                break

    assert has_tooltip, "No tooltip found in matrix view"


def test_sort_by_frequency(sample_data):
    """Test sorting intersections by frequency."""
    chart = au.UpSetAltair(
        data=sample_data,
        sets=["A", "B", "C"],
        sort_by="frequency",
        sort_order="descending",
    )

    # Get the matrix view component
    matrix_view = chart.chart.vconcat[1].hconcat[0]

    # Check sort configuration in the first layer
    encoding_dict = matrix_view.layer[0].encoding.to_dict()
    sort_config = encoding_dict["x"].get("sort", {})

    assert sort_config.get("field") == "count"
    assert sort_config.get("order") == "descending"


def test_sort_by_degree(sample_data):
    """Test sorting intersections by degree."""
    chart = au.UpSetAltair(
        data=sample_data, sets=["A", "B", "C"], sort_by="degree", sort_order="ascending"
    )

    # Get the matrix view component
    matrix_view = chart.chart.vconcat[1].hconcat[0]

    # Check sort configuration in the first layer
    encoding_dict = matrix_view.layer[0].encoding.to_dict()
    sort_config = encoding_dict["x"].get("sort", {})

    assert sort_config.get("field") == "degree"
    assert sort_config.get("order") == "ascending"


def test_custom_colors(sample_data):
    """Test applying custom colors to the chart."""
    custom_colors = ["#FF0000", "#00FF00", "#0000FF"]
    chart = au.UpSetAltair(
        data=sample_data, sets=["A", "B", "C"], color_range=custom_colors
    )

    # Check that custom colors are applied
    hconcat = chart.chart.vconcat[1]
    horizontal_bar = hconcat.hconcat[-1]
    assert "scale" in str(horizontal_bar.encoding.color)
    assert all(color in str(horizontal_bar.encoding.color) for color in custom_colors)
