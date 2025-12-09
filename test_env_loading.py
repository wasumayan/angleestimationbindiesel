#!/usr/bin/env python3
"""
Quick test to verify .env file is loaded correctly for OpenAI API key
"""

import os
from dotenv import load_dotenv

print("=" * 70)
print("Testing .env File Loading")
print("=" * 70)
print()

# Load .env file
print("[1] Loading .env file...")
load_dotenv()
print("✓ load_dotenv() called")
print()

# Check if key exists
print("[2] Checking OPENAI_API_KEY...")
api_key = os.getenv('OPENAI_API_KEY')

if api_key:
    # Show first and last 4 characters for verification (don't expose full key)
    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
    print(f"✓ OPENAI_API_KEY found: {masked_key}")
    print(f"  Full length: {len(api_key)} characters")
else:
    print("✗ OPENAI_API_KEY NOT FOUND in environment!")
    print("  Make sure .env file exists and contains: OPENAI_API_KEY=your_key_here")
    print()
    exit(1)

print()

# Test VoiceRecognizer initialization
print("[3] Testing VoiceRecognizer initialization...")
try:
    from voice_recognizer import VoiceRecognizer
    
    # Don't pass api_key - let it load from .env
    recognizer = VoiceRecognizer()
    print("✓ VoiceRecognizer initialized successfully!")
    print(f"  Model: {recognizer.model}")
    print(f"  API Key loaded: {'Yes' if recognizer.api_key else 'No'}")
    
    if recognizer.api_key:
        masked_key = f"{recognizer.api_key[:8]}...{recognizer.api_key[-4:]}" if len(recognizer.api_key) > 12 else "***"
        print(f"  API Key: {masked_key}")
    
    print()
    print("[4] Testing OpenAI API connection...")
    # Test a simple API call
    if recognizer.client:
        try:
            # Make a minimal test call to verify API key works
            response = recognizer.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a test assistant."},
                    {"role": "user", "content": "Say 'test'"}
                ],
                max_tokens=5
            )
            result = response.choices[0].message.content.strip()
            print(f"✓ OpenAI API connection successful!")
            print(f"  Test response: '{result}'")
            print()
            print("=" * 70)
            print("✅ ALL TESTS PASSED!")
            print("=" * 70)
            print("Your .env file is loaded correctly and OpenAI API key works!")
        except Exception as e:
            print(f"✗ OpenAI API test failed: {e}")
            print()
            print("Possible issues:")
            print("  1. API key is invalid or expired")
            print("  2. No internet connection")
            print("  3. OpenAI API is down")
            print("  4. Account has no credits")
    else:
        print("✗ OpenAI client not initialized")
    
    recognizer.cleanup()
    
except ValueError as e:
    print(f"✗ Error: {e}")
    print()
    print("Make sure your .env file contains:")
    print("  OPENAI_API_KEY=your_actual_key_here")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

print()


