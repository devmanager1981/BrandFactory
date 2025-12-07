"""
C2PA Verification Module for Global Brand Localizer

Handles:
- C2PA credential verification using c2patool
- Provenance metadata extraction
- Validation that images are signed by Bria
- Error handling for missing or invalid credentials
"""

import logging
import json
import subprocess
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class C2PAVerifier:
    """
    Verifies and extracts C2PA credentials from generated images.
    
    Note: Bria automatically embeds C2PA credentials during image generation.
    This class verifies their presence and extracts metadata for display.
    """
    
    def __init__(self, c2patool_path: str = "c2patool"):
        """
        Initialize C2PA Verifier.
        
        Args:
            c2patool_path: Path to c2patool executable (default: "c2patool" in PATH)
        """
        self.c2patool_path = c2patool_path
        self.c2patool_available = self._check_c2patool_available()
        
        if self.c2patool_available:
            logger.info("C2PA verifier initialized (c2patool available)")
        else:
            logger.warning("C2PA verifier initialized (c2patool NOT available - verification disabled)")
    
    def _check_c2patool_available(self) -> bool:
        """
        Check if c2patool is available in the system.
        
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
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def verify_image(self, image_path: Path) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify C2PA credentials in an image and extract metadata.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Tuple of (is_valid, metadata_dict)
            - is_valid: True if C2PA credentials are present and valid
            - metadata_dict: Extracted C2PA metadata
        """
        if not self.c2patool_available:
            logger.warning(f"c2patool not available - skipping verification for {image_path.name}")
            return False, {
                "status": "not_verified",
                "reason": "c2patool_not_available",
                "message": "C2PA verification tool not installed"
            }
        
        try:
            # Run c2patool to extract C2PA manifest
            result = subprocess.run(
                [self.c2patool_path, image_path, "--output", "json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.warning(f"C2PA verification failed for {image_path.name}: {result.stderr}")
                return False, {
                    "status": "no_credentials",
                    "reason": "verification_failed",
                    "message": result.stderr or "No C2PA credentials found",
                    "file": str(image_path.name)
                }
            
            # Parse JSON output
            try:
                c2pa_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse c2patool output: {e}")
                return False, {
                    "status": "parse_error",
                    "reason": "invalid_json",
                    "message": "Failed to parse C2PA data"
                }
            
            # Extract key metadata
            metadata = self._extract_metadata(c2pa_data, image_path)
            
            # Verify it's signed by Bria
            is_bria_signed = self._verify_bria_signature(c2pa_data)
            
            if is_bria_signed:
                logger.info(f"✓ C2PA credentials verified for {image_path.name} (signed by Bria)")
                metadata["status"] = "verified"
                metadata["signed_by_bria"] = True
                return True, metadata
            else:
                logger.warning(f"⚠ C2PA credentials found but not signed by Bria for {image_path.name}")
                metadata["status"] = "unverified_signer"
                metadata["signed_by_bria"] = False
                return False, metadata
                
        except subprocess.TimeoutExpired:
            logger.error(f"C2PA verification timeout for {image_path.name}")
            return False, {
                "status": "timeout",
                "reason": "verification_timeout",
                "message": "C2PA verification timed out"
            }
        except Exception as e:
            logger.error(f"Error verifying C2PA credentials: {e}")
            return False, {
                "status": "error",
                "reason": "exception",
                "message": str(e)
            }
    
    def _extract_metadata(self, c2pa_data: Dict[str, Any], image_path: Path) -> Dict[str, Any]:
        """
        Extract relevant metadata from C2PA manifest.
        
        Args:
            c2pa_data: Parsed C2PA JSON data
            image_path: Path to image file
        
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {
            "file": str(image_path.name),
            "has_credentials": True
        }
        
        # Extract manifest information
        if "active_manifest" in c2pa_data:
            manifest = c2pa_data["active_manifest"]
            
            # Extract claim generator (who created it)
            if "claim_generator" in manifest:
                metadata["claim_generator"] = manifest["claim_generator"]
            
            # Extract title
            if "title" in manifest:
                metadata["title"] = manifest["title"]
            
            # Extract signature info
            if "signature_info" in manifest:
                sig_info = manifest["signature_info"]
                metadata["signature_info"] = {
                    "issuer": sig_info.get("issuer"),
                    "time": sig_info.get("time")
                }
            
            # Extract assertions (provenance data)
            if "assertions" in manifest:
                metadata["assertions"] = self._extract_assertions(manifest["assertions"])
        
        return metadata
    
    def _extract_assertions(self, assertions: list) -> Dict[str, Any]:
        """
        Extract key assertions from C2PA manifest.
        
        Args:
            assertions: List of assertions from manifest
        
        Returns:
            Dictionary with extracted assertions
        """
        extracted = {}
        
        for assertion in assertions:
            label = assertion.get("label", "")
            
            # Extract creation info
            if "stds.schema-org.CreativeWork" in label:
                if "data" in assertion:
                    extracted["creative_work"] = assertion["data"]
            
            # Extract actions (what was done to the image)
            if "c2pa.actions" in label:
                if "data" in assertion:
                    extracted["actions"] = assertion["data"]
        
        return extracted
    
    def _verify_bria_signature(self, c2pa_data: Dict[str, Any]) -> bool:
        """
        Verify that the image is signed by Bria.
        
        Args:
            c2pa_data: Parsed C2PA JSON data
        
        Returns:
            True if signed by Bria, False otherwise
        """
        # Check claim generator
        if "active_manifest" in c2pa_data:
            manifest = c2pa_data["active_manifest"]
            
            # Check if claim generator mentions Bria
            claim_generator = manifest.get("claim_generator", "").lower()
            if "bria" in claim_generator:
                return True
            
            # Check signature issuer
            if "signature_info" in manifest:
                sig_info = manifest["signature_info"]
                issuer = sig_info.get("issuer", "").lower()
                if "bria" in issuer:
                    return True
        
        return False
    
    def extract_provenance_summary(self, image_path: Path) -> Dict[str, Any]:
        """
        Extract a summary of provenance data for display.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with provenance summary
        """
        is_valid, metadata = self.verify_image(image_path)
        
        summary = {
            "verified": is_valid,
            "status": metadata.get("status", "unknown"),
            "signed_by_bria": metadata.get("signed_by_bria", False),
            "file": str(image_path.name)
        }
        
        # Add claim generator if available
        if "claim_generator" in metadata:
            summary["generator"] = metadata["claim_generator"]
        
        # Add signature time if available
        if "signature_info" in metadata:
            sig_info = metadata["signature_info"]
            if "time" in sig_info:
                summary["signed_at"] = sig_info["time"]
        
        return summary


# Convenience function
def create_c2pa_verifier(c2patool_path: str = "c2patool") -> C2PAVerifier:
    """
    Create and initialize a C2PA Verifier.
    
    Args:
        c2patool_path: Path to c2patool executable
    
    Returns:
        Initialized C2PAVerifier instance
    """
    return C2PAVerifier(c2patool_path=c2patool_path)
