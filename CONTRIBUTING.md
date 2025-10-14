# Contributing to Agentic Graph RAG

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

---

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/lyzr-hackathon.git
cd lyzr-hackathon

# Add upstream remote
git remote add upstream https://github.com/harshit-codes/lyzr-hackathon.git
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install pytest pytest-cov black ruff mypy
```

### 3. Configure Snowflake

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Snowflake credentials
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
```

### 4. Run Tests

```bash
# Run all tests
pytest code/graph_rag/tests/

# Run with coverage
pytest --cov=code/graph_rag code/graph_rag/tests/

# Run specific test
pytest code/graph_rag/tests/test_models_unit.py -v
```

---

## 📝 Code Style

### Python Conventions

Follow the project's [Nomenclature Guide](https://contactingharshit.gitbook.io/lyzr-hack/appendix#nomenclature--style-guide):

**Naming Conventions**:
- **Classes**: `PascalCase` (e.g., `Project`, `Node`, `StructuredDataValidator`)
- **Functions/Methods**: `snake_case` (e.g., `validate_schema()`, `get_session()`)
- **Variables**: `snake_case` (e.g., `project_id`, `schema_name`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_DIMENSION`)
- **Private attributes**: `_leading_underscore` (e.g., `_internal_cache`)

**Method Prefixes**:
- `is_*` - Boolean predicates (e.g., `is_active()`)
- `has_*` - Existence checks (e.g., `has_vector`)
- `get_*` - Accessors (e.g., `get_attribute()`)
- `set_*` - Single field mutators (e.g., `set_name()`)
- `update_*` - Multiple field mutators (e.g., `update_stats()`)
- `validate_*` - Validation methods (e.g., `validate_schema()`)

### Type Hints

Always use type hints:

```python
from typing import Optional, List, Dict, Any
from uuid import UUID

def create_node(
    node_name: str,
    entity_type: str,
    structured_data: Dict[str, Any],
    project_id: UUID
) -> Node:
    """Create a new node with validation."""
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> tuple[bool, str]:
    """Validate data against schema definition.
    
    Args:
        data: Data to validate
        schema: Schema definition with types and constraints
        
    Returns:
        Tuple of (is_valid, error_message). error_message is empty if valid.
        
    Example:
        >>> schema = {"name": {"type": "string", "required": True}}
        >>> validate_schema({"name": "Alice"}, schema)
        (True, "")
    """
    pass
```

### Code Formatting

```bash
# Format code with black
black code/

# Lint with ruff
ruff check code/

# Type check with mypy
mypy code/graph_rag/
```

---

## 🧪 Testing

### Writing Tests

- Place tests in `code/graph_rag/tests/`
- Follow naming: `test_<module>_<function>.py`
- Use descriptive test names: `test_node_creation_with_valid_data()`
- Test edge cases and error conditions

Example test:

```python
import pytest
from code.graph_rag.models import Node
from uuid import uuid4

def test_node_creation_with_valid_data():
    """Test creating a node with valid structured data."""
    node = Node(
        node_name="test_node",
        entity_type="Person",
        schema_id=uuid4(),
        structured_data={"name": "Alice", "age": 30},
        project_id=uuid4()
    )
    
    assert node.node_name == "test_node"
    assert node.structured_data["name"] == "Alice"
    assert node.entity_type == "Person"

def test_node_creation_fails_with_invalid_data():
    """Test that node creation fails with invalid data."""
    with pytest.raises(ValidationError):
        Node(
            node_name="",  # Empty name should fail
            entity_type="Person",
            schema_id=uuid4(),
            structured_data={},
            project_id=uuid4()
        )
```

### Test Coverage

- Maintain >80% code coverage
- Every new feature must include tests
- Bug fixes should include regression tests

---

## 🔀 Git Workflow

### Branch Naming

- Feature: `feature/superscan-pdf-upload`
- Bug fix: `fix/schema-validation-error`
- Documentation: `docs/update-readme`
- Refactor: `refactor/database-connection`

### Commit Messages

Follow conventional commits:

```
feat: add PDF parsing for SuperScan
fix: correct schema validation for optional fields
docs: update architecture documentation
refactor: simplify node creation logic
test: add tests for entity resolution
chore: update dependencies
```

### Pull Request Process

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit**
   ```bash
   git add .
   git commit -m "feat: add your feature"
   ```

3. **Keep your branch updated**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create Pull Request**
   - Use clear title and description
   - Reference related issues
   - Include screenshots/examples if UI changes
   - Ensure tests pass

---

## 📚 Documentation

### Code Documentation

- Document all public APIs
- Add inline comments for complex logic
- Update README if changing project structure
- Update GitBook docs for user-facing changes

### GitBook Documentation

Published docs are in `docs/` and automatically synced to GitBook:

- `docs/README.md` - Overview
- `docs/architecture.md` - Architecture
- `docs/implementation.md` - Implementation details
- `docs/quick-start.md` - Setup guide
- `docs/roadmap.md` - Roadmap
- `docs/appendix.md` - Reference

To update documentation:

1. Edit markdown files in `docs/`
2. Commit and push to `main` branch
3. GitBook will auto-sync changes

---

## 🐛 Reporting Issues

### Bug Reports

Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, dependencies)
- Error messages and stack traces
- Minimal code example if applicable

### Feature Requests

Include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (if any)
- Examples of similar features elsewhere

---

## 💡 Development Tips

### Project Structure

```
code/
├── graph_rag/          # Phase 1: Foundation
├── superscan/          # PDF upload, schema design
├── superkb/            # Entity resolution, DB sync
├── superchat/          # Intelligent retrieval
└── demo/               # Streamlit demo
```

### Key Components

- **Models** (`code/graph_rag/models/`) - Data models
- **Validation** (`code/graph_rag/validation/`) - Validators
- **Database** (`code/graph_rag/db/`) - DB connection and sessions
- **Tests** (`code/graph_rag/tests/`) - Test suite

### Useful Commands

```bash
# Run tests in watch mode
pytest-watch code/graph_rag/tests/

# Generate coverage report
pytest --cov=code/graph_rag --cov-report=html code/graph_rag/tests/

# Check code style
black --check code/
ruff check code/
mypy code/graph_rag/

# Auto-fix style issues
black code/
ruff check --fix code/
```

---

## 🎯 Current Focus Areas

### SuperScan (In Progress)
- PDF upload and parsing
- Fast scan with LLM
- Schema proposal generation
- User feedback loop

### SuperKB (Planned)
- Deep scan with chunking
- Entity extraction and resolution
- Multi-database sync (Postgres, Neo4j, Pinecone)

### SuperChat (Planned)
- Agentic retrieval with tool selection
- Query analysis with LLM
- Context management

---

## 📞 Getting Help

- **Documentation**: https://contactingharshit.gitbook.io/lyzr-hack/
- **Issues**: https://github.com/harshit-codes/lyzr-hackathon/issues
- **Discussions**: https://github.com/harshit-codes/lyzr-hackathon/discussions

---

## 🙏 Thank You!

Your contributions help make this project better for everyone. We appreciate your time and effort!

---

**Remember**: Think deeply, reason clearly, and build intelligently. 🚀
