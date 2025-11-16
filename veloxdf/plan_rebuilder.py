# -*- coding: utf-8 -*-

from typing import List

from veloxdf.ast import DataSourceNode, FilterNode, PlanNode, ProjectNode


class PlanNodeRebuilder:
    """
    A helper class for immutably rebuilding PlanNodes during tree traversal.

    Its responsibility is to create a new parent node from an existing node
    and a new list of child nodes.
    """

    def build(self, node: PlanNode, new_children: List[PlanNode]) -> PlanNode:
        """
        A generic build method that dispatches to a specific build function
        based on the node type.
        """
        if isinstance(node, ProjectNode):
            return self.build_project(node, new_children[0])
        if isinstance(node, FilterNode):
            return self.build_filter(node, new_children[0])
        if isinstance(node, DataSourceNode):
            return node

        raise TypeError(f"No build method defined for node type {type(node)}")

    def build_project(self, node: ProjectNode, new_child: PlanNode) -> ProjectNode:
        """Creates a new ProjectNode from an old one and a new child."""
        return ProjectNode(projections=node.projections, child=new_child)

    def build_filter(self, node: FilterNode, new_child: PlanNode) -> FilterNode:
        """Creates a new FilterNode from an old one and a new child."""
        return FilterNode(predicate=node.predicate, child=new_child)
