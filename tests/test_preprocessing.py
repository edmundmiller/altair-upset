import pandas as pd

from altair_upset.preprocessing import preprocess_data


def test_preprocess_data_basic(sample_data, sample_sets):
    """Test basic preprocessing functionality."""
    data, set_to_abbre, set_to_order, abbre = preprocess_data(
        sample_data, sample_sets, None, "ascending"
    )

    # Check output types
    assert isinstance(data, pd.DataFrame)
    assert isinstance(set_to_abbre, pd.DataFrame)
    assert isinstance(set_to_order, pd.DataFrame)
    assert isinstance(abbre, list)

    # Check if required columns exist
    assert all(
        col in data.columns
        for col in ["count", "intersection_id", "degree", "set", "is_intersect"]
    )

    # Check if abbreviations default to set names when None
    assert abbre == sample_sets


def test_preprocess_data_sorting(sample_data, sample_sets):
    """Test different sorting orders."""
    # Test ascending
    data_asc, _, _, _ = preprocess_data(sample_data, sample_sets, None, "ascending")
    counts_asc = data_asc["count"].unique()
    assert list(counts_asc) == sorted(counts_asc)

    # Test descending
    data_desc, _, _, _ = preprocess_data(sample_data, sample_sets, None, "descending")
    counts_desc = data_desc["count"].unique()
    assert list(counts_desc) == sorted(counts_desc, reverse=True)


def test_preprocess_data_degree_calculation(sample_data, sample_sets):
    """Test if degree is calculated correctly."""
    data, _, _, _ = preprocess_data(sample_data, sample_sets, None, "ascending")
    # Get original row with all sets = 1
    all_ones_row = sample_data[sample_data[sample_sets].sum(axis=1) == len(sample_sets)]
    if not all_ones_row.empty:
        # Find corresponding degree in processed data
        max_degree = data["degree"].max()
        assert max_degree == len(sample_sets)


def test_preprocess_data_empty_input():
    """Test handling of empty input data."""
    empty_df = pd.DataFrame(columns=["set1", "set2"])
    sets = ["set1", "set2"]

    data, set_to_abbre, set_to_order, abbre = preprocess_data(
        empty_df, sets, None, "ascending"
    )
    assert len(data) == 0
    assert len(set_to_abbre) == len(sets)
    assert len(set_to_order) == len(sets)
