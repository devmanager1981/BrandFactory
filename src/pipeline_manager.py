"""
FIBO Pipeline Manager

Manages the dual-pipeline architecture:
1. VLM Bridge Pipeline (briaai/FIBO-VLM-prompt-to-JSON) - Image/Text → JSON
2. FIBO Generation Pipeline (briaai/FIBO) - JSON → Image

Handles initialization, error handling, and fallback to Cloud API.
"""

import logging
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path
from datetime import datetime
from PIL import Image

# Import API Manager and Schema Sanitizer
from api_manager import BriaAPIManager
from schema_sanitizer import SchemaSanitizer

# Optional torch import for local GPU support
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class FiboPipelineManager:
    """
    Manages FIBO pipelines with automatic fallback to Cloud API.
    
    Attributes:
        vlm_pipeline: VLM Bridge pipeline for Image/Text → JSON conversion
        fibo_pipeline: FIBO Generation pipeline for JSON → Image generation
        use_cloud_api: Flag indicating if Cloud API fallback is active
    """
    
    def __init__(self, use_local: bool = False, device: Optional[str] = None):
        """
        Initialize FIBO pipelines.
        
        Args:
            use_local: Whether to attempt local GPU initialization (default: False, use Cloud API)
            device: Specific device to use ('cuda', 'cpu', or None for auto-detect)
        """
        self.vlm_pipeline = None
        self.fibo_pipeline = None
        self.use_cloud_api = not use_local  # Default to Cloud API
        self.device = device or self._detect_device()
        
        # Initialize API Manager and Schema Sanitizer
        self.api_manager = BriaAPIManager()
        self.sanitizer = SchemaSanitizer()
        
        logger.info(f"Initializing FIBO Pipeline Manager on device: {self.device}")
        logger.info(f"Using Cloud API: {self.use_cloud_api}")
        
        if use_local:
            try:
                self._initialize_local_pipelines()
            except Exception as e:
                logger.error(f"Local pipeline initialization failed: {e}")
                logger.info("Will fallback to Cloud API when needed")
                self.use_cloud_api = True
        else:
            logger.info("Using Cloud API for all operations")
            self.use_cloud_api = True
    
    def _detect_device(self) -> str:
        """
        Auto-detect available device (CUDA or CPU).
        
        Returns:
            Device string ('cuda' or 'cpu')
        """
        if not TORCH_AVAILABLE:
            logger.info("PyTorch not available, will use Cloud API")
            return 'cpu'
        
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
        
        This method:
        1. Calls VLM Bridge API to analyze the image
        2. Sanitizes the output to ensure valid FIBO parameters
        3. Extracts locked and variable parameters
        4. Returns a properly structured Master JSON
        
        Args:
            image_path: Path to product image
            prompt: Optional text prompt to guide analysis
        
        Returns:
            Dictionary containing Master JSON with locked/variable parameters
        
        Raises:
            RuntimeError: If VLM Bridge fails
        """
        logger.info(f"Converting image to Master JSON: {image_path}")
        
        if self.use_cloud_api or self.vlm_pipeline is None:
            logger.info("Using Cloud API for image-to-JSON conversion")
            return self._image_to_json_cloud(image_path, prompt)
        
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Use VLM pipeline to analyze image
            result = self.vlm_pipeline(image)
            
            # Extract JSON from VLM output
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
        Convert image to Master JSON using Cloud API with sanitization.
        
        Process:
        1. Call Bria VLM Bridge API (image_to_json)
        2. Parse the structured_prompt from response
        3. Sanitize using Schema Sanitizer
        4. Extract locked and variable parameters
        5. Build Master JSON structure
        
        Args:
            image_path: Path to product image
            prompt: Optional text prompt to guide analysis
        
        Returns:
            Master JSON dictionary with locked/variable parameters
        
        Raises:
            RuntimeError: If API call or sanitization fails
        """
        try:
            # Step 1: Call VLM Bridge API
            logger.info("Calling VLM Bridge API (image-to-JSON)...")
            api_result = self.api_manager.image_to_json(
                image_path=image_path,
                prompt=prompt or "Analyze this product image and extract visual parameters",
                sync=True
            )
            
            # Step 2: Extract structured_prompt from API response
            # API v2 returns: {"result": {"structured_prompt": "...", "seed": 123}, "request_id": "..."}
            if "result" in api_result and "structured_prompt" in api_result["result"]:
                structured_prompt_str = api_result["result"]["structured_prompt"]
                seed_used = api_result["result"].get("seed")
                logger.info(f"Received structured prompt from VLM (seed: {seed_used})")
            else:
                logger.warning("Unexpected API response format, using fallback")
                structured_prompt_str = "{}"
            
            logger.info(f"Structured prompt length: {len(structured_prompt_str)} chars")
            
            # Parse JSON string
            try:
                structured_prompt = json.loads(structured_prompt_str)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse VLM output as JSON: {e}")
                logger.warning("Using default parameters")
                structured_prompt = self._get_default_structured_prompt()
            
            # Step 3: Sanitize VLM output
            logger.info("Sanitizing VLM output...")
            sanitized_prompt = self.sanitizer.sanitize(structured_prompt)
            logger.info("✓ VLM output sanitized successfully")
            
            # Step 4: Extract locked and variable parameters
            locked_params = self.sanitizer.extract_locked_parameters(sanitized_prompt)
            variable_params = self.sanitizer.extract_variable_parameters(sanitized_prompt)
            
            # Step 5: Build Master JSON
            master_json = {
                "version": "1.0",
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "source_image": str(image_path),
                    "campaign_id": f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "vlm_model": "briaai/FIBO-VLM-prompt-to-JSON"
                },
                "locked_parameters": locked_params,
                "variable_parameters": variable_params
            }
            
            logger.info("✓ Master JSON created successfully")
            logger.info(f"  - Locked parameters: {list(locked_params.keys())}")
            logger.info(f"  - Variable parameters: {list(variable_params.keys())}")
            
            return master_json
            
        except Exception as e:
            logger.error(f"Cloud API image-to-JSON failed: {e}")
            logger.warning("Returning default Master JSON structure")
            return self._get_default_master_json(image_path)
    
    def _get_default_structured_prompt(self) -> Dict[str, Any]:
        """
        Get default structured prompt when VLM fails.
        
        Returns:
            Default structured prompt dictionary
        """
        return {
            "short_description": "Professional product photo",
            "photographic_characteristics": {
                "camera_angle": "eye_level",
                "lens_focal_length": "50mm",
                "depth_of_field": "shallow",
                "focus": "sharp focus on subject"
            },
            "lighting": {
                "conditions": "soft_natural",
                "direction": "front lighting",
                "shadows": "soft shadows"
            },
            "style_medium": "photograph",
            "background_setting": "neutral studio background",
            "aesthetics": {
                "composition": "centered",
                "color_scheme": "neutral tones",
                "mood_atmosphere": "professional"
            }
        }
    
    def _get_default_master_json(self, image_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get default Master JSON when all else fails.
        
        Args:
            image_path: Path to source image
        
        Returns:
            Default Master JSON structure
        """
        return {
            "version": "1.0",
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "source_image": str(image_path),
                "campaign_id": f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "note": "Default parameters used due to VLM failure"
            },
            "locked_parameters": {
                "photographic_characteristics": {
                    "camera_angle": "eye_level",
                    "lens_focal_length": "50mm",
                    "depth_of_field": "shallow",
                    "focus": "sharp focus on subject"
                },
                "composition": "centered"
            },
            "variable_parameters": {
                "background_setting": "neutral studio background",
                "lighting": {
                    "conditions": "soft_natural",
                    "direction": "front lighting",
                    "shadows": "soft shadows"
                },
                "aesthetics": {
                    "color_scheme": "neutral tones",
                    "mood_atmosphere": "professional"
                }
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
            if not TORCH_AVAILABLE:
                raise RuntimeError("PyTorch not available for local generation")
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
            json_params: FIBO parameters (can be full Master JSON or just structured_prompt)
            seed: Random seed
            num_inference_steps: Denoising steps
            guidance_scale: Guidance scale
        
        Returns:
            Generated PIL Image
        """
        try:
            logger.info("Generating image via Cloud API...")
            
            # Convert json_params to a text prompt for the API
            # The Bria API works better with text prompts than raw structured_prompt JSON
            if "locked_parameters" in json_params and "variable_parameters" in json_params:
                # This is a full Master/Region JSON, convert to descriptive text prompt
                text_prompt = self._convert_to_text_prompt(json_params)
            elif isinstance(json_params, dict) and "short_description" in json_params:
                # This looks like a structured_prompt, extract description
                text_prompt = json_params.get("short_description", "Professional product photo")
            elif isinstance(json_params, str):
                # Already a text prompt
                text_prompt = json_params
            else:
                # Fallback
                text_prompt = "Professional product photo"
            
            logger.info(f"Using text prompt: {text_prompt[:100]}...")
            
            # Call Bria API to generate image
            api_result = self.api_manager.json_to_image(
                structured_prompt=text_prompt,  # Will be treated as text prompt
                seed=seed,
                steps_num=num_inference_steps,
                guidance_scale=guidance_scale,
                aspect_ratio="1:1",
                sync=True
            )
            
            # Extract image URL from response
            if "result" in api_result and "image_url" in api_result["result"]:
                image_url = api_result["result"]["image_url"]
            else:
                image_url = api_result.get("image_url")
            
            if not image_url:
                raise RuntimeError("No image URL in API response")
            
            logger.info(f"Image generated, downloading from URL")
            
            # Download the image
            image = self.api_manager.download_image(image_url)
            
            logger.info("✓ Image generation complete")
            return image
            
        except Exception as e:
            logger.error(f"Cloud API image generation failed: {e}")
            raise
    
    def _convert_to_text_prompt(self, region_json: Dict[str, Any]) -> str:
        """
        Convert Master/Region JSON to a descriptive text prompt.
        
        Args:
            region_json: Full Master or Region JSON
        
        Returns:
            Descriptive text prompt for image generation
        """
        locked = region_json.get("locked_parameters", {})
        variable = region_json.get("variable_parameters", {})
        
        # Build descriptive prompt
        parts = []
        
        # Start with product description from objects
        if "objects" in locked and locked["objects"]:
            first_object = locked["objects"][0]
            if "description" in first_object:
                parts.append(first_object["description"])
        
        # Add background
        if "background_setting" in variable:
            parts.append(f"Background: {variable['background_setting']}")
        
        # Add lighting
        if "lighting" in variable:
            lighting = variable["lighting"]
            if "conditions" in lighting:
                parts.append(f"Lighting: {lighting['conditions']}")
        
        # Add mood/atmosphere
        if "aesthetics" in variable:
            aesthetics = variable["aesthetics"]
            if "mood_atmosphere" in aesthetics:
                parts.append(f"Mood: {aesthetics['mood_atmosphere']}")
        
        # Join all parts
        prompt = ". ".join(parts)
        
        # Add professional photography keywords
        prompt += ". Professional product photography, high quality, detailed"
        
        return prompt
    
    def _convert_to_structured_prompt(self, region_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Master/Region JSON to structured_prompt format.
        
        Args:
            region_json: Full Master or Region JSON
        
        Returns:
            Structured prompt dictionary compatible with FIBO API
        """
        # Merge locked and variable parameters
        locked = region_json.get("locked_parameters", {})
        variable = region_json.get("variable_parameters", {})
        
        # Create structured prompt by merging - use the exact structure from VLM output
        structured_prompt = {
            "short_description": "Professional product photo with localized environment"
        }
        
        # Add photographic characteristics from locked
        if "photographic_characteristics" in locked:
            structured_prompt["photographic_characteristics"] = locked["photographic_characteristics"]
        
        # Add objects from locked
        if "objects" in locked:
            structured_prompt["objects"] = locked["objects"]
        
        # Add variable parameters
        if "background_setting" in variable:
            structured_prompt["background_setting"] = variable["background_setting"]
        
        if "lighting" in variable:
            structured_prompt["lighting"] = variable["lighting"]
        
        # Merge aesthetics
        aesthetics = {}
        if "composition" in locked:
            aesthetics["composition"] = locked["composition"]
        if "aesthetics" in variable:
            aesthetics.update(variable["aesthetics"])
        if aesthetics:
            structured_prompt["aesthetics"] = aesthetics
        
        # Add style_medium
        structured_prompt["style_medium"] = "photograph"
        
        logger.debug(f"Converted to structured_prompt with keys: {list(structured_prompt.keys())}")
        
        return structured_prompt
    
    def create_master_json_from_image(
        self,
        image_path: Union[str, Path],
        output_path: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """
        Create Master JSON from product image and optionally save to file.
        
        This is the main entry point for Task 5: Product Image to Master JSON.
        
        Args:
            image_path: Path to product image (e.g., 'images/wristwatch.png')
            output_path: Optional path to save Master JSON file
        
        Returns:
            Master JSON dictionary
        """
        logger.info(f"Creating Master JSON from image: {image_path}")
        
        # Convert image to Master JSON
        master_json = self.image_to_json(image_path)
        
        # Save to file if requested
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(master_json, f, indent=2)
            
            logger.info(f"✓ Master JSON saved to: {output_path}")
        
        return master_json
    
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
            "torch_available": TORCH_AVAILABLE,
            "cuda_available": torch.cuda.is_available() if TORCH_AVAILABLE else False,
            "api_manager_ready": self.api_manager is not None,
            "sanitizer_ready": self.sanitizer is not None
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
