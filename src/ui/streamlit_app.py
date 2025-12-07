#!/usr/bin/env python3
"""
Professional Streamlit UI for Global Brand Localizer

Features:
- Professional design with custom CSS
- Image upload capability + preexisting image selection
- Real-time progress tracking
- Results visualization
- Download capabilities
"""

import streamlit as st
import logging
from pathlib import Path
from PIL import Image
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Global Brand Localizer",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom header - more compact */
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.3rem 0 0 0;
        font-size: 0.95rem;
        opacity: 0.9;
    }
    
    /* Card styling - more compact */
    .custom-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e1e5e9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .custom-card h3 {
        margin-top: 0;
        font-size: 1.3rem;
        color: #1f77b4;
    }
    
    .custom-card h4 {
        margin-top: 1rem;
        font-size: 1.1rem;
        color: #2c3e50;
    }
    
    .custom-card ul, .custom-card ol {
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }
    
    .custom-card li {
        margin: 0.3rem 0;
        font-size: 0.95rem;
    }
    
    /* Status indicators */
    .status-success {
        background: #d4edda;
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border-left: 4px solid #2ca02c;
    }
    
    .status-warning {
        background: #fff3cd;
        color: #856404;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        border-left: 4px solid #ff7f0e;
    }
</style>
""", unsafe_allow_html=True)


def render_header():
    """Render the main header."""
    st.markdown("""
    <div class="main-header">
        <h1>🌍 Global Brand Localizer</h1>
        <p>AI-Powered Cultural Localization for Global Markets</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with configuration options."""
    st.sidebar.markdown("### ⚙️ Configuration")
    
    # Region selection
    try:
        from config.region_configs import REGION_CONFIGS
        available_regions = list(REGION_CONFIGS.keys())
    except:
        available_regions = ["tokyo_subway", "berlin_billboard", "nyc_times_square"]
    
    selected_regions = st.sidebar.multiselect(
        "Select Target Regions",
        options=available_regions,
        default=available_regions[:3] if len(available_regions) >= 3 else available_regions,
        help="Choose which regions to generate localized content for"
    )
    
    # Advanced settings
    st.sidebar.markdown("### 🔧 Advanced Settings")
    
    consistency_threshold = st.sidebar.slider(
        "Consistency Threshold",
        min_value=0.01,
        max_value=0.20,
        value=0.05,
        step=0.01,
        help="Maximum allowed pixel difference in product region (lower = stricter). Uses product segmentation to compare only the product, ignoring backgrounds."
    )
    
    enable_c2pa = st.sidebar.checkbox(
        "Enable C2PA Verification",
        value=True,
        help="Verify content authenticity credentials"
    )
    
    seed = st.sidebar.number_input(
        "Random Seed",
        min_value=1,
        max_value=999999,
        value=12345,
        help="For reproducible results"
    )
    
    return {
        "selected_regions": selected_regions,
        "consistency_threshold": consistency_threshold,
        "enable_c2pa": enable_c2pa,
        "seed": seed
    }


def render_image_input():
    """Render image input section with upload and preexisting options."""
    st.markdown("### 📸 Product Image Input")
    
    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["📤 Upload Image", "🖼️ Use Sample Image"])
    
    selected_image = None
    image_source = None
    
    with tab1:
        st.markdown("Upload your product image for localization:")
        uploaded_file = st.file_uploader(
            "Choose an image file",
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="Supported formats: PNG, JPG, JPEG, WEBP"
        )
        
        if uploaded_file is not None:
            try:
                selected_image = Image.open(uploaded_file)
                image_source = "uploaded"
                
                # Display uploaded image
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.image(selected_image, caption="Uploaded Image", use_column_width=True)
                
                # Image info
                st.info(f"📊 Image Info: {selected_image.size[0]}×{selected_image.size[1]} pixels, {selected_image.mode} mode")
                
            except Exception as e:
                st.error(f"Error loading image: {e}")
    
    with tab2:
        st.markdown("Select from sample product images:")
        
        # Check for sample images
        sample_images = {
            "Luxury Wristwatch": "images/wristwatch.png",
            "Premium Headphones": "images/headphones.png"
        }
        
        available_samples = {}
        for name, path in sample_images.items():
            if Path(path).exists():
                available_samples[name] = path
        
        if available_samples:
            selected_sample = st.selectbox(
                "Choose a sample image",
                options=["None"] + list(available_samples.keys())
            )
            
            if selected_sample != "None":
                try:
                    sample_path = available_samples[selected_sample]
                    selected_image = Image.open(sample_path)
                    image_source = sample_path
                    
                    # Display sample image
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.image(selected_image, caption=f"Sample: {selected_sample}", use_column_width=True)
                    
                    st.info(f"📊 Image Info: {selected_image.size[0]}×{selected_image.size[1]} pixels, {selected_image.mode} mode")
                    
                except Exception as e:
                    st.error(f"Error loading sample image: {e}")
        else:
            st.warning("No sample images found. Please upload your own image.")
    
    return selected_image, image_source


def process_pipeline(selected_image, image_source, config):
    """
    Process the uploaded/selected image through the complete pipeline.
    
    Args:
        selected_image: PIL Image object
        image_source: Source path or "uploaded"
        config: Configuration dictionary from sidebar
    
    Returns:
        Dictionary with results or None on error
    """
    import tempfile
    from datetime import datetime
    
    try:
        # Import pipeline components
        from src.pipeline_manager import FiboPipelineManager
        from src.localization_agent import LocalizationAgent
        from src.output_manager import OutputManager
        from config.region_configs import REGION_CONFIGS
        
        # Create unique campaign directory with timestamp
        campaign_id = f"ui_campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_dir = f"output/{campaign_id}"
        
        st.info(f"📁 Campaign ID: {campaign_id}")
        
        # Save uploaded image temporarily if needed
        if image_source == "uploaded":
            temp_dir = Path("output/temp")
            temp_dir.mkdir(parents=True, exist_ok=True)
            temp_image_path = temp_dir / f"uploaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            selected_image.save(temp_image_path)
            image_path = str(temp_image_path)
        else:
            image_path = image_source
        
        # Step 1: Generate Master JSON from image
        st.write("**Step 1/4:** 🔍 Analyzing product image...")
        progress_bar = st.progress(0.25)
        
        pipeline = FiboPipelineManager(use_local=False)  # Use Cloud API
        master_json = pipeline.image_to_json(image_path)
        st.success("✓ Master JSON generated")
        
        # Step 2: Generate Region JSONs
        st.write("**Step 2/4:** 🌍 Creating regional variations...")
        progress_bar.progress(0.50)
        
        agent = LocalizationAgent()
        region_jsons = {}
        
        for region_id in config['selected_regions']:
            region_config = REGION_CONFIGS[region_id]
            region_json = agent.merge_configs(master_json, region_config)
            region_jsons[region_id] = region_json
        
        st.success(f"✓ Created {len(region_jsons)} regional configurations")
        
        # Step 3: Generate Images using FIBO API
        st.write("**Step 3/4:** 🎨 Generating localized images...")
        progress_bar.progress(0.75)
        
        generated_images = {}
        for i, (region_id, region_json) in enumerate(region_jsons.items()):
            try:
                st.write(f"  Generating {region_id}... ({i+1}/{len(region_jsons)})")
                
                # Generate image using FIBO pipeline
                gen_image = pipeline.generate_image(
                    json_params=region_json,
                    seed=config['seed'],
                    num_inference_steps=30,  # Faster generation
                    guidance_scale=5.0
                )
                
                generated_images[region_id] = gen_image
                st.write(f"  ✓ {region_id} complete")
                
            except Exception as e:
                st.warning(f"  ⚠ Failed to generate {region_id}: {e}")
                logger.error(f"Generation failed for {region_id}: {e}")
        
        if not generated_images:
            raise RuntimeError("No images were generated successfully")
        
        st.success(f"✓ Generated {len(generated_images)} images")
        
        # Step 4: Save outputs
        st.write("**Step 4/4:** 💾 Saving outputs...")
        progress_bar.progress(1.0)
        
        output_manager = OutputManager(
            output_dir=output_dir,
            consistency_threshold=config['consistency_threshold'],
            enable_c2pa=config['enable_c2pa']
        )
        
        results = {
            'campaign_id': campaign_id,
            'output_dir': output_dir,
            'regions': {},
            'master_image_path': image_path
        }
        
        for region_id, gen_image in generated_images.items():
            result = output_manager.save_dual_output(
                image=gen_image,
                region_json=region_jsons[region_id],
                region_id=region_id,
                seed=config['seed'],
                master_image=selected_image
            )
            results['regions'][region_id] = result
        
        st.success("✓ All outputs saved successfully!")
        
        return results
        
    except Exception as e:
        st.error(f"❌ Error during processing: {e}")
        logger.exception("Pipeline processing error")
        return None


def main():
    """Main Streamlit application."""
    # Render header
    render_header()
    
    # Render sidebar
    config = render_sidebar()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Image input section
        selected_image, image_source = render_image_input()
        
        # Process button
        if selected_image is not None and config['selected_regions']:
            if st.button("🚀 Generate Localized Content", type="primary"):
                with st.spinner("Processing..."):
                    results = process_pipeline(selected_image, image_source, config)
                
                if results:
                    st.session_state['results'] = results
                    st.success("🎉 Processing complete!")
                    st.info(f"📁 Results saved to: {results['output_dir']}")
                    st.rerun()
        else:
            if selected_image is None:
                st.info("👆 Please select or upload an image to get started.")
            elif not config['selected_regions']:
                st.info("👈 Please select at least one target region in the sidebar.")
    
    with col2:
        # Results or Instructions section
        if 'results' in st.session_state:
            results = st.session_state['results']
            st.markdown("### 📊 Generation Results")
            
            st.success(f"✅ Campaign: {results['campaign_id']}")
            st.info(f"📁 Output directory: `{results['output_dir']}`")
            
            # Display results for each region
            for region_id, region_result in results['regions'].items():
                with st.expander(f"📍 {region_id.replace('_', ' ').title()}", expanded=True):
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        st.markdown("**Files Generated:**")
                        if region_result.get('tiff_saved'):
                            st.write(f"✅ 16-bit TIFF: `{Path(region_result['tiff_path']).name}`")
                        if region_result.get('png_saved'):
                            st.write(f"✅ 8-bit PNG: `{Path(region_result['png_path']).name}`")
                        if region_result.get('json_saved'):
                            st.write(f"✅ JSON: `{Path(region_result['json_path']).name}`")
                    
                    with col_b:
                        st.markdown("**Quality Metrics:**")
                        if region_result.get('consistency_score') is not None:
                            score = region_result['consistency_score']
                            threshold = config['consistency_threshold']
                            
                            if score <= threshold:
                                st.write(f"✅ Product Consistency: {score:.4f}")
                                st.caption("Product-only comparison (backgrounds ignored)")
                            else:
                                st.write(f"⚠️ Product Consistency: {score:.4f}")
                                st.caption(f"Exceeds threshold of {threshold:.2f}")
                            
                            # Add explanation as info box
                            st.info("""
                            **Product-Only Comparison:**  
                            Uses segmentation to compare only the product region.
                            
                            • **< 0.05**: Excellent consistency  
                            • **0.05-0.10**: Good with minor variations  
                            • **> 0.10**: Review needed
                            """)
                        
                        if region_result.get('flagged_for_review'):
                            st.warning("⚠️ Flagged for review")
            
            # Clear results button
            if st.button("🔄 Start New Campaign"):
                del st.session_state['results']
                st.rerun()
        else:
            # Instructions section - more compact and structured
            st.markdown("""
            <div class="custom-card">
                <h3>🎯 Quick Start</h3>
                <ol>
                    <li><strong>Upload/Select</strong> product image</li>
                    <li><strong>Choose regions</strong> in sidebar</li>
                    <li><strong>Generate</strong> localized content</li>
                    <li><strong>Download</strong> results</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="custom-card">
                <h3>✨ Key Features</h3>
                <ul>
                    <li><strong>🎨 Cultural Localization</strong> - AI-powered background adaptation</li>
                    <li><strong>📊 Product Consistency</strong> - Segmentation-based verification</li>
                    <li><strong>🔒 C2PA Authenticity</strong> - Content credentials & provenance</li>
                    <li><strong>📁 Dual Output</strong> - 16-bit TIFF (print) + 8-bit PNG (web)</li>
                    <li><strong>📋 Audit Trail</strong> - Complete JSON documentation</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Footer - more compact
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #999; padding: 0.5rem; font-size: 0.85rem;">
        🌍 Global Brand Localizer | Powered by Bria AI
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
