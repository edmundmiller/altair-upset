

def upsetaltair_top_level_configuration(
    base, legend_orient="top-left", legend_symbol_size=30
):
    return (
        base.configure_view(stroke=None)
        .configure_title(
            fontSize=18, fontWeight=400, anchor="start", subtitlePadding=10
        )
        .configure_axis(
            labelFontSize=14,
            labelFontWeight=300,
            titleFontSize=16,
            titleFontWeight=400,
            titlePadding=10,
        )
        .configure_legend(
            titleFontSize=16,
            titleFontWeight=400,
            labelFontSize=14,
            labelFontWeight=300,
            padding=20,
            orient=legend_orient,
            symbolType="circle",
            symbolSize=legend_symbol_size,
        )
        .configure_concat(spacing=0)
    )
