# -*- coding: utf-8 -*-

import json

from veloxdf import DataFrame
from veloxdf.ast import DataSourceNode, FilterNode, ProjectNode


def test_plan_building():
    """Tests if chained calls correctly build the logical plan tree."""
    df = DataFrame.from_source("my_table").filter("c0 > 10").map("c1 + 1 as c2")

    # Get the plan from the internal builder for testing
    plan = df._builder.get_plan_node()

    # Check the structure of the plan tree
    assert isinstance(plan, ProjectNode)
    assert isinstance(plan.child, FilterNode)
    assert isinstance(plan.child.child, DataSourceNode)
    assert plan.child.child.name == "my_table"


def test_optimizer_filter_pushdown():
    """
    Tests if the FilterPushdownRule works correctly.
    The rule should transform a Filter -> Project pattern into a Project -> Filter pattern.
    """
    # 1. Create a Filter -> Project plan
    df_before = DataFrame.from_source("my_table").map("c0 + 1 as c1").filter("c0 > 10")

    # 2. Run the optimizer
    df_after = df_before.optimize()

    # Get the plan from the internal builder for testing
    plan = df_after._builder.get_plan_node()

    # 3. Check that the optimized plan structure is Project -> Filter
    assert isinstance(plan, ProjectNode), "The root of the optimized plan should be a ProjectNode"

    assert isinstance(plan.child, FilterNode), "The child of the ProjectNode should be a FilterNode"

    assert isinstance(
        plan.child.child, DataSourceNode
    ), "The child of the FilterNode should be a DataSourceNode"

    assert plan.child.child.name == "my_table"


def test_to_json_serialization():
    """Tests if the to_json method generates the correct JSON string."""
    df = DataFrame.from_source("test_table").filter("c0.value > 1")

    json_string = df.to_json()

    # Parse the JSON string back into a Python dictionary for validation
    data = json.loads(json_string)

    # Verify the JSON structure and key values
    assert data["node_type"] == "FilterNode"
    assert data["child"]["node_type"] == "DataSourceNode"
    assert data["child"]["name"] == "test_table"

    predicate = data["predicate"]
    assert predicate["node_type"] == "BinaryOp"
    assert predicate["op"] == ">"

    # Key validation: ensure 'c0.value' is serialized correctly
    left_operand = predicate["left"]
    assert left_operand["node_type"] == "Column"
    assert left_operand["name"] == "c0.value"
