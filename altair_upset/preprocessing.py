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
