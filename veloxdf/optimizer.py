# -*- coding: utf-8 -*-

import abc
from typing import List, cast

from veloxdf.ast import FilterNode, Node, PlanNode, ProjectNode
from veloxdf.plan_rebuilder import PlanNodeRebuilder


class Visitor(abc.ABC):
    """A base class for visiting nodes in the AST."""

    def __init__(self):
        self.builder = PlanNodeRebuilder()

    def visit(self, node: Node) -> Node:
        """
        Dispatches the visit to the appropriate method based on node type.
        e.g., visit_ProjectNode for a ProjectNode.
        """
        method_name = f"visit_{node.__class__.__name__}"
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: Node) -> Node:
        """
        Default visitor behavior: recursively visits children and rebuilds the
        node if any child has changed.
        """
        if not isinstance(node, PlanNode):
            return node

        has_changed = False
        new_children = []
        for old_child in node.children:
            new_child = self.visit(old_child)
            if new_child is not old_child:
                has_changed = True
            new_children.append(new_child)

        if has_changed:
            return self.builder.build(node, new_children)

        return node


class Rule(Visitor):
    """Base class for all optimization rules."""

    pass


class FilterPushdownRule(Rule):
    """
    An RBO rule that pushes a FilterNode below a ProjectNode.

    Matches the pattern: FilterNode -> ProjectNode
    Transforms it into:  ProjectNode -> FilterNode
    """

    def visit_FilterNode(self, node: FilterNode) -> PlanNode:
        new_child = self.visit(node.child)

        if isinstance(new_child, ProjectNode):
            print("Optimizer: Found Filter -> Project pattern, pushing down filter.")
            project_node = new_child

            new_filter_node = self.builder.build_filter(node, project_node.child)
            new_project_node = self.builder.build_project(project_node, new_filter_node)
            return new_project_node

        if new_child is not node.child:
            return self.builder.build_filter(node, new_child)

        return node


class Optimizer:
    """A simple rule-based optimizer (RBO)."""

    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def optimize(self, plan: PlanNode) -> PlanNode:
        """Applies a list of rules to a plan until a fixed point is reached."""
        optimized_plan = plan
        print("--- Starting Optimization ---")
        for rule in self.rules:
            print(f"Applying rule: {rule.__class__.__name__}")
            optimized_plan = cast(PlanNode, rule.visit(optimized_plan))
        print("--- Optimization Finished ---")
        return optimized_plan
