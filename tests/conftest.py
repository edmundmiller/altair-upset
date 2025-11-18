import json
from pathlib import Path

import altair as alt
import pandas as pd
import pytest


@pytest.fixture
def output_dir():
    """Fixture providing the debug output directory"""
    dir_path = Path("tests/debug")
    dir_path.mkdir(exist_ok=True)
    return dir_path


@pytest.fixture
def covid_symptoms_data():
    """Fixture providing the COVID symptoms dataset"""
    return pd.read_csv("https://ndownloader.figshare.com/files/22339791")


@pytest.fixture
def covid_mutations_data():
    """Fixture to prepare mutations DataFrame"""
    # Raw data dictionary
    raw_data = {
        "Alpha": {
            "nonsynonymous": [
                "S:H69-",
                "S:N501Y",
                "S:A570D",
                "S:D614G",
                "S:P681H",
                "S:T716I",
                "S:S982A",
                "S:D1118H",
            ]
        },
        "Beta": {
            "nonsynonymous": [
                "S:D80A",
                "S:D215G",
                "S:K417N",
                "S:E484K",
                "S:N501Y",
                "S:D614G",
                "S:A701V",
            ]
        },
        "Gamma": {
            "nonsynonymous": [
                "S:L18F",
                "S:T20N",
                "S:P26S",
                "S:D138Y",
                "S:R190S",
                "S:K417T",
                "S:E484K",
                "S:N501Y",
                "S:D614G",
                "S:H655Y",
                "S:T1027I",
            ]
        },
        "Delta": {
            "nonsynonymous": [
                "S:T19R",
                "S:G142D",
                "S:E156G",
                "S:F157-",
                "S:R158-",
                "S:L452R",
                "S:T478K",
                "S:D614G",
                "S:P681R",
                "S:D950N",
            ]
        },
        "Kappa": {
            "nonsynonymous": [
                "S:T95I",
                "S:G142D",
                "S:E154K",
                "S:L452R",
                "S:E484Q",
                "S:D614G",
                "S:P681R",
                "S:Q1071H",
            ]
        },
        "Omicron": {
            "nonsynonymous": [
                "S:A67V",
                "S:T95I",
                "S:G142D",
                "S:N211I",
                "S:V213G",
                "S:G339D",
                "S:S371L",
                "S:S373P",
                "S:S375F",
                "S:K417N",
                "S:N440K",
                "S:G446S",
                "S:S477N",
                "S:T478K",
                "S:E484A",
                "S:Q493R",
                "S:G496S",
                "S:Q498R",
                "S:N501Y",
                "S:Y505H",
                "S:T547K",
                "S:D614G",
                "S:H655Y",
                "S:N679K",
                "S:P681H",
                "S:N764K",
                "S:D796Y",
                "S:N856K",
                "S:Q954H",
                "S:N969K",
                "S:L981F",
            ]
        },
        "Eta": {
            "nonsynonymous": [
                "S:A67V",
                "S:H69-",
                "S:V70-",
                "S:Y144-",
                "S:E484K",
                "S:D614G",
                "S:Q677H",
                "S:F888L",
            ]
        },
        "Iota": {
            "nonsynonymous": [
                "S:L5F",
                "S:T95I",
                "S:D253G",
                "S:E484K",
                "S:D614G",
                "S:A701V",
            ]
        },
        "Lambda": {
            "nonsynonymous": [
                "S:G75V",
                "S:T76I",
                "S:D253N",
                "S:L452Q",
                "S:F490S",
                "S:D614G",
                "S:T859N",
            ]
        },
        "Mu": {
            "nonsynonymous": [
                "S:T95I",
                "S:Y144S",
                "S:Y145N",
                "S:R346K",
                "S:E484K",
                "S:N501Y",
                "S:D614G",
                "S:P681H",
                "S:D950N",
            ]
        },
    }

    # Restructure and get unique mutations
    unique_mutations = set()
    for name in raw_data:
        mutations = raw_data[name]["nonsynonymous"]
        raw_data[name] = mutations
        unique_mutations.update(mutations)

    unique_vars = list(raw_data.keys())
    unique_mutations = list(unique_mutations)

    # Generate data for UpSet
    data = []
    for mutation in unique_mutations:
        row = {}
        for variant in unique_vars:
            row[variant] = 1 if mutation in raw_data[variant] else 0
        data.append(row)

    # Create DataFrame from list of dicts
    df = pd.DataFrame(data)
    df = df.reindex(
        columns=[
            "Alpha",
            "Beta",
            "Gamma",
            "Delta",
            "Kappa",
            "Omicron",
            "Eta",
            "Iota",
            "Lambda",
            "Mu",
        ]
    )

    return df


def normalize_spec(spec):
    """Normalize a Vega-Lite spec for comparison"""
    spec = spec.copy()

    # Normalize schema version
    if "$schema" in spec:
        spec["$schema"] = "https://vega.github.io/schema/vega-lite/v4.json"

    # Track view name mappings and param name mappings
    view_counter = {}
    param_mapping = {}

    def normalize_data(d):
        if isinstance(d, dict):
            # Remove data and datasets as they might have different orders
            d.pop("data", None)
            d.pop("datasets", None)

            # For selections, we only care about the values, not the specific IDs
            if "selection" in d:
                if isinstance(d["selection"], dict):
                    # Sort selection values and assign sequential IDs
                    values = sorted(
                        d["selection"].values(),
                        key=lambda x: json.dumps(x, sort_keys=True),
                    )
                    d["selection"] = {
                        f"selector{i:03d}": v for i, v in enumerate(values)
                    }
                # For string selections, just normalize to a fixed value
                elif isinstance(d["selection"], str):
                    d["selection"] = "selector000"

            # Normalize params - replace param_N names with param_0, param_1, etc.
            if "params" in d and isinstance(d["params"], list):
                for i, param in enumerate(d["params"]):
                    if isinstance(param, dict) and "name" in param:
                        old_name = param["name"]
                        new_name = f"param_{i}"
                        param_mapping[old_name] = new_name
                        param["name"] = new_name

            # Normalize param references in filters
            if "param" in d and isinstance(d["param"], str):
                if d["param"] in param_mapping:
                    d["param"] = param_mapping[d["param"]]

            # Normalize view names
            if (
                "name" in d
                and isinstance(d["name"], str)
                and d["name"].startswith("view_")
            ):
                if d["name"] not in view_counter:
                    view_counter[d["name"]] = f"view_{len(view_counter)}"
                d["name"] = view_counter[d["name"]]

            # Normalize views - replace view_N names with view_0, view_1, etc.
            if "views" in d and isinstance(d["views"], list):
                normalized_views = []
                for view_name in d["views"]:
                    if isinstance(view_name, str) and view_name.startswith("view_"):
                        if view_name not in view_counter:
                            view_counter[view_name] = f"view_{len(view_counter)}"
                        normalized_views.append(view_counter[view_name])
                    else:
                        normalized_views.append(view_name)
                d["views"] = normalized_views

            return {k: normalize_data(v) for k, v in sorted(d.items())}
        elif isinstance(d, list):
            if len(d) > 0 and not all(x is None for x in d):
                if isinstance(d[0], dict):
                    return sorted(
                        [normalize_data(x) for x in d if x is not None],
                        key=lambda x: json.dumps(x, sort_keys=True),
                    )
            return d
        return d

    if "config" in spec:
        if "background" in spec["config"]:
            del spec["config"]["background"]

        spec["config"].update(
            {
                "view": {
                    "continuousWidth": 400,
                    "continuousHeight": 300,
                    "stroke": None,
                },
                "axis": {
                    "labelFontSize": 14,
                    "labelFontWeight": 300,
                    "titleFontSize": 16,
                    "titleFontWeight": 400,
                    "titlePadding": 10,
                },
                "legend": {
                    "labelFontSize": 14,
                    "labelFontWeight": 300,
                    "orient": "top",
                    "padding": 20,
                    "symbolSize": 500.0,
                    "symbolType": "circle",
                    "titleFontSize": 16,
                    "titleFontWeight": 400,
                },
                "title": {
                    "anchor": "start",
                    "fontSize": 18,
                    "fontWeight": 400,
                    "subtitlePadding": 10,
                },
                "concat": {"spacing": 0},
            }
        )

    normalized = normalize_data(spec)
    return dict(sorted(normalized.items()))


@pytest.fixture
def sample_data():
    """Create sample dataset for testing."""
    return pd.DataFrame(
        {"set1": [1, 0, 1, 1, 0], "set2": [1, 1, 0, 1, 0], "set3": [0, 1, 1, 1, 0]}
    )


@pytest.fixture
def sample_sets():
    """List of set names."""
    return ["set1", "set2", "set3"]


@pytest.fixture
def sample_abbreviations():
    """List of set abbreviations."""
    return ["S1", "S2", "S3"]


@pytest.fixture
def base_chart():
    """Basic Altair chart for component testing."""
    return alt.Chart().mark_point()


@pytest.fixture
def legend_selection():
    """Legend selection for testing."""
    return alt.selection_point(fields=["set"], bind="legend")
