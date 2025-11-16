# -*- coding: utf-8 -*-

from typing import List

from veloxdf.ast import DataSourceNode, FilterNode, PlanNode, ProjectNode
from veloxdf.parser import ExpressionParser


class PlanBuilder:
    """
    Builds an immutable logical plan from scratch using a fluent API.
    Each method returns a new PlanBuilder instance.
    """

    def __init__(self, plan: PlanNode):
        self._plan = plan
        self._parser = ExpressionParser()

    @staticmethod
    def table_scan(name: str) -> "PlanBuilder":
        """Starting method: creates a plan representing a data source."""
        source_node = DataSourceNode(name=name)
        return PlanBuilder(source_node)

    def filter(self, predicate_sql: str) -> "PlanBuilder":
        """Adds a FilterNode on top of the current plan."""
        predicate_expr = self._parser.parse(predicate_sql)
        new_plan = FilterNode(predicate=predicate_expr, child=self._plan)
        return PlanBuilder(new_plan)

    def project(self, projection_sqls: List[str]) -> "PlanBuilder":
        """Adds a ProjectNode on top of the current plan."""
        projections = [self._parser.parse(sql) for sql in projection_sqls]
        new_plan = ProjectNode(projections=projections, child=self._plan)
        return PlanBuilder(new_plan)

    def get_plan_node(self) -> PlanNode:
        """Final method: returns the fully constructed PlanNode."""
        return self._plan
