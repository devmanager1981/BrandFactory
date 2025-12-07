"""
Test script for Core JSON-to-Image Generation.
Tests Task 8: Core FIBO JSON-to-Image Generation
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline_manager import FiboPipelineManager


def test_image_generation():
    """Test core JSON-to-Image generation."""
    print("=" * 80)
    print("Testing Core JSON-to-Image Generation (Task 8)")
    print("=" * 80)
    
    # Load a region JSON from previous task
    print("\n1. Loading region JSON...")
    region_file = Path("output/regions/region_tokyo_subway.json")
    
    if not region_file.exists():
        print(f"❌ Region JSON not found: {region_file}")
        print("   Please run test_localization_agent.py first")
        return False
    
    with open(region_file, 'r') as f:
        region_json = json.load(f)
    
    print(f"✓ Loaded region JSON: {region_json['metadata']['region_id']}")
    
    # Initialize Pipeline Manager
    print("\n2. Initializing FIBO Pipeline Manager...")
    manager = FiboPipelineManager(use_local=False)
    print("✓ Pipeline Manager initialized")
    
    # Generate image
    print("\n3. Generating image from region JSON...")
    print("   (This may take 30-60 seconds...)")
    
    try:
        image = manager.generate_image(
            json_params=region_json,
            seed=42,
            num_inference_steps=30,  # Reduced for faster testing
            guidance_scale=5
        )
        
        print("✓ Image generated successfully")
        print(f"  - Image size: {image.size}")
        print(f"  - Image mode: {image.mode}")
        
        # Save the image
        output_dir = Path("output/generated_images")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{region_json['metadata']['region_id']}_test.png"
        image.save(output_file)
        
        print(f"✓ Image saved to: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Image generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test with a simple structured prompt
    print("\n4. Testing with simple structured prompt...")
    
    simple_prompt = {
        "short_description": "A professional product photo of a wristwatch",
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
        "background_setting": "neutral studio background"
    }
    
    try:
        image2 = manager.generate_image(
            json_params=simple_prompt,
            seed=123,
            num_inference_steps=30,
            guidance_scale=5
        )
        
        print("✓ Image generated from simple prompt")
        print(f"  - Image size: {image2.size}")
        
        output_file2 = output_dir / "simple_prompt_test.png"
        image2.save(output_file2)
        
        print(f"✓ Image saved to: {output_file2}")
        
    except Exception as e:
        print(f"\n❌ Simple prompt generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)
    print("✅ All Image Generation tests passed!")
    print("=" * 80)
    print("\nGenerated images saved to: output/generated_images/")
    return True


if __name__ == "__main__":
    success = test_image_generation()
    sys.exit(0 if success else 1)
