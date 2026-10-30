"""Main application window."""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QProgressBar,
    QLabel,
    QFileDialog,
    QMessageBox,
    QHeaderView,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
from typing import Optional

from .config_dialog import ConfigDialog
from src.core.media_file import MediaFile
from src.core.organizer import FileOrganizer
from src.services.cache_service import CacheService
from src.services.tmdb_service import TMDBService


class WorkerThread(QThread):
    """Background worker for file processing."""

    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, int, int)  # success, processed, failed

    def __init__(
        self,
        media_files: list,
        config,
        tmdb_service: TMDBService,
        cache_service: CacheService,
    ):
        super().__init__()
        self.media_files = media_files
        self.config = config
        self.tmdb_service = tmdb_service
        self.cache_service = cache_service
        self.organizer: Optional[FileOrganizer] = None
        self.processed_count = 0
        self.failed_count = 0

    def run(self) -> None:
        """Execute file processing."""
        try:
            # Initialize the organizer
            self.organizer = FileOrganizer(
                config=self.config,
                cache_service=self.cache_service,
                tmdb_service=self.tmdb_service,
            )

            total = len(self.media_files)
            self.processed_count = 0
            self.failed_count = 0

            for i, media_file in enumerate(self.media_files):
                # Update status
                self.status.emit(
                    f"Procesando: {media_file.original_filename} "
                    f"({i + 1}/{total})"
                )

                # Process the file
                success, message = self.organizer.organize(media_file)

                if success:
                    self.processed_count += 1
                    self.status.emit(f"✓ {message}")
                else:
                    self.failed_count += 1
                    self.status.emit(f"✗ {message}")

                # Update progress
                progress = int(((i + 1) / total) * 100)
                self.progress.emit(progress)

            # Emit finished signal with counts
            success = self.failed_count == 0
            self.finished.emit(success, self.processed_count, self.failed_count)

        except Exception as e:
            self.status.emit(f"Error crítico: {str(e)}")
            self.finished.emit(False, self.processed_count, self.failed_count)


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, config) -> None:
        super().__init__()
        self.config = config
        self.worker: Optional[WorkerThread] = None
        self.media_files: list[MediaFile] = []
        self.tmdb_service: Optional[TMDBService] = None
        self.cache_service: Optional[CacheService] = None
        self._init_ui()
        self._init_services()

    def _init_services(self) -> None:
        """Initialize external services."""
        api_key = self.config.get("api.tmdb_api_key", "")
        language = self.config.get("api.tmdb_language", "es-ES")

        if api_key:
            self.tmdb_service = TMDBService(api_key=api_key, language=language)

        cache_enabled = self.config.get("cache.enabled", True)
        if cache_enabled:
            cache_path = self.config.get("cache.db_path", "cache.db")
            ttl_days = self.config.get("cache.ttl_days", 7)
            self.cache_service = CacheService(
                db_path=cache_path,
            )
            # Set TTL via a method or attribute (we'll use the set method with TTL)

    def _init_ui(self) -> None:
        """Initialize user interface."""
        self.setWindowTitle("MediaOrganizer")
        self.setMinimumSize(800, 600)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Toolbar
        toolbar_layout = QHBoxLayout()

        self.btn_add_files = QPushButton("Añadir Archivos")
        self.btn_add_files.clicked.connect(self._on_add_files)
        toolbar_layout.addWidget(self.btn_add_files)

        self.btn_add_folder = QPushButton("Añadir Carpeta")
        self.btn_add_folder.clicked.connect(self._on_add_folder)
        toolbar_layout.addWidget(self.btn_add_folder)

        toolbar_layout.addStretch()

        self.btn_preview = QPushButton("Vista Previa")
        self.btn_preview.clicked.connect(self._on_preview)
        self.btn_preview.setEnabled(False)
        toolbar_layout.addWidget(self.btn_preview)

        self.btn_config = QPushButton("Configuración")
        self.btn_config.clicked.connect(self._on_config)
        toolbar_layout.addWidget(self.btn_config)

        self.btn_process = QPushButton("Procesar")
        self.btn_process.clicked.connect(self._on_process)
        self.btn_process.setEnabled(False)
        toolbar_layout.addWidget(self.btn_process)

        layout.addLayout(toolbar_layout)

        # File table
        self.table_files = QTableWidget()
        self.table_files.setColumnCount(6)
        self.table_files.setHorizontalHeaderLabels([
            "Archivo", "Título", "Temp.", "Epis.", "Nuevo Nombre", "Estado"
        ])
        self.table_files.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.table_files.setColumnWidth(4, 250)
        layout.addWidget(self.table_files)

        # Status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_label = QLabel("Listo")

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        layout.addLayout(status_layout)

    def _on_add_files(self) -> None:
        """Handle add files button click."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar Archivos de Video",
            "",
            "Video Files (*.mp4 *.mkv *.avi *.mov *.wmv *.flv)",
        )
        if files:
            self._add_files_to_table(files)

    def _on_add_folder(self) -> None:
        """Handle add folder button click."""
        folder = QFileDialog.getExistingDirectory(
            self, "Seleccionar Carpeta"
        )
        if folder:
            video_extensions = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv"}
            files = [
                str(f) for f in Path(folder).rglob("*")
                if f.suffix.lower() in video_extensions
            ]
            self._add_files_to_table(files)

    def _add_files_to_table(self, files: list[str]) -> None:
        """Add files to the table widget."""
        current_rows = self.table_files.rowCount()
        self.table_files.setRowCount(current_rows + len(files))

        for i, file in enumerate(files):
            row = current_rows + i
            media_file = MediaFile.from_path(file)
            media_file.guess_info_from_filename()
            self.media_files.append(media_file)

            # File name
            self.table_files.setItem(row, 0, QTableWidgetItem(media_file.original_filename))

            # Title (guessed)
            title_item = QTableWidgetItem(media_file.title or "Sin metadata")
            title_item.setForeground(Qt.GlobalColor.darkGray)
            self.table_files.setItem(row, 1, title_item)

            # Season
            season_text = str(media_file.season) if media_file.season else "-"
            self.table_files.setItem(row, 2, QTableWidgetItem(season_text))

            # Episode
            episode_text = str(media_file.episode) if media_file.episode else "-"
            self.table_files.setItem(row, 3, QTableWidgetItem(episode_text))

            # New name (empty until preview)
            new_name_item = QTableWidgetItem("-")
            new_name_item.setForeground(Qt.GlobalColor.darkGray)
            self.table_files.setItem(row, 4, new_name_item)

            # Status
            status_item = QTableWidgetItem("Pendiente")
            status_item.setForeground(Qt.GlobalColor.darkGray)
            self.table_files.setItem(row, 5, status_item)

        self.btn_process.setEnabled(True)
        self.btn_preview.setEnabled(True)
        self.status_label.setText(f"{len(files)} archivo(s) añadido(s)")

    def _on_config(self) -> None:
        """Handle config button click."""
        dialog = ConfigDialog(self.config, self)
        dialog.exec()

    def _on_preview(self) -> None:
        """Handle preview button click."""
        if not self.media_files:
            QMessageBox.warning(
                self, "Advertencia", "No hay archivos para previsualizar."
            )
            return

        if not self.tmdb_service:
            QMessageBox.warning(
                self,
                "Advertencia",
                "Configura tu API Key de TMDB en Configuración > API para obtener metadatos.",
            )
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_preview.setEnabled(False)
        self.btn_process.setEnabled(False)
        self.status_label.setText("Generando vista previa...")

        # Create organizer for preview
        organizer = FileOrganizer(
            config=self.config,
            cache_service=self.cache_service,
            tmdb_service=self.tmdb_service,
        )

        total = len(self.media_files)
        success_count = 0
        failed_count = 0

        for i, media_file in enumerate(self.media_files):
            # Update status
            self.status_label.setText(
                f"Preview {i + 1}/{total}: {media_file.original_filename}"
            )

            # Run preview
            success, new_filename, new_path = organizer.preview(media_file)

            # Update table
            if success:
                success_count += 1
                # Update new name column
                new_name_item = QTableWidgetItem(new_filename)
                new_name_item.setForeground(Qt.GlobalColor.darkGreen)
                self.table_files.setItem(i, 4, new_name_item)

                # Update status
                status_item = QTableWidgetItem("✓ Listo")
                status_item.setForeground(Qt.GlobalColor.darkGreen)
                self.table_files.setItem(i, 5, status_item)
            else:
                failed_count += 1
                # Update new name column with error
                new_name_item = QTableWidgetItem("Error")
                new_name_item.setForeground(Qt.GlobalColor.darkRed)
                self.table_files.setItem(i, 4, new_name_item)

                # Update status with error message
                status_item = QTableWidgetItem("✗ Error")
                status_item.setForeground(Qt.GlobalColor.darkRed)
                self.table_files.setItem(i, 5, status_item)

            # Update progress
            progress = int(((i + 1) / total) * 100)
            self.progress_bar.setValue(progress)

        # Show summary
        summary = f"Vista previa completada: {success_count} listo(s)"
        if failed_count > 0:
            summary += f" | {failed_count} con error(es)"

        self.status_label.setText(summary)
        self.btn_preview.setEnabled(True)
        self.btn_process.setEnabled(True)

        if failed_count > 0:
            QMessageBox.warning(
                self,
                "Advertencia",
                f"La vista previa mostró {failed_count} error(es).\n{summary}",
            )
        else:
            QMessageBox.information(
                self,
                "Vista Previa",
                f"Todos los {success_count} archivos pueden ser organizados.\n\n{summary}",
            )

    def _on_process(self) -> None:
        """Handle process button click."""
        if not self.media_files:
            QMessageBox.warning(
                self, "Advertencia", "No hay archivos para procesar."
            )
            return

        if not self.tmdb_service:
            QMessageBox.warning(
                self,
                "Advertencia",
                "Configura tu API Key de TMDB en Configuración > API para obtener metadatos.",
            )
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_process.setEnabled(False)
        self.btn_process.setText("Procesando...")

        self.worker = WorkerThread(
            media_files=self.media_files,
            config=self.config,
            tmdb_service=self.tmdb_service,
            cache_service=self.cache_service,
        )
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.status.connect(self.status_label.setText)
        self.worker.finished.connect(self._on_processing_finished)
        self.worker.start()

    def _on_processing_finished(
        self, success: bool, processed: int, failed: int
    ) -> None:
        """Handle processing completion."""
        self.progress_bar.setVisible(False)
        self.btn_process.setEnabled(True)
        self.btn_process.setText("Procesar")

        # Update table status
        for row in range(self.table_files.rowCount()):
            status_item = QTableWidgetItem("Completado" if success else "Error")
            if success:
                status_item.setForeground(Qt.GlobalColor.green)
            else:
                status_item.setForeground(Qt.GlobalColor.red)
            self.table_files.setItem(row, 4, status_item)

        # Show summary
        summary = f"Procesados: {processed}"
        if failed > 0:
            summary += f" | Fallidos: {failed}"

        self.status_label.setText(summary)

        if success:
            QMessageBox.information(
                self, "Éxito", f"Todos los archivos fueron procesados correctamente.\n{summary}"
            )
        else:
            QMessageBox.warning(
                self,
                "Advertencia",
                f"Se completó el procesamiento con errores.\n{summary}",
            )

    def closeEvent(self, event) -> None:
        """Handle window close event."""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        event.accept()


