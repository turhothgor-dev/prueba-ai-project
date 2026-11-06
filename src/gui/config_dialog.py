"""Configuration dialog window."""

import logging

from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from src.utils.logger import get_logger
from src.utils.validators import (
    validate_base_directory,
    validate_pattern_placeholders,
    validate_pattern_syntax,
)

logger = get_logger(__name__)


class ConfigDialog(QDialog):
    """Dialog for application configuration."""

    # Language code mapping
    LANGUAGE_MAP = {
        "Español (es-ES)": "es-ES",
        "English (en-US)": "en-US",
        "Français (fr-FR)": "fr-FR",
        "Deutsch (de-DE)": "de-DE",
        "Português (pt-BR)": "pt-BR",
    }

    def __init__(self, config, parent=None) -> None:
        super().__init__(parent)
        self.config = config
        self._errors: dict[str, str] = {}
        self._init_ui()
        self._load_config()

    def _init_ui(self) -> None:
        """Initialize dialog UI."""
        self.setWindowTitle("Configuración")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # API Settings
        api_group = QGroupBox("Configuración de API")
        api_layout = QFormLayout()

        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("Opcional - Necesaria para buscar metadatos")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)

        # Create layout for API key with toggle button
        api_key_layout = QHBoxLayout()
        self.api_key_toggle_btn = QPushButton("👁")
        self.api_key_toggle_btn.setFixedSize(32, 28)
        self.api_key_toggle_btn.clicked.connect(self._toggle_api_key_visibility)
        self._api_key_visible = False
        api_key_layout.addWidget(self.api_key_input)
        api_key_layout.addWidget(self.api_key_toggle_btn)

        api_layout.addRow("TMDB API Key:", api_key_layout)

        self.language_combo = QComboBox()
        self.language_combo.addItems(list(self.LANGUAGE_MAP.keys()))
        api_layout.addRow("Idioma:", self.language_combo)

        self.use_imdb_check = QCheckBox("Usar IMDb como fuente alternativa")
        api_layout.addRow("", self.use_imdb_check)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Organization Settings
        org_group = QGroupBox("Organización de Archivos")
        org_layout = QFormLayout()

        self.base_dir_input = QLineEdit()
        browse_btn = QPushButton("Examinar...")
        browse_btn.clicked.connect(self._on_browse_base_dir)

        base_dir_layout = QHBoxLayout()
        base_dir_layout.addWidget(self.base_dir_input)
        base_dir_layout.addWidget(browse_btn)
        org_layout.addRow("Directorio Base:", base_dir_layout)

        self.base_dir_label = QLabel("")
        self.base_dir_label.setStyleSheet("color: red; font-size: 10pt;")
        org_layout.addRow("", self.base_dir_label)

        self.folder_pattern_input = QLineEdit()
        self.folder_pattern_input.setText("{title} ({year})")
        self.folder_pattern_input.setToolTip(
            "Ej: {title} ({year}) para películas\nEj: {title}/Season {season} para series"
        )
        org_layout.addRow("Patrón de Carpeta:", self.folder_pattern_input)

        self.folder_pattern_label = QLabel("")
        self.folder_pattern_label.setStyleSheet("color: red; font-size: 10pt;")
        org_layout.addRow("", self.folder_pattern_label)

        self.file_pattern_input = QLineEdit()
        self.file_pattern_input.setText("{title} - S{season:02d}E{episode:02d}")
        self.file_pattern_input.setToolTip(
            "Ej: {title} - ({year}) para películas\nEj: {title} - S{season:02d}E{episode:02d} para series"
        )
        org_layout.addRow("Patrón de Archivo:", self.file_pattern_input)

        self.file_pattern_label = QLabel("")
        self.file_pattern_label.setStyleSheet("color: red; font-size: 10pt;")
        org_layout.addRow("", self.file_pattern_label)

        self.season_folders_check = QCheckBox("Crear carpetas por temporada")
        self.season_folders_check.setChecked(True)
        org_layout.addRow("", self.season_folders_check)

        self.replace_existing_check = QCheckBox("Reemplazar archivos existentes")
        org_layout.addRow("", self.replace_existing_check)

        org_group.setLayout(org_layout)
        layout.addWidget(org_group)

        # Cache Settings
        cache_group = QGroupBox("Caché")
        cache_layout = QFormLayout()

        self.cache_enabled_check = QCheckBox("Habilitar caché local")
        self.cache_enabled_check.setChecked(True)
        cache_layout.addRow("", self.cache_enabled_check)

        self.cache_ttl_spin = QSpinBox()
        self.cache_ttl_spin.setRange(1, 365)
        self.cache_ttl_spin.setValue(7)
        self.cache_ttl_spin.setSuffix(" días")
        cache_layout.addRow("Tiempo de vida:", self.cache_ttl_spin)

        cache_group.setLayout(cache_layout)
        layout.addWidget(cache_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btn_cancel = QPushButton("Cancelar")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)

        self.btn_save = QPushButton("Guardar")
        self.btn_save.clicked.connect(self._on_save)
        button_layout.addWidget(self.btn_save)

        layout.addLayout(button_layout)

        # Connect real-time validation
        self.folder_pattern_input.textChanged.connect(self._validate_folder_pattern)
        self.file_pattern_input.textChanged.connect(self._validate_file_pattern)
        self.base_dir_input.textChanged.connect(self._validate_base_dir)

    def _load_config(self) -> None:
        """Load current config values into UI."""
        # API
        self.api_key_input.setText(self.config.get("api.tmdb_api_key", ""))
        self.use_imdb_check.setChecked(self.config.get("api.use_imdb", False))

        # Language
        saved_language = self.config.get("api.tmdb_language", "es-ES")
        for display_name, code in self.LANGUAGE_MAP.items():
            if code == saved_language:
                self.language_combo.setCurrentText(display_name)
                break

        # Organization
        self.base_dir_input.setText(self.config.get("organization.base_directory", ""))
        self.folder_pattern_input.setText(
            self.config.get("organization.folder_pattern", "{title} ({year})")
        )
        self.file_pattern_input.setText(
            self.config.get("organization.file_pattern", "{title} - S{season:02d}E{episode:02d}")
        )
        self.season_folders_check.setChecked(
            self.config.get("organization.create_season_folders", True)
        )
        self.replace_existing_check.setChecked(
            self.config.get("organization.replace_existing", False)
        )

        # Cache
        self.cache_enabled_check.setChecked(self.config.get("cache.enabled", True))
        self.cache_ttl_spin.setValue(self.config.get("cache.ttl_days", 7))

    def _toggle_api_key_visibility(self) -> None:
        """Toggle API key visibility between password and plain text."""
        self._api_key_visible = not self._api_key_visible
        if self._api_key_visible:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.api_key_toggle_btn.setText("🙈")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.api_key_toggle_btn.setText("👁")

    # ---- Real-time validation methods ----

    def _validate_folder_pattern(self, _text: str = "") -> None:
        """Validate folder pattern in real-time."""
        text = self.folder_pattern_input.text()
        is_valid, error, warnings = validate_pattern_syntax(text)

        if not is_valid:
            self.folder_pattern_label.setText(f"⚠ {error}")
            self.folder_pattern_label.setStyleSheet("color: red; font-size: 10pt; font-weight: bold;")
            self._errors["folder_pattern"] = error
        elif warnings:
            warning_msg = " | ".join(warnings)
            self.folder_pattern_label.setText(f"💡 {warning_msg}")
            self.folder_pattern_label.setStyleSheet("color: orange; font-size: 10pt;")
            self._errors.pop("folder_pattern", None)
        else:
            self.folder_pattern_label.setText("✅ Patrón válido")
            self.folder_pattern_label.setStyleSheet("color: green; font-size: 10pt;")
            self._errors.pop("folder_pattern", None)

        self._update_save_button_state()

    def _validate_file_pattern(self, _text: str = "") -> None:
        """Validate file pattern in real-time."""
        text = self.file_pattern_input.text()
        is_valid, error, warnings = validate_pattern_syntax(text)

        if not is_valid:
            self.file_pattern_label.setText(f"⚠ {error}")
            self.file_pattern_label.setStyleSheet("color: red; font-size: 10pt; font-weight: bold;")
            self._errors["file_pattern"] = error
        elif warnings:
            warning_msg = " | ".join(warnings)
            self.file_pattern_label.setText(f"💡 {warning_msg}")
            self.file_pattern_label.setStyleSheet("color: orange; font-size: 10pt;")
            self._errors.pop("file_pattern", None)
        else:
            self.file_pattern_label.setText("✅ Patrón válido")
            self.file_pattern_label.setStyleSheet("color: green; font-size: 10pt;")
            self._errors.pop("file_pattern", None)

        self._update_save_button_state()

    def _validate_base_dir(self, _text: str = "") -> None:
        """Validate base directory in real-time."""
        text = self.base_dir_input.text()

        if not text:
            self.base_dir_label.setText("")
            self._errors.pop("base_directory", None)
            self._update_save_button_state()
            return

        is_valid, error = validate_base_directory(text, must_exist=True)

        if not is_valid:
            self.base_dir_label.setText(f"⚠ {error}")
            self.base_dir_label.setStyleSheet("color: red; font-size: 10pt; font-weight: bold;")
            self._errors["base_directory"] = error
        else:
            self.base_dir_label.setText("✅ Directorio válido")
            self.base_dir_label.setStyleSheet("color: green; font-size: 10pt;")
            self._errors.pop("base_directory", None)

        self._update_save_button_state()

    def _update_save_button_state(self) -> None:
        """Enable/disable save button based on validation errors."""
        has_errors = bool(self._errors)
        self.btn_save.setEnabled(not has_errors)
        if has_errors:
            self.btn_save.setStyleSheet("QPushButton { color: red; font-weight: bold; }")
        else:
            self.btn_save.setStyleSheet("")

    def _on_browse_base_dir(self) -> None:
        """Open folder browser for base directory."""
        directory = QFileDialog.getExistingDirectory(self, "Seleccionar Directorio Base")
        if directory:
            self.base_dir_input.setText(directory)

    def _validate_inputs(self) -> tuple[bool, list[str], list[str]]:
        """Validate user inputs before saving.

        Returns:
            Tuple of (is_valid, errors, warnings)
            - is_valid: True if configuration can be saved
            - errors: List of critical error messages (block saving)
            - warnings: List of warning messages (allow saving)
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Validate API key (optional but warn if too short)
        api_key = self.api_key_input.text().strip()
        if api_key and len(api_key) < 10:
            warnings.append("La API key de TMDB parece muy corta. Verifica que sea correcta.")
        if not api_key:
            warnings.append(
                "No se proporcionó API key. La búsqueda automática de metadatos no estará disponible."
            )

        # Validate folder pattern
        folder_pattern = self.folder_pattern_input.text()
        if folder_pattern:
            is_valid, error = validate_pattern_placeholders(folder_pattern, "both")
            if not is_valid:
                errors.append(f"Patrón de Carpeta: {error}")

        # Validate file pattern
        file_pattern = self.file_pattern_input.text()
        if file_pattern:
            is_valid, error = validate_pattern_placeholders(file_pattern, "both")
            if not is_valid:
                errors.append(f"Patrón de Archivo: {error}")

        # Validate base directory (optional, but if provided must be valid)
        base_dir = self.base_dir_input.text()
        if base_dir:
            is_valid, error = validate_base_directory(base_dir, must_exist=True)
            if not is_valid:
                errors.append(f"Directorio Base: {error}")

        return len(errors) == 0, errors, warnings

    def _on_save(self) -> None:
        """Save configuration values."""
        # Validate inputs
        is_valid, errors, warnings = self._validate_inputs()

        # If there are critical errors, show them and don't save
        if errors:
            error_msg = "No se pudo guardar la configuración:\n\n" + "\n".join(f"• {e}" for e in errors)
            QMessageBox.critical(
                self,
                "Errores de Validación",
                error_msg,
                QMessageBox.StandardButton.Ok,
            )
            return

        # Save configuration
        try:
            # API
            self.config.set("api.tmdb_api_key", self.api_key_input.text().strip())
            self.config.set("api.use_imdb", self.use_imdb_check.isChecked())

            # Language
            selected_language = self.language_combo.currentText()
            language_code = self.LANGUAGE_MAP.get(selected_language, "es-ES")
            self.config.set("api.tmdb_language", language_code)

            # Organization
            self.config.set("organization.base_directory", self.base_dir_input.text())
            self.config.set("organization.folder_pattern", self.folder_pattern_input.text())
            self.config.set("organization.file_pattern", self.file_pattern_input.text())
            self.config.set(
                "organization.create_season_folders", self.season_folders_check.isChecked()
            )
            self.config.set(
                "organization.replace_existing", self.replace_existing_check.isChecked()
            )

            # Cache
            self.config.set("cache.enabled", self.cache_enabled_check.isChecked())
            self.config.set("cache.ttl_days", self.cache_ttl_spin.value())

            logger.info("Configuration saved successfully")
            logger.debug(
                "Saved config: base_dir=%s, folder_pattern=%s, file_pattern=%s",
                self.base_dir_input.text(),
                self.folder_pattern_input.text(),
                self.file_pattern_input.text(),
            )

        except Exception as e:
            logger.error("Failed to save configuration: %s", e, exc_info=True)
            QMessageBox.critical(self, "Error", f"No se pudo guardar la configuración: {str(e)}")
            return

        # Show appropriate message
        if warnings:
            warning_msg = "La configuración se ha guardado correctamente, pero se encontraron las siguientes advertencias:\n\n" + "\n".join(f"• {w}" for w in warnings)
            QMessageBox.warning(
                self,
                "Advertencia",
                warning_msg,
                QMessageBox.StandardButton.Ok,
            )
        else:
            QMessageBox.information(self, "Configuración", "Configuración guardada correctamente.")

        # Refresh services in main window if API key changed
        if self.parent() and hasattr(self.parent(), "_create_services"):
            self.parent()._create_services()

        self.accept()
