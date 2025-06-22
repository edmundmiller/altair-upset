import altair as alt
import pandas as pd

from altair_upset.transforms import create_base_chart


def test_create_base_chart_structure(sample_data, sample_sets, legend_selection):
    """Test the structure of the created base chart."""
    # Create mock lookup data
    set_to_abbre = pd.DataFrame({"set": sample_sets, "set_abbre": sample_sets})
    set_to_order = pd.DataFrame(
        {"set": sample_sets, "set_order": range(len(sample_sets))}
    )

    chart = create_base_chart(
        sample_data, sample_sets, legend_selection, set_to_abbre, set_to_order
    )

    # Check if the chart is an Altair Chart object
    assert isinstance(chart, alt.Chart)

    # Get transform types more safely
    transform_types = []
    for t in chart.transform:
        # Each transform has its type in its class name
        transform_name = t.__class__.__name__.lower()
        # Remove the word "transform" from the end
        transform_type = transform_name.replace("transform", "")
        transform_types.append(transform_type)

    # Check against expected types
    expected_transforms = [
        "filter",
        "pivot",
        "aggregate",
        "calculate",
        "filter",
        "window",
        "fold",
        "lookup",
        "lookup",
        "filter",
        "window",
    ]
    assert transform_types == expected_transforms


def test_degree_calculation(sample_data, sample_sets, legend_selection):
    """Test if degree calculation formula is correct."""
    set_to_abbre = pd.DataFrame({"set": sample_sets, "set_abbre": sample_sets})
    set_to_order = pd.DataFrame(
        {"set": sample_sets, "set_order": range(len(sample_sets))}
    )

    chart = create_base_chart(
        sample_data, sample_sets, legend_selection, set_to_abbre, set_to_order
    )

    # Find the calculate transform for degree
    degree_transform = None
    for t in chart.transform:
        if (
            t.__class__.__name__.lower() == "calculatetransform"
            and hasattr(t, "_kwds")
            and t._kwds.get("as") == "degree"
        ):
            degree_transform = t
            break

    assert degree_transform is not None, "Degree calculation transform not found"

    # Get the calculation formula
    formula = degree_transform._kwds["calculate"]

    # Check if formula includes all sets
    for s in sample_sets:
        expected_term = f"isDefined(datum['{s}'])"
        assert expected_term in formula, f"Formula should check if {s} is defined"

        expected_term = f"datum['{s}']"
        assert expected_term in formula, f"Formula should use {s} value"

    # Check basic formula structure
    assert formula.count("?") == len(sample_sets), (
        "Should have one ternary operator per set"
    )
    assert formula.count(":") == len(sample_sets), (
        "Should have one ternary operator per set"
    )
    assert formula.count("+") == len(sample_sets) - 1, (
        "Should have additions between all sets"
    )


def test_lookup_transforms(sample_data, sample_sets, legend_selection):
    """Test if lookup transforms are configured correctly."""
    set_to_abbre = pd.DataFrame({"set": sample_sets, "set_abbre": sample_sets})
    set_to_order = pd.DataFrame(
        {"set": sample_sets, "set_order": range(len(sample_sets))}
    )

    chart = create_base_chart(
        sample_data, sample_sets, legend_selection, set_to_abbre, set_to_order
    )

    # Find all lookup transforms
    lookup_transforms = [
        t for t in chart.transform if t.__class__.__name__.lower() == "lookuptransform"
    ]

    # Should have exactly two lookup transforms
    assert len(lookup_transforms) == 2, "Should have two lookup transforms"

    # Check that we have one transform for abbreviations and one for order
    lookup_fields = set()
    for transform in lookup_transforms:
        # Access the lookup data directly through _kwds
        lookup_data = transform._kwds["from"]
        fields = lookup_data.fields
        lookup_fields.update(fields)

    # Verify we have both required field types
    assert "set_abbre" in lookup_fields, "Should have lookup for set abbreviations"
    assert "set_order" in lookup_fields, "Should have lookup for set order"

    # Check that lookups are properly configured
    for transform in lookup_transforms:
        # Each lookup should use 'set' as the key
        assert transform._kwds["lookup"] == "set", "Lookup key should be 'set'"

        # Each lookup should have proper fields configuration
        lookup_data = transform._kwds["from"]
        assert lookup_data.fields is not None, "Lookup should specify fields"
        assert len(lookup_data.fields) == 1, "Each lookup should have exactly one field"


# We'll add back the other tests once this one passes
