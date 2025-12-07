"""
Bria Cloud API Manager
Handles all interactions with Bria's hosted FIBO models via REST API
"""

import os
import time
import requests
from typing import Dict, Any, Optional, Union
from pathlib import Path
import base64
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BriaAPIManager:
    """
    Manages interactions with Bria Cloud API for FIBO model access.
    
    Supports:
    - VLM Bridge: Image/Text → JSON (structured_prompt/generate)
    - FIBO Generation: JSON → Image (image/generate)
    - Async polling: Status checking (status/{request_id})
    """
    
    def __init__(
        self,
        api_token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 300,
        poll_interval: int = 2
    ):
        """
        Initialize Bria API Manager.
        
        Args:
            api_token: Bria API token (defaults to BRIA_API_TOKEN env var)
            base_url: API base URL (defaults to BRIA_API_BASE_URL env var)
            timeout: Maximum time to wait for async operations (seconds)
            poll_interval: Time between status polls (seconds)
        """
        self.api_token = api_token or os.getenv("BRIA_API_TOKEN")
        self.base_url = base_url or os.getenv(
            "BRIA_API_BASE_URL",
            "https://engine.prod.bria-api.com/v2"
        )
        self.timeout = timeout
        self.poll_interval = poll_interval
        
        if not self.api_token:
            raise ValueError(
                "Bria API token not found. Set BRIA_API_TOKEN environment variable "
                "or pass api_token parameter."
            )
        
        self.headers = {
            "api_token": self.api_token,  # Bria uses 'api_token' header, not Bearer
            "Content-Type": "application/json"
        }
    
    def _encode_image_to_base64(self, image_path: Union[str, Path]) -> str:
        """
        Encode image file to base64 string for API transmission.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
    
    def _poll_status(self, request_id: str) -> Dict[str, Any]:
        """
        Poll the status endpoint until completion or timeout.
        
        Args:
            request_id: The request ID to poll
            
        Returns:
            Final response with result
            
        Raises:
            TimeoutError: If operation exceeds timeout
            RuntimeError: If operation fails
        """
        status_url = f"{self.base_url}/status/{request_id}"
        start_time = time.time()
        
        while True:
            elapsed = time.time() - start_time
            if elapsed > self.timeout:
                raise TimeoutError(
                    f"Operation timed out after {self.timeout} seconds. "
                    f"Request ID: {request_id}"
                )
            
            response = requests.get(status_url, headers=self.headers)
            response.raise_for_status()
            
            result = response.json()
            status = result.get("status", "").upper()
            
            if status == "COMPLETED":
                return result
            elif status in ["FAILED", "ERROR"]:
                error_msg = result.get("error", "Unknown error")
                raise RuntimeError(
                    f"Operation failed: {error_msg}. Request ID: {request_id}"
                )
            
            # Still processing, wait and retry
            time.sleep(self.poll_interval)
    
    def text_to_json(
        self,
        prompt: str,
        sync: bool = True
    ) -> Dict[str, Any]:
        """
        Convert text prompt to FIBO structured JSON using VLM Bridge.
        
        Args:
            prompt: Natural language description
            sync: If True, wait for completion; if False, return immediately
            
        Returns:
            Dict containing 'structured_prompt' (the FIBO JSON string)
        """
        endpoint = f"{self.base_url}/structured_prompt/generate"
        
        payload = {
            "prompt": prompt,
            "sync": sync
        }
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # If async, poll for completion
        if not sync and "request_id" in result:
            result = self._poll_status(result["request_id"])
        
        return result
    
    def image_to_json(
        self,
        image_path: Union[str, Path],
        prompt: str = "",
        sync: bool = True
    ) -> Dict[str, Any]:
        """
        Convert image to FIBO structured JSON using VLM Bridge (Inspire Mode).
        
        Args:
            image_path: Path to product image
            prompt: Optional text prompt to guide analysis
            sync: If True, wait for completion; if False, return immediately
            
        Returns:
            Dict containing 'structured_prompt' (the FIBO JSON string)
        """
        endpoint = f"{self.base_url}/structured_prompt/generate"
        
        # Encode image to base64
        image_base64 = self._encode_image_to_base64(image_path)
        
        payload = {
            "images": [image_base64],
            "sync": sync
        }
        
        if prompt:
            payload["prompt"] = prompt
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # If async, poll for completion
        if not sync and "request_id" in result:
            result = self._poll_status(result["request_id"])
        
        return result
    
    def json_to_image(
        self,
        structured_prompt: Union[str, Dict[str, Any]],
        prompt: Optional[str] = None,
        aspect_ratio: str = "1:1",
        steps_num: int = 50,
        guidance_scale: int = 5,
        seed: Optional[int] = None,
        sync: bool = True
    ) -> Dict[str, Any]:
        """
        Generate image from FIBO structured JSON or text prompt.
        
        Args:
            structured_prompt: FIBO structured JSON (string or dict) or text prompt
            prompt: Optional refinement prompt (used with structured_prompt)
            aspect_ratio: Image aspect ratio (1:1, 16:9, etc.)
            steps_num: Number of diffusion steps (20-50)
            guidance_scale: Guidance scale (3-5)
            seed: Random seed for reproducibility
            sync: If True, wait for completion; if False, return immediately
            
        Returns:
            Dict containing 'image_url' (URL to generated image)
        """
        endpoint = f"{self.base_url}/image/generate"
        
        # Convert dict to string if needed
        if isinstance(structured_prompt, dict):
            import json
            structured_prompt = json.dumps(structured_prompt)
        
        payload = {
            "aspect_ratio": aspect_ratio,
            "steps_num": steps_num,
            "guidance_scale": guidance_scale,
            "sync": sync
        }
        
        # Check if structured_prompt is a JSON string or plain text
        try:
            import json
            json.loads(structured_prompt)
            # It's valid JSON, use as structured_prompt
            payload["structured_prompt"] = structured_prompt
            if prompt:
                payload["prompt"] = prompt  # Refinement prompt
        except (json.JSONDecodeError, TypeError):
            # It's plain text, use as prompt
            payload["prompt"] = structured_prompt
        
        if seed is not None:
            payload["seed"] = seed
        
        response = requests.post(endpoint, headers=self.headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # If async, poll for completion
        if not sync and "request_id" in result:
            result = self._poll_status(result["request_id"])
        
        return result
    
    def download_image(
        self,
        image_url: str,
        output_path: Optional[Union[str, Path]] = None
    ) -> Image.Image:
        """
        Download generated image from URL.
        
        Args:
            image_url: URL to generated image
            output_path: Optional path to save image
            
        Returns:
            PIL Image object
        """
        response = requests.get(image_url)
        response.raise_for_status()
        
        image = Image.open(BytesIO(response.content))
        
        if output_path:
            image.save(output_path)
        
        return image
    
    def test_connection(self) -> bool:
        """
        Test API connection and authentication.
        
        Returns:
            True if connection successful
            
        Raises:
            Exception if connection fails
        """
        try:
            # Simple test: try to generate JSON from a basic prompt
            result = self.text_to_json("A professional product photo", sync=True)
            # Check for result structure
            if "result" in result and "structured_prompt" in result["result"]:
                return True
            return "structured_prompt" in result
        except Exception as e:
            raise RuntimeError(f"API connection test failed: {str(e)}")


# Convenience function for quick testing
def test_api():
    """Test Bria API connection and basic functionality."""
    print("Testing Bria Cloud API connection...")
    
    try:
        api = BriaAPIManager()
        print("✓ API Manager initialized")
        
        # Test connection
        api.test_connection()
        print("✓ API connection successful")
        
        # Test text-to-JSON
        print("\nTesting text-to-JSON...")
        result = api.text_to_json("A professional product photo of a watch", sync=True)
        
        if "result" in result:
            structured_prompt = result["result"].get("structured_prompt", "")
            print(f"✓ Received structured prompt (length: {len(structured_prompt)} chars)")
        else:
            print(f"✓ Received response: {list(result.keys())}")
        
        print("\n✅ All API tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ API test failed: {str(e)}")
        return False


if __name__ == "__main__":
    test_api()
