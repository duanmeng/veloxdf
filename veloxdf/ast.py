# -*- coding: utf-8 -*-

import abc
from dataclasses import dataclass, fields
from typing import Any, List


class Node(abc.ABC):
    """Base class of all nodes"""

    def __repr__(self) -> str:
        attributes = ", ".join(f"{key}={value!r}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({attributes})"

    def to_dict(self) -> dict:
        def convert_value(value: Any) -> Any:
            if isinstance(value, Node):
                return value.to_dict()
            elif isinstance(value, list):
                return [convert_value(item) for item in value]
            else:
                return value

        result = {"node_type": self.__class__.__name__}

        for field in fields(self):
            value = getattr(self, field.name)
            result[field.name] = convert_value(value)

        return result


class Expression(Node):
    """Base class of all expression nodes"""

    pass


@dataclass(frozen=True)
class Column(Expression):
    name: str


@dataclass(frozen=True)
class Literal(Expression):
    value: Any


@dataclass(frozen=True)
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression


@dataclass(frozen=True)
class FunctionCall(Expression):
    name: str
    args: List[Expression]


@dataclass(frozen=True)
class Alias(Expression):
    child: Expression
    alias: str


class PlanNode(Node):
    """Base class of all plan nodes"""

    children: List["PlanNode"]


@dataclass
class DataSourceNode(PlanNode):
    name: str
    children: List[PlanNode] = None  # type: ignore

    def __post_init__(self):
        self.children = []


@dataclass
class ProjectNode(PlanNode):
    projections: List[Expression]
    child: PlanNode

    def __post_init__(self):
        self.children = [self.child]


@dataclass
class FilterNode(PlanNode):
    predicate: Expression
    child: PlanNode

    def __post_init__(self):
        self.children = [self.child]
