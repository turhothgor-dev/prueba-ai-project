"""Validation utilities."""

import re


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
    from pathlib import Path

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
