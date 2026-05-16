# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2026-05-16

### Added
- New §4.4 "Contract lifecycle vs task-message status" with mapping table to reconcile the two vocabularies.
- Deprecation policy to §9.2: deprecate in minor, remove in major.
- Surfacing recovery information for rejected transitions in §8.1 (Signed-envelope) and §8.2 (REST binding).
- Conformance test suite in `conformance/` directory.
- GitHub Actions workflow for conformance testing.

### Changed
- Updated `NACP_SPECIFICATION.md` status from `Draft` to `Stable`.
- Tightened conformance language in §4.2 to `MUST`, transport-neutrally.
- Re-annotated `detail` field in `schemas/rest_error.schema.json` as deprecated.
- Clarified that the patch digit of `protocol_version` is not transmitted (§9.2).

### Fixed
- Added missing `"paused"` value to the `status` enum in `schemas/task_status_response.schema.json`.

## [1.1.0] - 2026-04-30

### Added
- Initial release of NACP 1.1.
- Support for transport-neutral execution references.
- Core lifecycle states and transitions.
- Optional bindings for signed-message envelopes, REST, and WebSocket.
- Support for extension namespaces.

## [1.0.0] - 2026-03-01

### Added
- Initial release of NACP 1.0.
- Basic contract structure and identity references.
