# Relational Mapper Skill

## Description
Multi-table relationship detection and synthetic relational data generation. Handles foreign keys, referential integrity, and complex database schemas.

## Purpose
This custom skill enhances the synthetic data generator with:
- Multi-table schema detection
- Foreign key relationship inference
- Referential integrity maintenance
- Relational database generation
- Complex dependency management

## When to Use
Use this skill when:
- Generating multi-table synthetic databases
- Maintaining foreign key relationships
- Creating related datasets
- Building complex database schemas
- Testing relational database applications

## Capabilities

### 1. Relationship Detection
- **Primary Keys**: Identify primary key columns
- **Foreign Keys**: Detect foreign key relationships
- **One-to-One**: 1:1 relationships
- **One-to-Many**: 1:N relationships
- **Many-to-Many**: N:M relationships via junction tables
- **Self-Referencing**: Hierarchical relationships

### 2. Schema Mapping
- **Entity-Relationship Diagrams**: Build ER diagrams
- **Table Dependencies**: Determine generation order
- **Cardinality Detection**: Identify relationship cardinality
- **Cascade Rules**: Detect ON DELETE/UPDATE rules
- **Composite Keys**: Handle multi-column keys

### 3. Referential Integrity
- **Foreign Key Constraints**: Maintain valid references
- **Cascade Operations**: Handle cascading updates/deletes
- **Orphan Prevention**: Prevent orphaned records
- **Circular Dependencies**: Handle circular references
- **Constraint Validation**: Validate all constraints

### 4. Multi-Table Generation
- **Dependency Order**: Generate tables in correct order
- **Coordinated Generation**: Maintain relationships during generation
- **Batch Generation**: Generate related records in batches
- **Transaction Support**: Ensure atomic operations
- **Scalability**: Handle large multi-table schemas

## Usage Instructions

### Step 1: Analyze Multi-Table Schema
```python
# Analyze multiple related pattern files
relational_analysis = await analyze_relational_schema({
    "tables": {
        "customers": "customers_sample.csv",
        "orders": "orders_sample.csv",
        "order_items": "order_items_sample.csv",
        "products": "products_sample.csv"
    },
    "detect_relationships": True  # Activates this skill
})

# Review detected relationships
relationships = relational_analysis["relationships"]
for rel in relationships:
    print(f"{rel['from_table']}.{rel['from_column']} -> "
          f"{rel['to_table']}.{rel['to_column']} "
          f"({rel['relationship_type']})")
```

### Step 2: Define or Refine Relationships
```python
# Manually specify or refine relationships
relationship_config = {
    "relationships": [
        {
            "from_table": "orders",
            "from_column": "customer_id",
            "to_table": "customers",
            "to_column": "id",
            "type": "many_to_one",
            "on_delete": "CASCADE"
        },
        {
            "from_table": "order_items",
            "from_column": "order_id",
            "to_table": "orders",
            "to_column": "id",
            "type": "many_to_one",
            "on_delete": "CASCADE"
        },
        {
            "from_table": "order_items",
            "from_column": "product_id",
            "to_table": "products",
            "to_column": "id",
            "type": "many_to_one",
            "on_delete": "RESTRICT"
        }
    ]
}
```

### Step 3: Generate Relational Data
```python
# Generate all related tables
generation_result = await generate_relational_data({
    "schema": relational_analysis["schema"],
    "relationships": relationship_config["relationships"],
    "num_records": {
        "customers": 1000,
        "orders": 5000,  # 5 orders per customer on average
        "order_items": 15000,  # 3 items per order on average
        "products": 500
    },
    "maintain_referential_integrity": True
})
```

### Step 4: Export to Database Format
```python
# Export as SQL with relationships
export_result = await export_data_tool({
    "format": "sql",
    "output_path": "database_dump.sql",
    "session_id": generation_result["session_id"],
    "options": {
        "include_create_tables": True,
        "include_foreign_keys": True,
        "include_indexes": True
    }
})
```

## Relationship Detection Algorithms

### Foreign Key Detection
```python
def detect_foreign_key(from_table, from_column, to_table, to_column):
    """
    Detect if from_column references to_column
    """
    # Check 1: Name similarity
    if is_fk_naming_pattern(from_column, to_column):
        confidence = 0.7
    else:
        confidence = 0.3

    # Check 2: Value overlap
    from_values = set(from_table[from_column].unique())
    to_values = set(to_table[to_column].unique())
    overlap = len(from_values & to_values) / len(from_values)

    if overlap > 0.9:
        confidence += 0.3
    elif overlap > 0.7:
        confidence += 0.2

    # Check 3: Data type compatibility
    if from_table[from_column].dtype == to_table[to_column].dtype:
        confidence += 0.1

    # Check 4: Cardinality
    if is_many_to_one_cardinality(from_table, from_column, to_table, to_column):
        confidence += 0.1

    return {
        "is_foreign_key": confidence > 0.8,
        "confidence": confidence,
        "overlap_ratio": overlap
    }
```

### Cardinality Detection
```python
def detect_cardinality(table1, col1, table2, col2):
    """
    Determine relationship cardinality
    """
    # Count unique values
    unique_in_table1 = table1[col1].nunique()
    unique_in_table2 = table2[col2].nunique()

    # Count duplicates
    dup_rate_table1 = 1 - (unique_in_table1 / len(table1))
    dup_rate_table2 = 1 - (unique_in_table2 / len(table2))

    if dup_rate_table1 < 0.01 and dup_rate_table2 < 0.01:
        return "one_to_one"
    elif dup_rate_table1 > 0.5 and dup_rate_table2 < 0.01:
        return "many_to_one"
    elif dup_rate_table1 < 0.01 and dup_rate_table2 > 0.5:
        return "one_to_many"
    else:
        return "many_to_many"
```

### Dependency Order Calculation
```python
def calculate_generation_order(tables, relationships):
    """
    Topologically sort tables based on foreign key dependencies
    """
    # Build dependency graph
    graph = {}
    for table in tables:
        graph[table] = []

    for rel in relationships:
        # from_table depends on to_table
        graph[rel["from_table"]].append(rel["to_table"])

    # Topological sort (Kahn's algorithm)
    order = []
    in_degree = {table: 0 for table in tables}

    for table in graph:
        for dep in graph[table]:
            in_degree[dep] += 1

    queue = [t for t in tables if in_degree[t] == 0]

    while queue:
        table = queue.pop(0)
        order.append(table)

        for dep in graph[table]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    if len(order) != len(tables):
        raise CircularDependencyError("Circular dependencies detected")

    return order
```

## Relational Schema Output

### Detected Schema
```json
{
  "tables": {
    "customers": {
      "primary_key": "id",
      "columns": {
        "id": {"type": "integer", "nullable": false, "unique": true},
        "email": {"type": "string", "nullable": false, "unique": true},
        "name": {"type": "string", "nullable": false},
        "created_at": {"type": "timestamp", "nullable": false}
      }
    },
    "orders": {
      "primary_key": "id",
      "columns": {
        "id": {"type": "integer", "nullable": false, "unique": true},
        "customer_id": {"type": "integer", "nullable": false},
        "order_date": {"type": "date", "nullable": false},
        "total_amount": {"type": "decimal", "nullable": false}
      }
    },
    "order_items": {
      "primary_key": "id",
      "columns": {
        "id": {"type": "integer", "nullable": false, "unique": true},
        "order_id": {"type": "integer", "nullable": false},
        "product_id": {"type": "integer", "nullable": false},
        "quantity": {"type": "integer", "nullable": false},
        "price": {"type": "decimal", "nullable": false}
      }
    }
  },
  "relationships": [
    {
      "name": "fk_orders_customer",
      "from_table": "orders",
      "from_column": "customer_id",
      "to_table": "customers",
      "to_column": "id",
      "type": "many_to_one",
      "cardinality": "N:1",
      "on_delete": "CASCADE",
      "on_update": "CASCADE"
    },
    {
      "name": "fk_order_items_order",
      "from_table": "order_items",
      "from_column": "order_id",
      "to_table": "orders",
      "to_column": "id",
      "type": "many_to_one",
      "cardinality": "N:1",
      "on_delete": "CASCADE",
      "on_update": "CASCADE"
    }
  ],
  "generation_order": ["customers", "orders", "order_items"],
  "dependency_graph": {
    "nodes": ["customers", "orders", "order_items"],
    "edges": [
      {"from": "orders", "to": "customers"},
      {"from": "order_items", "to": "orders"}
    ]
  }
}
```

## Generation Strategy

### Dependency-Aware Generation
```python
# Generate tables in dependency order
for table_name in generation_order:
    # Get parent table data if needed
    parent_data = {}
    for rel in relationships:
        if rel["from_table"] == table_name:
            parent_table = rel["to_table"]
            parent_col = rel["to_column"]
            parent_data[rel["from_column"]] = generated_data[parent_table][parent_col]

    # Generate table with foreign key constraints
    generated_data[table_name] = generate_table(
        schema=schema[table_name],
        num_rows=num_records[table_name],
        foreign_keys=parent_data,
        maintain_integrity=True
    )
```

### Cardinality-Aware Generation
```python
def generate_related_records(parent_records, cardinality_config):
    """
    Generate child records based on cardinality
    """
    child_records = []

    for parent_id in parent_records:
        # Determine number of child records
        if cardinality_config["type"] == "one_to_one":
            num_children = 1
        elif cardinality_config["type"] == "one_to_many":
            # Use Poisson distribution for realistic counts
            avg_children = cardinality_config.get("avg_children", 3)
            num_children = np.random.poisson(avg_children)
        else:  # many_to_many
            num_children = np.random.randint(
                cardinality_config.get("min_children", 1),
                cardinality_config.get("max_children", 10)
            )

        # Generate child records
        for _ in range(num_children):
            child_record = generate_record(
                schema=child_schema,
                foreign_key_value=parent_id
            )
            child_records.append(child_record)

    return child_records
```

## Complex Scenarios

### Many-to-Many Relationships
```python
# Example: Students and Courses (many-to-many via enrollments)
schema = {
    "students": {...},
    "courses": {...},
    "enrollments": {  # Junction table
        "student_id": "FK -> students.id",
        "course_id": "FK -> courses.id",
        "enrollment_date": "date",
        "grade": "string"
    }
}

# Generate junction table with both foreign keys
generate_junction_table(
    table1="students",
    table2="courses",
    junction_table="enrollments",
    avg_links_per_table1_record=5,  # Avg 5 courses per student
    avg_links_per_table2_record=30  # Avg 30 students per course
)
```

### Self-Referencing Relationships
```python
# Example: Employees with manager_id referencing same table
schema = {
    "employees": {
        "id": "integer PRIMARY KEY",
        "name": "string",
        "manager_id": "integer FK -> employees.id",  # Self-reference
        "department": "string"
    }
}

# Generate with hierarchical structure
generate_hierarchical_table(
    schema=schema["employees"],
    num_records=1000,
    levels=4,  # Organization levels
    branching_factor=5  # Avg employees per manager
)
```

### Circular Dependencies
```python
# Example: Tables with circular foreign keys
# Table A -> Table B -> Table C -> Table A

# Strategy 1: Generate in stages
1. Generate Table A without FK to Table C
2. Generate Table B with FK to Table A
3. Generate Table C with FK to Table B
4. Update Table A with FK to Table C

# Strategy 2: Defer constraints
1. Generate all tables without FK constraints
2. Establish relationships after generation
3. Add FK constraints last
```

## SQL Export with Relationships

### CREATE TABLE Statements
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE order_items (
    id INTEGER PRIMARY KEY,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id)
        ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
        ON DELETE RESTRICT
);

CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
```

## Configuration

```yaml
relational_mapper:
  relationship_detection:
    enabled: true
    confidence_threshold: 0.8
    check_naming_patterns: true
    check_value_overlap: true
  generation:
    maintain_referential_integrity: true
    use_transactions: true
    batch_size: 1000
  cardinality:
    one_to_many_avg: 3
    many_to_many_avg: 5
  export:
    include_foreign_keys: true
    include_indexes: true
    include_constraints: true
```

## Best Practices

1. **Analyze First**: Analyze all tables before generation
2. **Verify Relationships**: Review detected relationships
3. **Test Small**: Generate small datasets first
4. **Check Integrity**: Validate referential integrity
5. **Use Transactions**: Ensure atomic operations
6. **Index Foreign Keys**: Add indexes for performance
7. **Document Schema**: Maintain ER diagrams

## Performance Optimization

- **Batch Generation**: Generate in batches for large datasets
- **Parallel Tables**: Generate independent tables in parallel
- **Index Creation**: Defer index creation until after inserts
- **Constraint Checking**: Defer constraint validation
- **Memory Management**: Stream large tables to disk

## Example Use Cases

### E-commerce Database
```python
tables = {
    "customers": 10000,
    "products": 1000,
    "orders": 50000,
    "order_items": 150000,
    "reviews": 75000,
    "categories": 50,
    "product_categories": 2000  # many-to-many
}
```

### Social Network
```python
tables = {
    "users": 100000,
    "posts": 500000,
    "comments": 2000000,
    "likes": 5000000,
    "friendships": 200000  # many-to-many self-reference
}
```

### Healthcare System
```python
tables = {
    "patients": 50000,
    "doctors": 500,
    "appointments": 200000,
    "prescriptions": 300000,
    "medications": 1000,
    "diagnoses": 5000
}
```

## Error Handling

- **Circular Dependencies**: Detect and resolve
- **Missing References**: Create parent records first
- **Constraint Violations**: Validate before insert
- **Orphaned Records**: Prevent with CASCADE rules
- **Type Mismatches**: Ensure compatible FK types

## Support

For relational mapping issues:
1. Review detected relationships
2. Verify generation order
3. Check referential integrity
4. Validate cardinality settings
5. Test with small datasets first
