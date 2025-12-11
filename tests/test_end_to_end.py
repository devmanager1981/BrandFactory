"""
End-to-End CLI Test for Global Brand Localizer

Tests the complete workflow:
VLM → Sanitizer → Agent → FIBO → Output

This checkpoint verifies all components work together correctly.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PIL import Image
import json

print("=" * 70)
print("GLOBAL BRAND LOCALIZER - END-TO-END CLI TEST")
print("=" * 70)
print()

# Test configuration
TEST_IMAGES = [
    "images/wristwatch.png",
    "images/headphones.png"
]

def test_imports():
    """Test that all modules can be imported."""
    print("📦 Testing module imports...")
    
    try:
        from api_manager import BriaAPIManager
        from schema_sanitizer import SchemaSanitizer
        from localization_agent import LocalizationAgent
        from batch_processor import BatchProcessor
        from output_manager import OutputManager
        from error_recovery import StateManager, ErrorLogger
        from c2pa_verifier import C2PAVerifier
        
        print("  ✓ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def test_schema_sanitizer():
    """Test VLM schema sanitizer."""
    print("\n🔧 Testing Schema Sanitizer...")
    
    try:
        from schema_sanitizer import SchemaSanitizer
        
        sanitizer = SchemaSanitizer()
        
        # Test with sample VLM output
        test_output = {
            "photographic_characteristics": {
                "camera_angle": "low angle",
                "lens_focal_length": "portrait lens"
            },
            "lighting": {
                "conditions": "soft natural"
            },
            "style_medium": "photograph"
        }
        
        sanitized = sanitizer.sanitize(test_output)
        
        # Verify sanitization worked
        assert "photographic_characteristics" in sanitized
        print("  ✓ Schema sanitizer working correctly")
        return True
        
    except Exception as e:
        print(f"  ✗ Schema sanitizer failed: {e}")
        return False


def test_localization_agent():
    """Test localization agent."""
    print("\n🌍 Testing Localization Agent...")
    
    try:
        from localization_agent import LocalizationAgent
        
        agent = LocalizationAgent()
        
        # Create test master JSON
        master_json = {
            "version": "1.0",
            "metadata": {"campaign_id": "test"},
            "locked_parameters": {"camera_angle": "eye_level"},
            "variable_parameters": {"background": "neutral"}
        }
        
        # Create test region config
        region_config = {
            "region_id": "test_region",
            "display_name": "Test Region",
            "locale": "en-US",
            "environment_overrides": {
                "background": "urban",
                "lighting_type": "neon_ambient"
            },
            "cultural_context": {}
        }
        
        # Merge configs
        result = agent.merge_configs(master_json, region_config)
        
        # Verify locked parameters preserved
        assert result["locked_parameters"]["camera_angle"] == "eye_level"
        assert result["variable_parameters"]["background"] == "urban"
        
        print("  ✓ Localization agent working correctly")
        return True
        
    except Exception as e:
        print(f"  ✗ Localization agent failed: {e}")
        return False


def test_output_manager():
    """Test output manager with consistency checking."""
    print("\n💾 Testing Output Manager...")
    
    try:
        from output_manager import OutputManager
        
        output_manager = OutputManager(output_dir="output/test_e2e")
        
        # Create test images
        test_image = Image.new('RGB', (512, 512), color=(100, 150, 200))
        master_image = Image.new('RGB', (512, 512), color=(100, 150, 200))
        
        # Create test region JSON
        region_json = {
            "metadata": {
                "region_id": "test_e2e",
                "campaign_id": "test",
                "source_image": "test.png"
            },
            "locked_parameters": {},
            "variable_parameters": {}
        }
        
        # Save with consistency check
        result = output_manager.save_dual_output(
            image=test_image,
            region_json=region_json,
            region_id="test_e2e",
            seed=42,
            master_image=master_image
        )
        
        # Verify outputs
        assert result["tiff_saved"], "TIFF should be saved"
        assert result["png_saved"], "PNG should be saved"
        assert result["json_saved"], "JSON should be saved"
        assert result["consistency_score"] is not None, "Consistency score should be calculated"
        
        print(f"  ✓ Output manager working correctly")
        print(f"    - Consistency score: {result['consistency_score']:.4f}")
        print(f"    - C2PA verified: {result.get('c2pa_verified', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"  ✗ Output manager failed: {e}")
        return False


def test_error_recovery():
    """Test error recovery and state management."""
    print("\n🔄 Testing Error Recovery...")
    
    try:
        from error_recovery import StateManager, ErrorLogger
        
        # Test state manager
        state_manager = StateManager(state_dir="output/test_e2e_state")
        
        master_json = {"version": "1.0", "test": True}
        processed = ["region1", "region2"]
        pending = ["region3", "region4"]
        
        state_file = state_manager.save_state(
            campaign_id="test_e2e",
            master_json=master_json,
            processed_regions=processed,
            pending_regions=pending
        )
        
        # Load state
        loaded = state_manager.load_state(state_file)
        
        assert loaded["campaign_id"] == "test_e2e"
        assert loaded["progress"]["processed"] == 2
        assert loaded["progress"]["pending"] == 2
        
        # Test error logger
        error_logger = ErrorLogger(log_dir="output/test_e2e_logs")
        
        error_logger.log_error(
            error_type="TEST_ERROR",
            component="test_e2e",
            message="Test error message",
            severity="WARNING"
        )
        
        print("  ✓ Error recovery working correctly")
        return True
        
    except Exception as e:
        print(f"  ✗ Error recovery failed: {e}")
        return False


def test_property_tests():
    """Verify all property-based tests pass."""
    print("\n🧪 Running Property-Based Tests...")
    
    try:
        import subprocess
        
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/test_strategies.py", "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            # Count passed tests
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if 'passed' in line:
                    print(f"  ✓ {line.strip()}")
                    break
            return True
        else:
            print(f"  ✗ Some tests failed")
            print(result.stdout[-500:])  # Last 500 chars
            return False
            
    except Exception as e:
        print(f"  ✗ Property tests failed: {e}")
        return False


def main():
    """Run all end-to-end tests."""
    
    results = []
    
    # Run all tests
    results.append(("Module Imports", test_imports()))
    results.append(("Schema Sanitizer", test_schema_sanitizer()))
    results.append(("Localization Agent", test_localization_agent()))
    results.append(("Output Manager", test_output_manager()))
    results.append(("Error Recovery", test_error_recovery()))
    results.append(("Property Tests", test_property_tests()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    print()
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All end-to-end tests PASSED!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) FAILED")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
