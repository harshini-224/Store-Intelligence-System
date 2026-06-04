import json
from pathlib import Path
from typing import Any, Dict, List

def validate_event_schema(event: Dict[str, Any]) -> List[str]:
    """Validate 9-field canonical schema."""
    required_fields = [
        "event_id", "visitor_id", "store_id", "camera_id",
        "timestamp", "event_type", "zone_id", "confidence", "metadata"
    ]
    errors = []
    for field in required_fields:
        if field not in event:
            errors.append(f"Missing required field: {field}")
    
    # Check visitor_id is int
    if "visitor_id" in event and not isinstance(event["visitor_id"], (int, float)):
        errors.append(f"visitor_id must be numeric, got {type(event['visitor_id'])}")
    
    # Check confidence is float
    if "confidence" in event and not isinstance(event["confidence"], (int, float)):
        errors.append(f"confidence must be numeric, got {type(event['confidence'])}")
    
    # Check metadata is dict
    if "metadata" in event and not isinstance(event["metadata"], dict):
        errors.append(f"metadata must be a dictionary, got {type(event['metadata'])}")
        
    return errors

def validate_jsonl_file(path: str):
    file_path = Path(path)
    if not file_path.exists():
        print(f"FAIL: {path} not found.")
        return False

    all_passed = True
    line_count = 0
    
    with open(file_path, "r") as f:
        for i, line in enumerate(f):
            line_count += 1
            line = line.strip()
            if not line:
                continue
            
            try:
                event = json.loads(line)
                errors = validate_event_schema(event)
                if errors:
                    print(f"FAIL: Line {i+1} schema errors: {', '.join(errors)}")
                    all_passed = False
            except json.JSONDecodeError as exc:
                print(f"FAIL: Line {i+1} is not valid JSON: {exc}")
                all_passed = False
    
    if all_passed:
        print(f"PASS: {path} validated ({line_count} events).")
    return all_passed

if __name__ == "__main__":
    result = validate_jsonl_file("data/outputs/events/events.jsonl")
    exit(0 if result else 1)
