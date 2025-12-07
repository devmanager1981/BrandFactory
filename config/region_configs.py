"""
Region Configurations for Global Brand Localizer

Pre-defined locale configurations for different global markets.
Each region specifies environment overrides and cultural context.
"""

from typing import Dict, Any, List


# Pre-defined region configurations
REGION_CONFIGS: Dict[str, Dict[str, Any]] = {
    "tokyo_subway": {
        "region_id": "tokyo_subway",
        "display_name": "Tokyo Subway Poster",
        "locale": "ja-JP",
        "environment_overrides": {
            "background_setting": "Busy Tokyo subway station with neon signs and modern architecture",
            "lighting": {
                "conditions": "neon_ambient",
                "direction": "mixed artificial lighting from multiple sources",
                "shadows": "minimal shadows due to ambient neon glow"
            },
            "aesthetics": {
                "color_scheme": "vibrant blues, pinks, and electric colors",
                "mood_atmosphere": "energetic, urban, futuristic"
            }
        },
        "cultural_context": {
            "color_preferences": ["blue", "white", "red"],
            "avoid_elements": ["number_4"]  # Cultural sensitivity - 4 sounds like "death"
        }
    },
    
    "berlin_billboard": {
        "region_id": "berlin_billboard",
        "display_name": "Berlin Street Billboard",
        "locale": "de-DE",
        "environment_overrides": {
            "background_setting": "Modern Berlin street with minimalist architecture and clean lines",
            "lighting": {
                "conditions": "natural_sunlight",
                "direction": "soft daylight from above",
                "shadows": "clean, defined shadows"
            },
            "aesthetics": {
                "color_scheme": "monochromatic with bold accent colors",
                "mood_atmosphere": "sophisticated, minimalist, modern"
            }
        },
        "cultural_context": {
            "color_preferences": ["black", "white", "red", "yellow"],
            "avoid_elements": []
        }
    },
    
    "nyc_times_square": {
        "region_id": "nyc_times_square",
        "display_name": "NYC Times Square Digital Display",
        "locale": "en-US",
        "environment_overrides": {
            "background_setting": "Iconic Times Square with bright digital billboards and urban energy",
            "lighting": {
                "conditions": "high_contrast_key_light",
                "direction": "dramatic lighting from multiple angles",
                "shadows": "strong, dynamic shadows"
            },
            "aesthetics": {
                "color_scheme": "bold primary colors with high contrast",
                "mood_atmosphere": "dynamic, bold, attention-grabbing"
            }
        },
        "cultural_context": {
            "color_preferences": ["red", "blue", "yellow", "white"],
            "avoid_elements": []
        }
    },
    
    "dubai_mall": {
        "region_id": "dubai_mall",
        "display_name": "Dubai Luxury Mall Display",
        "locale": "ar-AE",
        "environment_overrides": {
            "background_setting": "Luxurious Dubai mall interior with marble and gold accents",
            "lighting": {
                "conditions": "studio_lighting",
                "direction": "elegant overhead lighting with warm tones",
                "shadows": "soft, luxurious shadows"
            },
            "aesthetics": {
                "color_scheme": "gold, cream, deep blues, and rich purples",
                "mood_atmosphere": "luxurious, elegant, premium"
            }
        },
        "cultural_context": {
            "color_preferences": ["gold", "white", "blue", "green"],
            "avoid_elements": []
        }
    },
    
    "sydney_beach": {
        "region_id": "sydney_beach",
        "display_name": "Sydney Beach Lifestyle Ad",
        "locale": "en-AU",
        "environment_overrides": {
            "background_setting": "Bright Sydney beach scene with ocean and blue sky",
            "lighting": {
                "conditions": "golden_hour",
                "direction": "warm sunlight from the side",
                "shadows": "soft, warm shadows"
            },
            "aesthetics": {
                "color_scheme": "ocean blues, sandy yellows, bright whites",
                "mood_atmosphere": "relaxed, sunny, lifestyle-focused"
            }
        },
        "cultural_context": {
            "color_preferences": ["blue", "yellow", "white", "green"],
            "avoid_elements": []
        }
    },
    
    "paris_metro": {
        "region_id": "paris_metro",
        "display_name": "Paris Metro Station Poster",
        "locale": "fr-FR",
        "environment_overrides": {
            "background_setting": "Classic Parisian metro station with art nouveau styling",
            "lighting": {
                "conditions": "soft_natural",
                "direction": "romantic, diffused lighting",
                "shadows": "subtle, artistic shadows"
            },
            "aesthetics": {
                "color_scheme": "classic French palette - navy, cream, burgundy",
                "mood_atmosphere": "elegant, romantic, timeless"
            }
        },
        "cultural_context": {
            "color_preferences": ["navy", "cream", "burgundy", "gold"],
            "avoid_elements": []
        }
    },
    
    "london_tube": {
        "region_id": "london_tube",
        "display_name": "London Underground Poster",
        "locale": "en-GB",
        "environment_overrides": {
            "background_setting": "London Underground station with iconic roundel signage",
            "lighting": {
                "conditions": "studio_lighting",
                "direction": "clean, professional lighting",
                "shadows": "minimal, professional shadows"
            },
            "aesthetics": {
                "color_scheme": "British red, navy blue, and white",
                "mood_atmosphere": "professional, classic, trustworthy"
            }
        },
        "cultural_context": {
            "color_preferences": ["red", "navy", "white"],
            "avoid_elements": []
        }
    }
}


def get_region_config(region_id: str) -> Dict[str, Any]:
    """
    Get configuration for a specific region.
    
    Args:
        region_id: Region identifier (e.g., 'tokyo_subway')
    
    Returns:
        Region configuration dictionary
    
    Raises:
        KeyError: If region_id not found
    """
    if region_id not in REGION_CONFIGS:
        raise KeyError(f"Region '{region_id}' not found. Available regions: {list(REGION_CONFIGS.keys())}")
    
    return REGION_CONFIGS[region_id]


def get_all_region_ids() -> List[str]:
    """
    Get list of all available region IDs.
    
    Returns:
        List of region identifiers
    """
    return list(REGION_CONFIGS.keys())


def get_all_regions() -> Dict[str, Dict[str, Any]]:
    """
    Get all region configurations.
    
    Returns:
        Dictionary of all region configurations
    """
    return REGION_CONFIGS.copy()
