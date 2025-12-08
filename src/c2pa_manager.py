"""
C2PA Manager for Global Brand Localizer

Handles:
- C2PA content credentials embedding
- Provenance data management
- C2PA signing with error handling
- Verification support

Note: This implementation uses c2patool CLI as the C2PA SDK.
For production, consider using the c2pa-python library when available.
"""

import logging
import json
import subprocess
import hashlib
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class C2PAManager:
    """
    Manages C2PA content credentials for generated images.
    
    Key features:
    - Embeds provenance data (Master JSON fingerprint, region, seed, timestamp)
    - Uses c2patool CLI for signing
    - Graceful error handling when C2PA is unavailable
    - Verification support
    """
    
    def __init__(self, c2patool_path: Optional[str] = "c2patool"):
        """
        Initialize C2PA Manager.
        
        Args:
            c2patool_path: Path to c2patool executable (default: "c2patool" in PATH)
        """
        self.c2patool_path = c2patool_path
        self.c2pa_available = self._check_c2pa_availability()
        
        if self.c2pa_available:
            logger.info("C2PA Manager initialized (c2patool available)")
        else:
            logger.warning("C2PA Manager initialized (c2patool NOT available - signing disabled)")
    
    def _check_c2pa_availability(self) -> bool:
        """
        Check if c2patool is available on the system.
        
        Returns:
            True if c2patool is available, False otherwise
        """
        try:
            result = subprocess.run(
                [self.c2patool_path, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            logger.debug(f"c2patool not available: {e}")
            return False
    
    def calculate_json_fingerprint(self, json_data: Dict[str, Any]) -> str:
        """
        Calculate SHA-256 fingerprint of Master JSON.
        
        Args:
            json_data: Master JSON dictionary
        
        Returns:
            Hex string of SHA-256 hash
        """
        # Serialize JSON in a deterministic way
        json_str = json.dumps(json_data, sort_keys=True, separators=(',', ':'))
        
        # Calculate SHA-256 hash
        hash_obj = hashlib.sha256(json_str.encode('utf-8'))
        fingerprint = hash_obj.hexdigest()
        
        logger.debug(f"JSON fingerprint calculated: {fingerprint[:16]}...")
        
        return fingerprint
    
    def create_provenance_manifest(
        self,
        master_json: Dict[str, Any],
        region_config: Dict[str, Any],
        seed: int,
        generation_timestamp: str
    ) -> Dict[str, Any]:
        """
        Create C2PA provenance manifest with all required data.
        
        Args:
            master_json: Master JSON configuration
            region_config: Region-specific configuration
            seed: Random seed used for generation
            generation_timestamp: ISO8601 timestamp of generation
        
        Returns:
            Provenance manifest dictionary
        """
        # Calculate Master JSON fingerprint
        master_fingerprint = self.calculate_json_fingerprint(master_json)
        
        # Create manifest
        manifest = {
            "claim_generator": "Global Brand Localizer v1.0",
            "claim_generator_info": [
                {
                    "name": "Global Brand Localizer",
                    "version": "1.0.0"
                }
            ],
            "title": f"Localized Product Image - {region_config.get('display_name', 'Unknown')}",
            "format": "image/tiff",
            "instance_id": f"xmp.iid:{master_fingerprint[:32]}",
            "assertions": [
                {
                    "label": "c2pa.actions",
                    "data": {
                        "actions": [
                            {
                                "action": "c2pa.created",
                                "when": generation_timestamp,
                                "softwareAgent": "Global Brand Localizer/1.0 (Bria FIBO)"
                            }
                        ]
                    }
                },
                {
                    "label": "stds.schema-org.CreativeWork",
                    "data": {
                        "@context": "https://schema.org",
                        "@type": "CreativeWork",
                        "author": [
                            {
                                "@type": "Organization",
                                "name": "Global Brand Localizer"
                            }
                        ],
                        "dateCreated": generation_timestamp
                    }
                }
            ],
            "provenance": {
                "master_json_fingerprint": master_fingerprint,
                "region_id": region_config.get("region_id"),
                "region_name": region_config.get("display_name"),
                "locale": region_config.get("locale"),
                "generation_seed": seed,
                "generation_timestamp": generation_timestamp,
                "campaign_id": master_json.get("metadata", {}).get("campaign_id"),
                "source_image": master_json.get("metadata", {}).get("source_image")
            }
        }
        
        logger.info(f"Provenance manifest created for region: {region_config.get('region_id')}")
        
        return manifest
    
    def embed_credentials(
        self,
        image_path: Path,
        master_json: Dict[str, Any],
        region_config: Dict[str, Any],
        seed: int,
        output_path: Optional[Path] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Embed C2PA credentials into image file.
        
        Args:
            image_path: Path to image file to sign
            master_json: Master JSON configuration
            region_config: Region-specific configuration
            seed: Random seed used
            output_path: Optional output path (default: overwrite input)
        
        Returns:
            Tuple of (success, error_message)
        """
        if not self.c2pa_available:
            logger.warning("C2PA signing skipped - c2patool not available")
            return False, "c2patool not available"
        
        try:
            # Create provenance manifest
            generation_timestamp = datetime.now().isoformat()
            manifest = self.create_provenance_manifest(
                master_json=master_json,
                region_config=region_config,
                seed=seed,
                generation_timestamp=generation_timestamp
            )
            
            # Save manifest to temporary file
            manifest_path = image_path.parent / f"{image_path.stem}_manifest.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            # Determine output path
            if output_path is None:
                output_path = image_path
            
            # Run c2patool to embed credentials
            # Note: This is a simplified implementation
            # In production, you would use proper c2patool commands with certificates
            cmd = [
                self.c2patool_path,
                image_path,
                "-m", str(manifest_path),
                "-o", str(output_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Clean up manifest file
            try:
                manifest_path.unlink()
            except Exception:
                pass
            
            if result.returncode == 0:
                logger.info(f"✓ C2PA credentials embedded successfully: {image_path.name}")
                return True, None
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                logger.error(f"✗ C2PA signing failed: {error_msg}")
                return False, error_msg
                
        except subprocess.TimeoutExpired:
            error_msg = "C2PA signing timed out"
            logger.error(f"✗ {error_msg}")
            return False, error_msg
            
        except Exception as e:
            error_msg = f"C2PA signing error: {str(e)}"
            logger.error(f"✗ {error_msg}")
            return False, error_msg
    
    def verify_credentials(self, image_path: Path) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Verify C2PA credentials in an image file.
        
        Args:
            image_path: Path to image file to verify
        
        Returns:
            Tuple of (is_valid, manifest_data)
        """
        if not self.c2pa_available:
            logger.warning("C2PA verification skipped - c2patool not available")
            return False, None
        
        try:
            # Run c2patool to verify credentials
            cmd = [
                self.c2patool_path,
                image_path,
                "--detailed"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse output (simplified - actual parsing would be more complex)
                logger.info(f"✓ C2PA credentials verified: {image_path.name}")
                return True, {"raw_output": result.stdout}
            else:
                logger.warning(f"⚠ C2PA verification failed: {image_path.name}")
                return False, None
                
        except Exception as e:
            logger.error(f"✗ C2PA verification error: {e}")
            return False, None
    
    def get_provenance_summary(
        self,
        master_json: Dict[str, Any],
        region_config: Dict[str, Any],
        seed: int
    ) -> Dict[str, Any]:
        """
        Get a summary of provenance data without signing.
        
        Useful for displaying provenance info in UI before signing.
        
        Args:
            master_json: Master JSON configuration
            region_config: Region-specific configuration
            seed: Random seed used
        
        Returns:
            Provenance summary dictionary
        """
        fingerprint = self.calculate_json_fingerprint(master_json)
        
        return {
            "master_json_fingerprint": fingerprint,
            "region_id": region_config.get("region_id"),
            "region_name": region_config.get("display_name"),
            "locale": region_config.get("locale"),
            "generation_seed": seed,
            "campaign_id": master_json.get("metadata", {}).get("campaign_id"),
            "c2pa_available": self.c2pa_available
        }


# Convenience function
def create_c2pa_manager(c2patool_path: Optional[str] = None) -> C2PAManager:
    """
    Create and initialize a C2PA Manager.
    
    Args:
        c2patool_path: Optional path to c2patool executable
    
    Returns:
        Initialized C2PAManager instance
    """
    if c2patool_path:
        return C2PAManager(c2patool_path=c2patool_path)
    else:
        return C2PAManager()
