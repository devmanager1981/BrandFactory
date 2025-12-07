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
    
    /* Custom header */
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.2rem;
        opacity: 0.9;
    }
    
    /* Card styling */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #e1e5e9;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
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
        help="Maximum allowed pixel difference (lower = stricter)"
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
                st.success("✅ Ready to process! (Full pipeline integration pending)")
                st.info(f"Selected regions: {', '.join(config['selected_regions'])}")
                st.info(f"Consistency threshold: {config['consistency_threshold']}")
                st.info(f"C2PA enabled: {config['enable_c2pa']}")
                st.info(f"Seed: {config['seed']}")
        else:
            if selected_image is None:
                st.info("👆 Please select or upload an image to get started.")
            elif not config['selected_regions']:
                st.info("👈 Please select at least one target region in the sidebar.")
    
    with col2:
        # Instructions section
        st.markdown("""
        <div class="custom-card">
            <h3>🎯 How It Works</h3>
            <ol>
                <li><strong>Upload or Select</strong> a product image</li>
                <li><strong>Choose target regions</strong> from the sidebar</li>
                <li><strong>Click Generate</strong> to create localized content</li>
                <li><strong>Download results</strong> in multiple formats</li>
            </ol>
            
            <h4>✨ Features</h4>
            <ul>
                <li>🎨 AI-powered cultural localization</li>
                <li>📊 Consistency verification</li>
                <li>🔒 C2PA content authenticity</li>
                <li>📁 Dual-format output (TIFF + PNG)</li>
                <li>📋 Complete audit trail</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <p>🌍 Global Brand Localizer | Powered by Bria AI</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
