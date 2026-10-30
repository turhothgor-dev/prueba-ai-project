"""Configuration dialog window."""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QCheckBox,
    QSpinBox,
    QComboBox,
    QPushButton,
    QFileDialog,
    QGroupBox,
    QLabel,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from typing import Optional


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

        self.folder_pattern_input = QLineEdit()
        self.folder_pattern_input.setText("{title} ({year})")
        org_layout.addRow("Patrón de Carpeta:", self.folder_pattern_input)

        self.file_pattern_input = QLineEdit()
        self.file_pattern_input.setText("{title} - S{season:02d}E{episode:02d}")
        org_layout.addRow("Patrón de Archivo:", self.file_pattern_input)

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

    def _on_browse_base_dir(self) -> None:
        """Open folder browser for base directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Seleccionar Directorio Base"
        )
        if directory:
            self.base_dir_input.setText(directory)

    def _validate_inputs(self) -> tuple[bool, str]:
        """Validate user inputs before saving.
        
        Returns:
            Tuple of (is_valid, warning_message)
            - is_valid: True if configuration can be saved
            - warning_message: Warning message if API key is missing/invalid
        """
        api_key = self.api_key_input.text().strip()
        
        # API key is optional, but warn if invalid format when provided
        if api_key and len(api_key) < 10:
            return True, "La API key de TMDB parece muy corta. Verifica que sea correcta."
        
        # Warn if no API key provided
        if not api_key:
            return True, "No se proporcionó API key. La búsqueda automática de metadatos no estará disponible."
        
        return True, ""

    def _on_save(self) -> None:
        """Save configuration values."""
        # Validate inputs (non-blocking)
        is_valid, warning_msg = self._validate_inputs()
        
        # Always save configuration regardless of warnings
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
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar la configuración: {str(e)}")
            return
        
        # Show appropriate message
        if warning_msg:
            result = QMessageBox.warning(
                self,
                "Advertencia",
                f"{warning_msg}\n\nLa configuración se ha guardado correctamente.",
                QMessageBox.StandardButton.Ok,
            )
        else:
            QMessageBox.information(self, "Configuración", "Configuración guardada correctamente.")
        
        # Refresh services in main window if API key changed
        if self.parent() and hasattr(self.parent(), "_create_services"):
            self.parent()._create_services()
        
        self.accept()
