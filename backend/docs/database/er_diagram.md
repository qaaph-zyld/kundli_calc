# Entity Relationship Diagram Documentation

## Core Entities

### Users
- Primary entity for user management
- Relationships:
  - One-to-Many with Birth Charts
  - One-to-Many with Calculations

### Birth Charts
- Central entity for horoscope data
- Relationships:
  - Many-to-One with Users
  - One-to-Many with Planetary Positions
  - One-to-Many with House Systems
  - One-to-Many with Divisional Charts
  - One-to-Many with Dasha Periods
  - One-to-Many with Yoga Combinations

### Planetary Positions
- Stores planetary data for birth charts
- Relationships:
  - Many-to-One with Birth Charts
  - Referenced in Yoga Combinations

### House Systems
- Contains house cusps and related data
- Relationships:
  - Many-to-One with Birth Charts
  - Referenced in Yoga Combinations

## Calculation Entities

### Divisional Charts
- Stores D1-D60 chart data
- Relationships:
  - Many-to-One with Birth Charts
  - Referenced in Calculations

### Dasha Periods
- Time period calculations
- Relationships:
  - Many-to-One with Birth Charts
  - Referenced in Predictions

### Yoga Combinations
- Planetary combinations and effects
- Relationships:
  - Many-to-One with Birth Charts
  - References Planetary Positions
  - References House Systems

## Reference Entities

### Astrological References
- Lookup tables for calculations
- Relationships:
  - Referenced by multiple calculation entities
  - No direct foreign keys

## Performance Considerations

### Indexing Strategy
- Primary Keys: UUID for horizontal scaling
- Foreign Keys: B-tree indexes
- Temporal Data: Date-based indexes
- Spatial Data: GiST indexes for coordinates

### Partitioning Strategy
- Birth Charts: Range partitioning by date
- Calculations: Hash partitioning by birth_chart_id
- Historical Data: Archive partitioning

## Data Flow

### Calculation Flow
1. User creates birth chart
2. System calculates planetary positions
3. House systems are computed
4. Divisional charts are generated
5. Dasha periods are calculated
6. Yoga combinations are identified

### Cache Flow
1. Results stored in astrological_calculations
2. Cache invalidation based on time
3. Recalculation triggers on cache miss

## Diagram Notes

The complete ER diagram can be found in the attached draw.io file: `er_diagram.drawio`

Key relationships are marked with:
- Solid lines: Required relationships
- Dotted lines: Optional relationships
- Crow's foot: Many relationship
- Single line: One relationship
