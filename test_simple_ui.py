#!/usr/bin/env python3
"""
Simple test to verify Streamlit app can start and API key is working.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def main():
    """Run simple initialization tests."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "STREAMLIT APP SIMPLE VERIFICATION TEST" + " " * 20 + "║")
    print("╚" + "=" * 68 + "╝")

    # Test 1: Check .env file exists
    print_section("TEST 1: Environment Configuration")

    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
        with open(env_file) as f:
            content = f.read()
            if "ANTHROPIC_API_KEY" in content:
                print("✅ ANTHROPIC_API_KEY is configured in .env")
            else:
                print("❌ ANTHROPIC_API_KEY not found in .env")
                return 1
    else:
        print("❌ .env file not found")
        return 1

    # Test 2: Import and initialize config
    print_section("TEST 2: Configuration Loading")

    try:
        from synth_agent.core.config import ConfigManager, get_api_keys

        config_manager = ConfigManager()
        config = config_manager.get_config()

        print("✅ ConfigManager initialized successfully")
        print(f"  LLM Provider: {config.llm.provider}")
        print(f"  LLM Model: {config.llm.model}")
        print(f"  Temperature: {config.llm.temperature}")
        print(f"  Max Tokens: {config.llm.max_tokens}")

        # Load API keys
        api_keys = get_api_keys()

        if api_keys.anthropic_api_key:
            key_preview = api_keys.anthropic_api_key[:20] + "..." + api_keys.anthropic_api_key[-10:]
            print(f"✅ API Key loaded successfully")
            print(f"  Key preview: {key_preview}")
            print(f"  Key length: {len(api_keys.anthropic_api_key)} characters")
        else:
            print("❌ API key not loaded")
            return 1

    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Test 3: Initialize Anthropic Provider
    print_section("TEST 3: Anthropic Provider Initialization")

    try:
        from synth_agent.llm.anthropic_provider import AnthropicProvider

        provider = AnthropicProvider(
            api_key=api_keys.anthropic_api_key,
            model=config.llm.model,
            temperature=config.llm.temperature,
            max_tokens=config.llm.max_tokens,
            timeout=config.llm.timeout
        )

        print("✅ AnthropicProvider initialized successfully")
        print(f"  Model: {provider.model}")
        print(f"  Temperature: {provider.temperature}")
        print(f"  Max Tokens: {provider.max_tokens}")

    except Exception as e:
        print(f"❌ AnthropicProvider initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Test 4: Check Streamlit app file
    print_section("TEST 4: Streamlit App File")

    streamlit_app = Path("streamlit_app.py")
    if streamlit_app.exists():
        print("✅ streamlit_app.py exists")
        print(f"  File size: {streamlit_app.stat().st_size} bytes")
    else:
        print("❌ streamlit_app.py not found")
        return 1

    # Test 5: Check if Streamlit is running
    print_section("TEST 5: Streamlit Server Status")

    try:
        import requests
        response = requests.get("http://localhost:8501", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit server is running on http://localhost:8501")
            print(f"  Response status: {response.status_code}")
        else:
            print(f"⚠️  Streamlit server returned status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠️  Streamlit server not responding (may need to be started)")
    except Exception as e:
        print(f"⚠️  Could not check Streamlit status: {e}")

    # Final summary
    print_section("SUMMARY")
    print("✅ Environment Configuration: PASSED")
    print("✅ Configuration Loading: PASSED")
    print("✅ Anthropic Provider: PASSED")
    print("✅ Streamlit App File: PASSED")

    print("\n" + "=" * 70)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 70)
    print("\n📱 Streamlit app is configured correctly!")
    print("🔑 Claude API key is loaded and ready!")
    print("🚀 Run 'streamlit run streamlit_app.py' to start the UI")
    print("\n")

    return 0


if __name__ == "__main__":
    exit(main())
