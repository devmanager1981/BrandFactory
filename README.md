# Global Brand Localizer

An automated ad-campaign generation system that creates culturally-localized product imagery for global markets using Bria's FIBO model.

## Overview

The Global Brand Localizer leverages FIBO's JSON-native text-to-image foundation model to generate multiple localized versions of product imagery while maintaining strict visual consistency of the product itself across all variations. This addresses a critical enterprise need: generating 50+ market-specific versions of a single product image with guaranteed brand consistency, print-ready quality, and full legal compliance.

## Key Features

- **Deterministic Product Consistency**: Lock product parameters (camera angle, focal length, geometry) while varying environment
- **Automated Batch Localization**: Process multiple regions with a single command
- **Dual Output Format**: 16-bit TIFF for print + 8-bit PNG for web
- **Consistency Proof**: Pixel difference heatmaps validate product consistency
- **C2PA Compliance**: Full legal provenance tracking for generated assets
- **Pre-configured Regions**: 7 curated global markets (Tokyo, Berlin, NYC, Dubai, Sydney, Mumbai, São Paulo)

## Architecture

### Two-Pipeline System

1. **VLM Bridge Pipeline** (`briaai/FIBO-VLM-prompt-to-JSON`)
   - Analyzes product images and generates structured JSON parameters
   - Operates in Image → JSON mode

2. **FIBO Generation Pipeline** (`briaai/FIBO`)
   - Takes JSON + Seed and generates high-fidelity images
   - Supports local GPU and Cloud API fallback

### Core Components

- **Schema Sanitizer**: Validates VLM output against FIBO enumerations
- **Localization Agent**: Manages batch processing and region-specific modifications
- **Output Manager**: Handles dual-format saving, heatmap generation, and C2PA signing
- **Web UI**: Streamlit-based interface for campaign management

## Installation

### Prerequisites

- Python 3.9+
- CUDA-capable GPU (optional, will fallback to Cloud API)
- Git
- Bria API Token (get from https://bria.ai/)

### Setup

```bash
# Clone the repository
git clone https://github.com/devmanager1981/BrandFactory.git
cd BrandFactory

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure API tokens
cp .env.example .env
# Edit .env and add your BRIA_API_TOKEN
```

### Deployment

**No deployment needed!** This system uses **Bria Cloud API** exclusively:

- ✅ FIBO models are already hosted by Bria
- ✅ Just need your **Production API key** from https://bria.ai/
- ✅ No GPU required locally
- ✅ No model downloads
- ✅ Fast and reliable

**API Key Setup:**
1. Go to https://bria.ai/ and get your **Production** API token
2. Copy your Production token (the one marked "Production" in your dashboard)
3. Add it to `.env`:
   ```
   BRIA_API_TOKEN=your_production_token_here
   ```

That's it! The system will use Bria's cloud infrastructure for all image generation.

## Usage

### Command Line

```bash
# Generate localized images for all regions
python -m src.main --product images/wristwatch.png --regions all

# Generate for specific regions
python -m src.main --product images/headphones.png --regions tokyo_subway,berlin_billboard
```

### Web UI

```bash
# Launch Streamlit interface
streamlit run src/ui/app.py
```

## Project Structure

```
BrandFactory/
├── src/
│   ├── pipeline_manager.py    # FIBO pipeline initialization
│   ├── api_manager.py          # Cloud API fallback
│   ├── schema_sanitizer.py     # VLM output validation
│   ├── localization_agent.py   # Batch processing logic
│   ├── batch_processor.py      # Queue management
│   ├── output_manager.py       # File handling and C2PA
│   └── ui/
│       └── app.py              # Streamlit interface
├── config/
│   └── region_configs.py       # Pre-defined region settings
├── tests/
│   ├── test_sanitizer.py       # Property-based tests
│   ├── test_agent.py
│   └── ...
├── images/
│   ├── wristwatch.png          # Base product image (default)
│   └── headphones.png          # Alternative product image
├── output/                     # Generated images (gitignored)
├── requirements.txt
├── .gitignore
└── README.md
```

## Base Product Images

The system includes two pre-configured base product images:
- **`images/wristwatch.png`** - Luxury wristwatch with green leather strap (default)
- **`images/headphones.png`** - Premium over-ear headphones

## Pre-Defined Regions

- **Tokyo Subway** - Neon/urban aesthetic
- **Berlin Billboard** - Minimalist/modern
- **NYC Times Square** - Vibrant/energetic
- **Dubai Mall** - Luxury/elegant
- **Sydney Beach** - Lifestyle/relaxed
- **Mumbai Street** - Colorful/busy
- **São Paulo Metro** - Energetic/urban

## Testing

```bash
# Run all tests
pytest

# Run property-based tests only
pytest tests/ -k "property"

# Run with coverage
pytest --cov=src tests/
```

## Hackathon Categories

This project targets:
- **Best Overall**: Professional 16-bit output, C2PA compliance, consistency proof
- **Best JSON-Native or Agentic Workflow**: Deterministic JSON control, automated batch processing

## License

MIT License (to be added)

## Repository

https://github.com/devmanager1981/BrandFactory

## Development Status

🚧 Under active development for hackathon submission
