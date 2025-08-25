from typing import Dict, List

import pandas as pd


def preprocess_data(data, sets, abbre, sort_order):
    """Handles the data preprocessing for UpSet plots."""
    # Create a copy to avoid SettingWithCopyWarning
    data = data.copy()

    # Handle empty input data
    if len(data) == 0:
        # Create empty result DataFrame with required columns
        data = pd.DataFrame(columns=sets + ["count", "intersection_id", "degree"])
        data = pd.melt(data, id_vars=["intersection_id", "count", "degree"])
        data = data.rename(columns={"variable": "set", "value": "is_intersect"})

        if abbre is None:
            abbre = sets

        set_to_abbre = pd.DataFrame(
            [[sets[i], abbre[i]] for i in range(len(sets))],
            columns=["set", "set_abbre"],
        )
        set_to_order = pd.DataFrame(
            [[sets[i], 1 + sets.index(sets[i])] for i in range(len(sets))],
            columns=["set", "set_order"],
        )
        return data, set_to_abbre, set_to_order, abbre

    # Process non-empty data
    data.loc[:, "count"] = 0
    data = data[sets + ["count"]]
    data = data.groupby(sets).count().reset_index()

    data["intersection_id"] = data.index
    data["degree"] = data[sets].sum(axis=1)
    data = data.sort_values(
        by=["count"], ascending=True if sort_order == "ascending" else False
    )

    data = pd.melt(data, id_vars=["intersection_id", "count", "degree"])
    data = data.rename(columns={"variable": "set", "value": "is_intersect"})

    # Create a column of concurrent groups (future update for better labelling)
    # sets_mapping = (data.loc[data["is_intersect"] > 0]
    #                 .groupby("intersection_id")["set"]
    #                 .apply(lambda x: " ".join(sorted(x))).to_dict())
    #
    # data["sets_graph"] = data.apply(
    #     lambda row: (row["set"] if row["is_intersect"] == 0
    #                  else sets_mapping.get(row["intersection_id"], "")),
    #     axis=1).fillna("").astype(str)

    if abbre is None:
        abbre = sets

    set_to_abbre = pd.DataFrame(
        [[sets[i], abbre[i]] for i in range(len(sets))], columns=["set", "set_abbre"]
    )
    set_to_order = pd.DataFrame(
        [[sets[i], 1 + sets.index(sets[i])] for i in range(len(sets))],
        columns=["set", "set_order"],
    )

    return data, set_to_abbre, set_to_order, abbre


def preprocess_annotation_data(
    original_data: pd.DataFrame,
    sets: List[str],
    annotation_attributes: List[str],
    sort_order: str = "ascending"
) -> Dict[str, pd.DataFrame]:
    """
    Preprocess annotation data by aggregating attributes for each intersection.
    
    Parameters
    ----------
    original_data : pd.DataFrame
        Original data with set membership and attributes
    sets : List[str]
        List of set names
    annotation_attributes : List[str]
        List of attribute names to prepare for annotation
    sort_order : str
        Sorting order for intersections
        
    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary mapping attribute names to their aggregated data by intersection
    """
    # Create a copy to avoid modifying original data
    data = original_data.copy()
    
    # Add row index to track original items
    data['_item_id'] = data.index
    
    # Create intersection identifiers
    
    if not all(attr in data.columns for attr in annotation_attributes):
        missing_attrs = [
            attr for attr in annotation_attributes 
            if attr not in data.columns
        ]
        raise ValueError(f"Annotation attributes {missing_attrs} not found in data")
    
    # Group by set combinations to create intersection IDs
    temp_data = data[sets].copy()
    temp_data['count'] = 1
    intersection_summary = temp_data.groupby(sets).count().reset_index()
    intersection_summary['intersection_id'] = intersection_summary.index
    intersection_summary = intersection_summary.sort_values(
        by=['count'], ascending=True if sort_order == "ascending" else False
    )
    
    # Create intersection mapping
    intersection_mapping = {}
    for _, row in intersection_summary.iterrows():
        key = tuple(row[set_name] for set_name in sets)
        intersection_mapping[key] = row['intersection_id']
    
    # Add intersection IDs to original data
    data['intersection_id'] = data[sets].apply(
        lambda row: intersection_mapping[tuple(row)], axis=1
    )
    
    # Prepare annotation data for each attribute
    annotation_data = {}
    for attr in annotation_attributes:
        # Create long format data for this attribute
        attr_data = data[['intersection_id', '_item_id', attr] + sets].copy()
        
        # Remove rows with missing values for this attribute
        attr_data = attr_data.dropna(subset=[attr])
        
        annotation_data[attr] = attr_data
    
    return annotation_data


def create_intersection_summary(
    original_data: pd.DataFrame,
    sets: List[str],
    sort_order: str = "ascending"
) -> pd.DataFrame:
    """
    Create a summary of intersections with their properties.
    
    Parameters
    ----------
    original_data : pd.DataFrame
        Original data with set membership
    sets : List[str]
        List of set names
    sort_order : str
        Sorting order for intersections
        
    Returns
    -------
    pd.DataFrame
        Summary of intersections with ID, count, degree, and set membership
    """
    data = original_data[sets].copy()
    data['count'] = 1
    
    # Group by set combinations
    summary = data.groupby(sets).count().reset_index()
    summary['intersection_id'] = summary.index
    summary['degree'] = summary[sets].sum(axis=1)
    
    # Sort by count or degree
    sort_col = 'count'  # Default sorting by frequency
    summary = summary.sort_values(
        by=[sort_col], ascending=True if sort_order == "ascending" else False
    )
    
    # Reassign intersection IDs after sorting
    summary = summary.reset_index(drop=True)
    summary['intersection_id'] = summary.index
    
    return summary


def validate_annotation_attributes(
    data: pd.DataFrame,
    annotation_attributes: List[str]
) -> None:
    """
    Validate annotation attributes exist and are suitable for visualization.
    
    Parameters
    ----------
    data : pd.DataFrame
        Input data
    annotation_attributes : List[str]
        List of attribute names to validate
        
    Raises
    ------
    ValueError
        If attributes are missing or invalid
    """
    missing_attrs = [attr for attr in annotation_attributes if attr not in data.columns]
    if missing_attrs:
        raise ValueError(f"Annotation attributes {missing_attrs} not found in data")
    
    # Check if attributes have sufficient non-null values
    for attr in annotation_attributes:
        non_null_count = data[attr].notna().sum()
        if non_null_count == 0:
            raise ValueError(f"Annotation attribute '{attr}' has no non-null values")
        elif non_null_count < 2:
            raise ValueError(
                f"Annotation attribute '{attr}' has insufficient data for visualization"
            )
