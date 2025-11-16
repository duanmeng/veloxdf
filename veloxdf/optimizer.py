"""Optimizer with Rule-Based Optimization (RBO) for VeloxDF."""

from typing import Any, Dict, List


class Optimizer:
    """Optimizer for DataFrame operations using Rule-Based Optimization (RBO).
    
    This optimizer applies various optimization rules to improve query execution,
    such as filter pushdown, operation reordering, and redundant operation elimination.
    """
    
    def __init__(self):
        """Initialize the optimizer."""
        self._rules = [
            self._combine_filters,
            self._filter_pushdown,
        ]
    
    def optimize(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply optimization rules to a list of operations.
        
        Args:
            operations: List of operations to optimize
            
        Returns:
            Optimized list of operations
        """
        optimized = operations.copy()
        
        # Apply each optimization rule
        for rule in self._rules:
            optimized = rule(optimized)
        
        return optimized
    
    def _filter_pushdown(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Push filter operations as early as possible in the pipeline.
        
        Filter pushdown is a key optimization that moves filter operations earlier
        in the execution pipeline to reduce the amount of data processed by
        subsequent operations. Filters are moved before map and aggregation operations
        where possible.
        
        Args:
            operations: List of operations
            
        Returns:
            Optimized list with filters pushed down
        """
        if not operations:
            return operations
        
        # Repeatedly try to push filters earlier until no more changes
        changed = True
        result = operations.copy()
        
        while changed:
            changed = False
            i = 0
            while i < len(result):
                # If current operation is a filter and previous is map or agg, swap them
                if i > 0 and result[i]["type"] == "filter":
                    prev_type = result[i-1]["type"]
                    if prev_type in ["map", "agg"]:
                        # Swap filter with previous operation
                        result[i-1], result[i] = result[i], result[i-1]
                        changed = True
                        continue  # Don't increment i, check this position again
                i += 1
        
        return result
    
    def _combine_filters(self, operations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Combine consecutive filter operations into a single filter.
        
        This optimization merges multiple consecutive filter operations into one,
        reducing the overhead of multiple passes through the data.
        
        Args:
            operations: List of operations
            
        Returns:
            Optimized list with consecutive filters combined
        """
        if not operations:
            return operations
        
        optimized = []
        current_filters = []
        
        for op in operations:
            if op["type"] == "filter":
                current_filters.append(op)
            else:
                # Flush accumulated filters
                if current_filters:
                    if len(current_filters) == 1:
                        optimized.append(current_filters[0])
                    else:
                        # Combine multiple filters into one
                        combined = self._merge_filters(current_filters)
                        optimized.append(combined)
                    current_filters = []
                optimized.append(op)
        
        # Handle remaining filters
        if current_filters:
            if len(current_filters) == 1:
                optimized.append(current_filters[0])
            else:
                combined = self._merge_filters(current_filters)
                optimized.append(combined)
        
        return optimized
    
    def _merge_filters(self, filters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple filter operations into a single filter.
        
        Args:
            filters: List of filter operations to merge
            
        Returns:
            A single merged filter operation
        """
        predicates = [f["predicate"] for f in filters]
        
        def combined_predicate(row):
            """Combined predicate that applies all filters."""
            return all(pred(row) for pred in predicates)
        
        names = [f.get("name", "filter") for f in filters]
        combined_name = f"combined_filter({', '.join(names)})"
        
        return {
            "type": "filter",
            "predicate": combined_predicate,
            "name": combined_name
        }
    
    def add_rule(self, rule_func):
        """Add a custom optimization rule.
        
        Args:
            rule_func: Function that takes a list of operations and returns
                      an optimized list of operations
        """
        self._rules.append(rule_func)
    
    def get_rules(self) -> List:
        """Get the list of optimization rules.
        
        Returns:
            List of optimization rule functions
        """
        return self._rules.copy()
