"""AI Image Generation App Integration

Provides a wrapper service for integrating AI image generation into the recipe app.
Handles logging, error handling, app-specific configuration, and background processing.
"""

from typing import List, Optional
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal

from .config import ImageGenConfig
from .service import ImageGenService, ImagePairPaths
from dev_tools import DebugLogger


class ImageGenWorker(QObject):
    """Worker thread for AI image generation to prevent UI blocking."""
    
    # Signals
    finished = Signal(object)  # Emits ImagePairPaths or None
    error = Signal(str)       # Emits error message
    
    def __init__(self, service: ImageGenService, recipe_name: str):
        super().__init__()
        self.service = service
        self.recipe_name = recipe_name
    
    def run(self):
        """Run the image generation in background thread."""
        try:
            DebugLogger().log(f"Starting background image generation for '{self.recipe_name}'", "info")
            result = self.service.generate_for_recipe(self.recipe_name)
            DebugLogger().log(f"Background image generation completed for '{self.recipe_name}'", "info")
            self.finished.emit(result)
        except Exception as e:
            error_msg = f"Failed to generate images for '{self.recipe_name}': {e}"
            DebugLogger().log(error_msg, "error")
            self.error.emit(error_msg)


class AppImageGenService(QObject):
    """App-integrated AI image generation service.
    
    Provides a clean interface for the app to generate recipe images with:
    - Proper logging integration
    - Error handling with fallbacks
    - App-specific configuration
    - Background processing to prevent UI blocking
    """
    
    # Signals for async operations
    generation_finished = Signal(str, object)  # recipe_name, ImagePairPaths or None
    generation_failed = Signal(str, str)       # recipe_name, error_message
    
    def __init__(self):
        """Initialize the service with app-specific configuration."""
        super().__init__()
        # Load environment variables from .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()  # Load .env file if it exists
            DebugLogger().log("Loaded .env file", "debug")
        except ImportError:
            DebugLogger().log("python-dotenv not installed, using system environment only", "warning")
        
        # Check for API key
        import os
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            DebugLogger().log("OPENAI_API_KEY not found in environment variables", "error")
            DebugLogger().log("Make sure OPENAI_API_KEY is set in your .env file or environment", "error")
            self.service = None
            return
        else:
            DebugLogger().log(f"Found OPENAI_API_KEY (length: {len(api_key)})", "debug")
        
        self.config = ImageGenConfig(
            portrait_size="1024x1024",  # Square for recipe cards
            banner_size="1536x1024",   # Banner for full recipe view
            allow_overwrite=False,     # Don't regenerate existing images
            quality="standard"         # Balance cost vs quality
        )
        
        DebugLogger().log(f"Config output directory: {self.config.output_dir()}", "debug")
        
        try:
            self.service = ImageGenService(self.config)
            DebugLogger().log("AI Image Generation Service initialized successfully", "info")
        except Exception as e:
            DebugLogger().log(f"Failed to initialize AI Image Generation Service: {e}", "error")
            # Log more details about the failure
            import traceback
            DebugLogger().log(f"Full traceback: {traceback.format_exc()}", "debug")
            self.service = None
    
    def generate_recipe_images_async(self, recipe_name: str):
        """Generate both portrait and banner images for a recipe in background thread.
        
        Args:
            recipe_name: Name of the recipe to generate images for
            
        Emits:
            generation_finished(recipe_name, ImagePairPaths) on success
            generation_failed(recipe_name, error_message) on failure
        """
        if not self.service:
            error_msg = "AI Image Generation Service not available"
            DebugLogger().log(error_msg, "error")
            self.generation_failed.emit(recipe_name, error_msg)
            return
            
        if not recipe_name or not recipe_name.strip():
            error_msg = "Cannot generate images: recipe name is empty"
            DebugLogger().log(error_msg, "warning")
            self.generation_failed.emit(recipe_name, error_msg)
            return
            
        recipe_name = recipe_name.strip()
        DebugLogger().log(f"Starting async AI image generation for recipe: '{recipe_name}'", "info")
        
        # Create worker and thread
        self.worker = ImageGenWorker(self.service, recipe_name)
        self.thread = QThread()
        
        # Move worker to thread
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda result: self._on_generation_finished(recipe_name, result))
        self.worker.error.connect(lambda error: self._on_generation_error(recipe_name, error))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Start the thread
        self.thread.start()
        
    def _on_generation_finished(self, recipe_name: str, result: Optional[ImagePairPaths]):
        """Handle successful image generation."""
        if result:
            DebugLogger().log(
                f"Successfully generated images for '{recipe_name}':\n"
                f"  • Portrait: {result.portrait_path.name}\n" 
                f"  • Banner: {result.banner_path.name}",
                "info"
            )
            # TODO: Add toast notification for success
            self.generation_finished.emit(recipe_name, result)
        else:
            error_msg = "Generation completed but returned no result"
            DebugLogger().log(f"Failed to generate images for '{recipe_name}': {error_msg}", "error")
            self.generation_failed.emit(recipe_name, error_msg)
    
    def _on_generation_error(self, recipe_name: str, error_msg: str):
        """Handle image generation error."""
        DebugLogger().log(f"Failed to generate images for '{recipe_name}': {error_msg}", "error")
        # TODO: Add toast notification for errors
        self.generation_failed.emit(recipe_name, error_msg)
    
    def get_existing_images(self, recipe_name: str) -> Optional[ImagePairPaths]:
        """Check if images already exist for a recipe.
        
        Args:
            recipe_name: Name of the recipe to check
            
        Returns:
            ImagePairPaths if images exist, None otherwise
        """
        if not self.service or not recipe_name:
            return None
            
        try:
            portrait_path, banner_path = self.service._target_paths(recipe_name.strip())
            
            if portrait_path.exists() and banner_path.exists():
                DebugLogger().log(f"Found existing images for '{recipe_name}'", "debug")
                return ImagePairPaths(portrait_path=portrait_path, banner_path=banner_path)
                
        except Exception as e:
            DebugLogger().log(f"Error checking existing images for '{recipe_name}': {e}", "warning")
            
        return None
    
    def is_available(self) -> bool:
        """Check if the AI image generation service is available."""
        return self.service is not None