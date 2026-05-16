import json
import pytest

def canonical_json(envelope: dict) -> str:
    # §8.1.2 Canonical JSON for signing
    # 3. Signature exclusion: the signature field is REMOVED
    canonical = {k: v for k, v in envelope.items() if k != "signature"}
    # 2. Serialization: sort_keys=True, separators=(",", ":"), ensure_ascii=False
    return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

def test_canonical_json_identity():
    envelope = {
        "version": "1.1",
        "msg_id": "uuid-v4",
        "type": "TASK_ASSIGN",
        "priority": 5,
        "payload": {"foo": "bar"},
        "signature": "some-signature"
    }
    
    expected = '{"msg_id":"uuid-v4","payload":{"foo":"bar"},"priority":5,"type":"TASK_ASSIGN","version":"1.1"}'
    assert canonical_json(envelope) == expected

def test_canonical_json_omission():
    # 4. Optional fields: missing optional fields are OMITTED entirely, NOT set to null.
    envelope_with_null = {
        "version": "1.1",
        "reply_to": None,
        "signature": "sig"
    }
    # If the user explicitly sets it to None, it stays as null in JSON unless we filter it.
    # The spec says "missing optional fields are OMITTED".
    
    canonical = canonical_json(envelope_with_null)
    # The spec says missing fields are omitted. It doesn't explicitly say 
    # "if you provide null, you must strip it", but usually "missing" means 
    # not in the dict.
    
    # If we follow the python snippet in §8.1.2:
    # def canonical_json(envelope: dict) -> str:
    #     canonical = {k: v for k, v in envelope.items() if k != "signature"}
    #     return json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    
    # That snippet DOES NOT strip nulls. It just strips "signature".
    # However, Requirement 4 says "missing optional fields are OMITTED".
    
    # Let's test what the snippet produces.
    assert '"reply_to":null' in canonical

@pytest.mark.skip(reason="Verification requires ed25519 library")
def test_signature_verification():
    # In a real test, we would use ed25519 to sign and verify
    pass
