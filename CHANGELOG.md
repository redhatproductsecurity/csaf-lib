# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0b8] - 2026-02-02

## Changed
- Remove some default fields from document: lang, source_lang, distribution

## [0.1.0b7] - 2026-01-22

### Changed
- Schema validation now uses local CVSS schemas instead of downloading from network

## [0.1.0b6] - 2026-01-21

### Changed
- **BREAKING**: Package renamed from `csaf-vex` to `csaf-lib` to support both VEX and Advisory documents
- **BREAKING**: Python import changed from `csaf_vex` to `csaf_lib`
- **BREAKING**: CLI command changed from `csaf-vex` to `csaf-lib`
- **BREAKING**: Plugin entry point group changed from `csaf_vex.validators` to `csaf_lib.validators`
- **BREAKING**: Default generator engine name changed from `csaf-vex` to `csaf-lib`

## [0.1.0b5] - 2026-01-13

### Fixed

- Builder properly parses CVSS version instead of hardcoding `cvss_v3`

## [0.1.0b4] - 2026-01-10

### Changed
- Branch `to_dict()` now places `branches` field last for improved JSON readability when navigating nested structures

## [0.1.0b3] - 2026-01-06

### Fixed
- Validation module now properly exposed via `__init__.py` with exported objects

## [0.1.0b2] - 2025-12-16

### Added
- CSAFVEX builder for simplified document construction
- CSAFVEX internal representation with model classes
- Validator entrypoint for library usage
- Verification system for CSAF VEX documents

### Fixed
- Improved output formatting for validate command
- Version range detection for 'to' indicator

## [0.1.0b1] - 2025-12-03

### Added
- Project started
