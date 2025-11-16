#!/usr/bin/env python3
"""Example demonstrating VeloxDF usage."""

from veloxdf import DataFrame

def main():
    print("=== VeloxDF Example ===\n")
    
    # Example 1: Basic filtering and mapping
    print("Example 1: Filter and Map")
    print("-" * 40)
    employees = [
        {"id": 1, "name": "Alice", "age": 30, "salary": 70000, "department": "Engineering"},
        {"id": 2, "name": "Bob", "age": 25, "salary": 50000, "department": "Sales"},
        {"id": 3, "name": "Charlie", "age": 35, "salary": 80000, "department": "Engineering"},
        {"id": 4, "name": "Diana", "age": 28, "salary": 60000, "department": "Sales"},
    ]
    
    df = DataFrame(data=employees)
    
    # Filter employees older than 27 and give them a 10% bonus
    result = (df
        .filter(lambda row: row["age"] > 27)
        .map(lambda row: {**row, "bonus": row["salary"] * 0.1})
        .collect())
    
    print("Employees over 27 with bonus:")
    for emp in result:
        print(f"  {emp['name']}: salary=${emp['salary']}, bonus=${emp['bonus']}")
    
    # Example 2: Aggregation by department
    print("\n\nExample 2: Aggregation by Department")
    print("-" * 40)
    
    result = df.agg(
        {
            "avg_salary": ("salary", "avg"),
            "total_employees": "count",
            "max_age": ("age", "max")
        },
        group_by=["department"]
    ).collect()
    
    print("Department statistics:")
    for dept in result:
        print(f"  {dept['department']}:")
        print(f"    Average Salary: ${dept['avg_salary']:.2f}")
        print(f"    Total Employees: {dept['total_employees']}")
        print(f"    Max Age: {dept['max_age']}")
    
    # Example 3: Complex pipeline with optimization
    print("\n\nExample 3: Complex Pipeline (with automatic optimization)")
    print("-" * 40)
    
    sales_data = [
        {"product": "Laptop", "category": "Electronics", "price": 1200, "quantity": 5, "region": "North"},
        {"product": "Phone", "category": "Electronics", "price": 800, "quantity": 10, "region": "South"},
        {"product": "Desk", "category": "Furniture", "price": 300, "quantity": 3, "region": "North"},
        {"product": "Chair", "category": "Furniture", "price": 150, "quantity": 8, "region": "South"},
        {"product": "Tablet", "category": "Electronics", "price": 500, "quantity": 7, "region": "North"},
    ]
    
    df = DataFrame(data=sales_data)
    
    # Complex pipeline: filter high-value items, calculate revenue, aggregate by category
    result = (df
        .map(lambda row: {**row, "revenue": row["price"] * row["quantity"]})
        .filter(lambda row: row["price"] > 200)  # Filter will be pushed earlier by optimizer
        .filter(lambda row: row["quantity"] > 4)  # Multiple filters will be combined
        .agg(
            {
                "total_revenue": ("revenue", "sum"),
                "avg_price": ("price", "avg"),
                "product_count": "count"
            },
            group_by=["category"]
        )
        .collect())
    
    print("Sales analysis for high-value, high-quantity items:")
    for cat in result:
        print(f"  {cat['category']}:")
        print(f"    Total Revenue: ${cat['total_revenue']:.2f}")
        print(f"    Average Price: ${cat['avg_price']:.2f}")
        print(f"    Product Count: {cat['product_count']}")
    
    print("\n✓ All examples completed successfully!")
    print("Note: The optimizer automatically applied filter pushdown and filter combination")
    print("      to improve query execution efficiency.")

if __name__ == "__main__":
    main()
