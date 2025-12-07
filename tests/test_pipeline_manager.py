"""
Unit tests for FIBO Pipeline Manager
"""

import pytest
from pathlib import Path
from src.pipeline_manager import FiboPipelineManager, create_pipeline_manager


class TestPipelineManager:
    """Test suite for FiboPipelineManager"""
    
    def test_initialization_cpu_only(self):
        """Test pipeline manager initializes with CPU fallback"""
        manager = FiboPipelineManager(use_local=False)
        
        assert manager is not None
        assert manager.use_cloud_api == True
        assert manager.device in ['cuda', 'cpu']
    
    def test_device_detection(self):
        """Test device detection logic"""
        manager = FiboPipelineManager(use_local=False)
        device = manager._detect_device()
        
        assert device in ['cuda', 'cpu']
    
    def test_get_status(self):
        """Test status reporting"""
        manager = FiboPipelineManager(use_local=False)
        status = manager.get_status()
        
        assert 'device' in status
        assert 'vlm_pipeline_loaded' in status
        assert 'fibo_pipeline_loaded' in status
        assert 'using_cloud_api' in status
        assert 'cuda_available' in status
        
        assert isinstance(status['vlm_pipeline_loaded'], bool)
        assert isinstance(status['fibo_pipeline_loaded'], bool)
    
    def test_create_pipeline_manager_convenience(self):
        """Test convenience function"""
        manager = create_pipeline_manager(use_local=False)
        
        assert isinstance(manager, FiboPipelineManager)
        assert manager.use_cloud_api == True
    
    def test_image_to_json_placeholder(self):
        """Test image-to-JSON with placeholder implementation"""
        manager = FiboPipelineManager(use_local=False)
        
        # Use existing test image
        image_path = Path("images/wristwatch.png")
        if image_path.exists():
            result = manager.image_to_json(image_path)
            
            assert isinstance(result, dict)
            assert 'version' in result
            assert 'locked_parameters' in result
            assert 'variable_parameters' in result
            
            # Check locked parameters structure
            locked = result['locked_parameters']
            assert 'camera_angle' in locked
            assert 'focal_length' in locked
            assert 'aspect_ratio' in locked
            assert 'product_geometry' in locked
    
    def test_json_structure_validity(self):
        """Test that generated JSON has correct structure"""
        manager = FiboPipelineManager(use_local=False)
        image_path = Path("images/wristwatch.png")
        
        if image_path.exists():
            result = manager.image_to_json(image_path)
            
            # Validate product_geometry structure
            geometry = result['locked_parameters']['product_geometry']
            assert 'position' in geometry
            assert 'scale' in geometry
            assert 'rotation' in geometry
            
            assert isinstance(geometry['position'], list)
            assert len(geometry['position']) == 2
            assert isinstance(geometry['scale'], (int, float))
            assert isinstance(geometry['rotation'], (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
