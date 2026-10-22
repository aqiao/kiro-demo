from app.config import DEFAULT_DUCKDB_FEASIBILITY_PATH, validate_duckdb_feasibility

if __name__ == "__main__":
    validate_duckdb_feasibility(DEFAULT_DUCKDB_FEASIBILITY_PATH)
    print(f"DuckDB feasibility gate passed: {DEFAULT_DUCKDB_FEASIBILITY_PATH}")
