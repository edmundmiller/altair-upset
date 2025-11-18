# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Fixed

## [0.5.0] - 2025-11-17

### Added

- Programmatic highlighting via `highlight` parameter (`"least"`, `"greatest"`, index, or list of indices)
- Vertical orientation support with new `orientation` parameter
  - Horizontal orientation (default): cardinality bars on top (vertical), set sizes on right (horizontal)
  - Vertical orientation: cardinality bars on left (horizontal), set sizes on top (vertical)
  - Vertical layouts are ideal for interactive plots that can be scrolled
  - Horizontal layouts are best for static figures in papers
- Enhanced test normalization for auto-generated parameter and view names
- Comprehensive test suite for vertical orientation feature (6 new tests)

### Changed

- Out-of-bounds highlight indices now raise errors instead of failing silently
- Updated component functions to support both horizontal and vertical orientations
- Improved layout logic to handle orientation-specific rendering

### Fixed

- Improved vertical upset plot layout with consistent height ratios (0.6) and bar sizes (20px) matching horizontal orientation
- Fixed set label circles being covered by bars in vertical orientation by separating labels into distinct components
- Added proper Y-axis scale padding (0.1) to prevent matrix dots from being hidden behind set bars
- Added 5px spacing between vertical plot components for better visual separation

## [0.4.0] - 2025-01-20

### Added

- Test suite for Polars compatibility
- New example documentation for using Polars with UpSet plots
- Added pyarrow dependency for Polars support
- Added ReadTheDocs configuration and documentation structure
- Added CITATION.cff for proper academic citation
- Added VS Code settings for consistent development

### Changed

- Restructured documentation with Sphinx
- Enhanced example gallery with new use cases

### Fixed

- Improved handling of empty DataFrames in preprocessing
- Fixed a bug introduced in [5a34f7e](https://github.com/edmundmiller/altair-upset/commit/5a34f7e) that caused the vertical alignment the matrix and graph to be off.
- Fixed documentation build process
- Improved code formatting consistency

## [0.3.0] - 2025-01-19

### Added

- Type hints for better IDE support and code safety
- Theme support for customizing chart appearance
- Comprehensive documentation with examples
- GitHub Actions CI/CD pipeline
- Pre-commit hooks for code quality
- MIT License
- Proper package metadata and PyPI configuration
- Support for Python 3.8-3.11
- Interactive tooltips with set information
- Customizable chart dimensions and styling
- Proper error handling with descriptive messages
- Instructions for building and viewing the documentation

### Changed

- Improved API with better parameter organization
- Updated dependencies to latest stable versions
- Enhanced documentation with more examples
- Better code organization and modularity
- Stricter input validation

### Fixed

- Input validation for data types and values
- Error handling for invalid parameters
- Documentation formatting and examples

## [0.2.0] - 2025-01-18

### Changed

- Updated to support Altair 5.0.0 and Vega-Lite 5
- Replaced `alt.selection_multi()` with `alt.selection_point()` for legend selection
- Removed width/height properties from VConcatChart level
- Set width/height properties on individual chart components for proper validation
- Updated PNG snapshot generation to use Altair's built-in saving capabilities

### Added

- Comprehensive documentation in `docs.md`
- Detailed API reference with parameter descriptions
- Interactive features documentation
- Usage examples in documentation

### Fixed

- Fixed deprecation warning for selection_multi
- Fixed PNG snapshot generation and tracking
- Resolved validation errors for chart sizing in Altair 5

## [0.1.1] - 2025-01-18

### Changed

- Split the original function into separate files for division of concerns

## [0.1.0] - 2025-01-18

### Added

- Initial implementation of UpSetAltair
- Basic set visualization functionality
- Interactive features (hover highlighting, legend filtering)
- Support for customization (colors, sizes, sorting)
