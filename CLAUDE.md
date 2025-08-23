# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

altair-upset is a Python package that creates interactive UpSet plots using Altair. UpSet plots visualize set intersections as an alternative to Venn diagrams. The package supports both Pandas and Polars DataFrames and generates interactive Altair/Vega-Lite charts.

## Architecture

The codebase is organized into focused modules:

- `altair_upset/upset.py` - Main UpSetAltair class and UpSetChart wrapper
- `altair_upset/components.py` - Chart component creators (horizontal bar, matrix view, vertical bar)  
- `altair_upset/preprocessing.py` - Data preprocessing and validation
- `altair_upset/transforms.py` - Altair chart transformations and base chart creation
- `altair_upset/config.py` - Configuration management and top-level settings

The main entry point is the `UpSetAltair` class which orchestrates data preprocessing, chart component creation, and final visualization assembly.

## Development Commands

### Testing
```bash
# Run all tests with coverage
uv run pytest

# Run specific test file
uv run pytest tests/test_advanced_features.py

# Run single test with verbose output
uv run pytest tests/test_advanced_features.py::test_vertical_bar_y_axis_orient_right -v
```

### Code Quality
```bash
# Run linting
uv run ruff check

# Check formatting  
uv run ruff format --diff --check

# Fix linting and formatting
uv run task ruff-fix

# Run type checking
uv run mypy altair_upset tests
```

### Building and Publishing
```bash
# Clean and build
uv run task build

# Publish (after build)
uv run task publish
```

### Documentation
```bash
# Clean docs build
uv run task doc-clean

# Build HTML documentation
uv run task doc-build-html

# Clean and build docs
uv run task doc-clean-build
```

## Testing Infrastructure

- Uses `pytest` with `syrupy` for snapshot testing
- Visual regression tests compare generated PNG images and Vega-Lite JSON specs
- Test snapshots stored in `tests/__snapshots__/`
- Debug outputs saved to `tests/debug/` during development
- Supports both Pandas and Polars DataFrame inputs

## Key Dependencies

- `altair>=5.0.0` - Core visualization library
- `pandas>=2.0.0` - Primary data structure support
- `polars>=0.20.0` - Alternative DataFrame support (test/dev)
- `vl-convert-python>=1.7.0` - PNG conversion for tests