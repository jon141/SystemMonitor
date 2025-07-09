import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QGridLayout, QScrollArea, QGroupBox, QFrame)
from widgets.system_widgets import (RamWidget, DiskWidget, NetworkWidget, BatteryWidget,
                                    SystemInfoWidget, ProcessListWidget, DiskIOWidget,
                                    CpuInfoWidget, NetworkHistoryWidget, CpuCircleWidget, CpuCoreBarsWidget, CpuHistoryWidget)
from monitor.system_stats import get_all_system_stats
from PySide6.QtCore import QTimer
from PySide6.QtGui import QFont


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Monitor Dashboard")
        self.setMinimumSize(1200, 950)
        self.resize(1250, 950)

        # Hauptlayout
        main_layout = QVBoxLayout()

        # CPU-Sektion (Gruppe 1) - erweitert
        cpu_group = self.create_group_box("CPU Performance")
        cpu_group.setMinimumSize(1150, 225)
        cpu_layout = QHBoxLayout()

        self.cpu_circle = CpuCircleWidget()
        self.cpu_bars = CpuCoreBarsWidget()
        self.cpu_history = CpuHistoryWidget()
        self.cpu_info = CpuInfoWidget()  # Neues Widget für CPU-Info

        cpu_layout.addWidget(self.cpu_circle)
        cpu_layout.addWidget(self.cpu_bars)
        cpu_layout.addWidget(self.cpu_history)
        cpu_layout.addWidget(self.cpu_info)
        cpu_group.setLayout(cpu_layout)

        # Memory & Storage Sektion (Gruppe 2)
        memory_group = self.create_group_box("Memory / Storage")
        memory_layout = QHBoxLayout()

        self.ram_widget = RamWidget()
        self.disk_widget = DiskWidget()
        self.disk_io_widget = DiskIOWidget()

        memory_layout.addWidget(self.ram_widget)
        memory_layout.addWidget(self.disk_widget)
        memory_layout.addWidget(self.disk_io_widget)
        memory_group.setLayout(memory_layout)

        # Network & Power Sektion (Gruppe 3) - erweitert
        network_group = self.create_group_box("Network / Power")
        network_group.setMinimumSize(1150, 225)
        network_layout = QHBoxLayout()

        self.network_widget = NetworkWidget()
        self.network_history = NetworkHistoryWidget()  # Neues Widget für Netzwerk-Verlauf
        self.battery_widget = BatteryWidget()

        network_layout.addWidget(self.network_widget)
        network_layout.addWidget(self.network_history)
        network_layout.addWidget(self.battery_widget)
        network_group.setLayout(network_layout)

        # System Info & Processes Sektion (Gruppe 4)
        system_group = self.create_group_box("System Info / Processes")
        system_group.setMinimumSize(1150, 250)
        system_layout = QHBoxLayout()

        self.system_info_widget = SystemInfoWidget()
        self.process_list_widget = ProcessListWidget()

        system_layout.addWidget(self.system_info_widget)
        system_layout.addWidget(self.process_list_widget)
        system_group.setLayout(system_layout)

        # Alle Gruppen zum Hauptlayout hinzufügen
        main_layout.addWidget(cpu_group)
        main_layout.addWidget(memory_group)
        main_layout.addWidget(network_group)
        main_layout.addWidget(system_group)

        # Scroll Area für bessere Übersicht
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(main_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        # Hauptlayout mit Scroll Area
        final_layout = QVBoxLayout()
        final_layout.addWidget(scroll_area)
        self.setLayout(final_layout)

        # Styling
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                color: #ffffff;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #333333;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #1f1f1f;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
                color: #29b6f6;
            }
            QScrollArea {
                border: none;
                background-color: #1a1a1a;
            }
            QScrollBar:vertical {
                background: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #555555;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #666666;
            }
        """)

        # Timer für Updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # aktualisiere alle 1 Sekunde

        # Erste Aktualisierung
        self.update_stats()

    def create_group_box(self, title):
        """Erstellt eine GroupBox mit einheitlichem Styling"""
        group = QGroupBox(title)
        group.setMinimumHeight(180)
        return group

    def update_stats(self):
        """Aktualisiert alle Widget-Daten"""
        try:
            # Alle Systemdaten abrufen
            stats = get_all_system_stats()

            # CPU Widgets aktualisieren
            cpu = stats["cpu"]
            self.cpu_circle.set_auslastung(cpu["auslastung_prozent"])
            self.cpu_bars.set_usages(cpu["alle_kerne"])
            self.cpu_history.add_value(cpu["auslastung_prozent"])
            self.cpu_info.set_cpu_info(cpu, stats["boot"])  # Neues Widget aktualisieren

            # Memory & Storage Widgets aktualisieren
            self.ram_widget.set_ram_data(stats["ram"])
            self.disk_widget.set_disk_data(stats["usage"])
            self.disk_io_widget.set_disk_io_data(stats["io"])

            # Network & Power Widgets aktualisieren
            self.network_widget.set_network_data(
                stats["netzwerk"],
                stats["internet"],
                stats["network_interfaces"]

            )
            self.network_history.add_network_data(stats["netzwerk"])  # Neues Widget aktualisieren
            self.battery_widget.set_battery_data(stats["battery"])

            # System Info und Prozesse aktualisieren
            self.system_info_widget.set_system_data(stats["system_info"], stats["boot"])
            self.process_list_widget.set_processes(stats["cpu_prozesses"])

        except Exception as e:
            print(f"Fehler beim Aktualisieren der Stats: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())