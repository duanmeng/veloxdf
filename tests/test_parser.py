# -*- coding: utf-8 -*-

import pytest

from veloxdf.ast import Alias, BinaryOp, Column, FunctionCall, Literal
from veloxdf.parser import ExpressionParser

# Create a parser instance that can be reused across all tests
parser = ExpressionParser()


def test_parse_simple_column():
    """Tests parsing of a simple column name."""
    assert parser.parse("c0") == Column(name="c0")


def test_parse_nested_column():
    """
    Key test: ensures that the fix for nested column names (e.g., 'a.b')
    does not regress.
    """
    assert parser.parse("c0.value") == Column(name="c0.value")
    assert parser.parse("a.b.c") == Column(name="a.b.c")


def test_parse_literals():
    """Tests parsing of various literal types."""
    assert parser.parse("123") == Literal(value=123)
    assert parser.parse("'hello'") == Literal(value="hello")
    assert parser.parse("1.23") == Literal(value=1.23)


def test_parse_simple_binary_op():
    """Tests parsing of a simple binary operation."""
    expected = BinaryOp(left=Column(name="c0"), op=">", right=Literal(value=10))
    assert parser.parse("c0 > 10") == expected


def test_parse_complex_binary_op():
    """Tests parsing of a complex binary operation with AND."""
    expected = BinaryOp(
        left=BinaryOp(left=Column(name="c0"), op=">", right=Literal(value=10)),
        op="and",
        right=BinaryOp(left=Column(name="c1"), op="<", right=Literal(value=5)),
    )
    assert parser.parse("c0 > 10 AND c1 < 5") == expected


def test_parse_alias():
    """Tests parsing of an alias."""
    expected = Alias(
        child=BinaryOp(left=Column(name="c0"), op="+", right=Literal(value=1)),
        alias="c1",
    )
    assert parser.parse("c0 + 1 as c1") == expected


def test_parse_special_functions():
    """
    Key test: ensures that the custom logic for special sqlglot nodes
    (e.g., StartsWith, ArraySize) is correct.
    """
    # Test starts_with
    expected_starts_with = FunctionCall(
        name="STARTS_WITH", args=[Column(name="c1"), Literal(value="prefix")]
    )
    assert parser.parse("starts_with(c1, 'prefix')") == expected_starts_with

    # Test cardinality (from sqlglot's ArraySize)
    expected_cardinality = FunctionCall(name="CARDINALITY", args=[Column(name="c2")])
    assert parser.parse("cardinality(c2)") == expected_cardinality


def test_unsupported_expression_raises_error():
    """Tests that an unsupported syntax raises the expected exception."""
    # We have not implemented the modulo (%) operator, so it should fail.
    with pytest.raises((TypeError, NotImplementedError)):
        parser.parse("c0 % 5")
