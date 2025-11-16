Advanced Features Example
=========================

This example demonstrates the advanced features of UpSet plots including interactive
filtering, statistical analysis, and animated transitions.

Setup
-----

First, let's import our libraries and create some sample data with engagement metrics:

.. altair-plot::
    :output: none

    import altair_upset as au
    import pandas as pd
    import numpy as np

    # Create sample data with metrics
    np.random.seed(42)
    n_users = 1000

    # Generate platform usage data with engagement metrics
    platforms = ['Facebook', 'Instagram', 'Twitter', 'LinkedIn', 'TikTok']
    data = pd.DataFrame({
        platform: np.random.choice([0, 1], size=n_users, p=[0.3, 0.7])
        for platform in platforms
    })

    # Add engagement metrics
    data['daily_time_spent'] = np.random.lognormal(3, 1, n_users)  # minutes
    data['posts_per_week'] = np.random.poisson(5, n_users)
    data['engagement_rate'] = np.random.beta(2, 5, n_users)

Basic UpSet Plot with Metrics
-----------------------------

Create a basic UpSet plot showing platform usage with engagement metrics:

.. altair-plot::

    au.UpSetAltair(
        data=data,
        sets=platforms,
        title="Social Media Platform Usage Analysis",
        subtitle="Interactive analysis of user engagement patterns",
        width=800,
        height=500
    ).chart

Engagement Analysis
-------------------

Let's analyze the engagement patterns across different platform combinations:

.. code-block:: python

    # Calculate average engagement metrics for each platform
    for platform in platforms:
        platform_data = data[data[platform] == 1]
        print(f"\n{platform} Metrics:")
        print(f"Users: {len(platform_data)}")
        print(f"Average daily time: {platform_data['daily_time_spent'].mean():.1f} minutes")
        print(f"Average posts per week: {platform_data['posts_per_week'].mean():.1f}")
        print(
            f"Average engagement rate: {platform_data['engagement_rate'].mean()*100:.1f}%"
        )


    # Find most engaged platform combinations
    def get_engagement_metrics(group):
        return pd.Series(
            {
                "users": len(group),
                "avg_time": group["daily_time_spent"].mean(),
                "avg_posts": group["posts_per_week"].mean(),
                "avg_engagement": group["engagement_rate"].mean() * 100,
            }
        )


    # Calculate metrics for all combinations
    combinations = data.groupby(platforms).apply(get_engagement_metrics).reset_index()

    # Sort by average engagement
    top_engaged = combinations.sort_values("avg_engagement", ascending=False).head(3)
    print("\nTop 3 Most Engaged Platform Combinations:")
    for _, row in top_engaged.iterrows():
        active_platforms = [p for p, v in zip(platforms, row[platforms]) if v == 1]
        print(f"\n{' & '.join(active_platforms)}:")
        print(f"Users: {row['users']}")
        print(f"Avg Time: {row['avg_time']:.1f} minutes")
        print(f"Avg Posts: {row['avg_posts']:.1f} per week")
        print(f"Avg Engagement: {row['avg_engagement']:.1f}%")


Vertical Orientation
--------------------

UpSet plots can be displayed in either horizontal or vertical orientation. The choice depends
on your use case:

- **Horizontal layouts** (default) are best for static figures in papers
- **Vertical layouts** are better for interactive plots that can be scrolled

In vertical orientation, the cardinality (intersection size) is displayed horizontally on the
left, and set sizes are displayed vertically on top.

.. altair-plot::

    au.UpSetAltair(
        data=data,
        sets=platforms,
        title="Social Media Platform Usage (Vertical Layout)",
        subtitle="Better for interactive exploration with scrolling",
        orientation="vertical",  # Use vertical orientation
        width=700,
        height=900
    ).chart

The matrix can be sorted in various ways - by cardinality (size), degree, or sets - and this
works equally well in both orientations.

Comparing Horizontal and Vertical Layouts
------------------------------------------

Here's a comparison showing the same data in both orientations:

.. altair-plot::

    # Horizontal orientation (default)
    au.UpSetAltair(
        data=data,
        sets=platforms,
        title="Horizontal Layout",
        subtitle="Cardinality vertical (top), set sizes horizontal (right)",
        orientation="horizontal",
        width=800,
        height=500
    ).chart

.. altair-plot::

    # Vertical orientation
    au.UpSetAltair(
        data=data,
        sets=platforms,
        title="Vertical Layout",
        subtitle="Cardinality horizontal (left), set sizes vertical (top)",
        orientation="vertical",
        width=600,
        height=800
    ).chart
