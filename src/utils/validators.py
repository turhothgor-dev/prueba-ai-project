"""Validation utilities."""

import os
import re
from pathlib import Path


def validate_api_key(api_key: str) -> tuple[bool, str]:
    """Validate TMDB API key format.

    Args:
        api_key: API key to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not api_key:
        return False, "La API key no puede estar vacía"

    if len(api_key) < 10:
        return False, "La API key parece demasiado corta"

    # TMDB keys are typically 32 characters alphanumeric
    if not re.match(r"^[a-zA-Z0-9]+$", api_key):
        return False, "La API key contiene caracteres inválidos"

    return True, ""


def validate_directory(path: str) -> tuple[bool, str]:
    """Validate directory path.

    Args:
        path: Directory path to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "La ruta no puede estar vacía"

    try:
        dir_path = Path(path)
        if not dir_path.exists():
            return False, "El directorio no existe"
        if not dir_path.is_dir():
            return False, "La ruta no es un directorio"
        if not dir_path.is_absolute():
            return False, "La ruta debe ser absoluta"
    except Exception as e:
        return False, f"Error al validar la ruta: {str(e)}"

    return True, ""


def validate_pattern(pattern: str) -> tuple[bool, str]:
    """Validate filename/folder pattern syntax.

    Args:
        pattern: Pattern string with placeholders

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not pattern:
        return False, "El patrón no puede estar vacío"

    # Check for balanced braces
    if pattern.count("{") != pattern.count("}"):
        return False, "Llaves desbalanceadas en el patrón"

    # Valid placeholders
    valid_placeholders = {
        "title",
        "year",
        "season",
        "episode",
        "tmdb_id",
        "imdb_id",
        "original_title",
    }

    # Extract placeholders
    placeholders = re.findall(r"\{([^}:]+)(?::[^}]+)?\}", pattern)

    for placeholder in placeholders:
        # Remove format specifier if present
        base_name = placeholder.split(":")[0]
        if base_name not in valid_placeholders:
            return False, f"Placeholder inválido: {{{placeholder}}}"

    return True, ""


def validate_pattern_placeholders(
    pattern: str, media_type: str = "both"
) -> tuple[bool, str]:
    """Validate that a pattern has the required placeholders for a media type.

    For series, {season} and {episode} are required.
    For movies, season/episode are not required.

    Args:
        pattern: Pattern string with placeholders
        media_type: One of "movie", "tv", or "both"

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not pattern:
        return False, "El patrón no puede estar vacío"

    # Extract placeholders
    placeholders = re.findall(r"\{([^}:]+)(?::[^}]+)?\}", pattern)
    placeholder_names = {p.split(":")[0] for p in placeholders}

    # Check for series-specific requirements
    if media_type in ("tv", "both"):
        if "season" not in placeholder_names:
            return False, "Los patrones de serie requieren {season}"
        if "episode" not in placeholder_names:
            return False, "Los patrones de serie requieren {episode}"

    return True, ""


def validate_pattern_syntax(
    pattern: str,
) -> tuple[bool, str, list[str]]:
    """Validate pattern syntax with detailed feedback and warnings.

    Args:
        pattern: Pattern string with placeholders
        media_type: One of "movie", "tv", or "both"

    Returns:
        Tuple of (is_valid, error_message, warnings_list)
        - is_valid: True if pattern is syntactically valid
        - error_message: Error description if invalid
        - warnings_list: List of warning messages
    """
    warnings: list[str] = []

    if not pattern:
        return False, "El patrón no puede estar vacío", []

    # Check for balanced braces
    if pattern.count("{") != pattern.count("}"):
        return False, "Llaves desbalanceadas en el patrón", []

    # Valid placeholders
    valid_placeholders = {
        "title",
        "year",
        "season",
        "episode",
        "tmdb_id",
        "imdb_id",
        "original_title",
    }

    # Valid format specifiers (Python format spec style)
    valid_format_specs = {"02d", "03d", "d", ".2f", ".1f", "s"}

    # Extract all placeholder references
    placeholder_refs = re.findall(r"\{([^}]+)\}", pattern)

    found_placeholders: set[str] = set()

    for ref in placeholder_refs:
        # Split by colon to separate name from format
        parts = ref.split(":")
        name = parts[0].strip()
        found_placeholders.add(name)

        # Validate placeholder name
        if name not in valid_placeholders:
            return False, f"Placeholder inválido: {{{name}}}", []

        # Validate format specifier if present
        if len(parts) > 1:
            fmt = ":".join(parts[1:]).strip()
            if fmt and fmt not in valid_format_specs:
                warnings.append(
                    f"El especificador de formato '{fmt}' en {{{ref}}} puede no ser válido"
                )

    # Check for common issues
    if "title" not in found_placeholders:
        warnings.append("El patrón no incluye {title} (recomendado)")

    if not found_placeholders:
        warnings.append("El patrón no tiene placeholders (se usará el nombre original)")

    # Check for empty pattern (only static text)
    if not placeholder_refs:
        return True, "", ["El patrón no tiene placeholders"]

    return True, "", warnings


def validate_base_directory(path: str, must_exist: bool = False) -> tuple[bool, str]:
    """Validate a base directory path.

    Args:
        path: Directory path to validate
        must_exist: If True, the directory must already exist.
            If False, only validates the path format.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not path:
        return False, "La ruta no puede estar vacía"

    try:
        dir_path = Path(path)

        # Check if it's an absolute path
        if not dir_path.is_absolute():
            return False, "La ruta debe ser absoluta"

        # Check if it exists
        if must_exist:
            if not dir_path.exists():
                return False, "El directorio no existe"
            if not dir_path.is_dir():
                return False, "La ruta no es un directorio"

            # Check write permissions
            if not os.access(dir_path, os.W_OK):
                return False, "No tiene permisos de escritura en este directorio"

        else:
            # For non-existing paths, check if parent exists
            if not dir_path.exists():
                parent = dir_path.parent
                if not parent.exists():
                    return False, f"El directorio padre no existe: {parent}"

    except PermissionError as e:
        return False, f"Permiso denegado al acceder a la ruta: {e}"
    except Exception as e:
        return False, f"Error al validar la ruta: {str(e)}"

    return True, ""
