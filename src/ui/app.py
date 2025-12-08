"""
Streamlit UI for Global Brand Localizer

Professional web interface for campaign management with:
- Base product image selector (wristwatch/headphones)
- Custom image upload capability
- Region selection
- Campaign configuration
- Real-time progress tracking
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image
import json

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
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #374151;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 0.5rem;
    }
    .info-box {
        background-color: #f3f4f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3b82f6;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d1fae5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #10b981;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fef3c7;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f59e0b;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
        background-color: #3b82f6;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        border: none;
        transition: background-color 0.2s;
    }
    .stButton>button:hover {
        background-color: #2563eb;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'master_json' not in st.session_state:
    st.session_state.master_json = None
if 'selected_regions' not in st.session_state:
    st.session_state.selected_regions = []
if 'generation_results' not in st.session_state:
    st.session_state.generation_results = []


def main():
    """Main application."""
    
    # Header
    st.markdown('<div class="main-header">🌍 Global Brand Localizer</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Generate culturally-localized product imagery with guaranteed brand consistency</div>',
        unsafe_allow_html=True
    )
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Campaign ID
        campaign_id = st.text_input(
            "Campaign ID",
            value="campaign_001",
            help="Unique identifier for this campaign"
        )
        
        st.markdown("---")
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            consistency_threshold = st.slider(
                "Consistency Threshold",
                min_value=0.0,
                max_value=0.2,
                value=0.05,
                step=0.01,
                help="Maximum allowed pixel difference (5% default)"
            )
            
            enable_c2pa = st.checkbox(
                "Enable C2PA Verification",
                value=True,
                help="Verify Bria's embedded C2PA credentials"
            )
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["📸 Product Setup", "🌍 Localization", "📊 Results"])
    
    with tab1:
        product_setup_tab(campaign_id)
    
    with tab2:
        localization_tab()
    
    with tab3:
        results_tab()


def product_setup_tab(campaign_id: str):
    """Product image selection and upload tab."""
    
    st.markdown('<div class="section-header">Product Image Selection</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### Select Base Product")
        
        # Radio buttons for pre-configured images
        image_option = st.radio(
            "Choose a base product image:",
            options=["Luxury Wristwatch", "Premium Headphones", "Upload Custom Image"],
            index=0,
            help="Select from pre-configured products or upload your own"
        )
        
        # Map selection to file path
        image_path = None
        uploaded_file = None
        
        if image_option == "Luxury Wristwatch":
            image_path = Path("images/wristwatch.png")
        elif image_option == "Premium Headphones":
            image_path = Path("images/headphones.png")
        else:
            # Custom upload
            uploaded_file = st.file_uploader(
                "Upload Product Image",
                type=["png", "jpg", "jpeg"],
                help="Upload a high-quality product image (PNG or JPG)"
            )
    
    with col2:
        st.markdown("#### Preview")
        
        # Display preview
        preview_image = None
        
        if uploaded_file is not None:
            preview_image = Image.open(uploaded_file)
            st.image(preview_image, caption="Custom Upload", use_container_width=True)
        elif image_path and image_path.exists():
            preview_image = Image.open(image_path)
            st.image(preview_image, caption=image_option, use_container_width=True)
        else:
            st.info("👆 Select or upload an image to see preview")
    
    # Generate Master JSON button
    st.markdown("---")
    
    if st.button("🚀 Generate Master JSON", type="primary"):
        if preview_image:
            with st.spinner("Analyzing product image..."):
                # Placeholder for actual VLM Bridge call
                st.markdown('<div class="success-box">✓ Master JSON generated successfully!</div>', unsafe_allow_html=True)
                
                # Store in session state
                st.session_state.master_json = {
                    "version": "1.0",
                    "metadata": {
                        "campaign_id": campaign_id,
                        "source_image": str(image_path) if image_path else "custom_upload.png"
                    },
                    "locked_parameters": {
                        "camera_angle": "eye_level",
                        "focal_length": "50mm"
                    },
                    "variable_parameters": {
                        "background": "neutral",
                        "lighting_type": "soft_natural"
                    }
                }
                
                st.rerun()
        else:
            st.error("Please select or upload an image first")
    
    # Display Master JSON if generated
    if st.session_state.master_json:
        st.markdown('<div class="section-header">Master JSON</div>', unsafe_allow_html=True)
        
        with st.expander("📄 View Master JSON", expanded=False):
            st.json(st.session_state.master_json)


def localization_tab():
    """Region selection and campaign configuration tab."""
    
    if not st.session_state.master_json:
        st.markdown('<div class="info-box">ℹ️ Please generate a Master JSON in the Product Setup tab first</div>', unsafe_allow_html=True)
        return
    
    st.markdown('<div class="section-header">Target Regions</div>', unsafe_allow_html=True)
    
    # Available regions
    available_regions = [
        {"id": "tokyo_subway", "name": "Tokyo Subway", "locale": "ja-JP", "emoji": "🇯🇵"},
        {"id": "berlin_billboard", "name": "Berlin Billboard", "locale": "de-DE", "emoji": "🇩🇪"},
        {"id": "nyc_times_square", "name": "NYC Times Square", "locale": "en-US", "emoji": "🇺🇸"},
        {"id": "dubai_mall", "name": "Dubai Mall", "locale": "ar-AE", "emoji": "🇦🇪"},
        {"id": "sydney_beach", "name": "Sydney Beach", "locale": "en-AU", "emoji": "🇦🇺"},
        {"id": "paris_metro", "name": "Paris Metro", "locale": "fr-FR", "emoji": "🇫🇷"},
        {"id": "london_tube", "name": "London Tube", "locale": "en-GB", "emoji": "🇬🇧"}
    ]
    
    # Region selection with checkboxes
    st.markdown("Select target regions for localization:")
    
    cols = st.columns(3)
    selected_regions = []
    
    for idx, region in enumerate(available_regions):
        col = cols[idx % 3]
        with col:
            if st.checkbox(
                f"{region['emoji']} {region['name']}",
                key=f"region_{region['id']}"
            ):
                selected_regions.append(region)
    
    st.session_state.selected_regions = selected_regions
    
    # Brand guardrails
    st.markdown('<div class="section-header">Brand Guardrails</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        negative_prompts = st.text_area(
            "Negative Prompts (one per line)",
            value="distorted product\naltered logo\nincorrect colors",
            help="Elements to avoid in generated images"
        )
    
    with col2:
        forbidden_elements = st.text_area(
            "Forbidden Elements (one per line)",
            value="competitor brands\ninappropriate content",
            help="Elements that must not appear"
        )
    
    # Generation settings
    with st.expander("⚙️ Generation Settings"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            seed = st.number_input("Seed", min_value=1, max_value=999999, value=42)
        
        with col2:
            steps = st.slider("Inference Steps", min_value=20, max_value=50, value=30)
        
        with col3:
            guidance = st.slider("Guidance Scale", min_value=3, max_value=5, value=5)
    
    # Generate button
    st.markdown("---")
    
    if len(selected_regions) > 0:
        if st.button("🎨 Generate Localized Images", type="primary"):
            with st.spinner(f"Generating {len(selected_regions)} localized variations..."):
                st.markdown('<div class="success-box">✓ Generation started! Check the Results tab for progress.</div>', unsafe_allow_html=True)
                
                # Placeholder for actual generation
                # In real implementation, this would call the pipeline
                st.info("Note: This is a UI demo. Connect to pipeline for actual generation.")
    else:
        st.warning("Please select at least one target region")


def results_tab():
    """Results gallery and download interface."""
    
    st.markdown('<div class="section-header">Generated Images</div>', unsafe_allow_html=True)
    
    # Check for existing outputs
    output_dir = Path("output/final")
    
    if not output_dir.exists() or not any(output_dir.iterdir()):
        st.markdown('<div class="info-box">ℹ️ No generated images yet. Configure and generate in the Localization tab.</div>', unsafe_allow_html=True)
        return
    
    # Scan for generated images
    region_dirs = [d for d in output_dir.iterdir() if d.is_dir()]
    
    if not region_dirs:
        st.info("No results available yet")
        return
    
    # Display results in grid
    for region_dir in region_dirs:
        region_name = region_dir.name
        
        # Find images in this region
        png_files = list(region_dir.glob("*_8bit.png"))
        
        if png_files:
            st.markdown(f"### {region_name.replace('_', ' ').title()}")
            
            for png_file in png_files[:3]:  # Show up to 3 most recent
                # Extract metadata from filename
                base_name = png_file.stem.replace("_8bit", "")
                tiff_file = region_dir / f"{base_name}_16bit.tif"
                json_file = region_dir / f"{base_name}_params.json"
                heatmap_file = region_dir / f"{base_name}_heatmap.png"
                
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.image(str(png_file), caption="Generated Image", use_container_width=True)
                
                with col2:
                    if heatmap_file.exists():
                        st.image(str(heatmap_file), caption="Consistency Heatmap", use_container_width=True)
                    else:
                        st.info("No heatmap available")
                
                with col3:
                    # Load JSON for metadata
                    if json_file.exists():
                        with open(json_file, 'r') as f:
                            metadata = json.load(f)
                        
                        # Display metadata
                        st.markdown("**Metadata:**")
                        
                        gen_info = metadata.get("generation_info", {})
                        st.text(f"Seed: {gen_info.get('seed', 'N/A')}")
                        
                        consistency = metadata.get("consistency_check", {})
                        score = consistency.get("score")
                        if score is not None:
                            st.text(f"Consistency: {score:.2%}")
                            
                            if consistency.get("status") == "passed":
                                st.success("✓ Passed")
                            else:
                                st.warning("⚠ Flagged")
                        
                        c2pa = metadata.get("c2pa_credentials", {})
                        if c2pa.get("verified"):
                            st.success("✓ C2PA Verified")
                        else:
                            st.info("C2PA: Not verified")
                    
                    # Download buttons
                    st.markdown("**Downloads:**")
                    
                    if tiff_file.exists():
                        with open(tiff_file, 'rb') as f:
                            st.download_button(
                                "📥 TIFF (Print)",
                                data=f.read(),
                                file_name=tiff_file.name,
                                mime="image/tiff"
                            )
                    
                    if png_file.exists():
                        with open(png_file, 'rb') as f:
                            st.download_button(
                                "📥 PNG (Web)",
                                data=f.read(),
                                file_name=png_file.name,
                                mime="image/png"
                            )
                    
                    if json_file.exists():
                        with open(json_file, 'rb') as f:
                            st.download_button(
                                "📥 JSON",
                                data=f.read(),
                                file_name=json_file.name,
                                mime="application/json"
                            )
                
                st.markdown("---")


if __name__ == "__main__":
    main()
