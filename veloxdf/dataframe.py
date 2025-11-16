# -*- coding: utf-8 -*-

import json
from dataclasses import fields

from veloxdf.ast import PlanNode
from veloxdf.optimizer import FilterPushdownRule, Optimizer
from veloxdf.plan_builder import PlanBuilder


class DataFrame:
    """
    A user-friendly DataFrame API that internally uses a PlanBuilder to
    construct a logical plan. This class itself is immutable.
    """

    def __init__(self, builder: PlanBuilder):
        self._builder = builder

    @staticmethod
    def from_source(name: str) -> "DataFrame":
        """Starts building a DataFrame from a data source."""
        builder = PlanBuilder.table_scan(name)
        return DataFrame(builder)

    @staticmethod
    def _from_plan(plan: PlanNode) -> "DataFrame":
        """
        Internal method: creates a DataFrame from an existing PlanNode.
        Used after the optimizer has run.
        """
        builder = PlanBuilder(plan)
        return DataFrame(builder)

    def filter(self, predicate_sql: str) -> "DataFrame":
        """Applies a filter operation and returns a new DataFrame instance."""
        new_builder = self._builder.filter(predicate_sql)
        return DataFrame(new_builder)

    def map(self, *projection_sqls: str) -> "DataFrame":
        """Applies a projection/map operation and returns a new DataFrame instance."""
        new_builder = self._builder.project(list(projection_sqls))
        return DataFrame(new_builder)

    def optimize(self) -> "DataFrame":
        """
        Applies optimization rules to the current logical plan and returns a
        new DataFrame instance.
        """
        optimizer = Optimizer(rules=[FilterPushdownRule()])
        current_plan = self._builder.get_plan_node()
        optimized_plan = optimizer.optimize(current_plan)
        return DataFrame._from_plan(optimized_plan)

    def to_json(self, indent: int = 2) -> str:
        """Serializes the final logical plan into a JSON string."""
        plan_dict = self._builder.get_plan_node().to_dict()
        return json.dumps(plan_dict, indent=indent)

    def __repr__(self) -> str:
        return f"DataFrame(plan=\n{self._prettify_plan(self._builder.get_plan_node())}\n)"

    def _prettify_plan(self, node: PlanNode, indent: str = "") -> str:
        """Recursively pretty-prints the logical plan tree."""
        result = f"{indent}- {node.__class__.__name__}:"

        attributes = []
        for field in fields(node):
            # Do not print 'child' or 'children', as they are handled by recursion
            if field.name not in ("child", "children"):
                attributes.append(f"{field.name}={getattr(node, field.name)!r}")

        if attributes:
            result += f" {', '.join(attributes)}"

        for child in node.children:
            result += f"\n{self._prettify_plan(child, indent + '  ')}"

        return result
