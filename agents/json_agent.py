import json
from datetime import datetime
import re

def process_json(text):
    try:
        parsed = json.loads(text)
        
        # Analyze JSON structure
        analysis = analyze_json_structure(parsed)
        
        # Detect document type
        doc_type = detect_document_type(parsed)
        
        # Extract key information based on type
        extracted_info = extract_key_information(parsed, doc_type)
        
        # Validate data quality
        validation_results = validate_json_data(parsed)
        
        return {
            "json_data": parsed,
            "document_type": doc_type,
            "structure_analysis": analysis,
            "extracted_info": extracted_info,
            "validation": validation_results,
            "processed_at": datetime.now().isoformat()
        }
        
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON: {e}"}
    except Exception as e:
        return {"error": f"Processing error: {e}"}

def analyze_json_structure(data):
    """Analyze the structure of JSON data"""
    def count_elements(obj, depth=0):
        if isinstance(obj, dict):
            return {
                "type": "object",
                "keys": len(obj),
                "depth": depth,
                "nested_objects": sum(1 for v in obj.values() if isinstance(v, dict)),
                "arrays": sum(1 for v in obj.values() if isinstance(v, list))
            }
        elif isinstance(obj, list):
            return {
                "type": "array",
                "length": len(obj),
                "depth": depth,
                "item_types": list(set(type(item).__name__ for item in obj))
            }
        else:
            return {"type": type(obj).__name__, "depth": depth}
    
    return count_elements(data)

def detect_document_type(data):
    """Detect the type of JSON document"""
    if isinstance(data, dict):
        keys = set(str(k).lower() for k in data.keys())
        
        # Invoice detection
        invoice_keys = {"invoice", "amount", "total", "due", "billing", "payment"}
        if len(keys.intersection(invoice_keys)) >= 2:
            return "Invoice"
        
        # Order detection
        order_keys = {"order", "items", "quantity", "product", "customer"}
        if len(keys.intersection(order_keys)) >= 2:
            return "Order"
        
        # User/Profile detection
        user_keys = {"name", "email", "phone", "address", "profile"}
        if len(keys.intersection(user_keys)) >= 2:
            return "User Profile"
        
        # Product detection
        product_keys = {"product", "price", "description", "category", "sku"}
        if len(keys.intersection(product_keys)) >= 2:
            return "Product"
        
        # Configuration detection
        config_keys = {"config", "settings", "options", "parameters"}
        if len(keys.intersection(config_keys)) >= 1:
            return "Configuration"
    
    return "Generic"

def extract_key_information(data, doc_type):
    """Extract key information based on document type"""
    info = {}
    
    if not isinstance(data, dict):
        return info
    
    if doc_type == "Invoice":
        info.update({
            "invoice_number": find_value(data, ["invoice_number", "invoice_id", "number"]),
            "amount": find_value(data, ["amount", "total", "sum", "price"]),
            "date": find_value(data, ["date", "invoice_date", "created_date"]),
            "vendor": find_value(data, ["vendor", "company", "supplier", "from"]),
            "customer": find_value(data, ["customer", "client", "to", "bill_to"])
        })
    
    elif doc_type == "Order":
        info.update({
            "order_id": find_value(data, ["order_id", "id", "order_number"]),
            "customer": find_value(data, ["customer", "user", "buyer"]),
            "total": find_value(data, ["total", "amount", "sum"]),
            "items_count": len(data.get("items", [])) if "items" in data else None,
            "status": find_value(data, ["status", "state", "order_status"])
        })
    
    elif doc_type == "User Profile":
        info.update({
            "name": find_value(data, ["name", "full_name", "username"]),
            "email": find_value(data, ["email", "email_address"]),
            "phone": find_value(data, ["phone", "telephone", "mobile"]),
            "location": find_value(data, ["address", "location", "city", "country"])
        })
    
    # Remove None values
    return {k: v for k, v in info.items() if v is not None}

def find_value(data, keys):
    """Find value by trying multiple possible keys"""
    for key in keys:
        if key in data:
            return data[key]
        # Try case-insensitive search
        for data_key in data.keys():
            if str(data_key).lower() == key.lower():
                return data[data_key]
    return None

def validate_json_data(data):
    """Validate JSON data quality"""
    issues = []
    warnings = []
    
    def validate_recursive(obj, path=""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                
                # Check for empty values
                if value is None or value == "":
                    warnings.append(f"Empty value at {current_path}")
                
                # Check for suspicious patterns
                if isinstance(value, str):
                    if re.match(r'^[0-9]+$', value) and len(value) > 10:
                        warnings.append(f"Possible numeric string at {current_path}")
                    if value.lower() in ["null", "none", "undefined"]:
                        issues.append(f"String null value at {current_path}")
                
                validate_recursive(value, current_path)
        
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                validate_recursive(item, f"{path}[{i}]")
    
    validate_recursive(data)
    
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "total_keys": count_total_keys(data),
        "max_depth": calculate_max_depth(data)
    }

def count_total_keys(obj):
    """Count total number of keys in nested JSON"""
    if isinstance(obj, dict):
        return len(obj) + sum(count_total_keys(v) for v in obj.values())
    elif isinstance(obj, list):
        return sum(count_total_keys(item) for item in obj)
    return 0

def calculate_max_depth(obj, current_depth=0):
    """Calculate maximum nesting depth"""
    if isinstance(obj, dict):
        if not obj:
            return current_depth
        return max(calculate_max_depth(v, current_depth + 1) for v in obj.values())
    elif isinstance(obj, list):
        if not obj:
            return current_depth
        return max(calculate_max_depth(item, current_depth + 1) for item in obj)
    return current_depth
