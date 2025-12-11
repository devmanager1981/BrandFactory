"""
Test script for Localization Agent.
Tests Task 6: Localization Agent with Region Config & Guardrails
"""

import sys
import json
from pathlib import Path

# Add src and config to path
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent / "config"))

from localization_agent import LocalizationAgent
from region_configs import get_region_config, get_all_region_ids


def test_localization_agent():
    """Test Localization Agent functionality."""
    print("=" * 80)
    print("Testing Localization Agent (Task 6)")
    print("=" * 80)
    
    # Load Master JSON from previous task
    print("\n1. Loading Master JSON...")
    master_json_path = Path("output/master_json_wristwatch.json")
    
    if not master_json_path.exists():
        print(f"❌ Master JSON not found: {master_json_path}")
        print("   Please run test_master_json_creation.py first")
        return False
    
    with open(master_json_path, 'r') as f:
        master_json = json.load(f)
    
    print(f"✓ Loaded Master JSON")
    print(f"  - Campaign ID: {master_json['metadata']['campaign_id']}")
    print(f"  - Locked parameters: {list(master_json['locked_parameters'].keys())}")
    
    # Initialize Localization Agent
    print("\n2. Initializing Localization Agent...")
    agent = LocalizationAgent()
    print("✓ Agent initialized")
    
    # Test single region merge
    print("\n3. Testing single region merge (Tokyo)...")
    tokyo_config = get_region_config("tokyo_subway")
    
    tokyo_json = agent.merge_configs(
        master_json=master_json,
        region_config=tokyo_config
    )
    
    print("✓ Tokyo configuration merged")
    print(f"  - Region: {tokyo_json['metadata']['region_name']}")
    print(f"  - Locale: {tokyo_json['metadata']['locale']}")
    print(f"  - Background: {tokyo_json['variable_parameters']['background_setting'][:60]}...")
    
    # Validate locked parameters preserved
    print("\n4. Validating parameter lock preservation...")
    locked_preserved = agent.validate_locked_parameters(master_json, tokyo_json)
    
    if locked_preserved:
        print("✓ All locked parameters preserved correctly")
    else:
        print("❌ Locked parameters were modified!")
        return False
    
    # Test with brand guardrails
    print("\n5. Testing brand guardrails...")
    campaign_config = {
        "campaign_id": "summer_2024_global",
        "brand_guardrails": {
            "negative_prompts": [
                "distorted product",
                "altered logo",
                "incorrect colors"
            ],
            "forbidden_elements": [
                "competitor_brands",
                "inappropriate_content"
            ],
            "required_elements": [
                "brand_logo_visible",
                "product_centered"
            ]
        }
    }
    
    berlin_config = get_region_config("berlin_billboard")
    berlin_json = agent.merge_configs(
        master_json=master_json,
        region_config=berlin_config,
        campaign_config=campaign_config
    )
    
    print("✓ Berlin configuration with guardrails merged")
    
    # Validate guardrails applied
    if "negative_prompts" in berlin_json:
        print(f"  - Negative prompts: {len(berlin_json['negative_prompts'])} applied")
    else:
        print("  ❌ Negative prompts not applied!")
        return False
    
    if "forbidden_elements" in berlin_json["metadata"]:
        print(f"  - Forbidden elements: {len(berlin_json['metadata']['forbidden_elements'])} flagged")
    else:
        print("  ❌ Forbidden elements not flagged!")
        return False
    
    # Test batch processing
    print("\n6. Testing batch processing (all regions)...")
    all_region_ids = get_all_region_ids()
    region_configs = [get_region_config(rid) for rid in all_region_ids[:3]]  # Test with first 3
    
    region_jsons = agent.process_regions(
        master_json=master_json,
        region_configs=region_configs,
        campaign_config=campaign_config,
        output_dir=Path("output/regions")
    )
    
    print(f"✓ Batch processing complete")
    print(f"  - Processed: {len(region_jsons)}/{len(region_configs)} regions")
    print(f"  - Regions: {[r['metadata']['region_id'] for r in region_jsons]}")
    
    # Validate all regions have locked parameters preserved
    print("\n7. Validating all regions preserve locked parameters...")
    all_valid = all(
        agent.validate_locked_parameters(master_json, rj)
        for rj in region_jsons
    )
    
    if all_valid:
        print("✓ All regions preserve locked parameters correctly")
    else:
        print("❌ Some regions have modified locked parameters!")
        return False
    
    # Display sample region JSON
    print("\n8. Sample region JSON (Tokyo):")
    print("  " + "-" * 76)
    sample = {
        "version": tokyo_json["version"],
        "metadata": {
            k: v for k, v in tokyo_json["metadata"].items()
            if k in ["region_id", "region_name", "locale", "campaign_id"]
        },
        "locked_parameters": {k: "..." for k in tokyo_json["locked_parameters"].keys()},
        "variable_parameters": {k: "..." for k in tokyo_json["variable_parameters"].keys()},
        "negative_prompts": "..." if "negative_prompts" in tokyo_json else None
    }
    print("  " + json.dumps(sample, indent=2).replace("\n", "\n  "))
    
    print("\n" + "=" * 80)
    print("✅ All Localization Agent tests passed!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = test_localization_agent()
    sys.exit(0 if success else 1)
