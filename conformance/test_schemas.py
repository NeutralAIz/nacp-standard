import json
import os
import pytest
from jsonschema import validate, RefResolver

def get_schema_path(schema_name):
    return os.path.join("schemas", f"{schema_name}.schema.json")

def get_example_path(example_name):
    return os.path.join("examples", example_name)

@pytest.mark.parametrize("example_file, schema_name", [
    ("contract_completed_audit.json", "contract"),
    ("contract_failed_dispute.json", "contract"),
    ("contract_over_a2a.json", "contract"),
    ("contract_over_direct_api.json", "contract"),
    ("contract_over_mcp.json", "contract"),
    ("contract_settlement_external.json", "contract"),
    ("contract_with_artifact_evidence.json", "contract"),
])
def test_example_conformance(example_file, schema_name):
    example_path = get_example_path(example_file)
    schema_path = get_schema_path(schema_name)
    
    with open(example_path, "r") as f:
        example = json.load(f)
    
    with open(schema_path, "r") as f:
        schema = json.load(f)
        
    # We need to provide a local schema store to avoid remote resolution
    schema_dir = os.path.abspath("schemas")
    store = {}
    for filename in os.listdir(schema_dir):
        if filename.endswith(".schema.json"):
            with open(os.path.join(schema_dir, filename), "r") as f:
                s = json.load(f)
                if "$id" in s:
                    store[s["$id"]] = s
    
    resolver = RefResolver(f"file://{schema_dir}/", schema, store=store)
    
    validate(instance=example, schema=schema, resolver=resolver)
