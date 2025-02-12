# EuroTempl System

EuroTempl is a comprehensive parametric design and component management system built as a modular monolith. It combines the development simplicity of monolithic architecture with the scalability potential of microservices, enabling efficient creation and management of modular studio spaces and furniture with a focus on acoustics, noise insulation, and manufacturing efficiency.

## Core Features

The system provides powerful capabilities for parametric design and component management:

- Full parametric modeling with FreeCAD integration
- Spatial data handling with PostGIS for 3D operations
- Component and material management with comprehensive classification
- Version-controlled documentation system
- Bill of Materials (BOM) generation and management
- REST API with complete OpenAPI documentation

## Technology Stack

### Backend
- Django 4.2+ with Django REST Framework
- PostgreSQL 15+ with PostGIS extension
- Redis for caching and performance optimization
- Python 3.11+ for FreeCAD integration
- Token-based authentication system

### Frontend
- React 18+ with TypeScript
- Tailwind CSS for styling
- React Query for state management
- React Router for navigation

## Project Structure

The project follows a domain-driven vertical slice architecture:

```
/backend
  /core              # Base models and interfaces
  /components        # Component management domain
  /parameters        # Parameter management domain
  /materials         # Material management domain
  /geometry          # Spatial operations domain
  /docs              # Documentation management
  /api               # REST API endpoints
  /tests             # Test suites
  /cad_engine        # Handles FreeCAD integrations
  /core_logic        # Key system algorithms
  /utils             # Includes utility modules used across the engine.
/frontend
  /src
    /components      # Reusable UI components
    /features        # Domain-specific features
    /services        # API integration
    /utils           # Helper functions
    /types           # TypeScript definitions
    /tests           # Frontend tests
```

## Getting Started

### Prerequisites

Before setting up the project, ensure you have:

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with PostGIS
- FreeCAD with Python API

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourorg/eurotempl.git
   cd eurotempl
   ```

2. Create and activate a virtual environment:
   ```bash
   conda env create -f environment.yml
   conda activate EuroTempl  
# verify the installation
   python -c "import django; print(django.__version__)"
   python -c "import FreeCAD; print(FreeCAD.Version())"
   ```

3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

5. Set up the database:
   ```bash
   cd backend
   python manage.py migrate
   ```

6. Start the development servers:
   ```bash
   # Backend
   python manage.py runserver

   # Frontend
   cd frontend
   npm start
   ```

7. Build cad_engine cpp bindings :

```bash
cd backend/cad_engine
python setup.py build_ext --inplace   
```

8. build the C++ extensions for the parameters module:

   ```bash
   cd backend/parameters/build
   cmake ..
   cmake --build .
   ```
9. build the C++ extensions for the geometry module:

   ```bash
   cd backend/geometry
   ./build.sh
   ```

10. Run the tests:

   ```bash
   pytest
   ```

## Development Guidelines

### Code Quality

We maintain high code quality standards through:

- Comprehensive automated testing
- Regular code reviews
- Consistent code formatting
- Type checking with TypeScript
- Documentation requirements

### Architecture Principles

The system follows these key architectural principles:

- Modular design with clear boundaries
- Domain-driven development
- Clean architecture patterns
- Vertical slice architecture
- SOLID principles

### Testing

Run the test suites:

```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test
```

## Documentation

- API documentation is available at `/api/docs/` when running the server
- Component documentation can be found in the `/docs` directory
- Additional technical documentation is maintained in the wiki

## Deployment

The system can be deployed using Docker:

```bash
docker-compose up -d
```

Configuration for different environments is managed through environment variables defined in `.env` files.

## Contributing

Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

## License

This project is licensed under a proprietary License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- Create an issue in the GitHub repository
- Contact the development team at dev@eurotemp.org
- Check our [FAQ](FAQ.md) for common questions

## Acknowledgments

Special thanks to:
- The FreeCAD community for their excellent CAD platform
- PostgreSQL and PostGIS teams for spatial database capabilities
- All contributors who have helped shape this project