QFluentWidgets' Design Pattern

  Key Insights:
  1. Global StyleSheet Manager (styleSheetManager) - Singleton that tracks all styled widgets
  2. Enum-based Stylesheets (FluentStyleSheet.BUTTON) - Each widget type maps to a stylesheet
  3. Auto-apply in Constructor (FluentStyleSheet.BUTTON.apply(self)) - Line 31 in button.py
  4. Centralized Updates (updateStyleSheet()) - Updates all registered widgets at once
  5. Lazy Loading - Only updates visible widgets for performance

  Proposed Rework for Your Theme Manager

  class ThemeManager(QSingleton):
      """Redesigned theme manager with global and per-widget styling"""

      theme_refresh = Signal(dict)

      # Global stylesheet cache
      _global_stylesheet_cache: str = ""
      _widget_stylesheet_cache: Dict[type, str] = {}

      # Widget registries
      _widget_class_registry: Dict[type, Qss] = {}
      _widget_instance_registry = weakref.WeakKeyDictionary()

      def __init__(self):
          super().__init__()
          self._theme_color = None
          self._theme_mode = None
          self._current_color_map = {}

      # ── STARTUP METHODS ──
      @classmethod
      def preloadTheme(cls, color: Color, mode: Mode):
          """Pre-process all stylesheets during splash screen"""
          instance = cls._get_instance()
          instance._theme_color = color
          instance._theme_mode = mode
          instance._current_color_map = Stylesheet.generate_material_palette(color, mode)

          # 1. Cache global stylesheet
          base_content = Stylesheet.read(Qss.BASE)
          instance._global_stylesheet_cache = Stylesheet.inject_theme(
              base_content, instance._current_color_map
          )

          # 2. Cache all widget stylesheets
          for widget_class, qss_enum in cls._widget_class_registry.items():
              stylesheet_content = Stylesheet.read(qss_enum)
              if stylesheet_content:
                  processed_stylesheet = Stylesheet.inject_theme(
                      stylesheet_content, instance._current_color_map
                  )
                  cls._widget_stylesheet_cache[widget_class] = processed_stylesheet

          # 3. Apply global stylesheet
          app = QApplication.instance()
          app.setStyleSheet(instance._global_stylesheet_cache)

          DebugLogger.log("Theme preloaded and applied globally", "info")

      # ── WIDGET REGISTRATION ──
      @classmethod
      def registerWidgetClass(cls, widget_class: type, qss_enum: Qss):
          """Register widget class with stylesheet (call once per class)"""
          cls._widget_class_registry[widget_class] = qss_enum

          # If theme already loaded, cache this stylesheet
          instance = cls._get_instance()
          if instance._current_color_map:
              stylesheet_content = Stylesheet.read(qss_enum)
              if stylesheet_content:
                  processed_stylesheet = Stylesheet.inject_theme(
                      stylesheet_content, instance._current_color_map
                  )
                  cls._widget_stylesheet_cache[widget_class] = processed_stylesheet

      @classmethod
      def applyWidgetStyle(cls, widget):
          """Apply cached stylesheet to widget instance"""
          widget_class = widget.__class__

          # Use cached stylesheet if available
          if widget_class in cls._widget_stylesheet_cache:
              widget.setStyleSheet(cls._widget_stylesheet_cache[widget_class])
              cls._widget_instance_registry[widget] = widget_class
          else:
              DebugLogger.log(f"No cached stylesheet for {widget_class.__name__}", "warning")

      # ── THEME UPDATES ──
      @classmethod
      def updateTheme(cls, color: Color = None, mode: Mode = None):
          """Update theme and refresh all widgets"""
          instance = cls._get_instance()

          if color:
              instance._theme_color = color
          if mode:
              instance._theme_mode = mode

          # Regenerate color map
          instance._current_color_map = Stylesheet.generate_material_palette(
              instance._theme_color, instance._theme_mode
          )

          # Update global stylesheet
          base_content = Stylesheet.read(Qss.BASE)
          instance._global_stylesheet_cache = Stylesheet.inject_theme(
              base_content, instance._current_color_map
          )
          app = QApplication.instance()
          app.setStyleSheet(instance._global_stylesheet_cache)

          # Update widget stylesheet cache
          for widget_class, qss_enum in cls._widget_class_registry.items():
              stylesheet_content = Stylesheet.read(qss_enum)
              if stylesheet_content:
                  processed_stylesheet = Stylesheet.inject_theme(
                      stylesheet_content, instance._current_color_map
                  )
                  cls._widget_stylesheet_cache[widget_class] = processed_stylesheet

          # Update all widget instances
          cls._refreshAllWidgets()
          instance.theme_refresh.emit(instance._current_color_map)

      @classmethod
      def _refreshAllWidgets(cls):
          """Refresh all registered widget instances"""
          removes = []
          for widget, widget_class in list(cls._widget_instance_registry.items()):
              try:
                  if widget_class in cls._widget_stylesheet_cache:
                      widget.setStyleSheet(cls._widget_stylesheet_cache[widget_class])
              except RuntimeError:
                  removes.append(widget)

          for widget in removes:
              del cls._widget_instance_registry[widget]

  Usage Pattern

  # 1. During app startup (before splash screen)
  ThemeManager.registerWidgetClass(ToolButton, Qss.TOOLBUTTON)
  ThemeManager.registerWidgetClass(RecipeCard, Qss.RECIPE_CARD)

  # 2. During splash screen
  ThemeManager.preloadTheme(Color.BLUE, Mode.LIGHT)

  # 3. In widget constructors (zero performance cost)
  class ToolButton(QToolButton):
      def __init__(self, parent=None):
          super().__init__(parent)
          ThemeManager.applyWidgetStyle(self)  # Uses cached stylesheet

  # 4. Theme changes (updates everything instantly)
  ThemeManager.updateTheme(Color.RED, Mode.DARK)

  This approach gives you:
  - Global foundation styling via application stylesheet
  - Per-widget overrides via cached stylesheets
  - One-time preprocessing during splash screen
  - Zero performance cost for widget instantiation
  - Instant theme updates for all widgets
