"""
Localization Agent for Global Brand Localizer

Manages the batch generation process by:
1. Iterating through regions
2. Merging Master JSON with region configurations
3. Applying brand guardrails (negative prompts, forbidden elements)
4. Preserving locked parameters while modifying variable ones
"""

import logging
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
import copy

logger = logging.getLogger(__name__)


class LocalizationAgent:
    """
    Manages localization of Master JSON for different regions.
    
    Key responsibilities:
    - Merge Master JSON with region configurations
    - Preserve locked parameters (product consistency)
    - Apply brand guardrails (negative prompts, forbidden elements)
    - Generate region-specific JSONs for batch processing
    """
    
    def __init__(self):
        """Initialize Localization Agent."""
        logger.info("Localization Agent initialized")
    
    def merge_configs(
        self,
        master_json: Dict[str, Any],
        region_config: Dict[str, Any],
        campaign_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Merge Master JSON with region configuration while preserving locked parameters.
        
        This is the core method that implements Property 1: Parameter Lock Preservation.
        
        Args:
            master_json: Master JSON with locked/variable parameters
            region_config: Region-specific configuration
            campaign_config: Optional campaign configuration with brand guardrails
        
        Returns:
            Region-specific JSON ready for image generation
        """
        logger.info(f"Merging Master JSON with region: {region_config.get('region_id', 'unknown')}")
        
        # Start with a deep copy of master JSON
        result = copy.deepcopy(master_json)
        
        # Update metadata
        result["metadata"]["region_id"] = region_config.get("region_id")
        result["metadata"]["region_name"] = region_config.get("display_name")
        result["metadata"]["locale"] = region_config.get("locale")
        result["metadata"]["localized_at"] = datetime.now().isoformat()
        
        # CRITICAL: Locked parameters MUST NOT be modified
        # This ensures product consistency across all regions
        locked_params = result.get("locked_parameters", {})
        logger.info(f"Preserving {len(locked_params)} locked parameter groups")
        
        # Apply region-specific overrides to VARIABLE parameters only
        variable_params = result.get("variable_parameters", {})
        environment_overrides = region_config.get("environment_overrides", {})
        
        # Merge environment overrides into variable parameters
        for key, value in environment_overrides.items():
            if key in variable_params:
                if isinstance(value, dict) and isinstance(variable_params[key], dict):
                    # Deep merge for nested dicts (like lighting, aesthetics)
                    variable_params[key].update(value)
                else:
                    # Direct replacement for simple values
                    variable_params[key] = value
            else:
                # Add new variable parameter
                variable_params[key] = value
        
        logger.info(f"Applied {len(environment_overrides)} environment overrides")
        
        # Apply brand guardrails if campaign config provided
        if campaign_config:
            result = self._apply_brand_guardrails(result, campaign_config)
        
        # Add cultural context
        result["metadata"]["cultural_context"] = region_config.get("cultural_context", {})
        
        logger.info("✓ Configuration merge complete")
        return result
    
    def _apply_brand_guardrails(
        self,
        region_json: Dict[str, Any],
        campaign_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply brand guardrails to region-specific JSON.
        
        This implements Property 5: Brand Guardrail Enforcement.
        
        Args:
            region_json: Region-specific JSON
            campaign_config: Campaign configuration with guardrails
        
        Returns:
            JSON with brand guardrails applied
        """
        logger.info("Applying brand guardrails...")
        
        guardrails = campaign_config.get("brand_guardrails", {})
        
        # Add negative prompts
        negative_prompts = guardrails.get("negative_prompts", [])
        if negative_prompts:
            region_json["negative_prompts"] = negative_prompts
            logger.info(f"Added {len(negative_prompts)} negative prompts")
        
        # Add forbidden elements to metadata for validation
        forbidden_elements = guardrails.get("forbidden_elements", [])
        if forbidden_elements:
            region_json["metadata"]["forbidden_elements"] = forbidden_elements
            logger.info(f"Flagged {len(forbidden_elements)} forbidden elements")
        
        # Add required elements to metadata for validation
        required_elements = guardrails.get("required_elements", [])
        if required_elements:
            region_json["metadata"]["required_elements"] = required_elements
            logger.info(f"Flagged {len(required_elements)} required elements")
        
        logger.info("✓ Brand guardrails applied")
        return region_json
    
    def process_regions(
        self,
        master_json: Dict[str, Any],
        region_configs: List[Dict[str, Any]],
        campaign_config: Optional[Dict[str, Any]] = None,
        output_dir: Optional[Path] = None
    ) -> List[Dict[str, Any]]:
        """
        Process multiple regions and generate region-specific JSONs.
        
        Args:
            master_json: Master JSON template
            region_configs: List of region configurations
            campaign_config: Optional campaign configuration
            output_dir: Optional directory to save region JSONs
        
        Returns:
            List of region-specific JSONs ready for generation
        """
        logger.info(f"Processing {len(region_configs)} regions...")
        
        region_jsons = []
        
        for region_config in region_configs:
            region_id = region_config.get("region_id", "unknown")
            
            try:
                # Merge configuration
                region_json = self.merge_configs(
                    master_json=master_json,
                    region_config=region_config,
                    campaign_config=campaign_config
                )
                
                region_jsons.append(region_json)
                
                # Save to file if output directory specified
                if output_dir:
                    output_dir = Path(output_dir)
                    output_dir.mkdir(parents=True, exist_ok=True)
                    
                    output_file = output_dir / f"region_{region_id}.json"
                    with open(output_file, 'w') as f:
                        json.dump(region_json, f, indent=2)
                    
                    logger.info(f"✓ Saved region JSON: {output_file}")
                
            except Exception as e:
                logger.error(f"Failed to process region '{region_id}': {e}")
                # Continue processing other regions (implements Property 9: Batch Processing Isolation)
                continue
        
        logger.info(f"✓ Successfully processed {len(region_jsons)}/{len(region_configs)} regions")
        return region_jsons
    
    def validate_locked_parameters(
        self,
        master_json: Dict[str, Any],
        region_json: Dict[str, Any]
    ) -> bool:
        """
        Validate that locked parameters remain unchanged.
        
        This is used for testing Property 1: Parameter Lock Preservation.
        
        Args:
            master_json: Original Master JSON
            region_json: Region-specific JSON
        
        Returns:
            True if all locked parameters are preserved, False otherwise
        """
        master_locked = master_json.get("locked_parameters", {})
        region_locked = region_json.get("locked_parameters", {})
        
        # Deep comparison of locked parameters
        return self._deep_equal(master_locked, region_locked)
    
    def _deep_equal(self, obj1: Any, obj2: Any) -> bool:
        """
        Deep equality comparison for nested dictionaries.
        
        Args:
            obj1: First object
            obj2: Second object
        
        Returns:
            True if objects are deeply equal
        """
        if type(obj1) != type(obj2):
            return False
        
        if isinstance(obj1, dict):
            if set(obj1.keys()) != set(obj2.keys()):
                return False
            return all(self._deep_equal(obj1[k], obj2[k]) for k in obj1.keys())
        
        if isinstance(obj1, list):
            if len(obj1) != len(obj2):
                return False
            return all(self._deep_equal(a, b) for a, b in zip(obj1, obj2))
        
        return obj1 == obj2


# Convenience function
def create_localization_agent() -> LocalizationAgent:
    """
    Create and initialize a Localization Agent.
    
    Returns:
        Initialized LocalizationAgent instance
    """
    return LocalizationAgent()
