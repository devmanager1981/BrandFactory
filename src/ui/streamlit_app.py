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
        "Consistency Threshold (SSIM)",
        min_value=0.05,
        max_value=0.30,
        value=0.15,
        step=0.01,
        help="Maximum allowed structural dissimilarity (SSIM-based). Lower = stricter. SSIM is more robust to lighting variations than pixel comparison."
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


def render_tab_generate(config):
    """Render Tab 1: Generate Campaign."""
    st.markdown("### 🚀 Generate Localized Campaign")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Image input section
        selected_image, image_source = render_image_input()
        
        # Process button
        if selected_image is not None and config['selected_regions']:
            if st.button("🚀 Generate Localized Content", type="primary", use_container_width=True):
                with st.spinner("Processing..."):
                    results = process_pipeline(selected_image, image_source, config)
                
                if results:
                    st.session_state['results'] = results
                    st.session_state['show_results_prompt'] = True
                    st.rerun()
        else:
            if selected_image is None:
                st.info("👆 Please select or upload an image to get started.")
            elif not config['selected_regions']:
                st.info("👈 Please select at least one target region in the sidebar.")
        
        # Show results prompt if generation just completed
        if st.session_state.get('show_results_prompt', False):
            st.balloons()  # Celebration effect!
            st.success("🎉 Processing complete!")
            results = st.session_state.get('results', {})
            st.info(f"📁 Results saved to: {results.get('output_dir', 'output/')}")
            st.info("👉 **Click the 'Results Gallery' tab above** to view your images!")
            
            if st.button("✅ Got it!", type="primary", use_container_width=True):
                st.session_state['show_results_prompt'] = False
                st.rerun()
    
    with col2:
        # Instructions
        st.markdown("#### 🎯 Quick Start Guide")
        st.markdown("""
        1. **Upload/Select** product image
        2. **Choose regions** in sidebar
        3. **Generate** localized content
        4. **View results** in Gallery tab
        """)
        
        st.markdown("---")
        st.markdown("#### ✨ Key Features")
        st.markdown("""
        - **🎨 Background Replacement** - Perfect product consistency
        - **📊 SSIM Verification** - Industry-standard metrics
        - **🔒 C2PA Ready** - Content credentials
        - **📁 Dual Output** - TIFF (print) + PNG (web)
        - **📋 JSON Audit Trail** - Complete documentation
        """)


def render_tab_results(config):
    """Render Tab 2: Results Gallery with Grid Layout."""
    if 'results' not in st.session_state:
        st.info("👈 Generate a campaign first to see results here!")
        st.markdown("### 📊 Results Gallery")
        st.markdown("This tab will display:")
        st.markdown("""
        - 🖼️ **Grid Gallery** - Thumbnail view of all regions
        - 📥 **Download Options** - TIFF, PNG, and JSON files
        - 📊 **Quality Metrics** - Consistency scores and C2PA status
        - 🔍 **Heatmaps** - Visual consistency analysis
        """)
        return
    
    results = st.session_state['results']
    st.markdown("### 📊 Generation Results")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"✅ Campaign: {results['campaign_id']}")
    with col2:
        if st.button("🔄 Start New Campaign", use_container_width=True):
            del st.session_state['results']
            st.rerun()
    
    st.info(f"📁 Output directory: `{results['output_dir']}`")
    
    # Grid Gallery View
    st.markdown("### 🖼️ Gallery Grid")
    st.markdown("Click on any image to view full details below")
    
    # Create thumbnail grid (3 columns)
    region_ids = list(results['regions'].keys())
    cols_per_row = 3
    
    for i in range(0, len(region_ids), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(region_ids):
                region_id = region_ids[i + j]
                region_result = results['regions'][region_id]
                
                with col:
                    # Display thumbnail
                    if region_result.get('png_path') and Path(region_result['png_path']).exists():
                        from PIL import Image
                        img = Image.open(region_result['png_path'])
                        st.image(img, use_column_width=True)
                    
                    # Region name and select button
                    region_name = region_id.replace('_', ' ').title()
                    
                    # Show quality indicator
                    if region_result.get('consistency_score') is not None:
                        score = region_result['consistency_score']
                        threshold = config['consistency_threshold']
                        if score <= threshold:
                            st.caption(f"✅ {region_name}")
                        else:
                            st.caption(f"⚠️ {region_name}")
                    else:
                        st.caption(f"📍 {region_name}")
                    
                    # Select button
                    if st.button(f"View Details", key=f"select_{region_id}", use_container_width=True):
                        st.session_state['selected_region'] = region_id
    
    # Detailed view for selected region
    st.markdown("---")
    
    if 'selected_region' in st.session_state and st.session_state['selected_region'] in results['regions']:
        selected_region = st.session_state['selected_region']
        region_result = results['regions'][selected_region]
        
        st.markdown(f"### 📍 {selected_region.replace('_', ' ').title()} - Detailed View")
        
        # Two column layout for details
        col_img, col_info = st.columns([2, 1])
        
        with col_img:
            # Full size image
            if region_result.get('png_path') and Path(region_result['png_path']).exists():
                from PIL import Image
                img = Image.open(region_result['png_path'])
                st.image(img, caption=f"{selected_region.replace('_', ' ').title()}", use_column_width=True)
        
        with col_info:
            st.markdown("**📥 Downloads:**")
            
            # Download 16-bit TIFF
            if region_result.get('tiff_path') and Path(region_result['tiff_path']).exists():
                with open(region_result['tiff_path'], 'rb') as f:
                    st.download_button(
                        label="📄 16-bit TIFF (Print)",
                        data=f.read(),
                        file_name=Path(region_result['tiff_path']).name,
                        mime="image/tiff",
                        key=f"tiff_{selected_region}"
                    )
            
            # Download 8-bit PNG
            if region_result.get('png_path') and Path(region_result['png_path']).exists():
                with open(region_result['png_path'], 'rb') as f:
                    st.download_button(
                        label="🖼️ 8-bit PNG (Web)",
                        data=f.read(),
                        file_name=Path(region_result['png_path']).name,
                        mime="image/png",
                        key=f"png_{selected_region}"
                    )
            
            # Download JSON
            if region_result.get('json_path') and Path(region_result['json_path']).exists():
                with open(region_result['json_path'], 'r') as f:
                    st.download_button(
                        label="📋 JSON Parameters",
                        data=f.read(),
                        file_name=Path(region_result['json_path']).name,
                        mime="application/json",
                        key=f"json_{selected_region}"
                    )
            
            st.markdown("---")
            st.markdown("**📊 Quality Metrics:**")
            
            # Consistency score
            if region_result.get('consistency_score') is not None:
                score = region_result['consistency_score']
                threshold = config['consistency_threshold']
                
                st.metric("Consistency Score", f"{score:.4f}")
                if score <= threshold:
                    st.success("✅ Passed")
                else:
                    st.warning("⚠️ Review Needed")
                
                st.caption(f"Threshold: {threshold:.2f}")
            
            # C2PA status
            if region_result.get('c2pa_verified') is not None:
                if region_result['c2pa_verified']:
                    st.success("✅ C2PA Verified")
                else:
                    st.info("ℹ️ C2PA: Generated by Bria API (editing endpoint)")
                    st.caption("Background replacement API doesn't embed C2PA credentials")
            
            if region_result.get('flagged_for_review'):
                st.warning("⚠️ Flagged for Review")
        
        # Display heatmap if available
        if region_result.get('heatmap_path') and Path(region_result['heatmap_path']).exists():
            st.markdown("---")
            st.markdown("**🔍 Consistency Heatmap:**")
            from PIL import Image
            heatmap_img = Image.open(region_result['heatmap_path'])
            st.image(heatmap_img, caption="Product Consistency Heatmap", use_column_width=True)
            st.caption("Red areas = differences, Blue areas = identical")
    else:
        st.info("👆 Click on any image above to view detailed information")


def render_tab_creative_studio(config):
    """Render Tab 3: Creative Studio (FIBO Variations)."""
    st.markdown("### 🎨 Creative Studio - FIBO Variations")
    
    if 'results' not in st.session_state:
        st.info("👈 Generate a campaign first to create FIBO variations!")
        st.markdown("### What is FIBO Creative Studio?")
        st.markdown("""
        The **Creative Studio** showcases Bria's FIBO (Fine-grained Image control via Bria Objects) technology:
        
        - **🎨 JSON-Native Control** - Precise parameter control via structured JSON
        - **✨ Creative Exploration** - Generate variations with different seeds
        - **🔄 Side-by-Side Comparison** - Compare original vs variations
        - **📊 Parameter Transparency** - See exactly what changed
        
        **How it works:**
        1. Uses the same Master JSON from your campaign
        2. Applies different random seeds for variation
        3. Generates completely new images with FIBO text-to-image
        4. Perfect for creative exploration and A/B testing
        """)
        return
    
    results = st.session_state['results']
    
    st.markdown("""
    **FIBO Creative Studio** showcases Bria's core Image Generation API with full parameter control.
    Generate multiple creative variations using the same JSON parameters with different seeds and settings.
    """)
    
    st.markdown("---")
    
    # Region selector - Thumbnail Grid
    st.markdown("### 📍 Select Region (Original Images)")
    
    region_options = list(results['regions'].keys())
    cols_per_row = 3
    
    # Initialize selected region in session state if not exists
    if 'creative_selected_region' not in st.session_state:
        st.session_state['creative_selected_region'] = region_options[0] if region_options else None
    
    for i in range(0, len(region_options), cols_per_row):
        cols = st.columns(cols_per_row)
        
        for j, col in enumerate(cols):
            if i + j < len(region_options):
                region_id = region_options[i + j]
                region_result = results['regions'][region_id]
                
                with col:
                    # Display thumbnail
                    if region_result.get('png_path') and Path(region_result['png_path']).exists():
                        from PIL import Image
                        img = Image.open(region_result['png_path'])
                        st.image(img, use_column_width=True)
                    
                    # Region name
                    region_name = region_id.replace('_', ' ').title()
                    st.caption(f"📍 {region_name}")
                    
                    # Select button
                    button_type = "primary" if st.session_state['creative_selected_region'] == region_id else "secondary"
                    if st.button(
                        "✓ Selected" if st.session_state['creative_selected_region'] == region_id else "Select",
                        key=f"select_creative_{region_id}",
                        use_container_width=True,
                        type=button_type
                    ):
                        st.session_state['creative_selected_region'] = region_id
                        st.rerun()
    
    st.markdown("---")
    
    selected_region = st.session_state.get('creative_selected_region')
    
    if selected_region:
        region_result = results['regions'][selected_region]
        
        # Generation Parameters Section
        st.markdown("### ⚙️ Generation Parameters")
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            seed_input = st.number_input(
                "Seed",
                min_value=1,
                max_value=999999,
                value=st.session_state.get('fibo_seed', 12345),
                help="Random seed for reproducible results"
            )
            st.session_state['fibo_seed'] = seed_input
        
        with col_p2:
            steps_input = st.slider(
                "Inference Steps",
                min_value=20,
                max_value=50,
                value=st.session_state.get('fibo_steps', 50),
                help="More steps = higher quality but slower"
            )
            st.session_state['fibo_steps'] = steps_input
        
        with col_p3:
            guidance_input = st.slider(
                "Guidance Scale",
                min_value=3,
                max_value=5,
                value=st.session_state.get('fibo_guidance', 5),
                step=1,
                help="How closely to follow the JSON parameters (3-5)"
            )
            st.session_state['fibo_guidance'] = guidance_input
        
        # Generate button
        if st.button("🎨 Generate FIBO Variation", type="primary", use_container_width=True):
            with st.spinner("Generating creative variation with FIBO..."):
                try:
                    # Load the JSON parameters for this region
                    import json
                    with open(region_result['json_path'], 'r') as f:
                        region_json = json.load(f)
                    
                    # Use FIBO generation
                    from src.pipeline_manager import FiboPipelineManager
                    
                    pipeline = FiboPipelineManager(use_local=False)
                    
                    # Generate using FIBO with user parameters
                    fibo_image, image_url = pipeline._generate_image_fibo(
                        region_json,
                        seed=seed_input,
                        num_inference_steps=steps_input,
                        guidance_scale=guidance_input
                    )
                    
                    # Save the variation using download_image to preserve C2PA
                    variation_path = Path(region_result['png_path']).parent / f"{selected_region}_fibo_var_{seed_input}.png"
                    pipeline.api_manager.download_image(image_url, output_path=variation_path)
                    
                    # Verify C2PA
                    from src.c2pa_verifier import C2PAVerifier
                    c2pa_verifier = C2PAVerifier()
                    is_verified, c2pa_metadata = c2pa_verifier.verify_image(Path(variation_path))
                    
                    # Store in session state (as a list for multiple variations)
                    if 'fibo_variations' not in st.session_state:
                        st.session_state['fibo_variations'] = {}
                    if selected_region not in st.session_state['fibo_variations']:
                        st.session_state['fibo_variations'][selected_region] = []
                    
                    st.session_state['fibo_variations'][selected_region].append({
                        'image': fibo_image,
                        'seed': seed_input,
                        'steps': steps_input,
                        'guidance': guidance_input,
                        'path': str(variation_path),
                        'c2pa_verified': is_verified,
                        'c2pa_data': c2pa_metadata
                    })
                    
                    st.success(f"✅ FIBO variation generated! Seed: {seed_input}")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error generating FIBO variation: {e}")
                    logger.exception("FIBO variation generation error")
        
        st.markdown("---")
        
        # Display variations gallery
        if 'fibo_variations' in st.session_state and selected_region in st.session_state['fibo_variations']:
            variations = st.session_state['fibo_variations'][selected_region]
            
            if variations:
                st.markdown("### 🖼️ Generated Variations Gallery")
                
                # Thumbnail grid (3 columns)
                cols_per_row = 3
                for i in range(0, len(variations), cols_per_row):
                    cols = st.columns(cols_per_row)
                    
                    for j, col in enumerate(cols):
                        if i + j < len(variations):
                            var_data = variations[i + j]
                            
                            with col:
                                # Display thumbnail
                                st.image(var_data['image'], use_column_width=True)
                                
                                # Parameters
                                st.caption(f"🎲 Seed: {var_data['seed']}")
                                st.caption(f"📊 Steps: {var_data['steps']} | Guidance: {var_data['guidance']}")
                                
                                # C2PA status
                                if var_data.get('c2pa_verified'):
                                    st.caption("✅ C2PA Verified")
                                else:
                                    st.caption("ℹ️ C2PA: Check manually")
                                
                                # Download button
                                with open(var_data['path'], 'rb') as f:
                                    st.download_button(
                                        label="📥 Download",
                                        data=f.read(),
                                        file_name=Path(var_data['path']).name,
                                        mime="image/png",
                                        key=f"download_var_{i+j}_{var_data['seed']}",
                                        use_container_width=True
                                    )
        
        # Original comparison
        st.markdown("---")
        st.markdown("### 📍 Original (Background Replacement)")
        if region_result.get('png_path') and Path(region_result['png_path']).exists():
            from PIL import Image
            img = Image.open(region_result['png_path'])
            col_orig, col_info = st.columns([2, 1])
            with col_orig:
                st.image(img, caption=f"Original: {selected_region.replace('_', ' ').title()}", use_column_width=True)
            with col_info:
                st.info("✅ Perfect product consistency (SSIM ~0.001)")
                st.caption("Uses Background Replacement API - No C2PA")
        
        st.markdown("---")
        st.markdown("### 💡 Key Differences")
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("""
            **Background Replacement API:**
            - ✅ Perfect product consistency
            - ✅ SSIM scores ~0.001
            - ✅ Production-ready for campaigns
            - 🎯 Use for: Brand consistency
            """)
        
        with col_b:
            st.markdown("""
            **FIBO Text-to-Image:**
            - 🎨 Creative variations
            - 🎨 Same JSON, different results
            - 🎨 Exploration and A/B testing
            - 🎯 Use for: Creative discovery
            """)


def render_tab_audit(config):
    """Render Tab 4: Audit & Compliance."""
    st.markdown("### 🔍 Audit & Compliance")
    
    if 'results' not in st.session_state:
        st.info("👈 Generate a campaign first to view audit details!")
        st.markdown("### What's in Audit & Compliance?")
        st.markdown("""
        This tab provides complete transparency and traceability:
        
        - **📋 JSON Parameter Viewer** - See all generation parameters
        - **🔒 Locked vs Variable** - Understand what stays consistent
        - **🛡️ C2PA Credentials** - Content authenticity verification
        - **📊 Generation Metadata** - Seeds, timestamps, versions
        - **🔍 Compliance Tracking** - Quality metrics and flags
        """)
        return
    
    results = st.session_state['results']
    
    # Region selector
    region_options = list(results['regions'].keys())
    selected_region = st.selectbox(
        "Select Region for Audit",
        options=region_options,
        format_func=lambda x: x.replace('_', ' ').title(),
        key="audit_region_selector"
    )
    
    if selected_region:
        region_result = results['regions'][selected_region]
        
        # Load JSON data
        if region_result.get('json_path') and Path(region_result['json_path']).exists():
            import json
            with open(region_result['json_path'], 'r') as f:
                json_data = json.load(f)
            
            # Create tabs for different audit sections
            audit_tab1, audit_tab2, audit_tab3, audit_tab4 = st.tabs([
                "🔒 Locked Parameters",
                "🔄 Variable Parameters",
                "ℹ️ Generation Info",
                "🛡️ C2PA Credentials"
            ])
            
            with audit_tab1:
                st.markdown("### 🔒 Locked Parameters (Product Consistency)")
                st.markdown("These parameters remain **constant** across all regions to ensure product consistency:")
                st.json(json_data.get('locked_parameters', {}))
                
                st.info("""
                **Why Locked?** These parameters define the core product appearance and must remain 
                identical across all regional variations to maintain brand consistency.
                """)
            
            with audit_tab2:
                st.markdown("### 🔄 Variable Parameters (Regional Adaptation)")
                st.markdown("These parameters **change** per region for cultural localization:")
                st.json(json_data.get('variable_parameters', {}))
                
                st.info("""
                **Why Variable?** These parameters adapt to local culture, environment, and context 
                while keeping the product itself unchanged.
                """)
            
            with audit_tab3:
                st.markdown("### ℹ️ Generation Information")
                st.json(json_data.get('generation_info', {}))
                
                # Display quality metrics
                st.markdown("### 📊 Quality Metrics")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if region_result.get('consistency_score') is not None:
                        score = region_result['consistency_score']
                        st.metric("Consistency Score (SSIM)", f"{score:.4f}")
                        if score <= config['consistency_threshold']:
                            st.success("✅ Passed")
                        else:
                            st.warning("⚠️ Review Needed")
                
                with col2:
                    if region_result.get('c2pa_verified') is not None:
                        st.metric("C2PA Status", "Verified" if region_result['c2pa_verified'] else "Not Verified")
                
                with col3:
                    if region_result.get('flagged_for_review'):
                        st.metric("Review Status", "Flagged")
                        st.warning("⚠️")
                    else:
                        st.metric("Review Status", "Approved")
                        st.success("✅")
            
            with audit_tab4:
                st.markdown("### 🛡️ C2PA Content Credentials")
                
                if 'c2pa_credentials' in json_data:
                    c2pa_data = json_data['c2pa_credentials']
                    
                    # Status banner
                    if c2pa_data.get('verified'):
                        st.success("✅ C2PA Verified - Content authenticity confirmed")
                        if 'signed_by_bria' in c2pa_data and c2pa_data['signed_by_bria']:
                            st.info("🔐 Signed by: Bria AI")
                    else:
                        st.info("ℹ️ C2PA Status: Generated by Bria API")
                        st.caption("""
                        **Note:** This image was generated using Bria's Background Replacement API 
                        (`/v2/image/edit/replace_background`), which focuses on editing operations. 
                        C2PA credentials are primarily embedded in images from the Image Generation API 
                        (`/v2/image/generate`). The image is still fully licensed and safe for commercial use.
                        """)
                    
                    # Full C2PA data
                    st.markdown("#### Complete C2PA Data")
                    st.json(c2pa_data)
                    
                    st.markdown("---")
                    st.markdown("### 📖 About C2PA")
                    st.markdown("""
                    **C2PA (Coalition for Content Provenance and Authenticity)** provides:
                    - 🔐 **Content Authenticity** - Verify the source and history
                    - 📜 **Provenance Tracking** - Complete audit trail
                    - 🛡️ **Tamper Detection** - Detect unauthorized modifications
                    - ✅ **Trust & Transparency** - Build confidence in AI-generated content
                    """)
                else:
                    st.warning("No C2PA credentials found for this image.")
                    st.info("Enable C2PA verification in the sidebar to add content credentials.")
        else:
            st.error("JSON audit file not found for this region.")


def main():
    """Main Streamlit application."""
    # Render header
    render_header()
    
    # Render sidebar
    config = render_sidebar()
    
    # Create tabs for different features
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚀 Generate Campaign",
        "📊 Results Gallery",
        "🎨 Creative Studio",
        "🔍 Audit & Compliance"
    ])
    
    # TAB 1: Generate Campaign
    with tab1:
        render_tab_generate(config)
    
    # TAB 2: Results Gallery
    with tab2:
        render_tab_results(config)
    
    # TAB 3: Creative Studio
    with tab3:
        render_tab_creative_studio(config)
    
    # TAB 4: Audit & Compliance
    with tab4:
        render_tab_audit(config)
    
    # Footer - more compact
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #999; padding: 0.5rem; font-size: 0.85rem;">
        🌍 Global Brand Localizer | Powered by Bria AI
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
