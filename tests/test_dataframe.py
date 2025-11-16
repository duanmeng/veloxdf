"""Tests for DataFrame operations."""

import pytest
from veloxdf import DataFrame


def test_dataframe_creation():
    """Test DataFrame creation."""
    data = [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
    ]
    df = DataFrame(data=data)
    assert len(df.data) == 2
    assert df.data[0]["name"] == "Alice"


def test_dataframe_with_schema():
    """Test DataFrame creation with schema."""
    data = [{"id": 1, "value": 100}]
    schema = {"id": int, "value": int}
    df = DataFrame(data=data, schema=schema)
    assert df.schema == schema


def test_map_operation():
    """Test map operation."""
    data = [
        {"id": 1, "value": 10},
        {"id": 2, "value": 20},
    ]
    df = DataFrame(data=data)
    
    # Map to add 5 to value
    result = df.map(lambda row: {**row, "value": row["value"] + 5}).collect()
    
    assert len(result) == 2
    assert result[0]["value"] == 15
    assert result[1]["value"] == 25


def test_filter_operation():
    """Test filter operation."""
    data = [
        {"id": 1, "age": 30},
        {"id": 2, "age": 25},
        {"id": 3, "age": 35},
    ]
    df = DataFrame(data=data)
    
    # Filter age > 28
    result = df.filter(lambda row: row["age"] > 28).collect()
    
    assert len(result) == 2
    assert result[0]["age"] == 30
    assert result[1]["age"] == 35


def test_agg_without_groupby():
    """Test aggregation without group by."""
    data = [
        {"id": 1, "value": 10},
        {"id": 2, "value": 20},
        {"id": 3, "value": 30},
    ]
    df = DataFrame(data=data)
    
    # Aggregate sum and count (using tuple format to specify column)
    result = df.agg({"total": ("value", "sum"), "count": "count"}).collect()
    
    assert len(result) == 1
    assert result[0]["total"] == 60
    assert result[0]["count"] == 3


def test_agg_with_groupby():
    """Test aggregation with group by."""
    data = [
        {"category": "A", "value": 10},
        {"category": "B", "value": 20},
        {"category": "A", "value": 15},
        {"category": "B", "value": 25},
    ]
    df = DataFrame(data=data)
    
    # Group by category and sum values
    result = df.agg({"total": ("value", "sum")}, group_by=["category"]).collect()
    
    assert len(result) == 2
    # Sort by category for consistent comparison
    result = sorted(result, key=lambda x: x["category"])
    assert result[0]["category"] == "A"
    assert result[0]["total"] == 25
    assert result[1]["category"] == "B"
    assert result[1]["total"] == 45


def test_chained_operations():
    """Test chaining multiple operations."""
    data = [
        {"id": 1, "age": 30, "value": 100},
        {"id": 2, "age": 25, "value": 200},
        {"id": 3, "age": 35, "value": 150},
    ]
    df = DataFrame(data=data)
    
    # Chain filter and map
    result = (df
              .filter(lambda row: row["age"] > 28)
              .map(lambda row: {**row, "value": row["value"] * 2})
              .collect())
    
    assert len(result) == 2
    assert result[0]["value"] == 200
    assert result[1]["value"] == 300


def test_avg_aggregation():
    """Test average aggregation."""
    data = [
        {"id": 1, "score": 80},
        {"id": 2, "score": 90},
        {"id": 3, "score": 70},
    ]
    df = DataFrame(data=data)
    
    result = df.agg({"avg_score": ("score", "avg")}).collect()
    
    assert len(result) == 1
    assert result[0]["avg_score"] == 80


def test_min_max_aggregation():
    """Test min and max aggregations."""
    data = [
        {"id": 1, "value": 10},
        {"id": 2, "value": 30},
        {"id": 3, "value": 20},
    ]
    df = DataFrame(data=data)
    
    result = df.agg({"min_val": ("value", "min"), "max_val": ("value", "max")}).collect()
    
    assert len(result) == 1
    assert result[0]["min_val"] == 10
    assert result[0]["max_val"] == 30


def test_custom_aggregation():
    """Test custom aggregation function."""
    data = [
        {"id": 1, "value": 10},
        {"id": 2, "value": 20},
    ]
    df = DataFrame(data=data)
    
    # Custom aggregation to calculate product
    def product(rows):
        result = 1
        for row in rows:
            result *= row.get("value", 1)
        return result
    
    result = df.agg({"product": product}).collect()
    
    assert len(result) == 1
    assert result[0]["product"] == 200


def test_execute_with_optimize():
    """Test execute with optimization enabled."""
    data = [
        {"id": 1, "value": 10},
        {"id": 2, "value": 20},
    ]
    df = DataFrame(data=data)
    
    # Add operations
    df.filter(lambda row: row["value"] > 5)
    df.map(lambda row: {**row, "doubled": row["value"] * 2})
    
    result = df.execute(optimize=True)
    
    assert len(result.data) == 2
    assert "doubled" in result.data[0]


def test_execute_without_optimize():
    """Test execute without optimization."""
    data = [
        {"id": 1, "value": 10},
        {"id": 2, "value": 20},
    ]
    df = DataFrame(data=data)
    
    df.filter(lambda row: row["value"] > 5)
    
    result = df.execute(optimize=False)
    
    assert len(result.data) == 2


def test_dataframe_repr():
    """Test DataFrame string representation."""
    data = [{"id": 1}, {"id": 2}]
    df = DataFrame(data=data)
    df.filter(lambda row: row["id"] > 0)
    
    repr_str = repr(df)
    assert "DataFrame" in repr_str
    assert "rows=2" in repr_str
    assert "operations=1" in repr_str
