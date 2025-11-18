"""Example script to demonstrate vertical UpSet plot."""

import pandas as pd
from altair_upset import UpSetVertical

# Create sample data
data = pd.DataFrame(
    {
        "A": [1, 1, 0, 1, 0, 1, 0, 0],
        "B": [1, 0, 1, 1, 0, 0, 1, 0],
        "C": [0, 1, 1, 1, 0, 0, 0, 1],
    }
)

# Create vertical upset plot
chart = UpSetVertical(
    data=data,
    sets=["A", "B", "C"],
    title="Vertical UpSet Plot Example",
    subtitle="Set size bars on top, intersection matrix below",
    width=800,
    height=600,
    sort_by="frequency",
    sort_order="descending",
)

# Save the chart
chart.save("vertical_upset_example.png")
print("Saved vertical_upset_example.png")

# Also save the horizontal version for comparison
from altair_upset import UpSetAltair

chart_horizontal = UpSetAltair(
    data=data,
    sets=["A", "B", "C"],
    title="Horizontal UpSet Plot (Traditional)",
    subtitle="Intersection bars on top, set sizes on right",
    width=800,
    height=600,
    sort_by="frequency",
    sort_order="descending",
)

chart_horizontal.save("horizontal_upset_example.png")
print("Saved horizontal_upset_example.png")
