"""
Hypothesis strategies for property-based testing
Generates random test data for FIBO components
"""

from hypothesis import strategies as st, given, settings
from typing import Dict, Any
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


# Valid FIBO enumerations (based on vlm_to_fibo_map.json)
VALID_CAMERA_ANGLES = ["low_angle_iso", "eye_level", "overhead"]
VALID_LIGHTING_TYPES = [
    "soft_natural", "studio_lighting", "high_contrast_key_light",
    "neon_ambient", "golden_hour", "natural_sunlight"
]
VALID_STYLE_MEDIUMS = [
    "photograph", "digital_illustration", "oil_painting", "3d_render"
]


@st.composite
def structured_prompt_strategy(draw):
    """
    Generate random structured prompts for testing.
    
    Returns:
        Dict representing a FIBO structured prompt
    """
    return {
        "short_description": draw(st.text(min_size=10, max_size=200)),
        "photographic_characteristics": {
            "camera_angle": draw(st.sampled_from(VALID_CAMERA_ANGLES)),
            "lens_focal_length": draw(st.sampled_from(["24mm", "50mm", "85mm", "macro", "portrait"])),
            "depth_of_field": draw(st.sampled_from(["shallow", "deep"])),
            "focus": draw(st.sampled_from(["sharp focus on subject", "soft focus"]))
        },
        "lighting": {
            "conditions": draw(st.sampled_from(VALID_LIGHTING_TYPES)),
            "direction": draw(st.text(min_size=5, max_size=50)),
            "shadows": draw(st.text(min_size=5, max_size=50))
        },
        "style_medium": draw(st.sampled_from(VALID_STYLE_MEDIUMS)),
        "background_setting": draw(st.text(min_size=10, max_size=100)),
        "aesthetics": {
            "composition": draw(st.text(min_size=5, max_size=50)),
            "color_scheme": draw(st.text(min_size=5, max_size=50)),
            "mood_atmosphere": draw(st.text(min_size=5, max_size=50))
        }
    }


@st.composite
def vlm_raw_output_strategy(draw):
    """
    Generate VLM-like raw output with potentially invalid parameters.
    
    Returns:
        Dict with free-form text that needs sanitization
    """
    return {
        "short_description": draw(st.text(min_size=10, max_size=200)),
        "photographic_characteristics": {
            "camera_angle": draw(st.sampled_from([
                "low angle", "eye level", "overhead", "high angle",
                "low_angle", "eye-level", "super low angle"
            ])),
            "lens_focal_length": draw(st.sampled_from([
                "portrait lens", "macro", "standard lens", "50mm", "85mm"
            ])),
            "depth_of_field": draw(st.sampled_from(["shallow", "deep"])),
            "focus": draw(st.text(min_size=5, max_size=50))
        },
        "lighting": {
            "conditions": draw(st.sampled_from([
                "soft natural", "studio", "high contrast", "neon",
                "golden hour", "natural", "soft_natural"
            ])),
            "direction": draw(st.text(min_size=5, max_size=50)),
            "shadows": draw(st.text(min_size=5, max_size=50))
        },
        "style_medium": draw(st.sampled_from([
            "photograph", "photo", "digital illustration", "illustration",
            "oil painting", "painting", "3d render", "render"
        ])),
        "background_setting": draw(st.text(min_size=10, max_size=100))
    }


@st.composite
def master_json_strategy(draw):
    """
    Generate random Master JSON configurations.
    
    Returns:
        Dict representing a Master JSON
    """
    return {
        "version": "1.0",
        "metadata": {
            "created_at": draw(st.text(min_size=10, max_size=30)),
            "source_image": draw(st.text(min_size=5, max_size=50)),
            "campaign_id": draw(st.text(min_size=5, max_size=20))
        },
        "locked_parameters": draw(structured_prompt_strategy()),
        "variable_parameters": {
            "background": draw(st.text(min_size=5, max_size=50)),
            "lighting_type": draw(st.sampled_from(VALID_LIGHTING_TYPES)),
            "environment": draw(st.text(min_size=5, max_size=50)),
            "mood": draw(st.text(min_size=5, max_size=30))
        }
    }


@st.composite
def region_config_strategy(draw):
    """
    Generate random region configurations.
    
    Returns:
        Dict representing a region config
    """
    return {
        "region_id": draw(st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), whitelist_characters='_'))),
        "display_name": draw(st.text(min_size=5, max_size=50)),
        "locale": draw(st.sampled_from(["en-US", "ja-JP", "de-DE", "ar-AE", "en-AU"])),
        "environment_overrides": {
            "background": draw(st.text(min_size=5, max_size=50)),
            "lighting_type": draw(st.sampled_from(VALID_LIGHTING_TYPES)),
            "environment": draw(st.text(min_size=5, max_size=50)),
            "mood": draw(st.text(min_size=5, max_size=30))
        },
        "cultural_context": {
            "color_preferences": draw(st.lists(st.text(min_size=3, max_size=10), min_size=1, max_size=5)),
            "avoid_elements": draw(st.lists(st.text(min_size=3, max_size=20), min_size=0, max_size=3))
        }
    }


@st.composite
def campaign_config_strategy(draw):
    """
    Generate random campaign configurations.
    
    Returns:
        Dict representing a campaign config
    """
    return {
        "campaign_id": draw(st.text(min_size=5, max_size=30)),
        "master_json_path": draw(st.text(min_size=5, max_size=50)),
        "target_regions": draw(st.lists(st.text(min_size=5, max_size=20), min_size=1, max_size=7)),
        "brand_guardrails": {
            "negative_prompts": draw(st.lists(st.text(min_size=5, max_size=30), min_size=0, max_size=5)),
            "forbidden_elements": draw(st.lists(st.text(min_size=5, max_size=20), min_size=0, max_size=3)),
            "required_elements": draw(st.lists(st.text(min_size=5, max_size=20), min_size=0, max_size=3))
        },
        "generation_settings": {
            "seed": draw(st.integers(min_value=0, max_value=999999)),
            "num_inference_steps": draw(st.integers(min_value=20, max_value=50)),
            "guidance_scale": draw(st.integers(min_value=3, max_value=5))
        }
    }



# ============================================================================
# Property-Based Tests
# ============================================================================

def test_strategies_generate_valid_data():
    """Smoke test to ensure strategies can generate data."""
    from hypothesis import given
    
    @given(structured_prompt_strategy())
    def check_structured_prompt(prompt):
        assert "short_description" in prompt
        assert "photographic_characteristics" in prompt
        assert "lighting" in prompt
    
    check_structured_prompt()


# Feature: global-brand-localizer, Property 2: Schema Sanitizer Validity
# Validates: Requirements 3.1, 3.2
@settings(max_examples=100)
@given(vlm_raw_output_strategy())
def test_schema_sanitizer_validity(vlm_output):
    """
    Property 2: Schema Sanitizer Validity
    
    For any VLM raw output, the sanitized result should contain only valid
    FIBO enumerations for camera_angle, lighting_type, and style_medium.
    
    This ensures the sanitizer correctly maps free-form VLM text to valid
    FIBO parameters.
    """
    from schema_sanitizer import SchemaSanitizer
    
    sanitizer = SchemaSanitizer()
    sanitized = sanitizer.sanitize(vlm_output)
    
    # Valid FIBO enumerations
    valid_camera_angles = ["low_angle_iso", "eye_level", "overhead"]
    valid_lighting_types = [
        "soft_natural", "studio_lighting", "high_contrast_key_light",
        "neon_ambient", "golden_hour", "natural_sunlight"
    ]
    valid_style_mediums = [
        "photograph", "digital_illustration", "oil_painting", "3d_render"
    ]
    
    # Check camera_angle is valid
    if "photographic_characteristics" in sanitized:
        photo = sanitized["photographic_characteristics"]
        if "camera_angle" in photo:
            assert photo["camera_angle"] in valid_camera_angles, \
                f"Invalid camera_angle: {photo['camera_angle']}"
    
    # Check lighting conditions are valid
    if "lighting" in sanitized:
        lighting = sanitized["lighting"]
        if "conditions" in lighting:
            assert lighting["conditions"] in valid_lighting_types, \
                f"Invalid lighting type: {lighting['conditions']}"
    
    # Check style_medium is valid
    if "style_medium" in sanitized:
        assert sanitized["style_medium"] in valid_style_mediums, \
            f"Invalid style_medium: {sanitized['style_medium']}"


# Feature: global-brand-localizer, Property 2: Schema Sanitizer Validity (Edge Cases)
# Validates: Requirements 3.1, 3.2
@settings(max_examples=50)
@given(st.text(min_size=1, max_size=100))
def test_schema_sanitizer_handles_unknown_values(unknown_value):
    """
    Property 2 Extension: Schema Sanitizer handles unknown values gracefully.
    
    For any unknown/unmapped value, the sanitizer should return the original
    value rather than crashing or returning invalid data.
    """
    from schema_sanitizer import SchemaSanitizer
    
    sanitizer = SchemaSanitizer()
    
    # Test with unknown camera angle
    test_prompt = {
        "photographic_characteristics": {
            "camera_angle": unknown_value
        }
    }
    
    try:
        sanitized = sanitizer.sanitize(test_prompt)
        # Should not crash and should return something
        assert "photographic_characteristics" in sanitized
        assert "camera_angle" in sanitized["photographic_characteristics"]
    except Exception as e:
        # Should not raise exceptions for unknown values
        assert False, f"Sanitizer crashed on unknown value: {e}"



# Feature: global-brand-localizer, Property 1: Parameter Lock Preservation
# Validates: Requirements 2.1, 4.2
@settings(max_examples=100)
@given(master_json=master_json_strategy(), region_config=region_config_strategy())
def test_parameter_lock_preservation(master_json, region_config):
    """
    Property 1: Parameter Lock Preservation
    
    For any Master JSON and any region configuration, when the Localization Agent
    merges them, all locked parameters from the Master JSON must remain unchanged
    in the output JSON.
    
    This ensures product consistency across all localized variations.
    """
    from localization_agent import LocalizationAgent
    
    agent = LocalizationAgent()
    result = agent.merge_configs(master_json, region_config)
    
    # Validate that locked parameters are preserved
    assert agent.validate_locked_parameters(master_json, result), \
        "Locked parameters were modified during merge"
    
    # Verify locked parameters exist in result
    assert "locked_parameters" in result
    
    # Deep comparison of locked parameters
    master_locked = master_json.get("locked_parameters", {})
    result_locked = result.get("locked_parameters", {})
    
    # Check all keys are preserved
    assert set(master_locked.keys()) == set(result_locked.keys()), \
        f"Locked parameter keys changed: {set(master_locked.keys())} != {set(result_locked.keys())}"
    
    # Check all values are preserved
    for key in master_locked.keys():
        assert master_locked[key] == result_locked[key], \
            f"Locked parameter '{key}' was modified"


# Feature: global-brand-localizer, Property 5: Brand Guardrail Enforcement
# Validates: Requirements 4.3
@settings(max_examples=100)
@given(
    master_json=master_json_strategy(),
    region_config=region_config_strategy(),
    campaign_config=campaign_config_strategy()
)
def test_brand_guardrail_enforcement(master_json, region_config, campaign_config):
    """
    Property 5: Brand Guardrail Enforcement
    
    For any region-specific JSON generated by the Localization Agent, all negative
    prompts from the campaign's brand guardrails must be present in the final JSON.
    
    This ensures brand consistency and compliance across all generated images.
    """
    from localization_agent import LocalizationAgent
    
    agent = LocalizationAgent()
    result = agent.merge_configs(master_json, region_config, campaign_config)
    
    # Get expected negative prompts from campaign config
    expected_negative_prompts = campaign_config.get("brand_guardrails", {}).get("negative_prompts", [])
    
    if expected_negative_prompts:
        # Verify negative prompts are present in result
        assert "negative_prompts" in result, \
            "Negative prompts not added to result JSON"
        
        result_negative_prompts = result.get("negative_prompts", [])
        
        # All expected negative prompts must be present
        for prompt in expected_negative_prompts:
            assert prompt in result_negative_prompts, \
                f"Negative prompt '{prompt}' not found in result"
    
    # Verify forbidden elements are flagged in metadata
    expected_forbidden = campaign_config.get("brand_guardrails", {}).get("forbidden_elements", [])
    if expected_forbidden:
        assert "metadata" in result
        assert "forbidden_elements" in result["metadata"], \
            "Forbidden elements not flagged in metadata"
        
        result_forbidden = result["metadata"].get("forbidden_elements", [])
        for element in expected_forbidden:
            assert element in result_forbidden, \
                f"Forbidden element '{element}' not flagged in metadata"



# Feature: global-brand-localizer, Property 9: Batch Processing Isolation
# Validates: Requirements 8.3
@settings(max_examples=50)  # Reduced iterations due to complexity
@given(
    region_configs=st.lists(region_config_strategy(), min_size=3, max_size=5),
    fail_indices=st.lists(st.integers(min_value=0, max_value=4), min_size=1, max_size=2, unique=True)
)
def test_batch_processing_isolation(region_configs, fail_indices):
    """
    Property 9: Batch Processing Isolation
    
    For any batch of regions being processed, a failure in one region must not
    prevent the processing of other regions in the batch.
    
    This ensures robust batch processing with error isolation.
    """
    from batch_processor import BatchProcessor, JobStatus
    
    # Create mock region JSONs
    region_jsons = []
    for i, config in enumerate(region_configs):
        region_json = {
            "version": "1.0",
            "metadata": {
                "region_id": config["region_id"],
                "should_fail": i in fail_indices  # Mark which should fail
            },
            "locked_parameters": {},
            "variable_parameters": config["environment_overrides"]
        }
        region_jsons.append(region_json)
    
    # Mock processor function that fails for marked regions
    def mock_processor(region_json):
        if region_json["metadata"].get("should_fail", False):
            raise RuntimeError(f"Simulated failure for {region_json['metadata']['region_id']}")
        return {"status": "success"}
    
    # Process batch
    processor = BatchProcessor()
    result = processor.process_batch_sequential(
        region_jsons=region_jsons,
        processor_func=mock_processor
    )
    
    # Verify that non-failing regions completed successfully
    expected_successes = len(region_jsons) - len([i for i in fail_indices if i < len(region_jsons)])
    expected_failures = len([i for i in fail_indices if i < len(region_jsons)])
    
    assert result.completed == expected_successes, \
        f"Expected {expected_successes} successes, got {result.completed}"
    
    assert result.failed == expected_failures, \
        f"Expected {expected_failures} failures, got {result.failed}"
    
    # Verify all jobs were attempted (not stopped early)
    assert result.total_jobs == len(region_jsons), \
        "Not all jobs were attempted"
    
    # Verify failed jobs have error messages
    for job in result.jobs:
        if job.status == JobStatus.FAILED:
            assert job.error is not None, \
                f"Failed job {job.job_id} has no error message"



# Feature: global-brand-localizer, Property 3: Dual Output Consistency
# Validates: Requirements 7.1, 7.2
@settings(max_examples=20, deadline=None)  # Reduced due to file I/O, no deadline for I/O operations
@given(seed=st.integers(min_value=1, max_value=999999))
def test_dual_output_consistency(seed):
    """
    Property 3: Dual Output Consistency
    
    For any generated 16-bit TIFF image, the corresponding 8-bit PNG must be
    a valid downscaled representation with identical aspect ratio and content.
    """
    from output_manager import OutputManager
    from PIL import Image
    import numpy as np
    
    # Create a test image
    test_image = Image.new('RGB', (1024, 1024), color=(128, 128, 128))
    
    # Create output manager
    output_manager = OutputManager(output_dir="output/test_property3")
    
    # Create minimal region JSON
    region_json = {
        "metadata": {
            "region_id": f"test_{seed}",
            "region_name": "Test Region",
            "locale": "en-US",
            "campaign_id": "test_campaign"
        },
        "locked_parameters": {},
        "variable_parameters": {}
    }
    
    # Save dual output
    result = output_manager.save_dual_output(
        image=test_image,
        region_json=region_json,
        region_id=f"test_{seed}",
        seed=seed
    )
    
    # Verify both files were saved
    assert result['tiff_saved'], "TIFF file should be saved"
    assert result['png_saved'], "PNG file should be saved"
    
    # Verify consistency
    from pathlib import Path
    is_consistent, details = output_manager.verify_dual_output_consistency(
        tiff_path=Path(result['tiff_path']),
        png_path=Path(result['png_path'])
    )
    
    assert is_consistent, f"Dual output consistency failed: {details}"
    assert details['aspect_ratio_match'], "Aspect ratios should match"
    assert details['size_match'], "Sizes should be compatible"


# Feature: global-brand-localizer, Property 4: JSON Audit Completeness
# Validates: Requirements 7.3, 7.5, 7.6
@settings(max_examples=20, deadline=None)  # No deadline for I/O operations
@given(
    master_json=master_json_strategy(),
    region_config=region_config_strategy()
)
def test_json_audit_completeness(master_json, region_config):
    """
    Property 4: JSON Audit Completeness
    
    For any saved generation JSON, it must contain both the complete Master JSON
    parameters and all region-specific modifications, formatted as valid JSON.
    """
    from output_manager import OutputManager
    from localization_agent import LocalizationAgent
    from PIL import Image
    import json
    
    # Create region JSON
    agent = LocalizationAgent()
    region_json = agent.merge_configs(master_json, region_config)
    
    # Create test image
    test_image = Image.new('RGB', (512, 512), color=(100, 100, 100))
    
    # Save with output manager
    output_manager = OutputManager(output_dir="output/test_property4")
    result = output_manager.save_dual_output(
        image=test_image,
        region_json=region_json,
        region_id=region_config["region_id"],
        seed=12345
    )
    
    assert result['json_saved'], "JSON should be saved"
    
    # Load and verify JSON
    from pathlib import Path
    with open(Path(result['json_path']), 'r') as f:
        audit_json = json.load(f)
    
    # Verify required keys
    required_keys = [
        "generation_info",
        "output_files",
        "master_json",
        "locked_parameters",
        "variable_parameters"
    ]
    
    for key in required_keys:
        assert key in audit_json, f"Missing required key: {key}"
    
    # Verify it's valid JSON (already loaded, so it's valid)
    # Verify proper indentation by re-serializing
    json_str = json.dumps(audit_json, indent=2)
    assert len(json_str) > 0, "JSON should not be empty"
    assert "\n" in json_str, "JSON should have proper formatting"



# Feature: global-brand-localizer, Property 10: File Format Correctness
# Validates: Requirements 7.1
@settings(max_examples=10, deadline=None)
@given(seed=st.integers(min_value=1, max_value=999999))
def test_file_format_correctness(seed):
    """
    Property 10: File Format Correctness
    
    For any saved 16-bit TIFF file, it must be a valid TIFF format readable
    by standard image processing libraries.
    """
    from output_manager import OutputManager
    from PIL import Image
    
    # Create test image
    test_image = Image.new('RGB', (512, 512), color=(150, 150, 150))
    
    # Create output manager
    output_manager = OutputManager(output_dir="output/test_property10")
    
    # Create minimal region JSON
    region_json = {
        "metadata": {
            "region_id": f"test_{seed}",
            "campaign_id": "test"
        },
        "locked_parameters": {},
        "variable_parameters": {}
    }
    
    # Save dual output
    result = output_manager.save_dual_output(
        image=test_image,
        region_json=region_json,
        region_id=f"test_{seed}",
        seed=seed
    )
    
    assert result['tiff_saved'], "TIFF should be saved"
    
    # Try to open and verify the TIFF file
    from pathlib import Path
    tiff_path = Path(result['tiff_path'])
    
    try:
        # Open with PIL
        tiff_img = Image.open(tiff_path)
        
        # Verify it's a valid image
        assert tiff_img.size[0] > 0, "TIFF width should be positive"
        assert tiff_img.size[1] > 0, "TIFF height should be positive"
        
        # Verify format
        assert tiff_img.format == 'TIFF', f"Format should be TIFF, got {tiff_img.format}"
        
        # Try to load the image data (will fail if corrupted)
        _ = tiff_img.load()
        
    except Exception as e:
        assert False, f"TIFF file is not valid or readable: {e}"


# Feature: global-brand-localizer, Property 6: Consistency Score Bounds
# Validates: Requirements 5.3, 5.4
@settings(max_examples=30, deadline=None)  # Reduced from 100 to 30 - SSIM is expensive
@given(
    width=st.integers(min_value=64, max_value=256),  # Reduced max from 512 to 256
    height=st.integers(min_value=64, max_value=256),  # Reduced max from 512 to 256
    color1=st.tuples(st.integers(0, 255), st.integers(0, 255), st.integers(0, 255)),
    color2=st.tuples(st.integers(0, 255), st.integers(0, 255), st.integers(0, 255))
)
def test_consistency_score_bounds(width, height, color1, color2):
    """
    Property 6: Consistency Score Bounds
    
    For any generated image with a pixel difference heatmap, the consistency
    score must be a value between 0.0 and 1.0 (or 0% to 100%).
    
    This ensures the consistency metric is always valid and interpretable.
    
    Note: Reduced iterations and max size because this test involves:
    - Product mask extraction (segmentation)
    - SSIM calculation (computationally expensive)
    - Multiple image processing operations
    """
    from output_manager import OutputManager
    from PIL import Image
    
    # Create two test images with different colors
    image1 = Image.new('RGB', (width, height), color=color1)
    image2 = Image.new('RGB', (width, height), color=color2)
    
    # Create output manager
    output_manager = OutputManager()
    
    # Calculate consistency score
    consistency_score, heatmap = output_manager.calculate_consistency_score(image1, image2)
    
    # Verify score is within valid bounds
    assert consistency_score >= 0.0, \
        f"Consistency score {consistency_score} is below 0.0"
    
    assert consistency_score <= 1.0, \
        f"Consistency score {consistency_score} is above 1.0"
    
    # Verify heatmap is valid
    assert heatmap is not None, "Heatmap should not be None"
    assert heatmap.shape[0] > 0, "Heatmap height should be positive"
    assert heatmap.shape[1] > 0, "Heatmap width should be positive"
    
    # Verify heatmap values are in valid range (0-255 for uint8)
    assert heatmap.min() >= 0, "Heatmap values should be >= 0"
    assert heatmap.max() <= 255, "Heatmap values should be <= 255"
    
    # Special case: identical images should have score close to 0
    if color1 == color2:
        assert consistency_score < 0.01, \
            f"Identical images should have consistency score near 0, got {consistency_score}"


# Feature: global-brand-localizer, Property 6: Consistency Score Bounds (Edge Case)
# Validates: Requirements 5.3, 5.4
@settings(max_examples=10, deadline=None)  # Reduced from 50 to 10 - SSIM is expensive
@given(size=st.integers(min_value=64, max_value=256))  # Reduced max from 512 to 256
def test_consistency_score_identical_images(size):
    """
    Property 6 Extension: Identical images should have consistency score of 0.
    
    This tests the edge case where generated and master images are identical.
    
    Note: Reduced iterations and max size because this test involves:
    - Product mask extraction (segmentation)
    - SSIM calculation (computationally expensive)
    - Multiple image processing operations
    """
    from output_manager import OutputManager
    from PIL import Image
    import numpy as np
    
    # Create identical images
    image = Image.new('RGB', (size, size), color=(128, 128, 128))
    
    # Create output manager
    output_manager = OutputManager()
    
    # Calculate consistency score
    consistency_score, heatmap = output_manager.calculate_consistency_score(image, image)
    
    # Identical images should have score of 0 (or very close to 0)
    assert consistency_score < 0.001, \
        f"Identical images should have consistency score near 0, got {consistency_score}"
    
    # Heatmap should be all zeros (or very close)
    assert np.mean(heatmap) < 1.0, \
        f"Heatmap for identical images should be near zero, got mean {np.mean(heatmap)}"


# Feature: global-brand-localizer, Property 6: Consistency Score Bounds (Extreme Case)
# Validates: Requirements 5.3, 5.4
@settings(max_examples=10, deadline=None)  # Reduced from 50 to 10 - SSIM is expensive
@given(size=st.integers(min_value=64, max_value=256))  # Reduced max from 512 to 256
def test_consistency_score_opposite_images(size):
    """
    Property 6 Extension: Completely different images should have high consistency score.
    
    This tests the edge case where images are maximally different.
    
    Note: Reduced iterations and max size because this test involves:
    - Product mask extraction (segmentation)
    - SSIM calculation (computationally expensive)
    - Multiple image processing operations
    """
    from output_manager import OutputManager
    from PIL import Image
    
    # Create maximally different images (black vs white)
    image1 = Image.new('RGB', (size, size), color=(0, 0, 0))
    image2 = Image.new('RGB', (size, size), color=(255, 255, 255))
    
    # Create output manager
    output_manager = OutputManager()
    
    # Calculate consistency score
    consistency_score, heatmap = output_manager.calculate_consistency_score(image1, image2)
    
    # Maximally different images should have high score (close to 1.0)
    assert consistency_score > 0.5, \
        f"Maximally different images should have high consistency score, got {consistency_score}"
    
    # Score should still be within bounds
    assert consistency_score <= 1.0, \
        f"Consistency score should not exceed 1.0, got {consistency_score}"


# Feature: global-brand-localizer, Property 7: C2PA Provenance Completeness
# Validates: Requirements 6.1, 6.2
@settings(max_examples=20, deadline=None)
@given(
    master_json=master_json_strategy(),
    region_config=region_config_strategy(),
    seed=st.integers(min_value=1, max_value=999999)
)
def test_c2pa_provenance_completeness(master_json, region_config, seed):
    """
    Property 7: C2PA Provenance Completeness
    
    For any C2PA-signed image (or image that should have C2PA credentials),
    the embedded credentials must contain all required provenance data:
    Master JSON fingerprint, region config, seed, and timestamp.
    
    Note: This test verifies that our system properly tracks and stores
    provenance data, even if c2patool is not available for verification.
    """
    from output_manager import OutputManager
    from localization_agent import LocalizationAgent
    from PIL import Image
    import json
    
    # Create region JSON
    agent = LocalizationAgent()
    region_json = agent.merge_configs(master_json, region_config)
    
    # Create test image
    test_image = Image.new('RGB', (512, 512), color=(100, 150, 200))
    
    # Save with output manager (C2PA verification will be attempted if available)
    output_manager = OutputManager(output_dir="output/test_property7")
    result = output_manager.save_dual_output(
        image=test_image,
        region_json=region_json,
        region_id=region_config["region_id"],
        seed=seed
    )
    
    assert result['json_saved'], "JSON should be saved"
    
    # Load and verify JSON contains provenance data
    from pathlib import Path
    with open(Path(result['json_path']), 'r') as f:
        audit_json = json.load(f)
    
    # Verify C2PA credentials section exists
    assert "c2pa_credentials" in audit_json, \
        "C2PA credentials section should be present in audit JSON"
    
    c2pa_section = audit_json["c2pa_credentials"]
    
    # Verify status is tracked
    assert "status" in c2pa_section, \
        "C2PA status should be tracked"
    
    # Verify generation info contains required provenance data
    gen_info = audit_json.get("generation_info", {})
    
    # Required provenance fields
    assert "timestamp" in gen_info, "Timestamp should be present"
    assert "seed" in gen_info, "Seed should be present"
    assert gen_info["seed"] == seed, f"Seed should match: expected {seed}, got {gen_info['seed']}"
    assert "region_id" in gen_info, "Region ID should be present"
    
    # Verify master JSON reference
    master_section = audit_json.get("master_json", {})
    assert "campaign_id" in master_section or "source_image" in master_section, \
        "Master JSON reference should be present"
    
    # Verify locked and variable parameters are preserved
    assert "locked_parameters" in audit_json, "Locked parameters should be present"
    assert "variable_parameters" in audit_json, "Variable parameters should be present"


# Feature: global-brand-localizer, Property 7: C2PA Provenance Completeness (Edge Case)
# Validates: Requirements 6.1, 6.2
@settings(max_examples=10, deadline=None)
@given(seed=st.integers(min_value=1, max_value=999999))
def test_c2pa_status_tracking_without_tool(seed):
    """
    Property 7 Extension: System tracks C2PA status even when c2patool unavailable.
    
    This ensures provenance data is always recorded, regardless of verification capability.
    """
    from output_manager import OutputManager
    from PIL import Image
    
    # Create test image
    test_image = Image.new('RGB', (256, 256), color=(50, 100, 150))
    
    # Create output manager
    output_manager = OutputManager(output_dir="output/test_property7_edge")
    
    # Create minimal region JSON
    region_json = {
        "metadata": {
            "region_id": f"test_{seed}",
            "campaign_id": "test_campaign",
            "source_image": "test.png"
        },
        "locked_parameters": {"camera_angle": "eye_level"},
        "variable_parameters": {"background": "studio"}
    }
    
    # Save dual output
    result = output_manager.save_dual_output(
        image=test_image,
        region_json=region_json,
        region_id=f"test_{seed}",
        seed=seed
    )
    
    # Verify C2PA status is tracked in result
    assert "c2pa_status" in result, "C2PA status should be in result"
    
    # C2PA status should have a status field
    if result["c2pa_status"]:
        assert "status" in result["c2pa_status"], \
            "C2PA status should have status field"



# Feature: global-brand-localizer, Property 8: Error Recovery State Preservation
# Validates: Requirements 8.6
@settings(max_examples=50, deadline=None)
@given(
    campaign_id=st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), whitelist_characters='_')),
    num_processed=st.integers(min_value=0, max_value=5),
    num_pending=st.integers(min_value=1, max_value=5)
)
def test_error_recovery_state_preservation(campaign_id, num_processed, num_pending):
    """
    Property 8: Error Recovery State Preservation
    
    For any system error that triggers state saving, the saved state must
    contain sufficient information to resume processing from the point of failure.
    
    This ensures robust error recovery and prevents data loss.
    """
    from error_recovery import StateManager
    
    # Create state manager
    state_manager = StateManager(state_dir="output/test_property8")
    
    # Create mock master JSON
    master_json = {
        "version": "1.0",
        "metadata": {"campaign_id": campaign_id},
        "locked_parameters": {"camera_angle": "eye_level"},
        "variable_parameters": {"background": "studio"}
    }
    
    # Create mock processed and pending regions
    processed_regions = [f"region_{i}" for i in range(num_processed)]
    pending_regions = [f"region_{i}" for i in range(num_processed, num_processed + num_pending)]
    
    # Create mock error info
    error_info = {
        "error_type": "GENERATION_ERROR",
        "message": "Simulated error for testing",
        "failed_region": pending_regions[0] if pending_regions else None
    }
    
    # Save state
    state_file = state_manager.save_state(
        campaign_id=campaign_id,
        master_json=master_json,
        processed_regions=processed_regions,
        pending_regions=pending_regions,
        error_info=error_info
    )
    
    # Verify state file was created
    assert state_file.exists(), "State file should be created"
    
    # Load state and verify completeness
    loaded_state = state_manager.load_state(state_file)
    
    # Verify required fields for recovery
    required_fields = ["version", "saved_at", "campaign_id", "master_json", "progress"]
    for field in required_fields:
        assert field in loaded_state, f"State should contain '{field}'"
    
    # Verify campaign ID matches
    assert loaded_state["campaign_id"] == campaign_id, \
        f"Campaign ID should match: expected {campaign_id}, got {loaded_state['campaign_id']}"
    
    # Verify master JSON is preserved
    assert loaded_state["master_json"] == master_json, \
        "Master JSON should be preserved exactly"
    
    # Verify progress information
    progress = loaded_state["progress"]
    assert progress["processed"] == num_processed, \
        f"Processed count should match: expected {num_processed}, got {progress['processed']}"
    assert progress["pending"] == num_pending, \
        f"Pending count should match: expected {num_pending}, got {progress['pending']}"
    assert progress["total_regions"] == num_processed + num_pending, \
        "Total regions should equal processed + pending"
    
    # Verify region lists are preserved
    assert progress["processed_regions"] == processed_regions, \
        "Processed regions list should be preserved"
    assert progress["pending_regions"] == pending_regions, \
        "Pending regions list should be preserved"
    
    # Verify error info is preserved
    assert "error_info" in loaded_state, "Error info should be present"
    assert loaded_state["error_info"] == error_info, \
        "Error info should be preserved"
    
    # Verify recovery instructions are present
    assert "recovery_instructions" in loaded_state, \
        "Recovery instructions should be present"


# Feature: global-brand-localizer, Property 8: Error Recovery State Preservation (Edge Case)
# Validates: Requirements 8.6
@settings(max_examples=20, deadline=None)
@given(campaign_id=st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), whitelist_characters='_')))
def test_error_recovery_state_retrieval(campaign_id):
    """
    Property 8 Extension: Latest state can be retrieved for a campaign.
    
    This ensures state files can be found and loaded for recovery.
    """
    from error_recovery import StateManager
    
    # Create state manager
    state_manager = StateManager(state_dir="output/test_property8_edge")
    
    # Save multiple states for the same campaign
    for i in range(3):
        state_manager.save_state(
            campaign_id=campaign_id,
            master_json={"version": "1.0", "iteration": i},
            processed_regions=[f"region_{j}" for j in range(i)],
            pending_regions=[f"region_{i}"],
            error_info={"iteration": i}
        )
    
    # Get latest state
    latest_state_file = state_manager.get_latest_state(campaign_id)
    
    # Verify latest state was found
    assert latest_state_file is not None, \
        f"Latest state should be found for campaign {campaign_id}"
    
    # Load and verify it's the most recent
    loaded_state = state_manager.load_state(latest_state_file)
    assert loaded_state["master_json"]["iteration"] == 2, \
        "Latest state should be the most recent iteration"
