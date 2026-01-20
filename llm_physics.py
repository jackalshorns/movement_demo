"""
LLM Physics Customization Module

Translates natural language descriptions into physics slider values using Claude.
Example: "floaty moon gravity" → {gravity: 0.3, falling_gravity: 0.4, jump_force: 16}
"""

import os
import json
import threading
from typing import Optional, Callable

# Anthropic API - lazy import to avoid startup cost if not used
_anthropic = None
_client = None


def _init_anthropic():
    """Initialize Anthropic API client (lazy load)."""
    global _anthropic, _client
    if _client is not None:
        return True
    
    try:
        import anthropic
        _anthropic = anthropic
        
        # Load .env file if it exists
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass  # dotenv not required if env var already set
        
        # Get API key from environment
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("[LLM] Warning: No ANTHROPIC_API_KEY found in environment or .env file")
            return False
        
        _client = anthropic.Anthropic(api_key=api_key)
        return True
    except ImportError:
        print("[LLM] Warning: anthropic not installed. Run: pip install anthropic")
        return False
    except Exception as e:
        print(f"[LLM] Error initializing Anthropic: {e}")
        return False


# System prompt teaching the LLM about physics parameters
SYSTEM_PROMPT = """You are a physics translator for a 2D platformer game. Convert natural language descriptions into specific physics values.

Available parameters and their ranges:
- gravity: 0.1 to 2.0 (lower = floatier, higher = heavier. Default ~0.6)
- falling_gravity: 0.1 to 2.5 (gravity when falling. Often higher than rising gravity. Default ~1.0)
- walk_speed: 1.0 to 12.0 (horizontal movement speed. Default ~4-5)
- acceleration: 0.05 to 2.5 (how fast to reach max speed. Low = slippery/ice, High = snappy. Default ~0.3-0.5)
- jump_force: 5.0 to 20.0 (initial jump velocity. Higher = higher jumps. Default ~14)

Semantic mappings:
- "floaty", "moon", "space" → low gravity (0.2-0.4), low falling_gravity
- "heavy", "weighty", "chunky" → high gravity (0.8-1.2)
- "slippery", "ice", "skating" → low acceleration (0.1-0.2)
- "snappy", "responsive", "tight" → high acceleration (1.5-2.0)
- "fast", "speedy" → high walk_speed (8-10)
- "slow", "sluggish" → low walk_speed (2-3)
- "bouncy", "spring" → high jump_force (16-18)
- "grounded", "low jump" → low jump_force (8-10)

RESPOND WITH ONLY A JSON OBJECT. No markdown, no explanation. Example:
{"gravity": 0.4, "falling_gravity": 0.5, "walk_speed": 5.0, "acceleration": 0.3, "jump_force": 15.0}

Only include parameters that should change based on the description. Omit unchanged parameters."""


def process_description(
    description: str,
    callback: Optional[Callable[[dict, Optional[str]], None]] = None
) -> Optional[dict]:
    """
    Process a natural language description and return physics values.
    
    Args:
        description: User's natural language input (e.g., "floaty moon gravity")
        callback: Optional callback(result_dict, error_string) for async usage
        
    Returns:
        Dict of physics values, or None if async (uses callback)
    """
    if callback:
        # Async mode - run in background thread
        thread = threading.Thread(
            target=_process_async,
            args=(description, callback),
            daemon=True
        )
        thread.start()
        return None
    else:
        # Sync mode
        return _process_sync(description)


def _process_sync(description: str) -> dict:
    """Synchronous processing (blocks)."""
    if not _init_anthropic():
        return {"error": "Anthropic API not available"}
    
    try:
        message = _client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": f"Physics description: {description}"}
            ]
        )
        response_text = message.content[0].text
        return _parse_response(response_text)
    except Exception as e:
        print(f"[LLM] Error: {e}")
        return {"error": str(e)}


def _process_async(description: str, callback: Callable):
    """Async processing in background thread."""
    result = _process_sync(description)
    if "error" in result:
        callback(None, result["error"])
    else:
        callback(result, None)


def _parse_response(text: str) -> dict:
    """Parse LLM response into physics dict."""
    # Clean up response - remove markdown code blocks if present
    text = text.strip()
    if text.startswith("```"):
        # Remove ```json and ``` markers
        lines = text.split("\n")
        text = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
    
    try:
        data = json.loads(text)
        
        # Validate and clamp values
        valid_params = {
            "gravity": (0.1, 2.0),
            "falling_gravity": (0.1, 2.5),
            "walk_speed": (1.0, 12.0),
            "acceleration": (0.05, 2.5),
            "jump_force": (5.0, 20.0),
        }
        
        result = {}
        for key, (min_val, max_val) in valid_params.items():
            if key in data:
                val = float(data[key])
                result[key] = max(min_val, min(max_val, val))
        
        return result
    except json.JSONDecodeError as e:
        print(f"[LLM] JSON parse error: {e}")
        print(f"[LLM] Raw response: {text}")
        return {"error": f"Failed to parse response: {e}"}


def apply_physics(profile, physics_dict: dict, ui_panel=None):
    """
    Apply physics values to a CharacterProfile.
    
    Args:
        profile: CharacterProfile instance to modify
        physics_dict: Dict of parameter names to values
        ui_panel: Optional ControlPanel to refresh sliders
    """
    if "error" in physics_dict:
        print(f"[LLM] Cannot apply physics: {physics_dict['error']}")
        return False
    
    for key, value in physics_dict.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
            print(f"[LLM] Set {key} = {value:.2f}")
    
    # Refresh UI sliders if provided
    if ui_panel:
        ui_panel.create_sliders()
    
    return True


# Convenience function for testing
def test_llm():
    """Test the LLM integration."""
    test_cases = [
        "floaty moon gravity",
        "super slippery ice physics",
        "heavy and slow like a tank",
        "bouncy and responsive like Celeste",
    ]
    
    for desc in test_cases:
        print(f"\n>>> '{desc}'")
        result = process_description(desc)
        print(f"    Result: {result}")


if __name__ == "__main__":
    test_llm()
