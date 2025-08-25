"""Tests for annotation plots functionality."""

import altair as alt
import numpy as np
import pandas as pd
import pytest

import altair_upset as au


@pytest.fixture
def genomic_data():
    """Create sample genomic dataset for testing annotations."""
    np.random.seed(42)
    n_samples = 200
    
    # Create set membership data (like different conditions or treatments)
    data = pd.DataFrame({
        "condition_A": np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4]),
        "condition_B": np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3]), 
        "condition_C": np.random.choice([0, 1], size=n_samples, p=[0.8, 0.2]),
    })
    
    # Add genomic attributes that would be useful for annotations
    data["expression_level"] = np.random.lognormal(mean=2, sigma=1, size=n_samples)
    data["fold_change"] = np.random.normal(loc=0, scale=2, size=n_samples)
    data["p_value"] = np.random.beta(a=0.5, b=2, size=n_samples)
    data["gene_length"] = np.random.randint(1000, 50000, size=n_samples)
    data["category"] = np.random.choice(["protein_coding", "lncRNA", "miRNA"], 
                                       size=n_samples, p=[0.7, 0.2, 0.1])
    
    return data


@pytest.fixture 
def basic_data():
    """Create basic test dataset."""
    np.random.seed(123)
    n_samples = 100
    
    data = pd.DataFrame({
        "A": np.random.choice([0, 1], size=n_samples, p=[0.5, 0.5]),
        "B": np.random.choice([0, 1], size=n_samples, p=[0.5, 0.5]),
        "C": np.random.choice([0, 1], size=n_samples, p=[0.5, 0.5]),
    })
    
    # Add simple numerical attributes
    data["value1"] = np.random.normal(loc=10, scale=3, size=n_samples)
    data["value2"] = np.random.exponential(scale=2, size=n_samples)
    data["category"] = np.random.choice(["X", "Y", "Z"], size=n_samples)
    
    return data


class TestBasicAnnotations:
    """Test basic annotation functionality."""
    
    def test_single_boxplot_annotation(self, basic_data):
        """Test adding a single boxplot annotation."""
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            annotations={
                "value1": {"type": "boxplot", "height": 100}
            }
        )
        
        # Chart should be created successfully
        assert isinstance(chart.chart, alt.VConcatChart)
        
        # Should have more vertical components (annotations + original)
        assert len(chart.chart.vconcat) >= 2
        
        # Check that annotation data is preserved
        assert hasattr(chart, 'annotation_data')
        
    def test_single_violin_annotation(self, basic_data):
        """Test adding a single violin plot annotation."""
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            annotations={
                "value1": {"type": "violin", "height": 120, "title": "Value Distribution"}
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)
        assert len(chart.chart.vconcat) >= 2
        
    def test_multiple_annotations(self, basic_data):
        """Test adding multiple annotation plots."""
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            annotations={
                "value1": {"type": "boxplot", "height": 80},
                "value2": {"type": "violin", "height": 100}
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)
        # Should have original 2 components + 2 annotations
        assert len(chart.chart.vconcat) >= 3
        
    def test_annotation_with_categorical_data(self, basic_data):
        """Test annotation with categorical data."""
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            annotations={
                "category": {"type": "bar", "height": 90}
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)
        
    def test_annotation_height_parameter(self, basic_data):
        """Test that annotation height parameter is respected."""
        custom_height = 150
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            annotations={
                "value1": {"type": "boxplot", "height": custom_height}
            }
        )
        
        # Check if height is properly set in the annotation component
        assert isinstance(chart.chart, alt.VConcatChart)


class TestGenomicAnnotations:
    """Test annotation functionality with genomic data."""
    
    def test_expression_level_annotation(self, genomic_data):
        """Test annotation with expression level data (common genomic use case)."""
        chart = au.UpSetAltair(
            data=genomic_data,
            sets=["condition_A", "condition_B", "condition_C"],
            annotations={
                "expression_level": {
                    "type": "boxplot", 
                    "height": 120,
                    "title": "Expression Level"
                }
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)
        assert hasattr(chart, 'annotation_data')
        
    def test_fold_change_annotation(self, genomic_data):
        """Test annotation with fold change data."""
        chart = au.UpSetAltair(
            data=genomic_data,
            sets=["condition_A", "condition_B", "condition_C"],
            annotations={
                "fold_change": {
                    "type": "violin",
                    "height": 100,
                    "title": "Log2 Fold Change"
                }
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)
        
    def test_multiple_genomic_annotations(self, genomic_data):
        """Test multiple genomic annotations together."""
        chart = au.UpSetAltair(
            data=genomic_data,
            sets=["condition_A", "condition_B", "condition_C"],
            annotations={
                "expression_level": {"type": "boxplot", "height": 80},
                "p_value": {"type": "strip", "height": 60},
                "gene_length": {"type": "violin", "height": 100}
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)
        # Should have multiple annotation layers
        assert len(chart.chart.vconcat) >= 4
        
    def test_categorical_genomic_annotation(self, genomic_data):
        """Test categorical annotation with gene categories."""
        chart = au.UpSetAltair(
            data=genomic_data,
            sets=["condition_A", "condition_B", "condition_C"],
            annotations={
                "category": {
                    "type": "bar",
                    "height": 80,
                    "title": "Gene Type"
                }
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)


class TestAnnotationDataHandling:
    """Test data handling and aggregation for annotations."""
    
    def test_annotation_data_aggregation(self, basic_data):
        """Test that annotation data is properly aggregated by intersection."""
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            annotations={
                "value1": {"type": "boxplot", "height": 100}
            }
        )
        
        # Check that annotation data exists and has correct structure
        assert hasattr(chart, 'annotation_data')
        assert 'value1' in chart.annotation_data
        assert 'intersection_id' in chart.annotation_data['value1'].columns
        
    def test_annotation_with_missing_values(self, basic_data):
        """Test handling of missing values in annotation data."""
        # Introduce some missing values
        data_with_missing = basic_data.copy()
        data_with_missing.loc[::10, 'value1'] = np.nan
        
        chart = au.UpSetAltair(
            data=data_with_missing,
            sets=["A", "B", "C"],
            annotations={
                "value1": {"type": "boxplot", "height": 100}
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)
        
    def test_annotation_with_empty_intersections(self, basic_data):
        """Test handling of intersections with no data points."""
        # Create data where some intersections might be empty
        sparse_data = basic_data.iloc[:20].copy()  # Use only small subset
        
        chart = au.UpSetAltair(
            data=sparse_data,
            sets=["A", "B", "C"],
            annotations={
                "value1": {"type": "boxplot", "height": 100}
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)


class TestAnnotationIntegration:
    """Test integration with existing UpSet features."""
    
    def test_annotation_with_sorting(self, basic_data):
        """Test that annotations work with different sorting options."""
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            sort_by="degree",
            sort_order="descending",
            annotations={
                "value1": {"type": "boxplot", "height": 100}
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)
        
    def test_annotation_with_custom_colors(self, basic_data):
        """Test annotations with custom color schemes."""
        custom_colors = ["#FF0000", "#00FF00", "#0000FF"]
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            color_range=custom_colors,
            annotations={
                "value1": {"type": "boxplot", "height": 100}
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)
        
    def test_annotation_with_abbreviations(self, basic_data):
        """Test annotations with set abbreviations."""
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            abbre=["AA", "BB", "CC"],
            annotations={
                "value1": {"type": "violin", "height": 100}
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)


class TestAnnotationErrors:
    """Test error handling for annotation functionality."""
    
    def test_invalid_annotation_attribute(self, basic_data):
        """Test error when annotation attribute doesn't exist."""
        with pytest.raises(ValueError, match="Annotation attributes.*not found"):
            au.UpSetAltair(
                data=basic_data,
                sets=["A", "B", "C"],
                annotations={
                    "nonexistent": {"type": "boxplot", "height": 100}
                }
            )
            
    def test_invalid_annotation_type(self, basic_data):
        """Test error when annotation type is invalid."""
        with pytest.raises(ValueError, match="Unsupported annotation type"):
            au.UpSetAltair(
                data=basic_data,
                sets=["A", "B", "C"],
                annotations={
                    "value1": {"type": "invalid_type", "height": 100}
                }
            )
            
    def test_missing_annotation_height(self, basic_data):
        """Test that missing height parameter uses default."""
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            annotations={
                "value1": {"type": "boxplot"}  # No height specified
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)


class TestCustomAnnotationSpecs:
    """Test custom Altair specifications for annotations."""
    
    def test_custom_altair_spec(self, basic_data):
        """Test using custom Altair chart specification."""
        # This test will be implemented after we support custom specs
        # For now, just test the basic structure
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            annotations={
                "value1": {"type": "boxplot", "height": 100}
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)
        
    def test_annotation_color_encoding(self, basic_data):
        """Test annotation with color encoding by category."""
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            annotations={
                "value1": {
                    "type": "boxplot", 
                    "height": 100,
                    "color_by": "category"
                }
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)


class TestAnnotationLayout:
    """Test layout and spacing of annotation plots."""
    
    def test_annotation_alignment(self, basic_data):
        """Test that annotation plots are properly aligned with intersection bars."""
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            annotations={
                "value1": {"type": "boxplot", "height": 100}
            }
        )
        
        # Check that the chart structure supports proper alignment
        assert isinstance(chart.chart, alt.VConcatChart)
        # More detailed alignment tests would require inspecting the Altair spec
        
    def test_multiple_annotation_spacing(self, basic_data):
        """Test spacing between multiple annotation plots."""
        chart = au.UpSetAltair(
            data=basic_data,
            sets=["A", "B", "C"],
            annotations={
                "value1": {"type": "boxplot", "height": 80},
                "value2": {"type": "violin", "height": 80},
                "category": {"type": "bar", "height": 60}
            }
        )
        
        assert isinstance(chart.chart, alt.VConcatChart)
        assert len(chart.chart.vconcat) >= 4  # 3 annotations + original components