# -*- coding: utf-8 -*-

from veloxdf import DataFrame


def demo():
    df = DataFrame.from_source("datasource")
    df = df.map("c0 + 1 as c1").filter("c0 > 10")

    print("=" * 40)
    print("1. 原始逻辑计划")
    print("=" * 40)
    print(df)

    df_optimized = df.optimize()

    print("\n" + "=" * 40)
    print("2. 优化后的逻辑计划 (Filter下推)")
    print("=" * 40)
    print(df_optimized)

    print("\n" + "=" * 40)
    print("3. 复杂表达式解析示例")
    print("=" * 40)

    complex_df = (
        DataFrame.from_source("another_table")
        .filter("c0.value > 1 AND starts_with(c1, 'prefix')")
        .map("cardinality(c2) as c2_card")
    )

    print(complex_df)

    print("\n" + "=" * 40)
    print("4. 逻辑计划的 JSON 表示 (美化格式)")
    print("=" * 40)
    json_string_pretty = complex_df.to_json()
    print(json_string_pretty)


if __name__ == "__main__":
    demo()
