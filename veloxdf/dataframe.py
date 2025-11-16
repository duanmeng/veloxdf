"""DataFrame implementation for VeloxDF."""

from typing import Any, Callable, Dict, List, Optional, Union


class DataFrame:
    """A simple DataFrame class for Velox.
    
    This class provides a pipeline API for describing operations like map,
    filter, and aggregate. Operations are collected and can be optimized
    before execution.
    """
    
    def __init__(self, data: Optional[List[Dict[str, Any]]] = None, 
                 schema: Optional[Dict[str, type]] = None):
        """Initialize a DataFrame.
        
        Args:
            data: Initial data as a list of dictionaries
            schema: Schema defining column names and types
        """
        self._data = data if data is not None else []
        self._schema = schema if schema is not None else {}
        self._operations: List[Dict[str, Any]] = []
        self._optimized = False
        
    @property
    def schema(self) -> Dict[str, type]:
        """Get the schema of the DataFrame."""
        return self._schema
    
    @property
    def data(self) -> List[Dict[str, Any]]:
        """Get the data of the DataFrame."""
        return self._data
    
    @property
    def operations(self) -> List[Dict[str, Any]]:
        """Get the list of operations in the pipeline."""
        return self._operations
    
    def map(self, func: Callable[[Dict[str, Any]], Dict[str, Any]], 
            name: Optional[str] = None) -> "DataFrame":
        """Apply a map operation to each row.
        
        Args:
            func: Function to apply to each row
            name: Optional name for the operation
            
        Returns:
            Self for method chaining
        """
        self._operations.append({
            "type": "map",
            "func": func,
            "name": name or "map"
        })
        return self
    
    def filter(self, predicate: Callable[[Dict[str, Any]], bool],
               name: Optional[str] = None) -> "DataFrame":
        """Filter rows based on a predicate.
        
        Args:
            predicate: Function that returns True for rows to keep
            name: Optional name for the operation
            
        Returns:
            Self for method chaining
        """
        self._operations.append({
            "type": "filter",
            "predicate": predicate,
            "name": name or "filter"
        })
        return self
    
    def agg(self, aggregations: Dict[str, Union[str, Callable, tuple]],
            group_by: Optional[List[str]] = None,
            name: Optional[str] = None) -> "DataFrame":
        """Perform aggregation operations.
        
        Args:
            aggregations: Dictionary mapping output column names to 
                         aggregation specifications. Each value can be:
                         - A string function name ("sum", "count", "avg", "min", "max")
                           which will aggregate the column with same name as output
                         - A tuple of (column_name, function) for aggregating a specific column
                         - A custom callable function
            group_by: Optional list of columns to group by
            name: Optional name for the operation
            
        Returns:
            Self for method chaining
        """
        self._operations.append({
            "type": "agg",
            "aggregations": aggregations,
            "group_by": group_by,
            "name": name or "agg"
        })
        return self
    
    def execute(self, optimize: bool = True) -> "DataFrame":
        """Execute the pipeline of operations.
        
        Args:
            optimize: Whether to apply optimizations before execution
            
        Returns:
            A new DataFrame with the results
        """
        operations = self._operations.copy()
        
        # Apply optimizations if requested
        if optimize and not self._optimized:
            from .optimizer import Optimizer
            optimizer = Optimizer()
            operations = optimizer.optimize(operations)
        
        # Execute operations
        result_data = self._data.copy()
        
        for op in operations:
            if op["type"] == "map":
                result_data = [op["func"](row) for row in result_data]
            elif op["type"] == "filter":
                result_data = [row for row in result_data if op["predicate"](row)]
            elif op["type"] == "agg":
                result_data = self._execute_agg(result_data, op)
        
        # Create new DataFrame with results
        result_df = DataFrame(data=result_data, schema=self._schema.copy())
        result_df._optimized = True
        return result_df
    
    def _execute_agg(self, data: List[Dict[str, Any]], 
                     op: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute an aggregation operation.
        
        Args:
            data: Input data
            op: Aggregation operation details
            
        Returns:
            Aggregated data
        """
        aggregations = op["aggregations"]
        group_by = op.get("group_by", [])
        
        if not group_by:
            # No grouping, aggregate all data
            result = {}
            for output_col, agg_spec in aggregations.items():
                # Determine input column and function
                if isinstance(agg_spec, tuple):
                    # Tuple format: (column_name, function)
                    input_col, agg_func = agg_spec
                elif isinstance(agg_spec, str):
                    # String format: use output column name as input column
                    input_col = output_col
                    agg_func = agg_spec
                else:
                    # Custom callable
                    input_col = None
                    agg_func = agg_spec
                
                if isinstance(agg_func, str):
                    # Built-in aggregation function
                    if agg_func == "count":
                        result[output_col] = len(data)
                    elif agg_func == "sum":
                        values = [row.get(input_col, 0) for row in data]
                        result[output_col] = sum(values)
                    elif agg_func == "avg":
                        values = [row.get(input_col, 0) for row in data]
                        result[output_col] = sum(values) / len(values) if values else 0
                    elif agg_func == "min":
                        values = [row.get(input_col) for row in data if input_col in row]
                        result[output_col] = min(values) if values else None
                    elif agg_func == "max":
                        values = [row.get(input_col) for row in data if input_col in row]
                        result[output_col] = max(values) if values else None
                else:
                    # Custom aggregation function
                    result[output_col] = agg_func(data)
            return [result]
        else:
            # Group by columns
            groups: Dict[tuple, List[Dict[str, Any]]] = {}
            for row in data:
                key = tuple(row.get(col) for col in group_by)
                if key not in groups:
                    groups[key] = []
                groups[key].append(row)
            
            # Aggregate each group
            results = []
            for key, group_data in groups.items():
                result = {}
                # Add group by columns
                for i, col in enumerate(group_by):
                    result[col] = key[i]
                # Add aggregations
                for output_col, agg_spec in aggregations.items():
                    # Determine input column and function
                    if isinstance(agg_spec, tuple):
                        input_col, agg_func = agg_spec
                    elif isinstance(agg_spec, str):
                        input_col = output_col
                        agg_func = agg_spec
                    else:
                        input_col = None
                        agg_func = agg_spec
                    
                    if isinstance(agg_func, str):
                        if agg_func == "count":
                            result[output_col] = len(group_data)
                        elif agg_func == "sum":
                            values = [row.get(input_col, 0) for row in group_data]
                            result[output_col] = sum(values)
                        elif agg_func == "avg":
                            values = [row.get(input_col, 0) for row in group_data]
                            result[output_col] = sum(values) / len(values) if values else 0
                        elif agg_func == "min":
                            values = [row.get(input_col) for row in group_data if input_col in row]
                            result[output_col] = min(values) if values else None
                        elif agg_func == "max":
                            values = [row.get(input_col) for row in group_data if input_col in row]
                            result[output_col] = max(values) if values else None
                    else:
                        result[output_col] = agg_func(group_data)
                results.append(result)
            return results
    
    def collect(self) -> List[Dict[str, Any]]:
        """Execute the pipeline and return the results as a list.
        
        Returns:
            List of dictionaries containing the result data
        """
        return self.execute().data
    
    def __repr__(self) -> str:
        """String representation of the DataFrame."""
        return f"DataFrame(rows={len(self._data)}, operations={len(self._operations)})"
