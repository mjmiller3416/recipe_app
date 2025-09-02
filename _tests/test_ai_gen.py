#!/usr/bin/env python3
"""
Simple terminal-based test app for AI image generation package.

Tests recipe image generation with animated loading indicator.
"""

import asyncio
import sys
import threading
import time
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Add the app directory to sys.path for imports
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.services.ai_gen import create_recipe_service


class SpinnerAnimation:
    """Simple terminal spinner animation."""

    def __init__(self, message="Generating"):
        self.message = message
        self.spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        self.running = False
        self.thread = None

    def start(self):
        """Start the spinner animation."""
        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.start()

    def stop(self):
        """Stop the spinner animation."""
        self.running = False
        if self.thread:
            self.thread.join()
        # Clear the line
        print("\r" + " " * 50 + "\r", end="", flush=True)

    def _animate(self):
        """Animation loop."""
        idx = 0
        while self.running:
            char = self.spinner_chars[idx % len(self.spinner_chars)]
            print(f"\r{char} {self.message}...", end="", flush=True)
            time.sleep(0.1)
            idx += 1


async def test_recipe_generation(recipe_name: str, image_type: str = "standard", mock_mode: bool = False):
    """Test recipe image generation with animation."""

    mode_label = "MOCK" if mock_mode else "REAL"
    print(f"\n🧪 Testing AI Image Generation ({mode_label} MODE)")
    print(f"Recipe: {recipe_name}")
    print(f"Type: {image_type}")
    print("-" * 40)

    # Start spinner
    spinner_msg = "Generating mock image" if mock_mode else "Generating AI image"
    spinner = SpinnerAnimation(spinner_msg)

    try:
        # Create the service
        print("🔧 Initializing AI service...")
        service = create_recipe_service(mock_mode=mock_mode)

        # Start generation
        spinner.start()
        start_time = time.time()

        # Generate the image
        image_path = await service.generate_for_recipe(recipe_name, image_type)

        # Stop spinner
        spinner.stop()
        end_time = time.time()

        # Success message
        print(f"✅ Success! Image generated in {end_time - start_time:.1f}s")
        print(f"📁 Saved to: {image_path}")
        print(f"📏 File size: {image_path.stat().st_size / 1024:.1f} KB")

        return True

    except Exception as e:
        spinner.stop()
        print(f"❌ Error: {str(e)}")
        return False


async def test_batch_generation(recipe_name: str, mock_mode: bool = False):
    """Test generating both standard and banner images."""

    mode_label = "MOCK" if mock_mode else "REAL"
    print(f"\n🧪 Testing Batch Generation ({mode_label} MODE)")
    print(f"Recipe: {recipe_name}")
    print("-" * 40)

    # Start spinner
    spinner_msg = "Generating mock images" if mock_mode else "Generating both images"
    spinner = SpinnerAnimation(spinner_msg)

    try:
        # Create the service
        print("🔧 Initializing AI service...")
        service = create_recipe_service(mock_mode=mock_mode)

        # Start generation
        spinner.start()
        start_time = time.time()

        # Generate both images
        paths = await service.generate_both_for_recipe(recipe_name)

        # Stop spinner
        spinner.stop()
        end_time = time.time()

        # Success message
        print(f"✅ Success! Both images generated in {end_time - start_time:.1f}s")
        print(f"📁 Standard: {paths.standard}")
        print(f"📁 Banner: {paths.banner}")

        return True

    except Exception as e:
        spinner.stop()
        print(f"❌ Error: {str(e)}")
        return False


def get_recipe_input():
    """Get recipe name from user input."""
    while True:
        recipe_name = input("\n🍳 Enter recipe name (or 'quit' to exit): ").strip()

        if recipe_name.lower() == 'quit':
            return None

        if recipe_name:
            return recipe_name

        print("❌ Please enter a valid recipe name.")


def main():
    """Main test application."""

    print("=" * 50)
    print("🤖 AI Image Generation Test App")
    print("=" * 50)
    print("\nThis app will test your AI image generation package.")
    print("Make sure your OPENAI_API_KEY is set in your environment.")

    while True:
        recipe_name = get_recipe_input()

        if recipe_name is None:
            break

        # Show options
        print(f"\n📋 Test options for '{recipe_name}':")
        print("1. Generate standard image (REAL)")
        print("2. Generate both images - sequential workflow (REAL)")
        print("3. Generate standard image (MOCK)")
        print("4. Generate both images - sequential workflow (MOCK)")
        print("5. Enter new recipe name")

        choice = input("\n🔢 Choose option (1-5): ").strip()

        try:
            if choice == "1":
                asyncio.run(test_recipe_generation(recipe_name, "standard", mock_mode=False))
            elif choice == "2":
                asyncio.run(test_batch_generation(recipe_name, mock_mode=False))
            elif choice == "3":
                asyncio.run(test_recipe_generation(recipe_name, "standard", mock_mode=True))
            elif choice == "4":
                asyncio.run(test_batch_generation(recipe_name, mock_mode=True))
            elif choice == "5":
                continue
            else:
                print("❌ Invalid choice. Please select 1-5.")
                continue

        except KeyboardInterrupt:
            print("\n\n⏹️  Interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")

    print("\n👋 Thanks for testing! Goodbye.")


if __name__ == "__main__":
    main()
