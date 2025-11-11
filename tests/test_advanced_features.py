"""Tests for advanced UpSet plot features."""

import altair as alt
import numpy as np
import pandas as pd
import pytest

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


def test_vertical_bar_y_axis_orient_default(sample_data):
    """Test that the default vertical bar y-axis orientation is 'right'."""
    chart = au.UpSetAltair(data=sample_data, sets=["A", "B", "C"])

    # Get the vertical bar chart component (first layer of the first vconcat)
    vertical_bar = chart.chart.vconcat[0]
    first_layer = vertical_bar.layer[0]

    # Check y-axis orientation in the encoding
    encoding_dict = first_layer.encoding.to_dict()
    y_axis_config = encoding_dict["y"]["axis"]
    assert y_axis_config["orient"] == "right"


def test_vertical_bar_y_axis_orient_left(sample_data):
    """Test setting vertical bar y-axis orientation to 'left'."""
    chart = au.UpSetAltair(
        data=sample_data, sets=["A", "B", "C"], vertical_bar_y_axis_orient="left"
    )

    # Get the vertical bar chart component (first layer of the first vconcat)
    vertical_bar = chart.chart.vconcat[0]
    first_layer = vertical_bar.layer[0]

    # Check y-axis orientation in the encoding
    encoding_dict = first_layer.encoding.to_dict()
    y_axis_config = encoding_dict["y"]["axis"]
    assert y_axis_config["orient"] == "left"


def test_vertical_bar_y_axis_orient_right(sample_data):
    """Test setting vertical bar y-axis orientation to 'right'."""
    chart = au.UpSetAltair(
        data=sample_data, sets=["A", "B", "C"], vertical_bar_y_axis_orient="right"
    )

    # Get the vertical bar chart component (first layer of the first vconcat)
    vertical_bar = chart.chart.vconcat[0]
    first_layer = vertical_bar.layer[0]

    # Check y-axis orientation in the encoding
    encoding_dict = first_layer.encoding.to_dict()
    y_axis_config = encoding_dict["y"]["axis"]
    assert y_axis_config["orient"] == "right"


def test_vertical_bar_y_axis_orient_invalid_value(sample_data):
    """Test that invalid values for vertical_bar_y_axis_orient raise ValueError."""
    with pytest.raises(
        ValueError, match="vertical bar y axis orient must be 'left' or 'right'"
    ):
        au.UpSetAltair(
            data=sample_data, sets=["A", "B", "C"], vertical_bar_y_axis_orient="top"
        )

    with pytest.raises(
        ValueError, match="vertical bar y axis orient must be 'left' or 'right'"
    ):
        au.UpSetAltair(
            data=sample_data, sets=["A", "B", "C"], vertical_bar_y_axis_orient="bottom"
        )


def test_highlight_least(sample_data):
    """Test highlighting the intersection with the smallest size."""
    chart = au.UpSetAltair(data=sample_data, sets=["A", "B", "C"], highlight="least")

    # Calculate the expected result independently from the processed data
    processed_data = chart.data
    intersection_counts = (
        processed_data.groupby("intersection_id")["count"]
        .first()
        .reset_index()
    )
    expected_min_id = intersection_counts.loc[
        intersection_counts["count"].idxmin(), "intersection_id"
    ]

    # Extract actual highlighted intersection from chart spec
    spec = chart.chart.to_dict()
    params = spec.get("params", [])

    # Find the color_selection parameter (has intersection_id field)
    color_param = next(
        (p for p in params
         if "select" in p and "fields" in p["select"]
         and "intersection_id" in p["select"]["fields"]
         and "value" in p),
        None
    )

    assert color_param is not None, "No selection parameter with intersection_id found"

    # Verify the correct intersection is highlighted
    actual_ids = [v["intersection_id"] for v in color_param["value"]]
    assert len(actual_ids) == 1, f"Expected 1 highlighted intersection, got {len(actual_ids)}"
    assert actual_ids[0] == expected_min_id, (
        f"Expected intersection {expected_min_id} (smallest), but got {actual_ids[0]}"
    )

    # Verify it's actually the minimum count
    min_count = intersection_counts.loc[
        intersection_counts["intersection_id"] == expected_min_id, "count"
    ].values[0]
    assert min_count == intersection_counts["count"].min(), (
        "Highlighted intersection doesn't have the minimum count"
    )


def test_highlight_greatest(sample_data):
    """Test highlighting the intersection with the largest size."""
    chart = au.UpSetAltair(data=sample_data, sets=["A", "B", "C"], highlight="greatest")

    # Calculate the expected result independently from the processed data
    processed_data = chart.data
    intersection_counts = (
        processed_data.groupby("intersection_id")["count"]
        .first()
        .reset_index()
    )
    expected_max_id = intersection_counts.loc[
        intersection_counts["count"].idxmax(), "intersection_id"
    ]

    # Extract actual highlighted intersection from chart spec
    spec = chart.chart.to_dict()
    params = spec.get("params", [])

    # Find the color_selection parameter
    color_param = next(
        (p for p in params
         if "select" in p and "fields" in p["select"]
         and "intersection_id" in p["select"]["fields"]
         and "value" in p),
        None
    )

    assert color_param is not None, "No selection parameter with intersection_id found"

    # Verify the correct intersection is highlighted
    actual_ids = [v["intersection_id"] for v in color_param["value"]]
    assert len(actual_ids) == 1, f"Expected 1 highlighted intersection, got {len(actual_ids)}"
    assert actual_ids[0] == expected_max_id, (
        f"Expected intersection {expected_max_id} (largest), but got {actual_ids[0]}"
    )

    # Verify it's actually the maximum count
    max_count = intersection_counts.loc[
        intersection_counts["intersection_id"] == expected_max_id, "count"
    ].values[0]
    assert max_count == intersection_counts["count"].max(), (
        "Highlighted intersection doesn't have the maximum count"
    )


def test_highlight_specific_index(sample_data):
    """Test highlighting a specific intersection by index."""
    chart = au.UpSetAltair(data=sample_data, sets=["A", "B", "C"], highlight=0)

    # Calculate the expected result - index 0 should be the first intersection
    processed_data = chart.data
    intersections = (
        processed_data.groupby("intersection_id")["count"]
        .first()
        .reset_index()
        .sort_index()
    )
    expected_id = intersections.iloc[0]["intersection_id"]

    # Extract actual highlighted intersection from chart spec
    spec = chart.chart.to_dict()
    params = spec.get("params", [])

    # Find the color_selection parameter
    color_param = next(
        (p for p in params
         if "select" in p and "fields" in p["select"]
         and "intersection_id" in p["select"]["fields"]
         and "value" in p),
        None
    )

    assert color_param is not None, "No selection parameter with intersection_id found"

    # Verify the correct intersection is highlighted
    actual_ids = [v["intersection_id"] for v in color_param["value"]]
    assert len(actual_ids) == 1, f"Expected 1 highlighted intersection, got {len(actual_ids)}"
    assert actual_ids[0] == expected_id, (
        f"Expected intersection {expected_id} at index 0, but got {actual_ids[0]}"
    )


def test_highlight_multiple_indices(sample_data):
    """Test highlighting multiple intersections by indices."""
    chart = au.UpSetAltair(data=sample_data, sets=["A", "B", "C"], highlight=[0, 1, 2])

    # Calculate the expected results - indices 0, 1, 2
    processed_data = chart.data
    intersections = (
        processed_data.groupby("intersection_id")["count"]
        .first()
        .reset_index()
        .sort_index()
    )
    expected_ids = [
        intersections.iloc[0]["intersection_id"],
        intersections.iloc[1]["intersection_id"],
        intersections.iloc[2]["intersection_id"]
    ]

    # Extract actual highlighted intersections from chart spec
    spec = chart.chart.to_dict()
    params = spec.get("params", [])

    # Find the color_selection parameter
    color_param = next(
        (p for p in params
         if "select" in p and "fields" in p["select"]
         and "intersection_id" in p["select"]["fields"]
         and "value" in p),
        None
    )

    assert color_param is not None, "No selection parameter with intersection_id found"

    # Verify the correct intersections are highlighted
    actual_ids = [v["intersection_id"] for v in color_param["value"]]
    assert len(actual_ids) == 3, f"Expected 3 highlighted intersections, got {len(actual_ids)}"
    assert set(actual_ids) == set(expected_ids), (
        f"Expected intersections {expected_ids}, but got {actual_ids}"
    )


def test_highlight_none_default_hover(sample_data):
    """Test that None (default) enables hover behavior."""
    chart = au.UpSetAltair(data=sample_data, sets=["A", "B", "C"], highlight=None)

    # Get the chart spec and check for mouseover selection
    spec = chart.chart.to_dict()
    params = spec.get("params", [])
    assert len(params) > 0

    # Check that at least one selection has "on" set to "mouseover"
    has_mouseover = any(
        "select" in p and "on" in p["select"] and p["select"]["on"] == "mouseover"
        for p in params
    )
    assert has_mouseover, "Expected to find a selection parameter with mouseover"


def test_highlight_invalid_string(sample_data):
    """Test that invalid string values for highlight raise ValueError."""
    with pytest.raises(ValueError, match="highlight string must be 'least' or 'greatest'"):
        au.UpSetAltair(data=sample_data, sets=["A", "B", "C"], highlight="invalid")


def test_highlight_negative_index(sample_data):
    """Test that negative indices for highlight raise ValueError."""
    with pytest.raises(ValueError, match="highlight index must be non-negative"):
        au.UpSetAltair(data=sample_data, sets=["A", "B", "C"], highlight=-1)


def test_highlight_invalid_list(sample_data):
    """Test that invalid list values for highlight raise ValueError."""
    with pytest.raises(
        ValueError, match="highlight list must contain non-negative integers"
    ):
        au.UpSetAltair(data=sample_data, sets=["A", "B", "C"], highlight=[0, -1, 2])


def test_highlight_invalid_type(sample_data):
    """Test that invalid types for highlight raise TypeError."""
    with pytest.raises(TypeError, match="highlight must be None, str, int, or list of int"):
        au.UpSetAltair(data=sample_data, sets=["A", "B", "C"], highlight=1.5)
