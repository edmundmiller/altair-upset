from typing import List, Literal, Optional, Union

import altair as alt
import pandas as pd

from .components import (
    create_horizontal_bar,
    create_horizontal_cardinality_bar,
    create_matrix_view,
    create_vertical_bar,
    create_vertical_matrix,
    create_vertical_set_bars,
)
from .config import upsetaltair_top_level_configuration
from .preprocessing import preprocess_data
from .transforms import create_base_chart


def _determine_highlighted_intersections(
    data: pd.DataFrame,
    highlight: Union[Literal["least", "greatest"], int, List[int]],
) -> List[float]:
    """Determine which intersection IDs to highlight based on the highlight parameter.

    Parameters
    ----------
    data : pd.DataFrame
        The preprocessed data with intersection_id and count columns
    highlight : "least", "greatest", int, or list of int
        The highlighting criteria

    Returns
    -------
    list of float
        List of intersection_ids to highlight

    Raises
    ------
    IndexError
        If a single integer index is out of bounds
    ValueError
        If any index in a list is out of bounds
    """
    # Get unique intersections with their counts
    intersections = (
        data.groupby("intersection_id")["count"].first().reset_index().sort_index()
    )

    if isinstance(highlight, str):
        if highlight == "least":
            min_idx = intersections["count"].idxmin()
            return [intersections.loc[min_idx, "intersection_id"]]
        else:  # highlight == "greatest"
            max_idx = intersections["count"].idxmax()
            return [intersections.loc[max_idx, "intersection_id"]]
    elif isinstance(highlight, int):
        if highlight >= len(intersections):
            raise IndexError(
                f"highlight index {highlight} is out of bounds for "
                f"{len(intersections)} intersections"
            )
        return [intersections.iloc[highlight]["intersection_id"]]
    else:  # isinstance(highlight, list)
        # Validate all indices first
        invalid_indices = [i for i in highlight if i >= len(intersections)]
        if invalid_indices:
            raise ValueError(
                f"highlight indices {invalid_indices} are out of bounds for "
                f"{len(intersections)} intersections"
            )
        return [intersections.iloc[i]["intersection_id"] for i in highlight]


class UpSetChart:
    """A wrapper class for UpSet plots."""

    def __init__(self, chart, data, sets):
        """Initialize the UpSetChart.

        Parameters
        ----------
        chart : alt.Chart
            The base Altair chart
        data : pd.DataFrame
            The input data
        sets : list
            List of set names
        """
        self.chart = chart
        self.data = data
        self.sets = sets

    def save(self, filename):
        """Save the chart to a file."""
        self.chart.save(filename)

    def properties(self, **kwargs):
        """Update chart properties."""
        self.chart = self.chart.properties(**kwargs)
        return self

    def configure_axis(self, **kwargs):
        """Configure chart axes."""
        self.chart = self.chart.configure_axis(**kwargs)
        return self

    def configure_legend(self, **kwargs):
        """Configure chart legend."""
        self.chart = self.chart.configure_legend(**kwargs)
        return self

    def to_dict(self):
        """Convert the chart to a dictionary representation.

        Returns
        -------
        dict
            The Vega-Lite specification as a Python dictionary
        """
        return self.chart.to_dict()

    def __getattr__(self, name):
        """Delegate unknown attributes to the underlying chart."""
        return getattr(self.chart, name)


def UpSetAltair(
    data: pd.DataFrame,
    sets: List[str],
    *,
    title: str = "",
    subtitle: Union[str, List[str]] = "",
    abbre: Optional[List[str]] = None,
    sort_by: str = "frequency",
    sort_order: str = "ascending",
    width: int = 1200,
    height: int = 700,
    height_ratio: float = 0.6,
    horizontal_bar_chart_width: Optional[int] = None,
    color_range: List[str] = [
        "#55A8DB",
        "#3070B5",
        "#30363F",
        "#F1AD60",
        "#DF6234",
        "#BDC6CA",
    ],
    highlight_color: str = "#EA4667",
    highlight: Optional[Union[Literal["least", "greatest"], int, List[int]]] = None,
    glyph_size: int = 100,  # Reduced from 200
    set_label_bg_size: int = 500,  # Reduced from 1000
    line_connection_size: int = 1,  # Reduced from 2
    horizontal_bar_size: int = 20,
    vertical_bar_label_size: int = 16,
    vertical_bar_y_axis_orient: str = "right",
    theme: Optional[str] = None,
) -> UpSetChart:
    """Generate interactive UpSet plots using Altair. [Lex et al., 2014]_

    UpSet plots are used to visualize set intersections in a more scalable way
    than Venn diagrams. This implementation provides interactive features like
    hover highlighting and legend filtering.

    Parameters
    ----------
    data : pandas.DataFrame
        Input data where each column represents a set and contains binary
        values (0 or 1).
        Each row represents an element, and the columns indicate set membership.
    sets : list of str
        Names of the sets to visualize (must correspond to column names in data).
    title : str, default ""
        Title of the plot.
    subtitle : str or list of str, default ""
        Subtitle(s) of the plot. Can be a single string or list of strings
        for multiple lines.
    abbre : list of str, optional
        Abbreviations for set names (must have same length as sets).
    sort_by : {"frequency", "degree"}, default "frequency"
        Method to sort the intersections:
        - "frequency": sort by intersection size
        - "degree": sort by number of sets in intersection
    sort_order : {"ascending", "descending"}, default "ascending"
        Order of sorting for intersections.
    width : int, default 1200
        Total width of the plot in pixels.
    height : int, default 700
        Total height of the plot in pixels.
    height_ratio : float, default 0.6
        Ratio of vertical bar chart height to total height (between 0 and 1).
    horizontal_bar_chart_width : int, default 300
        Width of the horizontal bar chart in pixels.
    color_range : list of str
        List of colors for the sets. Defaults to a colorblind-friendly palette.
    highlight_color : str, default "#EA4667"
        Color used for highlighting on hover or programmatic highlighting.
    highlight : str, int, or list of int, optional
        Specifies which intersections to highlight programmatically:
        - None (default): interactive hover highlighting
        - "least": highlight the intersection with the smallest size
        - "greatest": highlight the intersection with the largest size
        - int: highlight the intersection at the specified index (0-based)
        - list of int: highlight multiple intersections by their indices
    glyph_size : int, default 200
        Size of the matrix glyphs in pixels.
    set_label_bg_size : int, default 1000
        Size of the set label background circles.
    line_connection_size : int, default 2
        Thickness of connecting lines in pixels.
    horizontal_bar_size : int, default 20
        Height of horizontal bars in pixels.
    vertical_bar_label_size : int, default 16
        Font size of vertical bar labels.
    vertical_bar_y_axis_orient : str, default "right"
        Whether to show the vertical bar chart Y axis on the right or left of the plot.
    theme : str, optional
        Altair theme to use. If None, uses the current default theme.

    Returns
    -------
    altair.Chart
        An Altair chart object representing the UpSet plot.

    Examples
    --------
    >>> import altair_upset as au
    >>> import pandas as pd
    >>> data = pd.DataFrame({
    ...     'set1': [1, 0, 1],
    ...     'set2': [1, 1, 0],
    ...     'set3': [0, 1, 1]
    ... })
    >>> chart = au.UpSetAltair(
    ...     data=data,
    ...     sets=["set1", "set2", "set3"],
    ...     title="Sample UpSet Plot"
    ... )

    Notes
    -----
    The plot consists of three main components:
    1. A matrix view showing set intersections
    2. A vertical bar chart showing intersection sizes
    3. A horizontal bar chart showing set sizes

    References
    ----------
    .. [Lex et al., 2014] Alexander Lex, Nils Gehlenborg, Hendrik Strobelt,
                Romain Vuillemot, Hanspeter Pfister.
                UpSet: Visualization of Intersecting Sets
                IEEE transactions on visualization and computer graphics,
                20(12), 1983-1992.
    """
    # Input validation
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    if not isinstance(sets, list) or not all(isinstance(s, str) for s in sets):
        raise TypeError("sets must be a list of strings")
    if not all(s in data.columns for s in sets):
        raise ValueError("all sets must be columns in data")
    if not all(data[s].isin([0, 1]).all() for s in sets):
        raise ValueError("all set columns must contain only 0s and 1s")
    if height_ratio <= 0 or height_ratio >= 1:
        raise ValueError("height_ratio must be between 0 and 1")
    if sort_by not in ["frequency", "degree"]:
        raise ValueError("sort_by must be either 'frequency' or 'degree'")
    if sort_order not in ["ascending", "descending"]:
        raise ValueError("sort_order must be either 'ascending' or 'descending'")
    if abbre is not None and len(sets) != len(abbre):
        raise ValueError("if provided, abbre must have the same length as sets")
    if vertical_bar_y_axis_orient not in ["left", "right"]:
        raise ValueError("vertical bar y axis orient must be 'left' or 'right'")
    if highlight is not None:
        if isinstance(highlight, str):
            if highlight not in ["least", "greatest"]:
                raise ValueError("highlight string must be 'least' or 'greatest'")
        elif isinstance(highlight, int):
            if highlight < 0:
                raise ValueError("highlight index must be non-negative")
        elif isinstance(highlight, list):
            if not all(isinstance(i, int) and i >= 0 for i in highlight):
                raise ValueError("highlight list must contain non-negative integers")
        else:
            raise TypeError("highlight must be None, str, int, or list of int")

    # Apply theme if specified
    if theme is not None:
        alt.themes.enable(theme)

    # Preprocess data
    data, set_to_abbre, set_to_order, abbre = preprocess_data(
        data, sets, abbre, sort_order
    )

    # Setup selections for interactivity
    legend_selection = alt.selection_point(fields=["set"], bind="legend")

    # Setup color selection based on highlight parameter
    if highlight is None:
        # Default hover behavior
        color_selection = alt.selection_point(
            fields=["intersection_id"], on="mouseover"
        )
    else:
        # Determine which intersections to highlight and create fixed selection
        highlighted_ids = _determine_highlighted_intersections(data, highlight)
        color_selection = alt.selection_point(
            fields=["intersection_id"],
            value=[{"intersection_id": id_} for id_ in highlighted_ids],
        )

    # Calculate dimensions
    if horizontal_bar_chart_width is None:
        horizontal_bar_chart_width = int(width * 0.15)  # Make it 25% of total width
    vertical_bar_chart_height = height * height_ratio
    matrix_height = (
        height - vertical_bar_chart_height
    ) * 0.8  # Reduce height to tighten spacing
    matrix_width = width - horizontal_bar_chart_width

    # Automatic padding
    num_intersections = max(1, len(data["intersection_id"].unique().tolist()))
    vertical_bar_size = min(30, (matrix_width / num_intersections) - 5)  # 5 is good

    # Setup styles
    main_color = "#3A3A3A"
    brush_color = alt.condition(
        ~color_selection, alt.value(main_color), alt.value(highlight_color)
    )
    is_show_horizontal_bar_label_bg = len(abbre[0]) <= 2 if abbre else True
    horizontal_bar_label_bg_color = (
        "white" if is_show_horizontal_bar_label_bg else "black"
    )
    x_sort = alt.Sort(
        field="count" if sort_by == "frequency" else "degree", order=sort_order
    )
    tooltip = [
        alt.Tooltip("count:Q", title="Cardinality"),
        alt.Tooltip("degree:Q", title="Degree"),
        # alt.Tooltip("sets_graph:N", title="Groups"),  # Bugged. sets_graph
        # is already available in preprocessing.py
    ]

    # Create base chart
    base = create_base_chart(data, sets, legend_selection, set_to_abbre, set_to_order)

    # Create components
    vertical_bar, vertical_bar_text = create_vertical_bar(
        base,
        matrix_width,
        vertical_bar_chart_height,
        main_color,
        vertical_bar_size,
        brush_color,
        x_sort,
        tooltip,
        vertical_bar_label_size,
        vertical_bar_y_axis_orient,
    )
    vertical_bar_chart = (
        (vertical_bar + vertical_bar_text)
        .add_params(color_selection)
        .properties(width=matrix_width, height=vertical_bar_chart_height)
    )

    circle_bg, rect_bg, circle, line_connection = create_matrix_view(
        vertical_bar,
        matrix_height,
        glyph_size,
        x_sort,
        brush_color,
        line_connection_size,
        main_color,
    )
    matrix_view = (
        (circle + rect_bg + circle_bg + line_connection + circle)
        .add_params(color_selection)
        .properties(width=matrix_width)
    )

    horizontal_bar_label_bg, horizontal_bar_label, horizontal_bar = (
        create_horizontal_bar(
            base,
            set_label_bg_size,
            sets,
            color_range,
            is_show_horizontal_bar_label_bg,
            horizontal_bar_label_bg_color,
            horizontal_bar_size,
            horizontal_bar_chart_width,
        )
    )
    horizontal_bar_axis = (
        (horizontal_bar_label_bg + horizontal_bar_label)
        if is_show_horizontal_bar_label_bg
        else horizontal_bar_label
    ).properties(width=horizontal_bar_chart_width)

    # Combine components
    upsetaltair = alt.vconcat(
        vertical_bar_chart,
        alt.hconcat(
            matrix_view,
            horizontal_bar_axis,
            horizontal_bar.properties(width=horizontal_bar_chart_width),
            spacing=0,
        ).resolve_scale(x="shared", y="shared"),
        spacing=5,
    ).add_params(legend_selection)

    # Apply configuration
    chart = upsetaltair_top_level_configuration(
        upsetaltair, legend_orient="top", legend_symbol_size=set_label_bg_size / 2.0
    ).properties(
        title={
            "text": title,
            "subtitle": subtitle,
            "fontSize": 20,
            "fontWeight": 500,
            "subtitleColor": main_color,
            "subtitleFontSize": 14,
        }
    )

    return UpSetChart(chart, data, sets)


def UpSetVertical(
    data: pd.DataFrame,
    sets: List[str],
    *,
    title: str = "",
    subtitle: Union[str, List[str]] = "",
    abbre: Optional[List[str]] = None,
    sort_by: str = "frequency",
    sort_order: str = "ascending",
    width: int = 1200,
    height: int = 700,
    height_ratio: float = 0.4,
    color_range: List[str] = [
        "#55A8DB",
        "#3070B5",
        "#30363F",
        "#F1AD60",
        "#DF6234",
        "#BDC6CA",
    ],
    highlight_color: str = "#EA4667",
    highlight: Optional[Union[Literal["least", "greatest"], int, List[int]]] = None,
    glyph_size: int = 100,
    set_label_bg_size: int = 500,
    line_connection_size: int = 1,
    set_bar_size: int = 30,
    cardinality_bar_width: Optional[int] = None,
    cardinality_bar_size: int = 20,
    cardinality_bar_label_size: int = 16,
    cardinality_bar_x_axis_orient: str = "bottom",
    theme: Optional[str] = None,
) -> UpSetChart:
    """Generate vertical UpSet plots with set bars on top and intersection matrix below.

    Parameters
    ----------
    data : pandas.DataFrame
        Input data where each column represents a set and contains binary
        values (0 or 1).
    sets : list of str
        Names of the sets to visualize.
    title : str, default ""
        Title of the plot.
    subtitle : str or list of str, default ""
        Subtitle(s) of the plot.
    abbre : list of str, optional
        Abbreviations for set names.
    sort_by : {"frequency", "degree"}, default "frequency"
        Method to sort the intersections.
    sort_order : {"ascending", "descending"}, default "ascending"
        Order of sorting for intersections.
    width : int, default 1200
        Total width of the plot in pixels.
    height : int, default 700
        Total height of the plot in pixels.
    height_ratio : float, default 0.4
        Ratio of set bar height to total height.
    color_range : list of str
        List of colors for the sets.
    highlight_color : str, default "#EA4667"
        Color used for highlighting.
    highlight : str, int, or list of int, optional
        Specifies which intersections to highlight programmatically.
    glyph_size : int, default 100
        Size of the matrix glyphs.
    set_label_bg_size : int, default 500
        Size of the set label background circles.
    line_connection_size : int, default 1
        Thickness of connecting lines.
    set_bar_size : int, default 30
        Width of set bars in pixels.
    theme : str, optional
        Altair theme to use.

    Returns
    -------
    UpSetChart
        An UpSetChart object representing the vertical UpSet plot.
    """
    # Input validation
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    if not isinstance(sets, list) or not all(isinstance(s, str) for s in sets):
        raise TypeError("sets must be a list of strings")
    if not all(s in data.columns for s in sets):
        raise ValueError("all sets must be columns in data")
    if not all(data[s].isin([0, 1]).all() for s in sets):
        raise ValueError("all set columns must contain only 0s and 1s")
    if height_ratio <= 0 or height_ratio >= 1:
        raise ValueError("height_ratio must be between 0 and 1")
    if sort_by not in ["frequency", "degree"]:
        raise ValueError("sort_by must be either 'frequency' or 'degree'")
    if sort_order not in ["ascending", "descending"]:
        raise ValueError("sort_order must be either 'ascending' or 'descending'")
    if abbre is not None and len(sets) != len(abbre):
        raise ValueError("if provided, abbre must have the same length as sets")
    if highlight is not None:
        if isinstance(highlight, str):
            if highlight not in ["least", "greatest"]:
                raise ValueError("highlight string must be 'least' or 'greatest'")
        elif isinstance(highlight, int):
            if highlight < 0:
                raise ValueError("highlight index must be non-negative")
        elif isinstance(highlight, list):
            if not all(isinstance(i, int) and i >= 0 for i in highlight):
                raise ValueError("highlight list must contain non-negative integers")
        else:
            raise TypeError("highlight must be None, str, int, or list of int")

    # Apply theme if specified
    if theme is not None:
        alt.themes.enable(theme)

    # Preprocess data
    data, set_to_abbre, set_to_order, abbre = preprocess_data(
        data, sets, abbre, sort_order
    )

    # Setup selections for interactivity
    legend_selection = alt.selection_point(fields=["set"], bind="legend")

    # Setup color selection based on highlight parameter
    if highlight is None:
        color_selection = alt.selection_point(
            fields=["intersection_id"], on="mouseover"
        )
    else:
        highlighted_ids = _determine_highlighted_intersections(data, highlight)
        color_selection = alt.selection_point(
            fields=["intersection_id"],
            value=[{"intersection_id": id_} for id_ in highlighted_ids],
        )

    # Calculate dimensions
    if cardinality_bar_width is None:
        cardinality_bar_width = int(width * 0.15)  # 15% of total width
    set_bar_height = height * height_ratio
    matrix_height = height - set_bar_height  # Use full available height
    matrix_width = width - cardinality_bar_width

    # Setup styles
    main_color = "#3A3A3A"
    brush_color = alt.condition(
        ~color_selection, alt.value(main_color), alt.value(highlight_color)
    )
    is_show_set_label_bg = len(abbre[0]) <= 2 if abbre else True
    set_label_bg_color = "white" if is_show_set_label_bg else "black"
    y_sort = alt.Sort(
        field="count" if sort_by == "frequency" else "degree", order=sort_order
    )

    # Automatic bar size for cardinality bars
    num_intersections = max(1, len(data["intersection_id"].unique().tolist()))
    cardinality_bar_size = min(30, (matrix_height / num_intersections) - 5)

    # Tooltip configuration for cardinality bars
    tooltip = [
        alt.Tooltip("count:Q", title="Cardinality"),
        alt.Tooltip("degree:Q", title="Degree"),
    ]

    # Create base chart
    base = create_base_chart(data, sets, legend_selection, set_to_abbre, set_to_order)

    # Create components
    set_label_bg, set_label, set_bar = create_vertical_set_bars(
        base,
        sets,
        color_range,
        set_label_bg_size,
        is_show_set_label_bg,
        set_label_bg_color,
        set_bar_size,
        width,
        main_color,
    )

    set_bar_chart = (set_label_bg + set_label + set_bar).properties(
        width=matrix_width, height=set_bar_height
    )

    circle_bg, rect_bg, circle, line_connection = create_vertical_matrix(
        base,
        matrix_height,
        glyph_size,
        y_sort,
        brush_color,
        line_connection_size,
        main_color,
    )

    matrix_view = (
        (circle + rect_bg + circle_bg + line_connection + circle)
        .add_params(color_selection)
        .properties(width=matrix_width, height=matrix_height)
    )

    # Create cardinality bars
    cardinality_bar, cardinality_bar_text = create_horizontal_cardinality_bar(
        base,
        cardinality_bar_width,
        matrix_height,
        main_color,
        cardinality_bar_size,
        brush_color,
        y_sort,
        tooltip,
        cardinality_bar_label_size,
        cardinality_bar_x_axis_orient,
    )

    cardinality_bar_chart = (
        (cardinality_bar + cardinality_bar_text)
        .add_params(color_selection)
        .properties(width=cardinality_bar_width, height=matrix_height)
    )

    # Create empty spacer for top-right area
    spacer = (
        alt.Chart(pd.DataFrame({"x": [0]}))
        .mark_text()
        .encode(text=alt.value(""))
        .properties(width=cardinality_bar_width, height=set_bar_height)
    )

    # Combine components vertically with cardinality bars
    upsetaltair = (
        alt.vconcat(
            alt.hconcat(
                set_bar_chart,
                spacer,
                spacing=0,
            ).resolve_scale(x="shared"),
            alt.hconcat(
                matrix_view,
                cardinality_bar_chart,
                spacing=0,
            ).resolve_scale(y="shared"),
            spacing=0,
        )
        .resolve_scale(x="shared")
        .add_params(legend_selection)
    )

    # Apply configuration
    chart = upsetaltair_top_level_configuration(
        upsetaltair, legend_orient="top", legend_symbol_size=set_label_bg_size / 2.0
    ).properties(
        title={
            "text": title,
            "subtitle": subtitle,
            "fontSize": 20,
            "fontWeight": 500,
            "subtitleColor": main_color,
            "subtitleFontSize": 14,
        },
        autosize=alt.AutoSizeParams(type="fit", resize=False, contains="padding"),
    )

    return UpSetChart(chart, data, sets)
