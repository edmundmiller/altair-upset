import pytest
import polars as pl
import pandas as pd
from altair_upset.preprocessing import preprocess_data
from altair_upset.upset import UpSetAltair


def test_polars_basic():
    """Test basic functionality with a Polars DataFrame."""
    # Create sample data using Polars
    data = pl.DataFrame(
        {"set1": [1, 0, 1, 0], "set2": [1, 1, 0, 0], "set3": [0, 1, 1, 0]}
    )
    sets = ["set1", "set2", "set3"]

    # Convert to pandas for processing
    pandas_df = data.to_pandas()

    # Process the data
    result, set_to_abbre, set_to_order, abbre = preprocess_data(
        pandas_df, sets, None, "ascending"
    )

    # Check results
    assert len(result) > 0
    assert all(
        col in result.columns for col in ["set", "is_intersect", "count", "degree"]
    )
    assert len(set_to_abbre) == len(sets)
    assert len(set_to_order) == len(sets)


def test_polars_empty():
    """Test handling of empty Polars DataFrame."""
    # Create empty Polars DataFrame
    data = pl.DataFrame(
        {"set1": pl.Series([], dtype=pl.Int64), "set2": pl.Series([], dtype=pl.Int64)}
    )
    sets = ["set1", "set2"]

    # Convert to pandas for processing
    pandas_df = data.to_pandas()

    # Process the data
    result, set_to_abbre, set_to_order, abbre = preprocess_data(
        pandas_df, sets, None, "ascending"
    )

    # Check results
    assert len(result) == 0
    assert len(set_to_abbre) == len(sets)
    assert len(set_to_order) == len(sets)


def test_polars_full_pipeline():
    """Test the full upset plot pipeline with Polars data."""
    # Create sample data using Polars
    data = pl.DataFrame(
        {"set1": [1, 0, 1, 1, 0], "set2": [1, 1, 0, 1, 0], "set3": [0, 1, 1, 1, 0]}
    )
    sets = ["set1", "set2", "set3"]

    # Convert to pandas for processing
    pandas_df = data.to_pandas()

    # Create upset plot
    chart = UpSetAltair(pandas_df, sets)

    # Check that we got a valid Altair chart
    assert chart is not None
    assert hasattr(chart, "to_dict")  # Basic check that it's an Altair chart object


def test_polars_different_dtypes():
    """Test compatibility with different Polars data types."""
    # Create data with different types
    data = pl.DataFrame(
        {
            "set1": pl.Series([True, False, True], dtype=pl.Boolean),
            "set2": pl.Series([1, 0, 1], dtype=pl.Int32),
            "set3": pl.Series([1.0, 0.0, 1.0], dtype=pl.Float64),
        }
    )
    sets = ["set1", "set2", "set3"]

    # Convert to pandas for processing
    pandas_df = data.to_pandas()

    # Process the data
    result, set_to_abbre, set_to_order, abbre = preprocess_data(
        pandas_df, sets, None, "ascending"
    )

    # Check results
    assert len(result) > 0
    assert all(
        col in result.columns for col in ["set", "is_intersect", "count", "degree"]
    )
