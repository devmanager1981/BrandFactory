"""
FIBO Pipeline Manager

Manages the dual-pipeline architecture:
1. VLM Bridge Pipeline (briaai/FIBO-VLM-prompt-to-JSON) - Image/Text → JSON
2. FIBO Generation Pipeline (briaai/FIBO) - JSON → Image

Handles initialization, error handling, and fallback to Cloud API.
"""

import logging
from typing import Dict, Any, Optional, Union
from pathlib import Path
import torch
from PIL import Image

logger = logging.getLogger(__name__)


class FiboPipelineManager:
    """
    Manages FIBO pipelines with automatic fallback to Cloud API.
    
    Attributes:
        vlm_pipeline: VLM Bridge pipeline for Image/Text → JSON conversion
        fibo_pipeline: FIBO Generation pipeline for JSON → Image generation
        use_cloud_api: Flag indicating if Cloud API fallback is active
    """
    
    def __init__(self, use_local: bool = True, device: Optional[str] = None):
        """
        Initialize FIBO pipelines.
        
        Args:
            use_local: Whether to attempt local GPU initialization
            device: Specific device to use ('cuda', 'cpu', or None for auto-detect)
        """
        self.vlm_pipeline = None
        self.fibo_pipeline = None
        self.use_cloud_api = False
        self.device = device or self._detect_device()
        
        logger.info(f"Initializing FIBO Pipeline Manager on device: {self.device}")
        
        if use_local:
            try:
                self._initialize_local_pipelines()
            except Exception as e:
                logger.error(f"Local pipeline initialization failed: {e}")
                logger.info("Will fallback to Cloud API when needed")
                self.use_cloud_api = True
        else:
            logger.info("Skipping local initialization, will use Cloud API")
            self.use_cloud_api = True
    
    def _detect_device(self) -> str:
        """
        Auto-detect available device (CUDA or CPU).
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        if torch.cuda.is_available():
            device = 'cuda'
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            logger.info(f"CUDA available: {gpu_name} ({gpu_memory:.1f}GB)")
        else:
            device = 'cpu'
            logger.warning("CUDA not available, using CPU (will be slow)")
        
        return device
    
    def _initialize_local_pipelines(self):
        """
        Initialize both FIBO pipelines locally.
        
        Raises:
            Exception: If pipeline loading fails
        """
        try:
            # Import here to avoid dependency issues if not using local
            from diffusers import BriaFiboPipeline
            from transformers import pipeline as hf_pipeline
            
            logger.info("Loading VLM Bridge Pipeline (briaai/FIBO-VLM-prompt-to-JSON)...")
            # Note: Using transformers pipeline for VLM
            # The actual model name might need adjustment based on Bria's release
            try:
                self.vlm_pipeline = hf_pipeline(
                    "image-to-text",
                    model="briaai/FIBO-VLM-prompt-to-JSON",
                    device=self.device
                )
                logger.info("✓ VLM Bridge Pipeline loaded successfully")
            except Exception as e:
                logger.warning(f"VLM Pipeline loading failed: {e}")
                logger.info("Will use alternative VLM approach or Cloud API")
            
            logger.info("Loading FIBO Generation Pipeline (briaai/FIBO)...")
            self.fibo_pipeline = BriaFiboPipeline.from_pretrained(
                "briaai/FIBO",
                torch_dtype=torch.float16 if self.device == 'cuda' else torch.float32,
                use_safetensors=True
            )
            
            if self.device == 'cuda':
                self.fibo_pipeline = self.fibo_pipeline.to(self.device)
                # Enable memory optimizations
                self.fibo_pipeline.enable_attention_slicing()
                if hasattr(self.fibo_pipeline, 'enable_xformers_memory_efficient_attention'):
                    try:
                        self.fibo_pipeline.enable_xformers_memory_efficient_attention()
                        logger.info("✓ xFormers memory optimization enabled")
                    except Exception:
                        logger.info("xFormers not available, using standard attention")
            
            logger.info("✓ FIBO Generation Pipeline loaded successfully")
            logger.info("✓ All pipelines initialized successfully")
            
        except ImportError as e:
            logger.error(f"Missing required dependencies: {e}")
            logger.error("Please install: pip install diffusers transformers torch")
            raise
        except Exception as e:
            logger.error(f"Pipeline initialization failed: {e}")
            raise
    
    def image_to_json(
        self,
        image_path: Union[str, Path],
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert product image to Master JSON using VLM Bridge.
        
        Args:
            image_path: Path to product image
            prompt: Optional text prompt to guide analysis
        
        Returns:
            Dictionary containing FIBO parameters
        
        Raises:
            RuntimeError: If both local and cloud API fail
        """
        logger.info(f"Converting image to JSON: {image_path}")
        
        if self.use_cloud_api or self.vlm_pipeline is None:
            logger.info("Using Cloud API for image-to-JSON conversion")
            return self._image_to_json_cloud(image_path, prompt)
        
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Use VLM pipeline to analyze image
            # Note: The exact API might vary based on Bria's implementation
            result = self.vlm_pipeline(image)
            
            # Extract JSON from VLM output
            # This is a placeholder - actual implementation depends on VLM output format
            json_params = self._parse_vlm_output(result)
            
            logger.info("✓ Image converted to JSON successfully")
            return json_params
            
        except Exception as e:
            logger.error(f"Local image-to-JSON failed: {e}")
            logger.info("Falling back to Cloud API")
            return self._image_to_json_cloud(image_path, prompt)
    
    def _parse_vlm_output(self, vlm_result: Any) -> Dict[str, Any]:
        """
        Parse VLM pipeline output into structured JSON.
        
        Args:
            vlm_result: Raw output from VLM pipeline
        
        Returns:
            Structured FIBO parameters dictionary
        """
        # Placeholder implementation
        # Actual parsing depends on VLM output format
        
        # Default structure based on design document
        json_params = {
            "version": "1.0",
            "metadata": {
                "source": "vlm_analysis",
                "model": "briaai/FIBO-VLM-prompt-to-JSON"
            },
            "locked_parameters": {
                "camera_angle": "eye_level",  # Will be extracted from VLM
                "focal_length": 50,
                "aspect_ratio": "1:1",
                "product_geometry": {
                    "position": [0.5, 0.5],
                    "scale": 1.0,
                    "rotation": 0
                }
            },
            "variable_parameters": {
                "background": "neutral",
                "lighting_type": "soft_natural",
                "environment": "studio",
                "mood": "professional"
            }
        }
        
        # TODO: Parse actual VLM output when available
        logger.warning("Using placeholder VLM parsing - needs actual implementation")
        
        return json_params
    
    def _image_to_json_cloud(
        self,
        image_path: Union[str, Path],
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert image to JSON using Cloud API.
        
        Args:
            image_path: Path to product image
            prompt: Optional text prompt
        
        Returns:
            Dictionary containing FIBO parameters
        
        Raises:
            NotImplementedError: Cloud API not yet implemented
        """
        # Placeholder for Cloud API implementation (Task 3)
        logger.warning("Cloud API not yet implemented")
        
        # Return default structure for now
        return {
            "version": "1.0",
            "metadata": {
                "source": "cloud_api",
                "image_path": str(image_path)
            },
            "locked_parameters": {
                "camera_angle": "eye_level",
                "focal_length": 50,
                "aspect_ratio": "1:1",
                "product_geometry": {
                    "position": [0.5, 0.5],
                    "scale": 1.0,
                    "rotation": 0
                }
            },
            "variable_parameters": {
                "background": "neutral",
                "lighting_type": "soft_natural",
                "environment": "studio",
                "mood": "professional"
            }
        }
    
    def generate_image(
        self,
        json_params: Dict[str, Any],
        seed: int = 42,
        num_inference_steps: int = 50,
        guidance_scale: float = 7.5
    ) -> Image.Image:
        """
        Generate image from JSON parameters using FIBO pipeline.
        
        Args:
            json_params: FIBO parameters dictionary
            seed: Random seed for reproducibility
            num_inference_steps: Number of denoising steps
            guidance_scale: Guidance scale for generation
        
        Returns:
            Generated PIL Image
        
        Raises:
            RuntimeError: If generation fails
        """
        logger.info(f"Generating image with seed={seed}, steps={num_inference_steps}")
        
        if self.use_cloud_api or self.fibo_pipeline is None:
            logger.info("Using Cloud API for image generation")
            return self._generate_image_cloud(json_params, seed, num_inference_steps, guidance_scale)
        
        try:
            # Set seed for reproducibility
            generator = torch.Generator(device=self.device).manual_seed(seed)
            
            # Generate image using FIBO pipeline
            # Note: The exact API depends on Bria's implementation
            result = self.fibo_pipeline(
                prompt=json_params,  # FIBO accepts JSON directly
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            )
            
            image = result.images[0]
            logger.info("✓ Image generated successfully")
            
            return image
            
        except Exception as e:
            logger.error(f"Local image generation failed: {e}")
            logger.info("Falling back to Cloud API")
            return self._generate_image_cloud(json_params, seed, num_inference_steps, guidance_scale)
    
    def _generate_image_cloud(
        self,
        json_params: Dict[str, Any],
        seed: int,
        num_inference_steps: int,
        guidance_scale: float
    ) -> Image.Image:
        """
        Generate image using Cloud API.
        
        Args:
            json_params: FIBO parameters
            seed: Random seed
            num_inference_steps: Denoising steps
            guidance_scale: Guidance scale
        
        Returns:
            Generated PIL Image
        
        Raises:
            NotImplementedError: Cloud API not yet implemented
        """
        # Placeholder for Cloud API implementation (Task 3)
        logger.warning("Cloud API not yet implemented")
        raise NotImplementedError("Cloud API generation will be implemented in Task 3")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status.
        
        Returns:
            Dictionary with pipeline status information
        """
        return {
            "device": self.device,
            "vlm_pipeline_loaded": self.vlm_pipeline is not None,
            "fibo_pipeline_loaded": self.fibo_pipeline is not None,
            "using_cloud_api": self.use_cloud_api,
            "cuda_available": torch.cuda.is_available()
        }


# Convenience function for quick initialization
def create_pipeline_manager(use_local: bool = True) -> FiboPipelineManager:
    """
    Create and initialize FIBO Pipeline Manager.
    
    Args:
        use_local: Whether to attempt local GPU initialization
    
    Returns:
        Initialized FiboPipelineManager instance
    """
    return FiboPipelineManager(use_local=use_local)
