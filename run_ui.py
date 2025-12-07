#!/usr/bin/env python3
"""
Launcher script for Global Brand Localizer Streamlit UI
"""

import subprocess
import sys
from pathlib import Path

def main():
    """Launch the Streamlit UI."""
    ui_path = Path("src/ui/streamlit_app.py")
    
    if not ui_path.exists():
        print(f"❌ Error: UI file not found at {ui_path}")
        return 1
    
    print("🚀 Launching Global Brand Localizer UI...")
    print("📍 Open your browser to: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the server\n")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(ui_path),
            "--server.port=8501",
            "--server.headless=true"
        ])
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down UI server...")
        return 0
    except Exception as e:
        print(f"❌ Error launching UI: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
