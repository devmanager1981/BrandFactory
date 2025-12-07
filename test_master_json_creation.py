"""
Test script for Master JSON creation from base product images.
Tests Task 5: Product Image to Master JSON (VLM Bridge)
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline_manager import FiboPipelineManager


def test_master_json_creation():
    """Test creating Master JSON from base product images."""
    print("=" * 80)
    print("Testing Master JSON Creation (Task 5)")
    print("=" * 80)
    
    # Initialize pipeline manager (using Cloud API)
    print("\n1. Initializing FIBO Pipeline Manager...")
    manager = FiboPipelineManager(use_local=False)
    print("✓ Pipeline Manager initialized")
    
    # Test with wristwatch image
    print("\n2. Testing with wristwatch.png...")
    wristwatch_path = Path("images/wristwatch.png")
    
    if not wristwatch_path.exists():
        print(f"❌ Image not found: {wristwatch_path}")
        return False
    
    try:
        master_json_wristwatch = manager.create_master_json_from_image(
            image_path=wristwatch_path,
            output_path="output/master_json_wristwatch.json"
        )
        
        print("\n✓ Master JSON created for wristwatch")
        print(f"  - Version: {master_json_wristwatch.get('version')}")
        print(f"  - Campaign ID: {master_json_wristwatch['metadata'].get('campaign_id')}")
        print(f"  - Locked parameters: {list(master_json_wristwatch.get('locked_parameters', {}).keys())}")
        print(f"  - Variable parameters: {list(master_json_wristwatch.get('variable_parameters', {}).keys())}")
        
        # Pretty print a sample
        print("\n  Sample of Master JSON:")
        print("  " + "-" * 76)
        sample = {
            "version": master_json_wristwatch.get("version"),
            "metadata": master_json_wristwatch.get("metadata"),
            "locked_parameters": {
                k: "..." for k in master_json_wristwatch.get("locked_parameters", {}).keys()
            },
            "variable_parameters": {
                k: "..." for k in master_json_wristwatch.get("variable_parameters", {}).keys()
            }
        }
        print("  " + json.dumps(sample, indent=2).replace("\n", "\n  "))
        
    except Exception as e:
        print(f"\n❌ Failed to create Master JSON for wristwatch: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test with headphones image
    print("\n3. Testing with headphones.png...")
    headphones_path = Path("images/headphones.png")
    
    if not headphones_path.exists():
        print(f"❌ Image not found: {headphones_path}")
        return False
    
    try:
        master_json_headphones = manager.create_master_json_from_image(
            image_path=headphones_path,
            output_path="output/master_json_headphones.json"
        )
        
        print("\n✓ Master JSON created for headphones")
        print(f"  - Version: {master_json_headphones.get('version')}")
        print(f"  - Campaign ID: {master_json_headphones['metadata'].get('campaign_id')}")
        print(f"  - Locked parameters: {list(master_json_headphones.get('locked_parameters', {}).keys())}")
        print(f"  - Variable parameters: {list(master_json_headphones.get('variable_parameters', {}).keys())}")
        
    except Exception as e:
        print(f"\n❌ Failed to create Master JSON for headphones: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)
    print("✅ All Master JSON creation tests passed!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = test_master_json_creation()
    sys.exit(0 if success else 1)
