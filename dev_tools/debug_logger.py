""" app/dev_tools/debug_logger.py

Enhanced debugging logger with color support and context-aware logging."""

# ── Imports ─────────────────────────────────────────────────────────────────────
import inspect
import logging
import re
import sys
from pathlib import Path
from datetime import datetime

import colorlog

# timestamp for current run (used to stamp log file names)
_RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# formatter to strip ANSI escape sequences for file logging
_ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')
class _StripAnsiFormatter(logging.Formatter):
    """Logging formatter that removes ANSI color codes from messages."""
    def format(self, record):
        formatted = super().format(record)
        return _ANSI_ESCAPE.sub('', formatted)


# ── Debug Logger ─────────────────────────────────────────────────────────────────────────────
class DebugLogger:
    """
    A class for enhanced debugging with color support and context-aware logging.
    """

    _logger = logging.getLogger("debug_logger")
    # Global logging control
    _enabled: bool = True
    # Workspace root directory for default log file paths
    _workspace_root: Path = Path(__file__).resolve().parents[1]
    _log_file_path: str | None = None
    _file_handler: logging.Handler | None = None
    _level: int = logging.DEBUG

    VARIABLE_COLOR = '\033[35m'  # purple for variables
    RESET_COLOR = '\033[0m'      # reset to default color
    CONTEXT_COLOR = '\033[35m'   # purple for context (class.method)
    BRACKET_COLOR = '\033[38;2;255;165;0m'   # green for brackets

    LOG_COLORS = {
        'DEBUG': 'green',
        'INFO': 'blue',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'bold_red',
        'CONTEXT': 'magenta'
    }

    ANSI_COLORS = {
        'DEBUG': '\033[32m',  # green
        'INFO': '\033[34m',   # blue
        'WARNING': '\033[33m',  # yellow
        'ERROR': '\033[31m',  # red
        'CRITICAL': '\033[1;31m',  # bold red
        'CONTEXT': '\033[35m'  # purple
    }

    @classmethod
    def _initialize_logger(cls):
        """Initializes the logger only once."""
        if not cls._logger.hasHandlers():
            handler = colorlog.StreamHandler()
            handler.setFormatter(colorlog.ColoredFormatter(
                '%(log_color)s[%(levelname)s]%(reset)s '  # log level color
                + f'{cls.CONTEXT_COLOR}[%(context)s]{cls.RESET_COLOR} '  # explicit context color
                + '%(message_log)s',  # message log
                datefmt='%H:%M:%S',
                log_colors=cls.LOG_COLORS,
                reset=True,  # ensure colors reset correctly
            ))
            cls._logger.addHandler(handler)
            cls._logger.setLevel(cls._level)
        # ensure file handler is added if a log file is set
        if cls._log_file_path and not cls._file_handler:
            fh = logging.FileHandler(cls._log_file_path)
            fh.setLevel(cls._level)
            fh.setFormatter(_StripAnsiFormatter(
                '%(asctime)s [%(levelname)s] [%(context)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            cls._logger.addHandler(fh)
            cls._file_handler = fh

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
        # skip logging if disabled
        if not cls._enabled:
            return
        cls._initialize_logger()
        # get calling context (class.method or function)
        caller_frame = inspect.stack()[1]
        local_vars = caller_frame[0].f_locals
        self_instance = local_vars.get('self', None)

        # regex pattern to match placeholders in the message
        pattern = r"{([^{}]+)}"

        def replace_variables(match):
            expr = match.group(1).strip()
            try:
                value = cls._resolve_variable(expr, local_vars, self_instance)
                if value is None:
                    value = "None"
            except Exception:
                return match.group(0)  # return the original placeholder if resolution fails

            # ensure variable is colored, and AFTER the variable, it reverts to the log color
            log_color = cls.ANSI_COLORS.get(log_type.upper(), "")
            return f"{cls.VARIABLE_COLOR}{value}{log_color}"  # maintain log color after variable

        # process the message to replace variables
        message = re.sub(pattern, replace_variables, message)

        # dynamically resolve the log method
        log_method = getattr(cls._logger, log_type.lower(), cls._logger.info)

        # apply log level color to the message
        log_color = cls.ANSI_COLORS.get(log_type.upper(), "")
        formatted_message = f"{log_color}{message}{cls.RESET_COLOR}"

        # add context to the log record
        class_name = self_instance.__class__.__name__ if self_instance else None
        method_name = caller_frame.function
        context = f"{class_name}.{method_name}" if class_name else method_name

         # highlight any [...] except the log‐level tag
        def highlight_brackets(match):
            inner = match.group(1)
            if inner == log_type.upper(): # skip your [INFO]/[DEBUG]/etc.
                return match.group(0)
            return f"{cls.BRACKET_COLOR}[{inner}]{cls.RESET_COLOR}{log_color}" # restore color

        message = re.sub(r"\[([^\]]+)\]", highlight_brackets, message)

        # now wrap the whole thing in the level’s ANSI color:
        formatted_message = f"{log_color}{message}{cls.RESET_COLOR}"
        # ──────────────────────────────────────────────────────────────────────────────

        # now actually log it (console and optional file)
        log_method = getattr(cls._logger, log_type.lower(), cls._logger.info)
        log_method(formatted_message, extra={"context": context, "message_log": formatted_message})
        sys.stdout.flush()

    @classmethod
    def log_and_raise(cls, message, exception_type=Exception):
        """Logs an error message and raises an exception."""
        cls.log(message, "error")
        raise exception_type(message)

    @classmethod
    def enable(cls, value: bool) -> None:
        """Enable or disable all logging output."""
        cls._enabled = bool(value)

    @classmethod
    def set_log_level(cls, level_name: str) -> None:
        """Set the minimum log level (e.g., 'DEBUG', 'INFO')."""
        lvl = logging.getLevelName(level_name.upper())
        if not isinstance(lvl, int):
            raise ValueError(f"Invalid log level: {level_name}")
        cls._level = lvl
        cls._logger.setLevel(lvl)
        if cls._file_handler:
            cls._file_handler.setLevel(lvl)

    @classmethod
    def set_log_file(cls, path: str) -> None:
        """Enable logging to the specified file (ANSI colors stripped).
        Relative paths are resolved under workspace_root/logs and stamped with a timestamp."""
        # remove existing file handler if present
        if cls._file_handler:
            cls._logger.removeHandler(cls._file_handler)
            try:
                cls._file_handler.close()
            except Exception:
                pass
            cls._file_handler = None
        # resolve path: if relative, place under workspace_root/logs; else use absolute
        p = Path(path)
        if not p.is_absolute():
            logs_dir = cls._workspace_root / "logs"
            logs_dir.mkdir(parents=True, exist_ok=True)
            p = logs_dir / p.name
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
        # apply run timestamp to filename (one file per run)
        p = p.with_name(f"{p.stem}_{_RUN_TIMESTAMP}{p.suffix}")
        cls._log_file_path = str(p)
        cls._initialize_logger()
