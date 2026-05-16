# NACP Conformance Suite

This directory contains automated tests to verify that an implementation (or a set of examples) conforms to the NACP standard.

## Structure

- `test_schemas.py`: Validates all files in `examples/` against the matching `schemas/*.schema.json`.
- `test_lifecycle.py`: Asserts the §4.2 transition table (every legal transition allowed, a sample of illegal ones rejected).
- `test_envelope.py`: Signed-envelope validation + canonical-JSON byte-identity (re-serialize an example, assert identical bytes).

## Usage

To run the suite, you need Python 3.9+ and the `jsonschema` and `ed25519` libraries.

```bash
pip install jsonschema ed25519
pytest conformance/
```

Downstream implementations SHOULD point their CI at a pinned tag of this repo and run this suite against their generated NACP artifacts.
