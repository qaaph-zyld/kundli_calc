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

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
