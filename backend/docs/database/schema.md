# Kundli Calculation WebService Database Schema

## Core Tables

### 1. Users
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false
);

CREATE INDEX idx_users_email ON users(email);
```

### 2. Birth Charts
```sql
CREATE TABLE birth_charts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    name VARCHAR(255) NOT NULL,
    birth_time TIMESTAMP WITH TIME ZONE NOT NULL,
    latitude DECIMAL(9,6) NOT NULL,
    longitude DECIMAL(9,6) NOT NULL,
    timezone VARCHAR(50) NOT NULL,
    place_name VARCHAR(255),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_birth_charts_user_id ON birth_charts(user_id);
CREATE INDEX idx_birth_charts_birth_time ON birth_charts(birth_time);
```

### 3. Planetary Positions
```sql
CREATE TABLE planetary_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    birth_chart_id UUID REFERENCES birth_charts(id) ON DELETE CASCADE,
    planet VARCHAR(50) NOT NULL,
    longitude DECIMAL(12,8) NOT NULL,
    latitude DECIMAL(12,8),
    speed DECIMAL(12,8),
    house_position INTEGER,
    is_retrograde BOOLEAN,
    dignity_status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_planetary_positions_birth_chart ON planetary_positions(birth_chart_id);
```

### 4. House Systems
```sql
CREATE TABLE house_systems (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    birth_chart_id UUID REFERENCES birth_charts(id) ON DELETE CASCADE,
    house_number INTEGER NOT NULL CHECK (house_number BETWEEN 1 AND 12),
    cusp_longitude DECIMAL(12,8) NOT NULL,
    sign VARCHAR(50) NOT NULL,
    degree DECIMAL(12,8) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_house_systems_birth_chart ON house_systems(birth_chart_id);
```

### 5. Divisional Charts
```sql
CREATE TABLE divisional_charts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    birth_chart_id UUID REFERENCES birth_charts(id) ON DELETE CASCADE,
    division_type VARCHAR(50) NOT NULL, -- D1, D2, D3, etc.
    planet VARCHAR(50) NOT NULL,
    longitude DECIMAL(12,8) NOT NULL,
    house_position INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_divisional_charts_birth_chart ON divisional_charts(birth_chart_id);
CREATE INDEX idx_divisional_charts_type ON divisional_charts(division_type);
```

### 6. Dasha Periods
```sql
CREATE TABLE dasha_periods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    birth_chart_id UUID REFERENCES birth_charts(id) ON DELETE CASCADE,
    dasha_type VARCHAR(50) NOT NULL, -- Vimshottari, Yogini, etc.
    planet VARCHAR(50) NOT NULL,
    sub_planet VARCHAR(50),
    sub_sub_planet VARCHAR(50),
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dasha_periods_birth_chart ON dasha_periods(birth_chart_id);
CREATE INDEX idx_dasha_periods_date_range ON dasha_periods(start_date, end_date);
```

### 7. Yoga Combinations
```sql
CREATE TABLE yoga_combinations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    birth_chart_id UUID REFERENCES birth_charts(id) ON DELETE CASCADE,
    yoga_type VARCHAR(100) NOT NULL,
    description TEXT,
    strength DECIMAL(5,2),
    planets_involved JSONB,
    houses_involved JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_yoga_combinations_birth_chart ON yoga_combinations(birth_chart_id);
```

### 8. Astrological Calculations
```sql
CREATE TABLE astrological_calculations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    birth_chart_id UUID REFERENCES birth_charts(id) ON DELETE CASCADE,
    calculation_type VARCHAR(100) NOT NULL,
    input_parameters JSONB NOT NULL,
    result JSONB NOT NULL,
    calculation_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    cache_valid_until TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_astrological_calculations_birth_chart ON astrological_calculations(birth_chart_id);
CREATE INDEX idx_astrological_calculations_type ON astrological_calculations(calculation_type);
```

## Reference Tables

### 9. Astrological References
```sql
CREATE TABLE astrological_references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    reference_type VARCHAR(100) NOT NULL,
    reference_key VARCHAR(100) NOT NULL,
    reference_value JSONB NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_astrological_references_type_key ON astrological_references(reference_type, reference_key);
```

## Performance Optimization

### Partitioning Strategy
- Birth charts table partitioned by creation date (monthly)
- Planetary positions partitioned by birth_chart_id
- Dasha periods partitioned by date range

### Indexing Strategy
- B-tree indexes on frequently queried columns
- GiST indexes for geometric calculations
- Partial indexes for specific queries

## Data Integrity Rules

### Cascading Deletes
- All child records cascade on birth chart deletion
- User deletion sets birth chart user_id to NULL

### Constraints
- Valid latitude range: -90 to 90
- Valid longitude range: -180 to 180
- Valid house numbers: 1 to 12
- Valid date ranges for dasha periods

## Maintenance Procedures

### Archiving Strategy
```sql
CREATE TABLE archived_birth_charts (LIKE birth_charts);
CREATE TABLE archived_calculations (LIKE astrological_calculations);

-- Archive procedure
CREATE OR REPLACE PROCEDURE archive_old_data(cutoff_date DATE)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO archived_birth_charts 
    SELECT * FROM birth_charts 
    WHERE created_at < cutoff_date;
    
    DELETE FROM birth_charts 
    WHERE created_at < cutoff_date;
END;
$$;
```

### Cleanup Procedures
```sql
CREATE OR REPLACE PROCEDURE cleanup_expired_calculations()
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM astrological_calculations 
    WHERE cache_valid_until < CURRENT_TIMESTAMP;
END;
$$;
```
