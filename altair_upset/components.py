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
    """Creates the vertical bar chart component showing intersection cardinality."""
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
    """Creates the matrix view component showing set intersections."""
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
    """Creates the horizontal bar chart component showing set sizes."""
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
                "sum(count):Q",
                axis=alt.Axis(grid=False, tickCount=3),
                title="Set Size",
            )
        )
    )

    return horizontal_bar_label_bg, horizontal_bar_label, horizontal_bar


def create_vertical_set_bars(
    base,
    sets,
    color_range,
    set_label_bg_size,
    is_show_set_label_bg,
    set_label_bg_color,
    set_bar_size,
    set_bar_width,
    main_color,
):
    """Creates vertical set size bars for vertical upset plots.

    Bars go upward showing the size of each set.
    """
    # Create labeled circles for set names
    set_label_bg = base.mark_circle(size=set_label_bg_size).encode(
        x=alt.X(
            "set_order:N",
            axis=alt.Axis(grid=False, labels=False, ticks=False, domain=False),
            title=None,
        ),
        color=alt.Color(
            "set:N", scale=alt.Scale(domain=sets, range=color_range), title=None
        ),
        opacity=alt.value(1),
    )

    set_label = set_label_bg.mark_text(align="center").encode(
        text=alt.Text("set_abbre:N"), color=alt.value(set_label_bg_color)
    )

    # Create vertical bars for set sizes
    set_bar = (
        set_label_bg.mark_bar(size=set_bar_size, color=main_color)
        .transform_filter(alt.datum["is_intersect"] == 1)
        .encode(
            y=alt.Y(
                "sum(count):Q",
                axis=alt.Axis(grid=False, tickCount=3, domain=False),
                scale=alt.Scale(zero=True, padding=0, nice=False),
                title="Set Size",
            )
        )
    )

    return set_label_bg, set_label, set_bar


def create_vertical_matrix(
    base,
    matrix_height,
    glyph_size,
    y_sort,
    brush_color,
    line_connection_size,
    main_color,
):
    """Creates the matrix view for vertical upset plots.

    Shows intersection dots arranged with sets on X-axis and intersections on Y-axis.
    """
    circle_bg = base.mark_circle(size=glyph_size, opacity=1).encode(
        x=alt.X(
            "set_order:N",
            axis=alt.Axis(grid=False, labels=False, ticks=False, domain=False),
            title=None,
        ),
        y=alt.Y(
            "intersection_id:N",
            axis=alt.Axis(grid=False, labels=False, ticks=False, domain=False),
            sort=y_sort,
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

    # Horizontal connection lines (connecting dots across sets)
    line_connection = (
        base.mark_bar(size=line_connection_size, color=main_color)
        .transform_filter(alt.datum["is_intersect"] == 1)
        .encode(
            x=alt.X("min(set_order):N"),
            x2=alt.X2("max(set_order):N"),
            y=alt.Y("intersection_id:N", sort=y_sort),
        )
    )

    return circle_bg, rect_bg, circle, line_connection


def create_horizontal_cardinality_bar(
    base,
    cardinality_bar_width,
    matrix_height,
    main_color,
    bar_size,
    brush_color,
    y_sort,
    tooltip,
    label_size,
    x_axis_orient,
):
    """Creates horizontal cardinality bars for vertical upset plots.

    Bars extend horizontally (left to right) showing intersection sizes,
    aligned with matrix rows.
    """
    cardinality_bar = base.mark_bar(color=main_color, size=bar_size).encode(
        y=alt.Y(
            "intersection_id:N",
            axis=alt.Axis(grid=False, labels=False, ticks=False, domain=True),
            sort=y_sort,
            title=None,
        ),
        x=alt.X(
            "max(count):Q",
            axis=alt.Axis(grid=False, tickCount=3, orient=x_axis_orient),
            scale=alt.Scale(zero=True, padding=0, nice=False),
            title="Intersection Size",
        ),
        color=brush_color,
        tooltip=tooltip,
    )

    cardinality_bar_text = cardinality_bar.mark_text(
        color=main_color, dx=10, size=label_size, align="left"
    ).encode(text=alt.Text("count:Q", format=".0f"))

    return cardinality_bar, cardinality_bar_text
