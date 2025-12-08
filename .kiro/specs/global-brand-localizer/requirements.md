# Requirements Document

## Introduction

The Global Brand Localizer is an automated ad-campaign generation system designed for enterprise marketing teams who need to create multiple localized versions of product imagery for different global markets. The system leverages Bria's FIBO model to generate culturally-adapted product images while maintaining strict visual consistency of the product itself across all variations. This addresses a critical enterprise need: generating 50+ market-specific versions of a single product image with guaranteed brand consistency, print-ready quality, and full legal compliance.

## Glossary

- **FIBO**: Bria's JSON-native text-to-image foundation model that provides deterministic control over image generation parameters
- **BriaFiboPipeline**: The Hugging Face diffusers pipeline that provides programmatic access to FIBO's generation capabilities
- **VLM Bridge**: Vision Language Model component that translates natural language prompts or analyzes images to generate structured JSON parameters
- **Master JSON**: The template JSON file containing locked product parameters (camera angle, focal length, product geometry) that remain constant across all localizations
- **Localization Agent**: The system component that modifies environment parameters (background, lighting) while preserving locked product parameters
- **Disentanglement**: FIBO's capability to independently control different aspects of image generation (product vs environment)

---

### Requirement 1: Core System Setup and Pipeline

**User Story:** As a developer, I need to reliably initialize the FIBO model and have a fallback mechanism, so that generation is robust against local hardware constraints.

#### Acceptance Criteria

1. WHEN the application starts THEN the System SHALL load the necessary FIBO pipelines (`briaai/FIBO` and `briaai/FIBO-VLM-prompt-to-JSON`).
2. WHEN the application detects local GPU limitations THEN the System SHALL automatically fall back to using a Cloud API endpoint for generation [New].
3. WHEN using the Cloud API THEN the System SHALL ensure the generated JSON is passed without modification.

---

### Requirement 2: Master JSON Management

**User Story:** As a campaign manager, I want a single source of truth for all critical product features, so that brand consistency is guaranteed across all localized variations.

#### Acceptance Criteria

1. WHEN generating a Master JSON THEN the System SHALL explicitly tag all product geometry parameters (e.g., focal length, aspect ratio) as "LOCKED".
2. WHEN generating a Master JSON THEN the System SHALL set all environment parameters (e.g., background, lighting) as "VARIABLE".

---

### Requirement 3: VLM Bridge and Parameter Sanitization

**User Story:** As an operator, I want the VLM to extract product features into a reliable, valid JSON format, so that the FIBO model receives only deterministic, approved parameters.

#### Acceptance Criteria

1. WHEN the VLM Bridge generates output THEN the System SHALL use a **Schema Sanitizer** to map free-form text values (e.g., "low angle") to the nearest valid FIBO enumeration (e.g., `"camera_angle": "low_angle_iso"`) [New].
2. WHEN an invalid or ambiguous parameter value is returned by the VLM THEN the System SHALL automatically snap the value to the nearest predefined valid parameter or revert to the Master JSON value [New].
3. WHEN a product image is uploaded THEN the VLM Bridge SHALL output a Master JSON with locked product parameters (e.g., focal length, aspect ratio) and placeholder environment parameters.
4. WHEN a text prompt is used THEN the VLM Bridge SHALL output a JSON with parameters derived from the prompt.

---

### Requirement 4: Localization Agent and Batch Processing

**User Story:** As a marketing manager, I want to process an entire list of regional requirements automatically, so that I can generate a complete campaign batch with a single command.

#### Acceptance Criteria

1. WHEN the Agent processes a region THEN it SHALL automatically generate cultural and contextual prompts and parameters (e.g., "Tokyo subway poster").
2. WHEN the Agent modifies the JSON THEN it SHALL strictly adhere to the locked parameters from the Master JSON.
3. WHEN the Agent modifies the JSON THEN it SHALL apply **Brand DNA Guardrails** (negative prompts/forbidden elements) based on campaign configuration [New].
4. WHEN the Agent finishes processing a region THEN it SHALL immediately queue the request to the FIBO Generation Pipeline.

---

### Requirement 5: FIBO Image Generation and Consistency Proof

**User Story:** As a QA specialist, I want visual proof that the product's appearance has not been altered during localization, ensuring brand consistency across all markets.

#### Acceptance Criteria

1. WHEN the Agent submits a request THEN the FIBO pipeline SHALL return a high-resolution, 16-bit image.
2. WHEN the Master JSON is used across multiple generations THEN the System SHALL generate images with deterministic, visually identical product features.
3. WHEN an image is generated using background replacement THEN the System SHALL calculate a **Structural Similarity (SSIM) Heatmap** comparing the product region to verify consistency [Updated].
4. WHEN using background replacement THEN the product SHALL remain pixel-perfect identical across all regions, with only the background changing [Updated].

---

### Requirement 6: C2PA Compliance and Provenance

**User Story:** As a compliance officer, I need full legal proof of origin and modification for every generated asset, so that we remain compliant with global media regulations.

#### Acceptance Criteria

1. WHEN an image is generated THEN the System SHALL collect all generation parameters (Master JSON, Region config, seed) as provenance data.
2. WHEN the output file is saved THEN the System SHALL embed Content Credentials (C2PA) directly into the image file.

---

### Requirement 7: Output Manager and File Handling

**User Story:** As a print manager, I need the final, high-quality images in a print-ready format and the corresponding source JSON for auditing.

#### Acceptance Criteria

1. WHEN the FIBO pipeline returns an image THEN the Output Manager SHALL save the **full-resolution 16-bit TIFF** for print production.
2. WHEN the FIBO pipeline returns an image THEN the Output Manager SHALL save a **compressed 8-bit PNG/JPG** for web gallery display and preview [New].
3. WHEN an image is saved THEN the System SHALL save the final, complete generation JSON alongside it for audit purposes.
4. WHEN C2PA signing is complete THEN the Output Manager SHALL embed the Content Credentials into the final 16-bit TIFF file.
5. WHEN the generation JSON is saved THEN the System SHALL include both the Master JSON parameters and region-specific modifications.
6. WHEN JSON parameters are saved THEN the System SHALL format them as valid, human-readable JSON with proper indentation.
7. WHEN reviewing saved parameters THEN the System SHALL enable identification of which parameters were locked and which were modified per region.

---

### Requirement 8: Error Handling and System Resilience

**User Story:** As a system administrator, I want the system to handle errors gracefully and provide clear diagnostics, so that I can quickly identify and resolve issues during campaign generation.

#### Acceptance Criteria

1. WHEN a pipeline loading failure occurs THEN the System SHALL log detailed error information and attempt the Cloud API fallback.
2. WHEN the VLM Bridge returns malformed JSON THEN the System SHALL log the error, attempt sanitization, and if unsuccessful, use default Master JSON parameters.
3. WHEN image generation fails for a specific region THEN the System SHALL log the failure, continue processing remaining regions, and report all failures at completion.
4. WHEN file I/O operations fail THEN the System SHALL retry up to 3 times with exponential backoff before reporting failure.
5. WHEN C2PA signing fails THEN the System SHALL save the image without credentials and flag it for manual review.
6. WHEN the system encounters an unrecoverable error THEN it SHALL save all intermediate state (Master JSON, processed regions) to enable recovery.

---

### Requirement 9: User Interface for Campaign Management

**User Story:** As a marketing manager, I want a simple web interface to upload product images, configure localization settings, and monitor generation progress, so that I can manage campaigns without using command-line tools.

#### Acceptance Criteria

1. WHEN a user accesses the interface THEN the System SHALL display a product image upload area.
2. WHEN a user uploads a product image THEN the System SHALL display a preview and enable Master JSON generation.
3. WHEN configuring a campaign THEN the System SHALL provide a region selection interface with predefined locale options.
4. WHEN a user initiates generation THEN the System SHALL display real-time progress for each region being processed.
5. WHEN generation completes THEN the System SHALL display a gallery view of all generated images with their corresponding regions and their **Pixel Difference Heatmaps** [New].
6. WHEN viewing generated images THEN the System SHALL show the compliance status badge for each image.
7. WHEN viewing an image in the gallery THEN the System SHALL provide a **"Generate Variations"** button that re-runs the generation with the exact same JSON but a new seed [New].
8. WHEN a user clicks on a generated image THEN the System SHALL display the full-resolution image and allow download of the 16-bit TIFF, 8-bit PNG/JPG, and its JSON parameters.