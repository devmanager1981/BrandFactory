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
