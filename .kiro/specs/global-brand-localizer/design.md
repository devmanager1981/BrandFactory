# Design Document

## Overview

The Global Brand Localizer is a Python-based application that automates the generation of culturally-localized product imagery for global marketing campaigns. The system uses Bria's FIBO model through the BriaFiboPipeline to achieve deterministic control over image generation, ensuring product consistency while varying environmental context across different markets.

The core innovation lies in leveraging FIBO's JSON-native architecture and disentanglement capabilities to independently control product parameters (locked) and environmental parameters (variable). This enables enterprises to generate dozens of market-specific variations from a single product image while maintaining perfect brand consistency.

The system targets the hackathon's "Best Overall" and "Best JSON-Native or Agentic Workflow" categories by demonstrating:
- Professional-grade 16-bit HDR output for print production
- Deterministic JSON-based control that guarantees visual consistency
- Automated agentic workflow for batch localization
- Full C2PA compliance for legal provenance tracking

## Architecture

### Critical Technical Note: Two-Pipeline Architecture

FIBO uses a **two-step process** that requires two separate pipeline instances:

1. **VLM Bridge Pipeline** (`ModularPipeline` from `briaai/FIBO-VLM-prompt-to-JSON`)
   - Converts natural language OR images into structured JSON
   - Operates in two modes:
     - **Generate Mode**: Text prompt → JSON
     - **Analysis Mode**: Image → JSON

2. **FIBO Generation Pipeline** (`BriaFiboPipeline` from `briaai/FIBO`)
   - Takes a structured JSON + Seed and generates a high-fidelity image

### Components

#### 1. VLM Bridge and Schema Sanitizer
**Purpose:** Translates user inputs (text/image) into Master JSON and validates/sanitizes VLM output to ensure it only contains valid FIBO parameter enumerations.

**Process Flow:**
1. **Input:** User prompt (Text) OR Product Image (Image).
2. **VLM Call:** Call VLM Bridge Pipeline to generate initial JSON.
3. **Schema Sanitizer (NEW):** Implements a mapping layer (`vlm_to_fibo_map.json`) to convert VLM-generated free-form text (e.g., "high contrast") into the corresponding FIBO enum (e.g., `"lighting_type": "high_contrast_key_light"`). If an extracted parameter is outside the allowed list of FIBO enumerations, it is either corrected or dropped, ensuring deterministic control [New].
4. **Output:** Valid Master JSON with locked product parameters.

#### 2. Localization Agent
**Purpose:** Manages the batch generation process, iterating through regions, modifying environmental parameters, and applying brand controls.

**Process Flow:**
1. **Input:** Master JSON + List of target regions (e.g., 'Tokyo', 'Sydney').
2. **Region Configuration:** Load `region_configs.py` (e.g., Tokyo = "Busy street, neon signs").
3. **Parameter Modification:** Merge Master JSON (locked) with Region config (variable).
4. **Brand DNA Guardrails (NEW):** Automatically injects **negative prompts** and checks for `forbidden_elements` (e.g., 'No red colors', 'Avoid water') based on campaign settings [New].
5. **Output:** A list of ready-to-process, region-specific JSON files.

#### 3. FIBO Generation Pipeline
**Purpose:** The core engine that runs the image generation using the BriaFiboPipeline.
**Hybrid Execution:** Supports both local GPU execution and Cloud API requests, managed by a central `PipelineManager` [New].

#### 4. Output Manager
**Purpose:** Handles image persistence, C2PA signing, and quality control metrics.

**Process Flow:**
1. **Input:** 16-bit RAW image data from FIBO + Final Generation JSON.
2. **SSIM-Based Consistency Check (UPDATED):** Uses Structural Similarity Index (SSIM) to compare the generated product region against the Master Product image. The system first extracts product masks from both images, then neutralizes backgrounds by setting non-product pixels to gray before SSIM calculation. This ensures only the product regions are compared, ignoring background differences. SSIM is an industry-standard perceptual metric that measures structural similarity while being robust to lighting and color variations. The system converts SSIM scores (range: -1 to 1, where 1 = identical) to dissimilarity scores (range: 0 to 1, where 0 = identical) using the formula: `dissimilarity = (1.0 - ssim) / 2.0`. Generates a visual heatmap overlay for the UI [Updated].
3. **File Saving (UPDATED):**
    - **Primary Output:** Save original 16-bit image as **TIFF** (`.tif`) for print.
    - **Secondary Output:** Downscale/convert and save as **8-bit PNG/JPG** thumbnail (`.png`) for the web gallery/UI [New].
4. **C2PA Signing:** Embed Content Credentials into the 16-bit TIFF.
5. **JSON Archival:** Save the final generation JSON (including seed).

#### 5. User Interface (UI)
**Purpose:** Provides a web-based dashboard for campaign management.

**Key Features:**
- **Base Product Selector:** Radio buttons or dropdown to select from pre-configured base product images:
  - `images/wristwatch.png` (default)
  - `images/headphones.png`
  - Optional: Custom image upload
- **One-Click Variations (NEW):** Button next to each result to re-run generation using the same JSON but a new seed for A/B testing variations [New].
- **Gallery View:** Displays output, C2PA status, and the **Pixel Difference Heatmap** overlay [New].

### Hackathon-Specific Optimizations

**Targeting "Best Overall" Category:**
- Emphasize 16-bit HDR output in demo
- **NEW:** Demo the **Pixel Difference Heatmap** as definitive proof of product consistency across localizations [New].
- Highlight C2PA compliance for enterprise use.

**Targeting "Best JSON-Native or Agentic Workflow" Category:**
- Show Master JSON structure clearly
- Demonstrate automated region iteration
- Highlight parameter locking mechanism
- Show JSON audit trail for reproducibility

---

## Data Models

### Master JSON Schema

```python
{
  "version": "1.0",
  "metadata": {
    "created_at": "ISO8601 timestamp",
    "source_image": "path/to/original.png",
    "campaign_id": "unique_campaign_identifier"
  },
  "locked_parameters": {
    "camera_angle": "low_angle_iso",  # LOCKED
    "focal_length": 50,                # LOCKED
    "aspect_ratio": "16:9",            # LOCKED
    "product_geometry": {              # LOCKED
      "position": [0.5, 0.5],
      "scale": 1.0,
      "rotation": 0
    }
  },
  "variable_parameters": {
    "background": "neutral",           # VARIABLE
    "lighting_type": "soft_natural",   # VARIABLE
    "environment": "studio",           # VARIABLE
    "mood": "professional"             # VARIABLE
  }
}
```

### Region Configuration Schema

```python
{
  "region_id": "tokyo_subway",
  "display_name": "Tokyo Subway Poster",
  "locale": "ja-JP",
  "environment_overrides": {
    "background": "urban_night",
    "lighting_type": "neon_ambient",
    "environment": "subway_station",
    "mood": "energetic"
  },
  "cultural_context": {
    "text_overlay_position": "top_right",
    "color_preferences": ["blue", "white", "red"],
    "avoid_elements": ["number_4"]  # Cultural sensitivity
  }
}
```

### Campaign Configuration Schema

```python
{
  "campaign_id": "summer_2024_global",
  "master_json_path": "path/to/master.json",
  "target_regions": ["tokyo_subway", "berlin_billboard", "nyc_times_square"],
  "brand_guardrails": {
    "negative_prompts": [
      "distorted product",
      "altered logo",
      "incorrect colors"
    ],
    "forbidden_elements": [
      "competitor_brands",
      "inappropriate_content"
    ],
    "required_elements": [
      "brand_logo_visible",
      "product_centered"
    ]
  },
  "generation_settings": {
    "seed": 42,
    "num_inference_steps": 50,
    "guidance_scale": 7.5
  }
}
```

### Python Class Structures

```python
@dataclass
class MasterJSON:
    version: str
    metadata: Dict[str, Any]
    locked_parameters: Dict[str, Any]
    variable_parameters: Dict[str, Any]
    
    def lock_parameter(self, key: str) -> None:
        """Move parameter from variable to locked"""
        
    def is_locked(self, key: str) -> bool:
        """Check if parameter is locked"""

@dataclass
class RegionConfig:
    region_id: str
    display_name: str
    locale: str
    environment_overrides: Dict[str, Any]
    cultural_context: Dict[str, Any]

@dataclass
class GenerationResult:
    region_id: str
    image_16bit: np.ndarray
    image_8bit: np.ndarray
    generation_json: Dict[str, Any]
    seed: int
    consistency_score: float
    heatmap: np.ndarray
    c2pa_signed: bool
    timestamp: datetime
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Parameter Lock Preservation
*For any* Master JSON and any region configuration, when the Localization Agent merges them, all locked parameters from the Master JSON must remain unchanged in the output JSON.
**Validates: Requirements 2.1, 4.2**

### Property 2: Schema Sanitizer Validity
*For any* VLM-generated JSON output, after passing through the Schema Sanitizer, all parameter values must be valid FIBO enumerations from the predefined mapping.
**Validates: Requirements 3.1, 3.2**

### Property 3: Dual Output Consistency
*For any* generated 16-bit TIFF image, the corresponding 8-bit PNG must be a valid downscaled representation with identical aspect ratio and content.
**Validates: Requirements 7.1, 7.2**

### Property 4: JSON Audit Completeness
*For any* saved generation JSON, it must contain both the complete Master JSON parameters and all region-specific modifications, formatted as valid JSON.
**Validates: Requirements 7.3, 7.5, 7.6**

### Property 5: Brand Guardrail Enforcement
*For any* region-specific JSON generated by the Localization Agent, all negative prompts from the campaign's brand guardrails must be present in the final JSON.
**Validates: Requirements 4.3**

### Property 6: Consistency Score Bounds and SSIM Conversion
*For any* generated image with an SSIM-based consistency check, the dissimilarity score must be a value between 0.0 (identical) and 1.0 (completely different), correctly converted from SSIM scores using the formula: dissimilarity = (1.0 - ssim) / 2.0. The SSIM calculation must be performed on masked images where backgrounds are neutralized to ensure only product regions are compared.
**Validates: Requirements 5.3, 5.4**

### Property 7: C2PA Provenance Completeness
*For any* C2PA-signed image, the embedded credentials must contain all required provenance data: Master JSON fingerprint, region config, seed, and timestamp.
**Validates: Requirements 6.1, 6.2**

### Property 8: Error Recovery State Preservation
*For any* system error that triggers state saving, the saved state must contain sufficient information to resume processing from the point of failure.
**Validates: Requirements 8.6**

### Property 9: Batch Processing Isolation
*For any* batch of regions being processed, a failure in one region must not prevent the processing of other regions in the batch.
**Validates: Requirements 8.3**

### Property 10: File Format Correctness
*For any* saved 16-bit TIFF file, it must be a valid TIFF format readable by standard image processing libraries.
**Validates: Requirements 7.1**

---

## Error Handling

### Error Categories and Strategies

#### 1. Pipeline Initialization Errors
**Scenarios:**
- CUDA out of memory
- Missing model files
- Incompatible library versions

**Strategy:**
- Log detailed error with system diagnostics
- Attempt Cloud API fallback automatically
- If both fail, provide clear user guidance on resolution

#### 2. VLM Bridge Errors
**Scenarios:**
- Malformed JSON output
- Missing required parameters
- Invalid parameter values

**Strategy:**
- Log raw VLM output for debugging
- Attempt Schema Sanitizer correction
- Fall back to default Master JSON parameters
- Continue processing with warnings

#### 3. Image Generation Errors
**Scenarios:**
- FIBO pipeline timeout
- Invalid JSON parameters
- Memory exhaustion

**Strategy:**
- Retry with reduced inference steps (50 → 30 → 20)
- Log failure with full context
- Continue batch processing other regions
- Report all failures in summary

#### 4. File I/O Errors
**Scenarios:**
- Disk full
- Permission denied
- Network storage unavailable

**Strategy:**
- Retry up to 3 times with exponential backoff (1s, 2s, 4s)
- Attempt alternate output directory
- Save to temporary location if primary fails
- Alert user with specific error details

#### 5. C2PA Signing Errors
**Scenarios:**
- c2patool not installed
- Invalid certificate
- Signing timeout

**Strategy:**
- Save image without C2PA credentials
- Flag image for manual review
- Log detailed error for troubleshooting
- Continue processing

#### 6. Consistency Check Errors
**Scenarios:**
- Product region detection fails
- Heatmap calculation error
- Threshold exceeded

**Strategy:**
- Log warning but save image
- Set consistency score to -1 (indicating error)
- Flag for manual review
- Continue processing

### Error Logging Format

```python
{
  "timestamp": "ISO8601",
  "error_type": "VLM_BRIDGE_ERROR",
  "severity": "WARNING",
  "component": "schema_sanitizer",
  "message": "Invalid parameter value detected",
  "context": {
    "raw_vlm_output": {...},
    "invalid_parameter": "camera_angle",
    "invalid_value": "super low angle",
    "corrected_value": "low_angle_iso"
  },
  "recovery_action": "Applied nearest valid enumeration"
}
```

---

## Testing Strategy

### Dual Testing Approach

The system employs both **unit testing** and **property-based testing** to ensure comprehensive coverage:

- **Unit tests** verify specific examples, edge cases, and integration points
- **Property tests** verify universal properties that should hold across all inputs
- Together they provide complete coverage: unit tests catch concrete bugs, property tests verify general correctness

### Property-Based Testing

**Framework:** Hypothesis (Python)

**Configuration:**
- Minimum 100 iterations per property test
- Each property test must reference its corresponding correctness property using the format: `# Feature: global-brand-localizer, Property X: [property text]`
- Each correctness property must be implemented by a SINGLE property-based test

**Property Test Examples:**

```python
# Feature: global-brand-localizer, Property 1: Parameter Lock Preservation
@given(master_json=master_json_strategy(), region_config=region_config_strategy())
@settings(max_examples=100)
def test_parameter_lock_preservation(master_json, region_config):
    agent = LocalizationAgent()
    result = agent.merge_configs(master_json, region_config)
    
    # All locked parameters must be unchanged
    for key, value in master_json.locked_parameters.items():
        assert result[key] == value

# Feature: global-brand-localizer, Property 2: Schema Sanitizer Validity
@given(vlm_output=vlm_json_strategy())
@settings(max_examples=100)
def test_schema_sanitizer_validity(vlm_output):
    sanitizer = SchemaSanitizer()
    result = sanitizer.sanitize(vlm_output)
    
    # All parameters must be valid FIBO enumerations
    for key, value in result.items():
        assert value in VALID_FIBO_ENUMS[key]
```

### Unit Testing

**Framework:** pytest

**Coverage Areas:**
- Specific examples demonstrating correct behavior
- Edge cases (empty inputs, boundary values, malformed data)
- Integration points between components
- Error handling paths

**Unit Test Examples:**

```python
def test_master_json_creation_from_image():
    """Test VLM Bridge creates valid Master JSON from product image"""
    manager = FiboPipelineManager()
    master_json = manager.image_to_master_json("tests/fixtures/product.png")
    
    assert "locked_parameters" in master_json
    assert "variable_parameters" in master_json
    assert master_json["locked_parameters"]["camera_angle"] is not None

def test_empty_region_list_handling():
    """Test batch processor handles empty region list gracefully"""
    processor = BatchProcessor()
    results = processor.process_regions(master_json={}, regions=[])
    
    assert results == []
    assert processor.error_count == 0

def test_c2pa_signing_failure_recovery():
    """Test system continues when C2PA signing fails"""
    output_manager = OutputManager()
    result = output_manager.save_with_c2pa(
        image=test_image,
        json_data=test_json,
        c2pa_available=False
    )
    
    assert result.saved == True
    assert result.c2pa_signed == False
    assert result.flagged_for_review == True
```

### Integration Testing

**Scope:** End-to-end workflow validation

**Test Scenarios:**
1. Complete workflow: Upload image → Generate Master JSON → Process 3 regions → Verify outputs
2. Cloud API fallback: Simulate GPU failure → Verify API usage → Validate results
3. Error recovery: Inject failure in region 2 of 5 → Verify other regions complete
4. Consistency validation: Generate variations with same JSON → Verify consistency scores

### Test Data Strategy

**Fixtures:**
- Sample product images (various sizes, formats)
- Pre-generated Master JSONs (valid and invalid)
- Region configurations (diverse locales)
- Mock VLM outputs (valid, malformed, edge cases)

**Generators (for property-based testing):**
- `master_json_strategy()`: Generates valid Master JSON structures
- `region_config_strategy()`: Generates valid region configurations
- `vlm_json_strategy()`: Generates VLM-like outputs (including invalid ones)
- `campaign_config_strategy()`: Generates campaign configurations

---
