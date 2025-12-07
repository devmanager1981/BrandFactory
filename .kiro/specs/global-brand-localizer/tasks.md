# Implementation Plan

## Overview

This implementation plan follows a hybrid testing approach: implement functionality first, write tests immediately after, then verify. Each task concludes with a git commit to enable recovery and demonstrate progress.

The plan is structured to build incrementally, with early validation of core FIBO integration and robust error handling before building higher-level features.

---

## Tasks (Adjusted for Priority and Feedback)

- [ ] 1. Project Setup and Environment Configuration


  - Initialize Python project structure with proper directory layout
  - Create `requirements.txt` with all dependencies: `diffusers`, `transformers`, `torch`, `numpy`, `opencv-python`, `Pillow`, `pytest`, `hypothesis`
  - Set up `.gitignore` for Python (exclude `__pycache__`, `.pytest_cache`, model cache, output files)
  - Create basic `README.md` with project description and setup instructions
  - Verify `images/` folder contains base product images: `wristwatch.png` and `headphones.png`
  - Initialize git repository and make initial commit
  - **Commit**: "chore: initialize project structure and dependencies"
  - _Requirements: 1.1, 1.2_

- [ ] 2. FIBO Pipeline Integration and Validation
  - Create `src/pipeline_manager.py` with `FiboPipelineManager` class
  - Implement dual-pipeline initialization (VLM Bridge + FIBO Image pipelines)
  - Load `briaai/FIBO-VLM-prompt-to-JSON` using `ModularPipeline.from_pretrained()`
  - Load `briaai/FIBO` using `BriaFiboPipeline.from_pretrained()`
  - Add error handling for model loading failures (missing dependencies, GPU issues)
  - **Commit**: "feat: core FIBO pipelines integrated"
  - _Requirements: 1.1, 8.1_

- [ ] **3. CRITICAL: Cloud API/Remote Execution Fallback (MOVED UP)** [New]
  - Create `src/api_manager.py` with methods to interact with a cloud-based FIBO API endpoint [New].
  - Implement a check in `FiboPipelineManager` to use the API if local GPU setup fails or is too slow [New].
  - Test simple text-to-JSON and JSON-to-Image request/response cycles via API [New].
  - **Commit**: "feat: implemented cloud API fallback (safety net)"
  - _Requirements: 1.3_

- [ ] **4. VLM Schema Sanitizer Implementation** [New]
  - Create `src/schema_sanitizer.py` with predefined mapping dictionaries (`vlm_to_fibo_map.json`) [New].
  - Implement logic to take VLM raw output and forcefully convert parameters (`camera_angle`, `lighting_type`, etc.) to valid FIBO enumerations [New].
  - Create test data generators for property-based testing (Hypothesis strategies)
  - **Commit**: "feat: VLM output schema sanitization and validation"
  - _Requirements: 3.1, 3.2_

- [ ] 4.1 Write property-based test for Schema Sanitizer
  - **Property 2: Schema Sanitizer Validity**
  - Implement test using Hypothesis with 100+ iterations
  - Verify all sanitized parameters are valid FIBO enumerations
  - **Validates: Requirements 3.1, 3.2**
  - **Commit**: "test: property-based test for schema sanitizer validity"

- [ ] 5. Product Image to Master JSON (VLM Bridge) (Previously 3)
  - Implement logic in `FiboPipelineManager` to use VLM Bridge (Image mode) to analyze a product PNG and output the Master JSON
  - Integrate with the **Schema Sanitizer (Task 4)** to clean VLM output [New]
  - Lock product parameters (geometry, aspect ratio, focal length) and save as Master JSON template
  - Support loading base product images from `images/` folder (wristwatch.png, headphones.png)
  - **Commit**: "feat: VLM bridge from image to master JSON"
  - _Requirements: 3.3, 3.4_

- [ ] 6. Localization Agent: Region Config & Guardrails (Previously 4)
  - Create `config/region_configs.py` with initial locale JSON snippets (e.g., Tokyo, Berlin, NYC).
  - Implement the **Localization Agent** class that iterates through regions and merges Master JSON with region config.
  - Implement **"Brand DNA" Guardrails** to inject negative prompts and check `forbidden_elements` based on campaign settings [New].
  - **Commit**: "feat: localization agent with region configs and brand guardrails"
  - _Requirements: 4.1, 4.2, 4.3_

- [ ] 6.1 Write property-based test for Parameter Lock Preservation
  - **Property 1: Parameter Lock Preservation**
  - Test that locked parameters remain unchanged after merge
  - Use Hypothesis to generate random Master JSONs and region configs
  - **Validates: Requirements 2.1, 4.2**
  - **Commit**: "test: property-based test for parameter lock preservation"

- [ ] 6.2 Write property-based test for Brand Guardrail Enforcement
  - **Property 5: Brand Guardrail Enforcement**
  - Test that all negative prompts are present in final JSON
  - Generate random campaign configurations with guardrails
  - **Validates: Requirements 4.3**
  - **Commit**: "test: property-based test for brand guardrail enforcement"

- [ ] 7. Batch Generation & Queue Management (Previously 5)
  - Implement `BatchProcessor` to manage the list of region-specific JSONs generated in Task 6.
  - Use a simple job queue (e.g., Python's `queue` or `asyncio`) to process generations sequentially or in parallel.
  - Implement error isolation so one region failure doesn't stop others
  - **Commit**: "feat: batch processor and generation queue established"
  - _Requirements: 4.4, 8.3_

- [ ] 7.1 Write property-based test for Batch Processing Isolation
  - **Property 9: Batch Processing Isolation**
  - Test that failures in one region don't prevent others from processing
  - Inject random failures and verify remaining regions complete
  - **Validates: Requirements 8.3**
  - **Commit**: "test: property-based test for batch processing isolation"

- [ ] 8. Core JSON-to-Image Generation (FIBO) (Previously 7)
  - Implement the core generation loop: take a region JSON, pass it to the FIBO Image Pipeline, and retrieve the 16-bit image raw data.
  - **Commit**: "feat: core FIBO JSON-to-image generation loop"
  - _Requirements: 5.1, 5.2_

- [ ] 9. Output Manager: Dual-Output Saving (Previously 8)
  - Implement the `OutputManager` to receive 16-bit raw data.
  - **Primary Output:** Save the image as **16-bit TIFF** for print [New].
  - **Secondary Output:** Downscale/convert and save as **8-bit PNG** for web preview [New].
  - Archive the final generation JSON alongside the images.
  - Implement file I/O retry logic with exponential backoff
  - **Commit**: "feat: output manager with dual 16-bit TIFF and 8-bit PNG saving"
  - _Requirements: 7.1, 7.2, 7.3, 8.4_

- [ ] 9.1 Write property-based test for Dual Output Consistency
  - **Property 3: Dual Output Consistency**
  - Test that 8-bit PNG is valid downscaled version of 16-bit TIFF
  - Verify aspect ratio and content consistency
  - **Validates: Requirements 7.1, 7.2**
  - **Commit**: "test: property-based test for dual output consistency"

- [ ] 9.2 Write property-based test for JSON Audit Completeness
  - **Property 4: JSON Audit Completeness**
  - Test that saved JSON contains Master JSON + region modifications
  - Verify valid JSON formatting with proper indentation
  - **Validates: Requirements 7.3, 7.5, 7.6**
  - **Commit**: "test: property-based test for JSON audit completeness"

- [ ] 9.3 Write property-based test for File Format Correctness
  - **Property 10: File Format Correctness**
  - Test that saved TIFF files are valid and readable
  - Use PIL/OpenCV to verify format integrity
  - **Validates: Requirements 7.1**
  - **Commit**: "test: property-based test for file format correctness"

- [ ] **10. Consistency Proof: Pixel Difference Heatmap** [New]
  - Implement image comparison logic (e.g., using OpenCV/NumPy) in `OutputManager` [New].
  - Calculate the pixel difference between the generated product cutout and the master product [New].
  - Generate a simple **visual heatmap** image and the final difference score [New].
  - Implement 5% threshold check and flagging logic
  - **Commit**: "feat: implemented product consistency proof with pixel difference heatmap"
  - _Requirements: 5.3, 5.4_

- [ ] 10.1 Write property-based test for Consistency Score Bounds
  - **Property 6: Consistency Score Bounds**
  - Test that consistency scores are always between 0.0 and 1.0
  - Generate random image pairs and verify score validity
  - **Validates: Requirements 5.3, 5.4**
  - **Commit**: "test: property-based test for consistency score bounds"

- [ ] 11. C2PA Compliance Implementation (Previously 10)
  - Integrate C2PA SDK (e.g., `c2patool`).
  - Implement logic to embed provenance data (Agent logic, Master JSON fingerprint, region) into the output file's metadata.
  - Implement error handling for C2PA signing failures
  - **Commit**: "feat: C2PA content credentials embedding"
  - _Requirements: 6.1, 6.2, 8.5_

- [ ] 11.1 Write property-based test for C2PA Provenance Completeness
  - **Property 7: C2PA Provenance Completeness**
  - Test that all required provenance data is embedded
  - Verify Master JSON fingerprint, region config, seed, timestamp
  - **Validates: Requirements 6.1, 6.2**
  - **Commit**: "test: property-based test for C2PA provenance completeness"

- [ ] 12. Error Recovery and State Management
  - Implement state saving on unrecoverable errors
  - Add recovery mechanism to resume from saved state
  - Implement comprehensive error logging with structured format
  - **Commit**: "feat: error recovery and state management"
  - _Requirements: 8.1, 8.2, 8.6_

- [ ] 12.1 Write property-based test for Error Recovery State Preservation
  - **Property 8: Error Recovery State Preservation**
  - Test that saved state contains sufficient recovery information
  - Inject random errors and verify state completeness
  - **Validates: Requirements 8.6**
  - **Commit**: "test: property-based test for error recovery state preservation"

- [ ] 13. Checkpoint: End-to-End CLI Test (Previously 11)
  - Run the entire workflow (VLM -> Sanitizer -> Agent -> FIBO -> Output) from the command line
  - Test with both base product images: `images/wristwatch.png` (default) and `images/headphones.png`
  - Verify all property-based tests pass
  - Test error recovery scenarios
  - **Commit**: "test: cli end-to-end test checkpoint"
  - _Requirements: All above_

- [ ] 14. UI Setup (Streamlit/Flask) (Previously 12)
  - Set up a basic web interface using Flask/Streamlit/FastAPI with HTML frontend
  - Implement **base product image selector** with radio buttons or dropdown for:
    - `images/wristwatch.png` (default selection)
    - `images/headphones.png`
  - Display preview of selected base product image
  - Implement file upload option for custom product images (optional)
  - Implement form handling for campaign configuration
  - **Commit**: "feat: basic UI setup with base product selector and file upload"
  - _Requirements: 9.1, 9.2_

- [ ] 15. UI: Gallery and Download Interface (Previously 13)
  - Implement a dashboard that shows the results from the `output/` directory.
  - Display the 8-bit PNG thumbnails.
  - Implement download buttons for the 16-bit TIFF, 8-bit PNG, and JSON [New].
  - **Commit**: "feat: UI gallery view and downloads"
  - _Requirements: 9.5, 9.8 (part)_

- [ ] 16. UI: Progress, Heatmap, and Variations (Previously 14)
  - Add real-time progress updates.
  - Display the **Pixel Difference Heatmap** alongside the generated image in the gallery [New].
  - Implement the **"Generate Variations"** button logic (re-run batch processor with same JSON, new seed) [New].
  - **Commit**: "feat: UI progress, heatmap, and variation generation"
  - _Requirements: 9.4, 9.5 (part), 9.7_

- [ ] 17. Compliance and Audit UI (Previously 15)
  - Display C2PA status badge.
  - Display the archived JSON, clearly differentiating locked vs. modified parameters.
  - **Commit**: "feat: C2PA status and JSON audit viewer in UI"
  - _Requirements: 9.6_

- [ ] 18. Code Quality and Final Refactor (Previously 19)
  - Write unit tests for edge cases and integration points
  - Review all code for clarity and adherence to Python standards (PEP8)
  - Ensure all error handling and logging is robust
  - Verify all 10 property-based tests pass with 100+ iterations
  - **Commit**: "chore: final code review and cleanup"
  - _Requirements: All_

- [ ] 19. Demo Video & Documentation (Previously 20)
  - Finalize the demo video script based on Hackathon Optimization section.
  - Record and edit the 3-minute submission video.
  - Write the final `README.md` and project description.
  - **Commit**: "docs: final video script and documentation complete"
  - _Requirements: Hackathon submission_

- [ ] 20. Final Submission Package (Previously 21)
  - Verify GitHub repository is public and well-organized.
  - Ensure README has clear setup instructions.
  - Add LICENSE file (MIT or Apache 2.0).
  - Tag final version: `git tag v1.0-hackathon-submission`.
  - Push all commits and tags to GitHub.
  - Prepare Devpost submission text.
  - Submit to hackathon with:
    - Category selection (Best Overall + Best JSON-Native or Agentic Workflow)
    - Project description
    - Demo video link
    - GitHub repository link
    - Screenshots and sample outputs
  - **Commit**: "chore: final submission package complete"
  - _Requirements: Hackathon submission_

---

## Notes

- All tasks including property-based tests are required for comprehensive quality
- **10 Correctness Properties** are defined in the design document, each with a corresponding property-based test
- **Checkpoints (tasks 13, 18) are critical validation points**
- Property-based tests use Hypothesis with minimum 100 iterations
- Each property test references its design document property using format: `# Feature: global-brand-localizer, Property X: [text]`
- Demo preparation (task 19) should start early to allow time for refinement
- Keep commits atomic and descriptive for judges to review

## Base Product Images

The system includes two pre-configured base product images in the `images/` folder:
- **`images/wristwatch.png`** - Default selection (luxury wristwatch with green leather strap)
- **`images/headphones.png`** - Alternative option (premium over-ear headphones)

Users can select either base image via the UI, or optionally upload their own custom product image. The wristwatch is selected by default for demo purposes.

## Property-Based Test Summary

The following properties are tested throughout implementation:
1. **Property 1**: Parameter Lock Preservation (Task 6.1)
2. **Property 2**: Schema Sanitizer Validity (Task 4.1)
3. **Property 3**: Dual Output Consistency (Task 9.1)
4. **Property 4**: JSON Audit Completeness (Task 9.2)
5. **Property 5**: Brand Guardrail Enforcement (Task 6.2)
6. **Property 6**: Consistency Score Bounds (Task 10.1)
7. **Property 7**: C2PA Provenance Completeness (Task 11.1)
8. **Property 8**: Error Recovery State Preservation (Task 12.1)
9. **Property 9**: Batch Processing Isolation (Task 7.1)
10. **Property 10**: File Format Correctness (Task 9.3)

## Estimated Timeline

- Days 1-2: Tasks 1-5 (Setup, Pipelines, API Fallback, Sanitizer + Tests, Master JSON)
- Days 3-4: Tasks 6-9 (Localization Agent + Tests, Batch + Tests, Generation, Output Manager + Tests)
- Days 5-6: Tasks 10-13 (Consistency Proof + Tests, C2PA + Tests, Error Recovery + Tests, End-to-End Checkpoint)
- Days 7-8: Tasks 14-17 (Full UI Implementation)
- Days 9-11: Tasks 18-20 (Code Quality, Video, Final Submission)