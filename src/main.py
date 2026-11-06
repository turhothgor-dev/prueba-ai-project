"""MediaOrganizer - Main application entry point."""

import sys

from PyQt6.QtWidgets import QApplication

from src.core.config import Config
from src.gui.main_window import MainWindow


def main() -> int:
    """Main application entry point.

    Returns:
        Exit code
    """
    # Initialize configuration
    config = Config()

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("MediaOrganizer")
    app.setOrganizationName("MediaOrganizer")
    app.setApplicationVersion("0.1.0")

    # Create and show main window
    window = MainWindow(config)
    window.show()

    # Execute application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
