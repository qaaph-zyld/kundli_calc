# South Indian Kundli Calculator

A comprehensive web service for calculating and displaying Vedic birth charts in South Indian style.

## Features

- Accurate astronomical calculations using Swiss Ephemeris
- South Indian style chart rendering
- RESTful API endpoints
- Modern, responsive UI
- Traditional design principles

## Requirements

- Python 3.9+
- Poetry for dependency management
- PostgreSQL database
- Node.js and npm (for frontend)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/qaaph-zyld/kundli_calc.git
cd kundli_calc
```

2. Install dependencies:
```bash
poetry install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
poetry run alembic upgrade head
```

5. Run the development server:
```bash
poetry run uvicorn app.main:app --reload
```

## Project Structure

```
kundli/
├── backend/
│   ├── app/
│   │   ├── core/          # Core calculation engine
│   │   ├── api/           # API endpoints
│   │   └── services/      # Business logic
│   ├── tests/             # Test suite
│   └── alembic/           # Database migrations
├── frontend/              # React frontend (to be added)
└── docker/               # Docker configuration
```

## Performance Optimization

The ayanamsa calculation module has been optimized for performance:

- Average calculation time < 1ms per operation
- Multi-system switching overhead < 1.5ms
- Date range calculations < 2ms across extreme ranges
- Performance monitoring via decorators
- Comprehensive test suite for performance validation

Performance metrics are logged automatically and can be monitored through the logging system.

## Validation System

The ayanamsa calculation module includes robust input validation:

- Comprehensive date range validation (1 CE to 9999 CE)
- Ayanamsa system validation with detailed error messages
- Type checking for all inputs
- Performance-optimized validation system
- Extensive test coverage for validation logic

Validation metrics and error messages are logged automatically for monitoring.

## Memory Optimization

The ayanamsa calculation module implements efficient memory management:

- LRU caching for frequently accessed calculations
- Optimized data structures for system mappings
- Memory-efficient Julian Day conversions
- Cached nutation calculations
- Memory usage monitoring and testing

Key metrics:
- Memory usage per calculation < 0.001MB
- Cache hit ratio > 90% for repeated calculations
- Minimal memory footprint for system operations

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
