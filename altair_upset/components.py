from typing import List

import altair as alt


def create_vertical_bar(
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
):
    """Creates the vertical bar chart component."""
    vertical_bar = base.mark_bar(color=main_color, size=vertical_bar_size).encode(
        x=alt.X(
            "intersection_id:N",
            axis=alt.Axis(grid=False, labels=False, ticks=False, domain=True),
            sort=x_sort,
            title=None,
        ),
        y=alt.Y(
            "max(count):Q",
            axis=alt.Axis(grid=False, tickCount=3, orient=vertical_bar_y_axis_orient),
            title="Intersection Size",
        ),
        color=brush_color,
        tooltip=tooltip,
    )

    vertical_bar_text = vertical_bar.mark_text(
        color=main_color, dy=-10, size=vertical_bar_label_size
    ).encode(text=alt.Text("count:Q", format=".0f"))

    return vertical_bar, vertical_bar_text


def create_matrix_view(
    vertical_bar,
    matrix_height,
    glyph_size,
    x_sort,
    brush_color,
    line_connection_size,
    main_color,
):
    """Creates the matrix view component."""
    circle_bg = vertical_bar.mark_circle(size=glyph_size, opacity=1).encode(
        x=alt.X(
            "intersection_id:N",
            axis=alt.Axis(grid=False, labels=False, ticks=False, domain=False),
            sort=x_sort,
            title=None,
        ),
        y=alt.Y(
            "set_order:N",
            axis=alt.Axis(grid=False, labels=False, ticks=False, domain=False),
            title=None,
        ),
        color=alt.value("#E6E6E6"),
    )

    rect_bg = (
        circle_bg.mark_rect()
        .transform_filter(alt.datum["set_order"] % 2 == 1)
        .encode(color=alt.value("#F7F7F7"))
    )

    circle = circle_bg.transform_filter(alt.datum["is_intersect"] == 1).encode(
        color=brush_color
    )

    line_connection = (
        vertical_bar.mark_bar(size=line_connection_size, color=main_color)
        .transform_filter(alt.datum["is_intersect"] == 1)
        .encode(y=alt.Y("min(set_order):N"), y2=alt.Y2("max(set_order):N"))
    )

    return circle_bg, rect_bg, circle, line_connection


def create_horizontal_bar(
    base,
    set_label_bg_size,
    sets,
    color_range,
    is_show_horizontal_bar_label_bg,
    horizontal_bar_label_bg_color,
    horizontal_bar_size,
    horizontal_bar_chart_width,
):
    """Creates the horizontal bar chart component."""
    horizontal_bar_label_bg = base.mark_circle(size=set_label_bg_size).encode(
        y=alt.Y(
            "set_order:N",
            axis=alt.Axis(grid=False, labels=False, ticks=False, domain=False),
            title=None,
        ),
        color=alt.Color(
            "set:N", scale=alt.Scale(domain=sets, range=color_range), title=None
        ),
        opacity=alt.value(1),
    )

    horizontal_bar_label = horizontal_bar_label_bg.mark_text(
        align=("center" if is_show_horizontal_bar_label_bg else "center")
    ).encode(
        text=alt.Text("set_abbre:N"), color=alt.value(horizontal_bar_label_bg_color)
    )

    horizontal_bar = (
        horizontal_bar_label_bg.mark_bar(size=horizontal_bar_size)
        .transform_filter(alt.datum["is_intersect"] == 1)
        .encode(
            x=alt.X(
                "sum(count):Q", axis=alt.Axis(grid=False, tickCount=3), title="Set Size"
            )
        )
    )

    return horizontal_bar_label_bg, horizontal_bar_label, horizontal_bar


def integrate_annotation_charts(
    annotation_charts: List[alt.Chart],
    vertical_bar_chart: alt.Chart,
    main_upset_chart: alt.Chart,
    spacing: int = 5
) -> alt.Chart:
    """
    Integrate annotation charts above the main UpSet plot.
    
    Parameters
    ----------
    annotation_charts : List[alt.Chart]
        List of annotation charts to place above the main plot
    vertical_bar_chart : alt.Chart
        The vertical bar chart component
    main_upset_chart : alt.Chart
        The main UpSet chart (matrix + horizontal bars)
    spacing : int
        Spacing between chart components
        
    Returns
    -------
    alt.Chart
        Combined chart with annotations above the main plot
    """
    if not annotation_charts:
        return alt.vconcat(
            vertical_bar_chart,
            main_upset_chart,
            spacing=spacing
        )
    
    # Create the full vertical concatenation:
    # Annotations (top to bottom) -> Vertical bar chart -> Matrix + horizontal bars
    all_components = annotation_charts + [vertical_bar_chart, main_upset_chart]
    
    return alt.vconcat(
        *all_components,
        spacing=spacing
    )
