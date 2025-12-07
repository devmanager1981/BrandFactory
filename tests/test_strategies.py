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
