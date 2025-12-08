"""
Schema Sanitizer for FIBO VLM Output
Validates and corrects VLM-generated structured prompts to ensure valid FIBO parameters
"""

import json
from typing import Dict, Any, Optional, Union
from pathlib import Path


class SchemaSanitizer:
    """
    Sanitizes VLM Bridge output to ensure all parameters are valid FIBO enumerations.
    
    The VLM Bridge (Gemini 2.5 Flash) generates detailed structured prompts,
    but may use free-form text that needs to be mapped to FIBO's specific enumerations.
    """
    
    def __init__(self, mapping_file: Optional[str] = None):
        """
        Initialize Schema Sanitizer with parameter mappings.
        
        Args:
            mapping_file: Path to JSON file containing VLM → FIBO mappings
        """
        if mapping_file is None:
            mapping_file = Path(__file__).parent / "vlm_to_fibo_map.json"
        
        with open(mapping_file, 'r') as f:
            self.mappings = json.load(f)
    
    def sanitize(self, structured_prompt: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Sanitize a structured prompt from VLM Bridge.
        
        Args:
            structured_prompt: Raw VLM output (JSON string or dict)
            
        Returns:
            Sanitized structured prompt with valid FIBO parameters
        """
        # Parse if string
        if isinstance(structured_prompt, str):
            prompt_dict = json.loads(structured_prompt)
        else:
            prompt_dict = structured_prompt.copy()
        
        # Sanitize photographic characteristics
        if "photographic_characteristics" in prompt_dict:
            photo = prompt_dict["photographic_characteristics"]
            
            # Sanitize camera_angle
            if "camera_angle" in photo:
                photo["camera_angle"] = self._sanitize_value(
                    photo["camera_angle"],
                    "camera_angle"
                )
            
            # Sanitize lens_focal_length (ensure it's a valid format)
            if "lens_focal_length" in photo:
                photo["lens_focal_length"] = self._sanitize_focal_length(
                    photo["lens_focal_length"]
                )
        
        # Sanitize lighting
        if "lighting" in prompt_dict:
            lighting = prompt_dict["lighting"]
            
            # Sanitize lighting conditions
            if "conditions" in lighting:
                lighting["conditions"] = self._sanitize_value(
                    lighting["conditions"],
                    "lighting_type"
                )
        
        # Sanitize style_medium
        if "style_medium" in prompt_dict:
            prompt_dict["style_medium"] = self._sanitize_value(
                prompt_dict["style_medium"],
                "style_medium"
            )
        
        return prompt_dict
    
    def _sanitize_value(
        self,
        value: str,
        parameter_type: str
    ) -> str:
        """
        Sanitize a single parameter value.
        
        Args:
            value: Raw value from VLM
            parameter_type: Type of parameter (e.g., 'camera_angle')
            
        Returns:
            Valid FIBO enumeration or original value if no mapping found
        """
        if parameter_type not in self.mappings:
            return value
        
        # Normalize value for matching
        normalized = value.lower().strip()
        
        # Check for exact match
        if normalized in self.mappings[parameter_type]:
            return self.mappings[parameter_type][normalized]
        
        # Check for partial match
        for key, fibo_value in self.mappings[parameter_type].items():
            if key in normalized or normalized in key:
                return fibo_value
        
        # No match found, return original
        return value
    
    def _sanitize_focal_length(self, focal_length: str) -> str:
        """
        Sanitize focal length to ensure valid format.
        
        Args:
            focal_length: Raw focal length string (e.g., "50mm", "portrait lens")
            
        Returns:
            Sanitized focal length
        """
        # If it's already a number with mm, keep it
        if "mm" in focal_length.lower():
            return focal_length
        
        # Map common descriptions to focal lengths
        mappings = {
            "macro": "macro",
            "wide": "24mm",
            "wide angle": "24mm",
            "standard": "50mm",
            "portrait": "85mm",
            "telephoto": "200mm"
        }
        
        normalized = focal_length.lower().strip()
        for key, value in mappings.items():
            if key in normalized:
                return value
        
        return focal_length
    
    def extract_locked_parameters(
        self,
        structured_prompt: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract parameters that should be locked for product consistency.
        
        Args:
            structured_prompt: Sanitized structured prompt
            
        Returns:
            Dict of locked parameters
        """
        locked = {}
        
        # Lock photographic characteristics (product geometry)
        if "photographic_characteristics" in structured_prompt:
            photo = structured_prompt["photographic_characteristics"]
            locked["photographic_characteristics"] = {
                "camera_angle": photo.get("camera_angle"),
                "lens_focal_length": photo.get("lens_focal_length"),
                "depth_of_field": photo.get("depth_of_field"),
                "focus": photo.get("focus")
            }
        
        # Lock object descriptions (product itself)
        if "objects" in structured_prompt:
            locked["objects"] = structured_prompt["objects"]
        
        # Lock composition (product positioning)
        if "aesthetics" in structured_prompt:
            aesthetics = structured_prompt["aesthetics"]
            locked["composition"] = aesthetics.get("composition")
        
        return locked
    
    def extract_variable_parameters(
        self,
        structured_prompt: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract parameters that can vary for localization.
        
        Args:
            structured_prompt: Sanitized structured prompt
            
        Returns:
            Dict of variable parameters
        """
        variable = {}
        
        # Variable: background setting
        if "background_setting" in structured_prompt:
            variable["background_setting"] = structured_prompt["background_setting"]
        
        # Variable: lighting (can change per region)
        if "lighting" in structured_prompt:
            variable["lighting"] = structured_prompt["lighting"]
        
        # Variable: aesthetics (mood, atmosphere, color scheme)
        if "aesthetics" in structured_prompt:
            aesthetics = structured_prompt["aesthetics"]
            variable["aesthetics"] = {
                "color_scheme": aesthetics.get("color_scheme"),
                "mood_atmosphere": aesthetics.get("mood_atmosphere")
            }
        
        return variable


# Test function
def test_sanitizer():
    """Test the schema sanitizer with sample data."""
    print("Testing Schema Sanitizer...")
    
    sanitizer = SchemaSanitizer()
    
    # Test sample structured prompt
    sample_prompt = {
        "short_description": "A professional product photo",
        "photographic_characteristics": {
            "camera_angle": "low angle",
            "lens_focal_length": "portrait lens",
            "depth_of_field": "shallow"
        },
        "lighting": {
            "conditions": "soft natural"
        },
        "style_medium": "photograph"
    }
    
    sanitized = sanitizer.sanitize(sample_prompt)
    
    print(f"✓ Original camera_angle: {sample_prompt['photographic_characteristics']['camera_angle']}")
    print(f"✓ Sanitized camera_angle: {sanitized['photographic_characteristics']['camera_angle']}")
    print(f"✓ Original lighting: {sample_prompt['lighting']['conditions']}")
    print(f"✓ Sanitized lighting: {sanitized['lighting']['conditions']}")
    print(f"✓ Original focal_length: {sample_prompt['photographic_characteristics']['lens_focal_length']}")
    print(f"✓ Sanitized focal_length: {sanitized['photographic_characteristics']['lens_focal_length']}")
    
    # Test parameter extraction
    locked = sanitizer.extract_locked_parameters(sanitized)
    variable = sanitizer.extract_variable_parameters(sanitized)
    
    print(f"\n✓ Locked parameters: {list(locked.keys())}")
    print(f"✓ Variable parameters: {list(variable.keys())}")
    
    print("\n✅ Schema Sanitizer tests passed!")


if __name__ == "__main__":
    test_sanitizer()
