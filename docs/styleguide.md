# MultiCloud Style Guide

## TOC
- [Code Style](#code-style)
    - [Versioning](#versioning)
    - [Python Code Conventions](#python-code-conventions)
    - [Naming Conventions](#naming-conventions)
    - [Type Hints](#type-hints)
    - [Docstrings](#docstrings)
    - [Import Organization](#import-organization)
- [Documentation Style](#documentation-style)
    - [API Documentation](#api-documentation)
    - [Code Examples](#code-examples)
    - [Comments](#comments)
- [Project Structure](#project-structure)
    - [Directory Organization](#directory-organization)
    - [File Naming](#file-naming)
    - [Module Organization](#module-organization)
- [Git Conventions](#git-conventions)
    - [Commit Messages](#commit-messages)
    - [Branch Naming](#branch-naming)
    - [Pull Request Guidelines](#pull-request-guidelines)
- [Testing Standards](#testing-standards)
    - [Test Structure](#test-structure)
    - [Test Naming](#test-naming)
    - [Coverage Requirements](#coverage-requirements)
- [Error Handling](#error-handling)
    - [Exception Conventions](#exception-conventions)
    - [Error Messages](#error-messages)
    - [Logging Standards](#logging-standards)
- [Configuration](#configuration)
    - [Environment Variables](#environment-variables)
    - [Configuration Files](#configuration-files)
    - [Default Values](#default-values)

## Code Style

### Versioning

### Python Code Conventions
- **PEP 8 Complaince**: Follow Python PEP 8 style guidlines
- **Line Length**: Maximum 88 characters
- **Indentation**: 4 spaces (no tabs)
- **Linting**:
    - Use `pylint`
    ```bash
    pylint src/
    ```
    - Use Repositories `.pylintrc`
    - Linting Score must be at least `9.2/10`

### Naming Conventions
 - **Classes**: PascalCase
 - **Functions/Methods**: snake_case
 - **Variables**: snake_case
 - **Constants**: UPPER_SNAKE_CASE
 - **Private methods**: leading underscore `_internal_method`

 Method and Variable names should be descriptive. Avoid abbreviations as much as possible (Use `get_request` instead of `get_req` or `response` instead of `res`).

### Type Hints

### Docstrings

### Import Organization
- Keep `__init__.py` files minimal
- Use `__all__.py` to control public API
- Import Order:
    - Standard Library Imports
    - Third-Party imports second
    - Local imports last
- Blank line after each import group
- Use absolute imports when possilbe
- 2 Blank lines after imports
- Only import what is used, avoid wildcard imports

## Documentation Style

### API Documentation

**Class Markdown Template**
```markdown
# Class Name
`import path`

## Overview
Brief overview of what the class or method does

## Class Definition

## Properties
Table describing the properties of a Class
| Property | Type | Description | Default |
| :------- | :--- | :---------- | :------ |
| sample_propery | str | What the property is for | Required or Default Value |

## Methods
### Method Group *If Applicable*
### Method Name
`method(param: type = default) -> Returns`

Brief description of the method's use

**Parameters**
- `param`: Parameter Description

**Returns**: Possible Return Types

**Example**:

```

### Code Examples

### Comments
Comments should directly above the line of code being commented, or at the end of the line if staying under the 100 character line limit. Coments should have 1 `#` followed by a space. When commenting out a line of code, do not put a space between the hash and the code.

```python
# Check if the event has a json payload
if event.is_json():
    body_json = event.get_json() # Get a copy of the body
    #body_json.get_xml()
```

## Project Structure

### Directory Organization
```
src/multicloud/
|--__init__.py
|-- functions/
|   |--__init__.py
|   |-- common/
|   |   |-- __init__.py
|   |   |-- Other common function utils
|   |-- knative/
|   |   |-- __init__.py
|   |   |-- adapters.py
|   |-- aws/
|   |-- azure/
```

### File Naming
- File names use snake_case
- `multicloud` should also be one work. Not `multi_cloud`

### Module Organization

## Git Conventions

### Commit Messages

### Branch Naming

### Pull Request Guidelines

## Testing Standards
All tests must pass for all supported python versions before a pull request will be excepted.

### Test Structure

There are two levels of testing:
- Unit Tests: Cover individual classes and methods
- Integration Tests: Cover workflows

### Test Naming
All test files, classes, and functions should start with `test` and follow project naming conventions (PascalCase for classes, snake_case for files and functions). 

### Coverage Requirements
Coverage is measured by pytest.
```bash
pytest --cov=src/
```
Minimum test coverage is `85%` with a minimum of `75%` for each file. 

## Error Handling

### Exception Conventions

### Error Messages

### Logging Standards

## Configuration

### Environment Variables

### Configuration Files

### Default Values
