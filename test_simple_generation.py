"""
Simple test for image generation with text prompt.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from pipeline_manager import FiboPipelineManager


def test_simple_generation():
    """Test simple text-to-image generation."""
    print("Testing simple text-to-image generation...")
    
    # Initialize Pipeline Manager
    manager = FiboPipelineManager(use_local=False)
    
    # Simple text prompt
    simple_prompt = "A professional product photo of a luxury wristwatch on a dark wood surface"
    
    print(f"\nGenerating image from prompt: {simple_prompt}")
    print("(This may take 30-60 seconds...)")
    
    try:
        # Use the API manager directly for simplicity
        result = manager.api_manager.json_to_image(
            structured_prompt=simple_prompt,  # This will be treated as a text prompt
            seed=42,
            steps_num=30,
            guidance_scale=5,
            aspect_ratio="1:1",
            sync=True
        )
        
        print("\n✓ API call successful!")
        print(f"Result keys: {list(result.keys())}")
        
        if "result" in result:
            print(f"Image URL: {result['result'].get('image_url', 'N/A')}")
            
            # Download the image
            image_url = result['result']['image_url']
            image = manager.api_manager.download_image(image_url)
            
            # Save it
            output_dir = Path("output/generated_images")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "simple_test.png"
            image.save(output_file)
            
            print(f"✓ Image saved to: {output_file}")
            print(f"  Size: {image.size}")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_simple_generation()
    sys.exit(0 if success else 1)
