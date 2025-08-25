"""Annotation plots for UpSet visualizations."""

from typing import Any, Dict, List, Optional, Union

import altair as alt
import pandas as pd


class AnnotationSpec:
    """Specification for an annotation plot."""
    
    def __init__(
        self,
        attribute: str,
        plot_type: str,
        height: int = 100,
        title: Optional[str] = None,
        color_by: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize annotation specification.
        
        Parameters
        ----------
        attribute : str
            Name of the attribute to visualize
        plot_type : str
            Type of plot ('boxplot', 'violin', 'strip', 'bar')
        height : int
            Height of the annotation plot in pixels
        title : str, optional
            Title for the annotation plot
        color_by : str, optional
            Attribute to use for color encoding
        **kwargs
            Additional parameters for plot customization
        """
        self.attribute = attribute
        self.plot_type = plot_type
        self.height = height
        self.title = title or attribute.replace('_', ' ').title()
        self.color_by = color_by
        self.kwargs = kwargs


def create_annotation_plot(
    data: pd.DataFrame,
    spec: AnnotationSpec,
    width: int,
    x_sort: alt.Sort,
    main_color: str = "#3A3A3A"
) -> alt.Chart:
    """
    Create an annotation plot based on the specification.
    
    Parameters
    ----------
    data : pd.DataFrame
        Annotation data with intersection_id and attribute values
    spec : AnnotationSpec
        Specification for the annotation plot
    width : int
        Width of the plot
    x_sort : alt.Sort
        Sorting specification for x-axis alignment
    main_color : str
        Default color for the plot
        
    Returns
    -------
    alt.Chart
        Altair chart for the annotation
    """
    # Validate plot type
    supported_types = ['boxplot', 'violin', 'strip', 'bar']
    if spec.plot_type not in supported_types:
        raise ValueError(f"Unsupported annotation type '{spec.plot_type}'. "
                        f"Supported types: {supported_types}")
    
    # Base chart
    base = alt.Chart(data).add_params(
        alt.selection_point(fields=["intersection_id"], on="mouseover")
    )
    
    # Create the appropriate plot type
    if spec.plot_type == 'boxplot':
        chart = create_boxplot_annotation(base, spec, x_sort, main_color)
    elif spec.plot_type == 'violin':
        chart = create_violin_annotation(base, spec, x_sort, main_color)
    elif spec.plot_type == 'strip':
        chart = create_strip_annotation(base, spec, x_sort, main_color)
    elif spec.plot_type == 'bar':
        chart = create_bar_annotation(base, spec, x_sort, main_color)
    else:
        raise ValueError(f"Plot type '{spec.plot_type}' not implemented")
    
    # Configure the chart
    chart = chart.properties(
        width=width,
        height=spec.height,
        title=alt.TitleParams(
            text=spec.title,
            fontSize=12,
            anchor='start'
        )
    ).resolve_scale(
        x='shared'  # Share x-axis with main upset plot
    )
    
    return chart


def create_boxplot_annotation(
    base: alt.Chart,
    spec: AnnotationSpec,
    x_sort: alt.Sort,
    main_color: str
) -> alt.Chart:
    """Create a boxplot annotation."""
    # Determine color encoding
    color_encoding = alt.value(main_color)
    if spec.color_by:
        color_encoding = alt.Color(
            f"{spec.color_by}:N",
            title=spec.color_by.replace('_', ' ').title()
        )
    
    # Configure mark properties based on color encoding
    mark_props = {"size": 30}
    if not spec.color_by:
        mark_props["color"] = main_color
        
    chart = base.mark_boxplot(**mark_props).encode(
        x=alt.X(
            "intersection_id:N",
            axis=alt.Axis(
                labels=False,
                ticks=False,
                grid=False,
                domain=False,
                title=None
            ),
            sort=x_sort
        ),
        y=alt.Y(
            f"{spec.attribute}:Q",
            axis=alt.Axis(
                title=spec.title,
                grid=True,
                tickCount=3
            )
        ),
        color=color_encoding,
        tooltip=[
            alt.Tooltip("intersection_id:N", title="Intersection"),
            alt.Tooltip(f"median({spec.attribute}):Q", title="Median", format=".2f"),
            alt.Tooltip(f"q1({spec.attribute}):Q", title="Q1", format=".2f"),
            alt.Tooltip(f"q3({spec.attribute}):Q", title="Q3", format=".2f"),
        ]
    )
    
    return chart


def create_violin_annotation(
    base: alt.Chart,
    spec: AnnotationSpec,
    x_sort: alt.Sort,
    main_color: str
) -> alt.Chart:
    """Create a violin plot annotation."""
    # For violin plots, we'll use a density transform
    # Note: Altair doesn't have native violin plots, so we approximate with area plots
    
    color_encoding = alt.value(main_color)
    if spec.color_by:
        color_encoding = alt.Color(f"{spec.color_by}:N")
    
    # Create a density estimate for each intersection
    chart = base.transform_density(
        spec.attribute,
        groupby=["intersection_id"],
        as_=[spec.attribute, "density"]
    ).mark_area(
        opacity=0.6,
        interpolate='monotone'
    ).encode(
        x=alt.X(
            "intersection_id:N",
            axis=alt.Axis(
                labels=False,
                ticks=False,
                grid=False,
                domain=False,
                title=None
            ),
            sort=x_sort
        ),
        y=alt.Y(
            f"{spec.attribute}:Q",
            axis=alt.Axis(
                title=spec.title,
                grid=True,
                tickCount=3
            )
        ),
        color=color_encoding,
        tooltip=[
            alt.Tooltip("intersection_id:N", title="Intersection"),
            alt.Tooltip(f"{spec.attribute}:Q", title=spec.title, format=".2f")
        ]
    )
    
    return chart


def create_strip_annotation(
    base: alt.Chart,
    spec: AnnotationSpec,
    x_sort: alt.Sort,
    main_color: str
) -> alt.Chart:
    """Create a strip plot (jittered points) annotation."""
    color_encoding = alt.value(main_color)
    if spec.color_by:
        color_encoding = alt.Color(f"{spec.color_by}:N")
    
    chart = base.mark_circle(
        size=20,
        opacity=0.6
    ).encode(
        x=alt.X(
            "intersection_id:N",
            axis=alt.Axis(
                labels=False,
                ticks=False,
                grid=False,
                domain=False,
                title=None
            ),
            sort=x_sort
        ),
        y=alt.Y(
            f"{spec.attribute}:Q",
            axis=alt.Axis(
                title=spec.title,
                grid=True,
                tickCount=3
            )
        ),
        color=color_encoding,
        tooltip=[
            alt.Tooltip("intersection_id:N", title="Intersection"),
            alt.Tooltip(f"{spec.attribute}:Q", title=spec.title, format=".2f")
        ]
    ).transform_calculate(
        # Add jitter to x position for better visibility
        jittered_x="datum.intersection_id + (random() - 0.5) * 0.4"
    )
    
    return chart


def create_bar_annotation(
    base: alt.Chart,
    spec: AnnotationSpec,
    x_sort: alt.Sort,
    main_color: str
) -> alt.Chart:
    """Create a bar chart annotation for categorical data."""
    # For categorical data, we'll show the most common category per intersection
    
    # Aggregate categorical data by intersection
    chart = base.mark_bar().encode(
        x=alt.X(
            "intersection_id:N",
            axis=alt.Axis(
                labels=False,
                ticks=False,
                grid=False,
                domain=False,
                title=None
            ),
            sort=x_sort
        ),
        y=alt.Y(
            f"count({spec.attribute}):Q",
            axis=alt.Axis(
                title=f"Count of {spec.title}",
                grid=True,
                tickCount=3
            )
        ),
        color=alt.Color(
            f"{spec.attribute}:N",
            title=spec.title
        ) if not spec.color_by else alt.Color(f"{spec.color_by}:N"),
        tooltip=[
            alt.Tooltip("intersection_id:N", title="Intersection"),
            alt.Tooltip(f"{spec.attribute}:N", title=spec.title),
            alt.Tooltip(f"count({spec.attribute}):Q", title="Count")
        ]
    )
    
    return chart


def create_annotation_charts(
    annotation_data: Dict[str, pd.DataFrame],
    annotation_specs: List[AnnotationSpec],
    width: int,
    x_sort: alt.Sort,
    main_color: str = "#3A3A3A"
) -> List[alt.Chart]:
    """
    Create multiple annotation charts.
    
    Parameters
    ----------
    annotation_data : Dict[str, pd.DataFrame]
        Dictionary mapping attribute names to their data
    annotation_specs : List[AnnotationSpec]
        List of annotation specifications
    width : int
        Width for the charts
    x_sort : alt.Sort
        Sorting specification for x-axis alignment
    main_color : str
        Default color for plots
        
    Returns
    -------
    List[alt.Chart]
        List of annotation charts
    """
    charts = []
    
    for spec in annotation_specs:
        if spec.attribute not in annotation_data:
            raise ValueError(
                f"Annotation attribute '{spec.attribute}' not found in data"
            )
        
        data = annotation_data[spec.attribute]
        chart = create_annotation_plot(data, spec, width, x_sort, main_color)
        charts.append(chart)
    
    return charts


def parse_annotation_specs(
    annotations: Union[
        Dict[str, Dict[str, Any]], List[Dict[str, Any]], List[AnnotationSpec]
    ]
) -> List[AnnotationSpec]:
    """
    Parse various annotation specification formats into AnnotationSpec objects.
    
    Parameters
    ----------
    annotations : Union[Dict, List]
        Annotation specifications in various formats
        
    Returns
    -------
    List[AnnotationSpec]
        List of parsed annotation specifications
    """
    if not annotations:
        return []
    
    specs = []
    
    # Handle dictionary format: {'attr': {'type': 'boxplot', ...}}
    if isinstance(annotations, dict):
        for attr, config in annotations.items():
            if isinstance(config, dict):
                plot_type = config.get('type', 'boxplot')
                height = config.get('height', 100)
                title = config.get('title')
                color_by = config.get('color_by')
                kwargs = {k: v for k, v in config.items() 
                         if k not in ['type', 'height', 'title', 'color_by']}
                
                specs.append(AnnotationSpec(
                    attribute=attr,
                    plot_type=plot_type,
                    height=height,
                    title=title,
                    color_by=color_by,
                    **kwargs
                ))
    
    # Handle list format
    elif isinstance(annotations, list):
        for item in annotations:
            if isinstance(item, AnnotationSpec):
                specs.append(item)
            elif isinstance(item, dict):
                if 'attribute' not in item:
                    raise ValueError(
                        "List format requires 'attribute' key in each item"
                    )
                
                attr = item['attribute']
                plot_type = item.get('type', 'boxplot')
                height = item.get('height', 100)
                title = item.get('title')
                color_by = item.get('color_by')
                kwargs = {
                    k: v for k, v in item.items()
                    if k not in ['attribute', 'type', 'height', 'title', 'color_by']
                }
                
                specs.append(AnnotationSpec(
                    attribute=attr,
                    plot_type=plot_type,
                    height=height,
                    title=title,
                    color_by=color_by,
                    **kwargs
                ))
            else:
                raise ValueError(f"Invalid annotation specification: {item}")
    
    else:
        raise ValueError(f"Invalid annotations format: {type(annotations)}")
    
    return specs