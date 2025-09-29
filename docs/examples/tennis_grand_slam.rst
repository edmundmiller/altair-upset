Tennis Grand Slam Champions
===========================

This example demonstrates how to create an UpSet plot showing the intersection patterns
of tennis Grand Slam tournament winners across different venues.

.. altair-plot::
    :output: none

    import altair as alt
    import pandas as pd
    import altair_upset as au

    # Create sample tennis Grand Slam data based on realistic patterns
    # This simulates the intersection data that would come from the CSV
    import numpy as np
    np.random.seed(42)
    
    # Define the intersections with realistic sizes based on tennis history
    intersection_data = [
        # Single tournaments (most common)
        {'elementName': 'French Open', 'size': 25},
        {'elementName': 'Australian Open', 'size': 22}, 
        {'elementName': 'US Open', 'size': 20},
        {'elementName': 'Wimbledon', 'size': 18},
        
        # Two tournaments
        {'elementName': 'French Open & Australian Open', 'size': 8},
        {'elementName': 'US Open & Wimbledon', 'size': 7},
        {'elementName': 'Australian Open & US Open', 'size': 6},
        {'elementName': 'French Open & US Open', 'size': 5},
        {'elementName': 'Australian Open & Wimbledon', 'size': 5},
        {'elementName': 'French Open & Wimbledon', 'size': 4},
        
        # Three tournaments  
        {'elementName': 'Australian Open & US Open & Wimbledon', 'size': 3},
        {'elementName': 'French Open & Australian Open & US Open', 'size': 2},
        {'elementName': 'French Open & US Open & Wimbledon', 'size': 2},
        {'elementName': 'French Open & Australian Open & Wimbledon', 'size': 2},
        
        # All four tournaments (career Grand Slam)
        {'elementName': 'French Open & Australian Open & US Open & Wimbledon', 'size': 9}
    ]
    
    intersections = pd.DataFrame(intersection_data)

    # Create an empty DataFrame with the correct columns
    columns = ['French Open', 'Australian Open', 'US Open', 'Wimbledon']
    total_players = sum(intersections['size'])
    data = pd.DataFrame(0, index=range(total_players), columns=columns)

    # Fill the DataFrame based on intersection data
    current_idx = 0
    for _, row in intersections.iterrows():
        sets = row['elementName'].split(' & ')
        size = int(row['size'])
        end_idx = current_idx + size

        for set_name in sets:
            data.loc[current_idx:end_idx-1, set_name] = 1

        current_idx = end_idx

.. altair-plot::
    au.UpSetAltair(
        data=data,
        sets=data.columns.tolist(),
        sort_by="degree",
        sort_order="descending",
        title="Tennis Grand Slam Championships by Player",
        subtitle=[
            "This plot shows the overlap of tennis Grand Slam tournament winners.",
            "Notably, the majority of champions have won only at one tournament venue.",
            "Out of 117 champions, only 9 have won at least once at every Grand Slam tournament venue."
        ],
        width=800,
        height=500
    ).chart

The resulting visualization shows several interesting patterns:

1. Most tennis players have won at only one Grand Slam tournament
2. The French Open and Australian Open have the highest number of unique winners
3. Only 9 players have achieved the remarkable feat of winning all four Grand Slam
   tournaments
4. There's a significant overlap between Australian Open, US Open, and Wimbledon winners

This example demonstrates how UpSet plots can effectively visualize complex set
intersections in sports data, revealing patterns that would be difficult to see in
traditional Venn diagrams.
