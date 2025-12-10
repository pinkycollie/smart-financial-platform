#!/usr/bin/env python3
"""
OpenAPI Specification Validator

This script validates the OpenAPI specification for correctness and completeness.
"""

import json
import sys
from pathlib import Path


def load_openapi_spec(spec_path: str) -> dict:
    """Load the OpenAPI specification from a JSON file."""
    try:
        with open(spec_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Specification file not found: {spec_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in specification file: {e}")
        sys.exit(1)


def validate_structure(spec: dict) -> list:
    """Validate the basic structure of the OpenAPI specification."""
    errors = []
    
    # Check required top-level fields
    required_fields = ['openapi', 'info', 'paths']
    for field in required_fields:
        if field not in spec:
            errors.append(f"Missing required top-level field: {field}")
    
    # Validate OpenAPI version
    if 'openapi' in spec:
        version = spec['openapi']
        if not version.startswith('3.'):
            errors.append(f"Unsupported OpenAPI version: {version}. Expected 3.x")
    
    return errors


def validate_info(spec: dict) -> list:
    """Validate the info section."""
    errors = []
    
    if 'info' not in spec:
        return errors
    
    info = spec['info']
    required_info_fields = ['title', 'version']
    
    for field in required_info_fields:
        if field not in info:
            errors.append(f"Missing required field in info section: {field}")
    
    return errors


def validate_paths(spec: dict) -> list:
    """Validate the paths section."""
    errors = []
    
    if 'paths' not in spec:
        return errors
    
    paths = spec['paths']
    
    if not paths:
        errors.append("Paths section is empty")
        return errors
    
    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            errors.append(f"Invalid path item for {path}")
            continue
        
        # Check for at least one HTTP method
        http_methods = ['get', 'post', 'put', 'delete', 'patch']
        has_method = any(method in path_item for method in http_methods)
        
        if not has_method:
            errors.append(f"Path {path} has no HTTP methods defined")
        
        # Validate each operation
        for method, operation in path_item.items():
            if method not in http_methods:
                continue
            
            if not isinstance(operation, dict):
                errors.append(f"Invalid operation for {method.upper()} {path}")
                continue
            
            # Check for responses
            if 'responses' not in operation:
                errors.append(f"Missing responses for {method.upper()} {path}")
    
    return errors


def validate_schemas(spec: dict) -> list:
    """Validate the components/schemas section."""
    errors = []
    
    if 'components' not in spec:
        errors.append("Missing components section")
        return errors
    
    components = spec['components']
    
    if 'schemas' not in components:
        errors.append("Missing schemas in components section")
        return errors
    
    schemas = components['schemas']
    
    # Validate DHH-specific schemas
    dhh_schemas = [
        'DHHClientIntake',
        'NeedsAssessmentRequest',
        'TaxDataInput',
        'RefundEstimateResponse',
        'InsuranceQuoteRequestDHH'
    ]
    
    for schema_name in dhh_schemas:
        if schema_name not in schemas:
            errors.append(f"Missing DHH-specific schema: {schema_name}")
        else:
            schema = schemas[schema_name]
            
            # Check for type
            if 'type' not in schema:
                errors.append(f"Schema {schema_name} is missing 'type' field")
            
            # Check for properties
            if schema.get('type') == 'object' and 'properties' not in schema:
                errors.append(f"Object schema {schema_name} is missing 'properties' field")
    
    return errors


def validate_dhh_requirements(spec: dict) -> list:
    """Validate DHH-specific requirements."""
    errors = []
    
    # Check for DHH-specific endpoints
    required_endpoints = [
        '/api/intake/tax-client',
        '/api/intake/needs-assessment',
        '/api/tax/refund-estimate',
        '/api/insurance/quote/request'
    ]
    
    paths = spec.get('paths', {})
    
    for endpoint in required_endpoints:
        if endpoint not in paths:
            errors.append(f"Missing required DHH endpoint: {endpoint}")
    
    # Check DHHClientIntake schema for communication preferences
    schemas = spec.get('components', {}).get('schemas', {})
    dhh_intake = schemas.get('DHHClientIntake', {})
    
    if dhh_intake:
        properties = dhh_intake.get('properties', {})
        
        if 'communication_preference' not in properties:
            errors.append("DHHClientIntake schema missing 'communication_preference' field")
        else:
            comm_pref = properties['communication_preference']
            expected_values = ['ASL_Interpreter', 'VRI', 'Captioned_Phone', 'Text_Only']
            enum_values = comm_pref.get('enum', [])
            
            for expected in expected_values:
                if expected not in enum_values:
                    errors.append(
                        f"DHHClientIntake communication_preference missing value: {expected}"
                    )
    
    return errors


def validate_security(spec: dict) -> list:
    """Validate security configuration."""
    errors = []
    
    components = spec.get('components', {})
    
    if 'securitySchemes' not in components:
        errors.append("Missing securitySchemes in components section")
        return errors
    
    security_schemes = components['securitySchemes']
    
    # Check for OAuth 2.0 or API Key
    if 'oauth2' not in security_schemes and 'apiKey' not in security_schemes:
        errors.append("No security schemes defined (expected oauth2 or apiKey)")
    
    return errors


def main():
    """Main validation function."""
    # Path to OpenAPI specification
    spec_path = Path(__file__).parent.parent / 'api' / 'specs' / 'openapi.json'
    
    print(f"Validating OpenAPI specification: {spec_path}")
    print("-" * 60)
    
    # Load specification
    spec = load_openapi_spec(str(spec_path))
    
    # Run validations
    all_errors = []
    
    all_errors.extend(validate_structure(spec))
    all_errors.extend(validate_info(spec))
    all_errors.extend(validate_paths(spec))
    all_errors.extend(validate_schemas(spec))
    all_errors.extend(validate_dhh_requirements(spec))
    all_errors.extend(validate_security(spec))
    
    # Report results
    if all_errors:
        print(f"\n❌ Validation FAILED with {len(all_errors)} error(s):\n")
        for i, error in enumerate(all_errors, 1):
            print(f"{i}. {error}")
        sys.exit(1)
    else:
        print("✅ Validation PASSED")
        print("\nAll checks completed successfully:")
        print("  - Structure validation")
        print("  - Info section validation")
        print("  - Paths validation")
        print("  - Schemas validation")
        print("  - DHH-specific requirements")
        print("  - Security configuration")
        sys.exit(0)


if __name__ == '__main__':
    main()
