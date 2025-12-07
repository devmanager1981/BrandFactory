"""
Test script for Batch Processor.
Tests Task 7: Batch Generation & Queue Management
"""

import sys
import json
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from batch_processor import BatchProcessor, JobStatus


def test_batch_processor():
    """Test Batch Processor functionality."""
    print("=" * 80)
    print("Testing Batch Processor (Task 7)")
    print("=" * 80)
    
    # Load region JSONs from previous task
    print("\n1. Loading region JSONs...")
    region_dir = Path("output/regions")
    
    if not region_dir.exists():
        print(f"❌ Region directory not found: {region_dir}")
        print("   Please run test_localization_agent.py first")
        return False
    
    region_files = list(region_dir.glob("region_*.json"))
    if not region_files:
        print(f"❌ No region JSON files found in {region_dir}")
        return False
    
    region_jsons = []
    for file in region_files:
        with open(file, 'r') as f:
            region_jsons.append(json.load(f))
    
    print(f"✓ Loaded {len(region_jsons)} region JSONs")
    
    # Initialize Batch Processor
    print("\n2. Initializing Batch Processor...")
    processor = BatchProcessor(max_concurrent=2)
    print("✓ Batch Processor initialized")
    
    # Define a mock processor function
    def mock_image_generator(region_json: dict) -> dict:
        """Mock image generation function."""
        region_id = region_json.get("metadata", {}).get("region_id", "unknown")
        
        # Simulate processing time
        time.sleep(0.5)
        
        # Simulate occasional failure for testing error isolation
        if "fail" in region_id:
            raise RuntimeError(f"Simulated failure for {region_id}")
        
        return {
            "region_id": region_id,
            "image_url": f"https://example.com/images/{region_id}.png",
            "status": "success"
        }
    
    # Test sequential processing
    print("\n3. Testing sequential batch processing...")
    
    result = processor.process_batch_sequential(
        region_jsons=region_jsons,
        processor_func=mock_image_generator
    )
    
    print(f"✓ Sequential processing complete")
    print(f"  - Total jobs: {result.total_jobs}")
    print(f"  - Completed: {result.completed}")
    print(f"  - Failed: {result.failed}")
    print(f"  - Success rate: {result.success_rate * 100:.1f}%")
    
    if result.completed != len(region_jsons):
        print(f"  ⚠ Warning: Not all jobs completed successfully")
    
    # Test error isolation
    print("\n4. Testing error isolation...")
    
    # Add a region that will fail
    import copy
    failing_region = copy.deepcopy(region_jsons[0])
    failing_region["metadata"]["region_id"] = "fail_test_region"
    
    test_regions = [region_jsons[0], failing_region, region_jsons[1]]
    
    processor2 = BatchProcessor()
    result2 = processor2.process_batch_sequential(
        region_jsons=test_regions,
        processor_func=mock_image_generator
    )
    
    print(f"✓ Error isolation test complete")
    print(f"  - Total jobs: {result2.total_jobs}")
    print(f"  - Completed: {result2.completed}")
    print(f"  - Failed: {result2.failed}")
    
    # Verify that other jobs completed despite one failure
    if result2.completed >= 2 and result2.failed == 1:
        print("✓ Error isolation working correctly")
    else:
        print("❌ Error isolation failed!")
        return False
    
    # Test job status tracking
    print("\n5. Testing job status tracking...")
    
    jobs = processor.get_all_jobs()
    print(f"✓ Retrieved {len(jobs)} jobs")
    
    for job in jobs[:3]:  # Show first 3
        print(f"  - Job: {job.job_id}")
        print(f"    Region: {job.region_id}")
        print(f"    Status: {job.status.value}")
        if job.error:
            print(f"    Error: {job.error}")
    
    # Test summary
    print("\n6. Testing batch summary...")
    summary = processor.get_summary()
    
    print(f"✓ Batch summary:")
    print(f"  - Total: {summary['total']}")
    print(f"  - Completed: {summary['completed']}")
    print(f"  - Failed: {summary['failed']}")
    print(f"  - Success rate: {summary['success_rate'] * 100:.1f}%")
    
    # Test result serialization
    print("\n7. Testing result serialization...")
    result_dict = result.to_dict()
    
    print(f"✓ Result serialized to dictionary")
    print(f"  - Keys: {list(result_dict.keys())}")
    
    # Save result to file
    output_file = Path("output/batch_result.json")
    with open(output_file, 'w') as f:
        json.dump(result_dict, f, indent=2)
    
    print(f"✓ Result saved to: {output_file}")
    
    print("\n" + "=" * 80)
    print("✅ All Batch Processor tests passed!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = test_batch_processor()
    sys.exit(0 if success else 1)
