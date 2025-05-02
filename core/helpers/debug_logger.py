""" co"""

import inspect
import logging
import re
#🔸System Imports
import sys

#🔸Third-party Imports
import colorlog


class DebugLogger:
    """
    A class for enhanced debugging with color support and context-aware logging.
    """

    _logger = logging.getLogger("debug_logger")

    VARIABLE_COLOR = '\033[35m'  # Purple for variables
    RESET_COLOR = '\033[0m'      # Reset to default color
    CONTEXT_COLOR = '\033[35m'   # Purple for context (class.method)

    LOG_COLORS = {
        'DEBUG': 'green',
        'INFO': 'blue',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
        'CONTEXT': 'magenta'
    }

    ANSI_COLORS = {
        'DEBUG': '\033[32m',  # Green
        'INFO': '\033[34m',   # Blue
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',  # Red
        'CRITICAL': '\033[1;31m',  # Bold Red
        'CONTEXT': '\033[35m'  # Purple
    }

    @classmethod
    def _initialize_logger(cls):
        """Initializes the logger only once."""
        if not cls._logger.hasHandlers():
            handler = colorlog.StreamHandler()
            handler.setFormatter(colorlog.ColoredFormatter(
                '%(log_color)s[%(levelname)s]%(reset)s '  # Log level color
                + f'{cls.CONTEXT_COLOR}[%(context)s]{cls.RESET_COLOR} '  # Explicit context color
                + '%(message_log)s',  # Message log
                datefmt='%H:%M:%S',
                log_colors=cls.LOG_COLORS,
                reset=True,  # 🔥 Ensure colors reset correctly
            ))
            cls._logger.addHandler(handler)
            cls._logger.setLevel(logging.DEBUG)

    @classmethod
    def _resolve_variable(cls, expr, local_vars, self_instance):
        """
        Resolves an expression like 'label.objectName()' or 'var.attr'
        using attribute lookup. Only supports simple attribute access
        and no-argument method calls.

        Args:
            expr (str): The expression to resolve.
            local_vars (dict): The caller's local variables.
            self_instance (object): The 'self' instance if available.

        Returns:
            The resolved value or a string indicating an error.
        """
        parts = expr.split('.')
        if not parts:
            return None

        if parts[0] in local_vars:
            obj = local_vars[parts[0]]
        elif self_instance and hasattr(self_instance, parts[0]):
            obj = getattr(self_instance, parts[0])
        else:
            return f"Error: {parts[0]} not found"

        for part in parts[1:]:
            if part.endswith("()"):
                method_name = part[:-2]
                func = getattr(obj, method_name, None)
                if func and callable(func):
                    try:
                        obj = func()
                    except Exception as e:
                        return f"Error calling {expr}: {e}"
                else:
                    return f"Error: {expr} has no callable method {method_name}"
            else:
                obj = getattr(obj, part, None)
                if obj is None:
                    return f"Error: {expr} has no attribute {part}"
        return obj

    @classmethod
    def log(cls, message, log_type="info", **kwargs):
        """
        Logs a message with the specified log level, dynamically replacing
        variables enclosed in curly braces {} with their values from the caller's local scope.
        Supports placeholders with simple method calls (no parameters).

        Args:
            message (str): The message to log, with variables enclosed in curly braces {}.
            log_type (str): The logging level ('debug', 'info', 'warning', 'error', 'critical').
        """
        cls._initialize_logger()

        # Get calling context (class.method or function)
        caller_frame = inspect.stack()[1]
        local_vars = caller_frame[0].f_locals
        self_instance = local_vars.get('self', None)

        # Regex pattern to match placeholders in the message
        pattern = r"{([^{}]+)}"

        def replace_variables(match):
            expr = match.group(1).strip()
            try:
                value = cls._resolve_variable(expr, local_vars, self_instance)
                if value is None:
                    value = "None"
            except Exception:
                return match.group(0)  # Return the original placeholder if resolution fails

            # Ensure variable is colored, and AFTER the variable, it reverts to the log color
            log_color = cls.ANSI_COLORS.get(log_type.upper(), "")
            return f"{cls.VARIABLE_COLOR}{value}{log_color}"  # Maintain log color after variable

        # Process the message to replace variables
        message = re.sub(pattern, replace_variables, message)

        # Dynamically resolve the log method
        log_method = getattr(cls._logger, log_type.lower(), cls._logger.info)

        # Apply log level color to the message
        log_color = cls.ANSI_COLORS.get(log_type.upper(), "")
        formatted_message = f"{log_color}{message}{cls.RESET_COLOR}"

        # Add context to the log record
        class_name = self_instance.__class__.__name__ if self_instance else None
        method_name = caller_frame.function
        context = f"{class_name}.{method_name}" if class_name else method_name

        # Log the message with full color formatting
        log_method(formatted_message, extra={"context": context, "message_log": formatted_message})
        sys.stdout.flush()  # Force flush to remove extra formatting artifacts

    @classmethod
    def log_and_raise(cls, message, exception_type=Exception):
        """Logs an error message and raises an exception."""
        cls.log(message, "error")
        raise exception_type(message)

# Example usage
if __name__ == "__main__":
    logger = DebugLogger()

    # Example variable and method to test logging
    class Dummy:
        def __init__(self):
            self.value = 42

        def get_value(self):
            return self.value

    dummy = Dummy()

    logger.log("This is an info message", "info")
    logger.log("This is a warning message", "warning")
    logger.log("This is an error message", "error")
    logger.log("This is a debug message", "debug")

    test_var1 = 42
    test_var2 = 54
    test_var3 = 25
    test_var4 = 88

    logger.log("The value of test_var is {test_var1}. Verify text color is swapping after var.", "info")
    logger.log("The value of test_var is {test_var2}. Verify text color is swapping after var.", "warning")
    logger.log("The value of test_var is {test_var3}. Verify text color is swapping after var.", "error")
    logger.log("The value of test_var is {test_var4}. Verify text color is swapping after var.", "debug")