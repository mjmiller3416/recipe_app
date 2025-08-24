"""tools/imagegen_demo.py
Quick demo runner so you can test without touching your main app.

Run:
    set OPENAI_API_KEY=sk-...   (Windows)
    export OPENAI_API_KEY=sk-... (macOS/Linux)

    python tools/imagegen_demo.py
"""

from __future__ import annotations

import sys
import threading
import time

from dotenv import load_dotenv

from config import ImageGenConfig
from service import ImageGenService


class LoadingIndicator:
    """Animated loading indicator for terminal output."""

    def __init__(self, message="Processing", delay=0.5):
        self.message = message
        self.delay = delay
        self.running = False
        self.thread = None

    def start(self):
        """Start the animated loading indicator."""
        self.running = True
        self.thread = threading.Thread(target=self._animate)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        """Stop the animated loading indicator."""
        self.running = False
        if self.thread:
            self.thread.join()
        # Clear the line
        sys.stdout.write('\r' + ' ' * (len(self.message) + 10) + '\r')
        sys.stdout.flush()

    def _animate(self):
        """Animation loop with rotating dots."""
        dots = ['', '.', '..', '...']
        i = 0
        while self.running:
            sys.stdout.write(f'\r{self.message}{dots[i % len(dots)]}')
            sys.stdout.flush()
            time.sleep(self.delay)
            i += 1


def main() -> None:
    load_dotenv() # Load environment variables from .env file

    cfg = ImageGenConfig(
        # Tweak these freely:
        portrait_size="1024x1024",
        banner_size="1536x1024",
        allow_overwrite=False,
        # Example: adjust prompt template here if you want a consistent brand style
        prompt_template=(
            "Appetizing, realistic food photo of {recipe_name}. "
            "Brand style: clean, modern, natural props, subtle depth-of-field, no text."
        ),
    )

    svc = ImageGenService(cfg)

    # Hard-code some names while you iterate:
    recipes = [
        "Chicken Parmesan",
        "Creamy Mushroom Risotto",
        "BBQ Pulled Pork Sandwich",
    ]

    print(f"🎨 Starting AI image generation for {len(recipes)} recipes...")
    print(f"📁 Output directory: {cfg.output_dir()}")
    print(f"🤖 Using model: {cfg.model}")
    print()

    for i, name in enumerate(recipes, 1):
        print(f"[{i}/{len(recipes)}] {name}")

        # Check if files already exist
        portrait_path, banner_path = svc._target_paths(name)
        if not cfg.allow_overwrite and portrait_path.exists() and banner_path.exists():
            print(f"  ✅ Images already exist, skipping...")
            print(f"     • {portrait_path}")
            print(f"     • {banner_path}")
            print()
            continue

        # Generate with animated loading indicator
        loader = LoadingIndicator(f"  🎨 Generating images for '{name}'", delay=0.4)
        loader.start()

        try:
            pair = svc.generate_for_recipe(name)
            loader.stop()

            print(f"  ✅ Generated successfully!")
            print(f"     • Portrait: {pair.portrait_path.name}")
            print(f"     • Banner: {pair.banner_path.name}")

        except KeyboardInterrupt:
            loader.stop()
            print(f"  ❌ Interrupted by user")
            print("\n🛑 Process stopped by user")
            break

        except Exception as e:
            loader.stop()
            print(f"  ❌ Error: {e}")

        print()

    print("🎉 Image generation complete!")


if __name__ == "__main__":
    main()
