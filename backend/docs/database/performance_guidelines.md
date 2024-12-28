# Database Performance Optimization Guidelines

## 1. Indexing Strategy

### Primary Indexes
```sql
-- Example of efficient index creation
CREATE INDEX CONCURRENTLY idx_birth_charts_composite 
ON birth_charts (user_id, birth_time);

-- Partial index for active users
CREATE INDEX idx_active_users 
ON users (id) 
WHERE is_active = true;
```

### Query Optimization
- Use EXPLAIN ANALYZE for query planning
- Implement covering indexes for frequent queries
- Consider partial indexes for filtered queries
- Use appropriate index types (B-tree, GiST, etc.)

## 2. Partitioning Strategy

### Time-Based Partitioning
```sql
-- Example partition creation
CREATE TABLE birth_charts_partition OF birth_charts
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Automatic partition creation
CREATE OR REPLACE PROCEDURE create_monthly_partition()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Create next month's partition
    -- Implementation details
END;
$$;
```

### Data Distribution
- Partition large tables by date range
- Use hash partitioning for evenly distributed data
- Implement partition pruning in queries

## 3. Caching Strategy

### Query Cache
```sql
-- Cache table structure
CREATE TABLE query_cache (
    cache_key TEXT PRIMARY KEY,
    cache_value JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Cache cleanup
CREATE INDEX idx_query_cache_expiry ON query_cache(expires_at);
```

### Invalidation Strategy
- Time-based invalidation
- Event-based invalidation
- Selective cache updates

## 4. Query Optimization

### Best Practices
```sql
-- Use CTEs for complex queries
WITH planetary_data AS (
    SELECT * FROM planetary_positions
    WHERE birth_chart_id = :id
)
SELECT * FROM planetary_data;

-- Efficient joins
SELECT * 
FROM birth_charts b
JOIN LATERAL (
    SELECT * FROM planetary_positions
    WHERE birth_chart_id = b.id
    LIMIT 1
) pp ON true;
```

### Performance Monitoring
```sql
-- Track slow queries
CREATE TABLE slow_query_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT,
    execution_time INTERVAL,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 5. Connection Management

### Connection Pool Configuration
```python
# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)
```

### Connection Monitoring
```sql
-- Active connection monitoring
SELECT * FROM pg_stat_activity
WHERE state = 'active';
```

## 6. Maintenance Procedures

### Statistics Update
```sql
-- Regular ANALYZE
CREATE OR REPLACE PROCEDURE update_statistics()
LANGUAGE plpgsql
AS $$
BEGIN
    ANALYZE VERBOSE;
END;
$$;
```

### Index Maintenance
```sql
-- Reindex procedure
CREATE OR REPLACE PROCEDURE maintain_indexes()
LANGUAGE plpgsql
AS $$
BEGIN
    REINDEX DATABASE kundli_db;
END;
$$;
```

## 7. Monitoring and Alerting

### Performance Metrics
```sql
-- Performance monitoring view
CREATE VIEW performance_metrics AS
SELECT 
    schemaname,
    relname,
    seq_scan,
    idx_scan,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables;
```

### Alert Thresholds
- Query execution time > 1 second
- Table size > 10GB
- Index bloat > 30%
- Cache hit ratio < 90%

## 8. Backup Strategy

### Backup Procedures
```sql
-- Backup procedure
CREATE OR REPLACE PROCEDURE create_backup()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Implementation details
END;
$$;
```

### Recovery Testing
- Regular recovery testing
- Point-in-time recovery validation
- Backup verification procedures

## 9. Security Optimization

### Access Control
```sql
-- Row-level security
ALTER TABLE birth_charts ENABLE ROW LEVEL SECURITY;

CREATE POLICY birth_charts_access_policy ON birth_charts
    USING (user_id = current_user_id());
```

### Audit Logging
```sql
-- Audit log table
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name TEXT,
    operation TEXT,
    old_data JSONB,
    new_data JSONB,
    user_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## 10. Development Guidelines

### Code Standards
- Use prepared statements
- Implement connection pooling
- Handle database errors gracefully
- Use transactions appropriately

### Testing Requirements
- Performance testing for new queries
- Load testing for critical operations
- Regression testing for optimizations
