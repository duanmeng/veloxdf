"""Tests for Optimizer with RBO."""

import pytest
from veloxdf import DataFrame, Optimizer


def test_optimizer_creation():
    """Test Optimizer creation."""
    optimizer = Optimizer()
    assert optimizer is not None
    assert len(optimizer.get_rules()) > 0


def test_filter_pushdown():
    """Test filter pushdown optimization."""
    optimizer = Optimizer()
    
    # Create operations: map -> filter
    operations = [
        {"type": "map", "func": lambda x: x, "name": "map1"},
        {"type": "filter", "predicate": lambda x: x["id"] > 0, "name": "filter1"},
    ]
    
    optimized = optimizer.optimize(operations)
    
    # Filter should be pushed before map
    assert optimized[0]["type"] == "filter"
    assert optimized[1]["type"] == "map"


def test_filter_pushdown_multiple_filters():
    """Test filter pushdown with multiple filters."""
    optimizer = Optimizer()
    
    # Create operations: map -> filter -> map -> filter
    operations = [
        {"type": "map", "func": lambda x: x, "name": "map1"},
        {"type": "filter", "predicate": lambda x: x["id"] > 0, "name": "filter1"},
        {"type": "map", "func": lambda x: x, "name": "map2"},
        {"type": "filter", "predicate": lambda x: x["value"] > 10, "name": "filter2"},
    ]
    
    optimized = optimizer.optimize(operations)
    
    # All filters should be pushed to the beginning before maps
    # (In a more sophisticated optimizer, we might track dependencies,
    # but for this simple implementation, all filters go first)
    assert optimized[0]["type"] == "filter"
    assert optimized[1]["type"] == "filter"
    assert optimized[2]["type"] == "map"
    assert optimized[3]["type"] == "map"


def test_filter_pushdown_with_agg():
    """Test filter pushdown before aggregation."""
    optimizer = Optimizer()
    
    # Create operations: agg -> filter
    operations = [
        {"type": "agg", "aggregations": {"sum": "sum"}, "name": "agg1"},
        {"type": "filter", "predicate": lambda x: x["id"] > 0, "name": "filter1"},
    ]
    
    optimized = optimizer.optimize(operations)
    
    # Filter should be pushed before agg
    assert optimized[0]["type"] == "filter"
    assert optimized[1]["type"] == "agg"


def test_combine_consecutive_filters():
    """Test combining consecutive filter operations."""
    optimizer = Optimizer()
    
    # Create operations with consecutive filters
    operations = [
        {"type": "filter", "predicate": lambda x: x["id"] > 0, "name": "filter1"},
        {"type": "filter", "predicate": lambda x: x["value"] > 10, "name": "filter2"},
    ]
    
    optimized = optimizer.optimize(operations)
    
    # Two filters should be combined into one
    assert len(optimized) == 1
    assert optimized[0]["type"] == "filter"
    assert "combined_filter" in optimized[0]["name"]


def test_combine_filters_with_other_ops():
    """Test combining filters with other operations in between."""
    optimizer = Optimizer()
    
    # Create operations: filter -> filter -> map -> filter
    operations = [
        {"type": "filter", "predicate": lambda x: x["id"] > 0, "name": "filter1"},
        {"type": "filter", "predicate": lambda x: x["value"] > 10, "name": "filter2"},
        {"type": "map", "func": lambda x: x, "name": "map1"},
        {"type": "filter", "predicate": lambda x: x["age"] > 18, "name": "filter3"},
    ]
    
    optimized = optimizer.optimize(operations)
    
    # First two consecutive filters should be combined, then all filters pushed before map
    assert len(optimized) == 3
    assert optimized[0]["type"] == "filter"
    assert "combined_filter" in optimized[0]["name"]
    assert optimized[1]["type"] == "filter"
    assert optimized[1]["name"] == "filter3"
    assert optimized[2]["type"] == "map"


def test_combined_filter_predicate():
    """Test that combined filter predicate works correctly."""
    data = [
        {"id": 1, "value": 20},
        {"id": 2, "value": 5},
        {"id": -1, "value": 30},
    ]
    df = DataFrame(data=data)
    
    # Apply two filters that should be combined
    result = (df
              .filter(lambda row: row["id"] > 0)
              .filter(lambda row: row["value"] > 10)
              .collect())
    
    # Only first row should pass both filters
    assert len(result) == 1
    assert result[0]["id"] == 1
    assert result[0]["value"] == 20


def test_optimization_in_dataframe_execution():
    """Test that DataFrame uses optimizer during execution."""
    data = [
        {"id": 1, "value": 10},
        {"id": 2, "value": 20},
        {"id": 3, "value": 30},
    ]
    df = DataFrame(data=data)
    
    # Create a pipeline that can be optimized
    result = (df
              .map(lambda row: {**row, "doubled": row["value"] * 2})
              .filter(lambda row: row["id"] > 1)
              .collect())
    
    # Verify results are correct (optimization should not change output)
    assert len(result) == 2
    assert result[0]["id"] == 2
    assert result[0]["doubled"] == 40


def test_add_custom_rule():
    """Test adding a custom optimization rule."""
    optimizer = Optimizer()
    
    def custom_rule(operations):
        """Custom rule that does nothing."""
        return operations
    
    initial_rules = len(optimizer.get_rules())
    optimizer.add_rule(custom_rule)
    
    assert len(optimizer.get_rules()) == initial_rules + 1


def test_optimizer_with_empty_operations():
    """Test optimizer with empty operations list."""
    optimizer = Optimizer()
    
    optimized = optimizer.optimize([])
    
    assert optimized == []


def test_filter_pushdown_complex_pipeline():
    """Test filter pushdown in a complex pipeline."""
    data = [
        {"id": 1, "value": 10, "category": "A"},
        {"id": 2, "value": 20, "category": "B"},
        {"id": 3, "value": 30, "category": "A"},
        {"id": 4, "value": 5, "category": "B"},
    ]
    df = DataFrame(data=data)
    
    # Complex pipeline with multiple operations
    result = (df
              .map(lambda row: {**row, "doubled": row["value"] * 2})
              .filter(lambda row: row["value"] > 8)
              .map(lambda row: {**row, "tripled": row["value"] * 3})
              .filter(lambda row: row["category"] == "A")
              .collect())
    
    # Verify correct results
    assert len(result) == 2
    assert all(row["category"] == "A" for row in result)
    assert all(row["value"] > 8 for row in result)
