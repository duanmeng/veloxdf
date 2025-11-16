# veloxdf

A simple dataframe library for Velox with built-in query optimization.

## Overview

VeloxDF provides a Pythonic API for describing data pipelines using operations like `map`, `filter`, and `agg` (aggregate). It includes an optimizer with Rule-Based Optimization (RBO) that automatically applies optimizations such as filter pushdown to improve query execution performance.

## Installation

```bash
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

## Features

- **DataFrame API**: Simple, chainable API for data manipulation
- **Core Operations**:
  - `map`: Transform each row with a function
  - `filter`: Filter rows based on predicates
  - `agg`: Aggregate data with grouping support
- **Query Optimizer**: Automatic optimization with Rule-Based Optimization (RBO)
  - Filter pushdown: Moves filter operations earlier in the pipeline
  - Filter combination: Merges consecutive filters for efficiency
- **Extensible**: Add custom aggregation functions and optimization rules

## Quick Start

### Basic DataFrame Operations

```python
from veloxdf import DataFrame

# Create a DataFrame
data = [
    {"id": 1, "name": "Alice", "age": 30, "salary": 70000},
    {"id": 2, "name": "Bob", "age": 25, "salary": 50000},
    {"id": 3, "name": "Charlie", "age": 35, "salary": 80000},
]
df = DataFrame(data=data)

# Filter operation
result = df.filter(lambda row: row["age"] > 28).collect()
print(result)
# Output: [{"id": 1, "name": "Alice", "age": 30, "salary": 70000},
#          {"id": 3, "name": "Charlie", "age": 35, "salary": 80000}]
```

### Map Operation

```python
# Transform data
result = (df
    .map(lambda row: {**row, "salary": row["salary"] * 1.1})
    .collect())
# Increases all salaries by 10%
```

### Chaining Operations

```python
# Chain multiple operations
result = (df
    .filter(lambda row: row["age"] > 25)
    .map(lambda row: {**row, "bonus": row["salary"] * 0.1})
    .collect())
```

### Aggregations

```python
# Simple aggregation
data = [
    {"category": "A", "value": 10},
    {"category": "B", "value": 20},
    {"category": "A", "value": 15},
]
df = DataFrame(data=data)

# Aggregate without grouping
result = df.agg({"total": ("value", "sum"), "count": "count"}).collect()
# Output: [{"total": 45, "count": 3}]

# Aggregate with grouping
result = df.agg(
    {"total": ("value", "sum"), "avg": ("value", "avg")},
    group_by=["category"]
).collect()
# Output: [{"category": "A", "total": 25, "avg": 12.5},
#          {"category": "B", "total": 20, "avg": 20.0}]
```

### Built-in Aggregation Functions

VeloxDF supports the following built-in aggregation functions:
- `sum`: Sum of values
- `avg`: Average of values
- `count`: Count of rows
- `min`: Minimum value
- `max`: Maximum value

### Custom Aggregation Functions

```python
# Define a custom aggregation
def product(rows):
    result = 1
    for row in rows:
        result *= row.get("value", 1)
    return result

result = df.agg({"product": product}).collect()
```

## Query Optimization

VeloxDF automatically optimizes queries using Rule-Based Optimization (RBO). The optimizer applies rules like:

### Filter Pushdown

Moves filter operations earlier in the pipeline to reduce data processed by subsequent operations:

```python
# Before optimization: map -> filter
# After optimization: filter -> map

df = DataFrame(data=data)
result = (df
    .map(lambda row: {**row, "doubled": row["value"] * 2})
    .filter(lambda row: row["id"] > 0)  # Filter pushed before map
    .collect())
```

### Filter Combination

Merges consecutive filter operations into a single filter:

```python
# Before: filter -> filter -> map
# After: combined_filter -> map

result = (df
    .filter(lambda row: row["age"] > 25)
    .filter(lambda row: row["salary"] > 60000)  # Combined with previous filter
    .collect())
```

### Custom Optimization Rules

You can add custom optimization rules:

```python
from veloxdf import Optimizer

optimizer = Optimizer()

def my_custom_rule(operations):
    # Your optimization logic
    return optimized_operations

optimizer.add_rule(my_custom_rule)
```

### Disabling Optimization

If needed, you can disable optimization:

```python
result = df.execute(optimize=False)
```

## API Reference

### DataFrame

#### `__init__(data=None, schema=None)`
Create a new DataFrame.

**Parameters:**
- `data`: List of dictionaries containing row data
- `schema`: Optional dictionary defining column types

#### `map(func, name=None)`
Apply a transformation function to each row.

**Parameters:**
- `func`: Function that takes a row dict and returns a transformed row dict
- `name`: Optional name for the operation

**Returns:** Self for method chaining

#### `filter(predicate, name=None)`
Filter rows based on a predicate.

**Parameters:**
- `predicate`: Function that takes a row dict and returns True/False
- `name`: Optional name for the operation

**Returns:** Self for method chaining

#### `agg(aggregations, group_by=None, name=None)`
Perform aggregation operations.

**Parameters:**
- `aggregations`: Dict mapping output columns to aggregation specs
  - String: Use same column name for input and output
  - Tuple `(column, function)`: Specify input column and function
  - Callable: Custom aggregation function
- `group_by`: Optional list of columns to group by
- `name`: Optional name for the operation

**Returns:** Self for method chaining

#### `execute(optimize=True)`
Execute the pipeline and return a new DataFrame with results.

**Parameters:**
- `optimize`: Whether to apply optimizations (default: True)

**Returns:** New DataFrame with results

#### `collect()`
Execute the pipeline and return results as a list of dictionaries.

**Returns:** List of row dictionaries

### Optimizer

#### `__init__()`
Create a new Optimizer with default RBO rules.

#### `optimize(operations)`
Apply optimization rules to a list of operations.

**Parameters:**
- `operations`: List of operation dictionaries

**Returns:** Optimized list of operations

#### `add_rule(rule_func)`
Add a custom optimization rule.

**Parameters:**
- `rule_func`: Function that takes operations list and returns optimized list

## Running Tests

```bash
pytest tests/
```

## Development

### Project Structure

```
veloxdf/
├── veloxdf/           # Main package
│   ├── __init__.py    # Package initialization
│   ├── dataframe.py   # DataFrame implementation
│   └── optimizer.py   # Optimizer with RBO
├── tests/             # Test suite
│   ├── test_dataframe.py
│   ├── test_optimizer.py
│   └── test_init.py
├── setup.py           # Package configuration
├── requirements.txt   # Dependencies
└── README.md          # This file
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run tests: `pytest tests/`
6. Submit a pull request

## License

This project is provided as-is for educational and development purposes.

## Examples

### Example 1: Sales Analysis

```python
from veloxdf import DataFrame

sales_data = [
    {"product": "A", "region": "North", "amount": 100, "quantity": 5},
    {"product": "B", "region": "South", "amount": 200, "quantity": 10},
    {"product": "A", "region": "South", "amount": 150, "quantity": 7},
    {"product": "B", "region": "North", "amount": 180, "quantity": 9},
]

df = DataFrame(data=sales_data)

# Calculate total sales by product
result = df.agg(
    {"total_amount": ("amount", "sum"), "total_quantity": ("quantity", "sum")},
    group_by=["product"]
).collect()

print(result)
# [{"product": "A", "total_amount": 250, "total_quantity": 12},
#  {"product": "B", "total_amount": 380, "total_quantity": 19}]
```

### Example 2: Data Cleaning Pipeline

```python
# Filter, transform, and aggregate in a pipeline
result = (df
    .filter(lambda row: row["amount"] > 120)  # Keep high-value sales
    .map(lambda row: {**row, "avg_price": row["amount"] / row["quantity"]})
    .agg(
        {"max_price": ("avg_price", "max"), "count": "count"},
        group_by=["region"]
    )
    .collect())
```

## Roadmap

Future enhancements may include:
- Additional optimization rules (e.g., projection pushdown)
- Join operations
- Window functions
- Lazy evaluation with physical execution planning
- Integration with actual Velox engine
- Performance benchmarking tools

