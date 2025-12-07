"""
Test script for Output Manager.
Tests Task 9: Output Manager with Dual-Output Saving
"""

import sys
import json
from pathlib import Path
from PIL import Image

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from output_manager import OutputManager


def test_output_manager():
    """Test Output Manager functionality."""
    print("=" * 80)
    print("Testing Output Manager (Task 9)")
    print("=" * 80)
    
    # Load a test image
    print("\n1. Loading test image...")
    test_image_path = Path("output/generated_images/tokyo_subway_test.png")
    
    if not test_image_path.exists():
        print(f"❌ Test image not found: {test_image_path}")
        print("   Please run test_image_generation.py first")
        return False
    
    test_image = Image.open(test_image_path)
    print(f"✓ Loaded test image: {test_image.size}")
    
    # Load region JSON
    print("\n2. Loading region JSON...")
    region_json_path = Path("output/regions/region_tokyo_subway.json")
    
    with open(region_json_path, 'r') as f:
        region_json = json.load(f)
    
    print(f"✓ Loaded region JSON: {region_json['metadata']['region_id']}")
    
    # Initialize Output Manager
    print("\n3. Initializing Output Manager...")
    output_manager = OutputManager(output_dir="output/final_test")
    print("✓ Output Manager initialized")
    
    # Test dual-output saving
    print("\n4. Testing dual-output saving...")
    result = output_manager.save_dual_output(
        image=test_image,
        region_json=region_json,
        region_id="tokyo_subway",
        seed=42
    )
    
    print(f"✓ Dual-output save complete")
    print(f"  - TIFF saved: {result['tiff_saved']}")
    print(f"  - PNG saved: {result['png_saved']}")
    print(f"  - JSON saved: {result['json_saved']}")
    print(f"  - All saved: {result['all_saved']}")
    
    if not result['all_saved']:
        print("❌ Not all outputs were saved!")
        return False
    
    # Verify files exist
    print("\n5. Verifying output files...")
    tiff_path = Path(result['tiff_path'])
    png_path = Path(result['png_path'])
    json_path = Path(result['json_path'])
    
    if not tiff_path.exists():
        print(f"❌ TIFF file not found: {tiff_path}")
        return False
    print(f"✓ TIFF exists: {tiff_path.name}")
    
    if not png_path.exists():
        print(f"❌ PNG file not found: {png_path}")
        return False
    print(f"✓ PNG exists: {png_path.name}")
    
    if not json_path.exists():
        print(f"❌ JSON file not found: {json_path}")
        return False
    print(f"✓ JSON exists: {json_path.name}")
    
    # Verify dual output consistency
    print("\n6. Verifying dual output consistency...")
    is_consistent, details = output_manager.verify_dual_output_consistency(
        tiff_path=tiff_path,
        png_path=png_path
    )
    
    if is_consistent:
        print("✓ Dual output consistency verified")
        print(f"  - Aspect ratio match: {details['aspect_ratio_match']}")
        print(f"  - Size match: {details['size_match']}")
        print(f"  - TIFF size: {details['tiff_size']}")
        print(f"  - PNG size: {details['png_size']}")
    else:
        print("❌ Dual output consistency check failed!")
        print(f"  Details: {details}")
        return False
    
    # Verify JSON content
    print("\n7. Verifying JSON audit trail...")
    with open(json_path, 'r') as f:
        audit_json = json.load(f)
    
    required_keys = ["generation_info", "output_files", "master_json", 
                     "locked_parameters", "variable_parameters"]
    
    for key in required_keys:
        if key not in audit_json:
            print(f"❌ Missing key in audit JSON: {key}")
            return False
    
    print("✓ JSON audit trail complete")
    print(f"  - Generation timestamp: {audit_json['generation_info']['timestamp']}")
    print(f"  - Seed: {audit_json['generation_info']['seed']}")
    print(f"  - Region: {audit_json['generation_info']['region_name']}")
    
    # Test retry logic with a failing operation
    print("\n8. Testing retry logic...")
    
    def failing_operation():
        raise IOError("Simulated I/O error")
    
    success = output_manager._save_with_retry(
        save_func=failing_operation,
        max_retries=2,
        operation="test operation"
    )
    
    if success:
        print("❌ Retry logic should have failed!")
        return False
    
    print("✓ Retry logic working correctly (failed as expected)")
    
    # Test output summary
    print("\n9. Testing output summary...")
    summary = output_manager.get_output_summary(region_id="tokyo_subway")
    
    print(f"✓ Output summary:")
    print(f"  - Total outputs: {summary['total_outputs']}")
    print(f"  - TIFF files: {summary['tiff_files']}")
    print(f"  - PNG files: {summary['png_files']}")
    print(f"  - JSON files: {summary['json_files']}")
    
    if summary['total_outputs'] < 1:
        print("❌ No outputs found in summary!")
        return False
    
    print("\n" + "=" * 80)
    print("✅ All Output Manager tests passed!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = test_output_manager()
    sys.exit(0 if success else 1)
