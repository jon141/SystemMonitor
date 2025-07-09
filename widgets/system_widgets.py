# widgets/system_widgets.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtGui import QPainter, QColor, QFont, QPen
from PySide6.QtCore import Qt
from collections import deque




class CpuCircleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.auslastung = 0.0  # CPU-Auslastung in %
        self.setMinimumSize(160, 160)

    def set_auslastung(self, value: float):
        self.auslastung = max(0.0, min(100.0, value))  # Clamp zwischen 0 und 100
        self.update()

    def paintEvent(self, event):
        size = min(self.width(), self.height())
        background_radius = size / 2 - 4
        progress_radius = background_radius - 3

        center = self.rect().center()

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Hintergrundfarbe (dunkler Kreis)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#1f1f28"))
        painter.drawEllipse(center, background_radius, background_radius)

        # Fortschrittsbogen (blau, wie im Screenshot)
        pen = QPen(QColor("#29b6f6"))
        pen.setWidth(8)
        pen.setCapStyle(Qt.FlatCap)
        painter.setPen(pen)

        start_angle = -90 * 16
        span_angle = -int(self.auslastung / 100 * 360 * 16)
        painter.drawArc(center.x() - progress_radius, center.y() - progress_radius,
                        2 * progress_radius, 2 * progress_radius, start_angle, span_angle)

        # Text: zentrierte CPU-Auslastung
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        painter.setFont(font)
        text = f"{self.auslastung:.1f} %"
        painter.drawText(self.rect(), Qt.AlignCenter, text)

        painter.end()


class CpuCoreBarsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.usages = []
        self.setMinimumSize(200, 120)

    def set_usages(self, usages: list[float]):
        self.usages = usages
        self.update()

    def paintEvent(self, event):
        if not self.usages:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Berechne Layout-Parameter
        num_cores = len(self.usages)
        margin = 10
        spacing = 3
        available_width = self.width() - 2 * margin
        bar_width = max(8, (available_width - (num_cores - 1) * spacing) / num_cores)
        bar_width = min(bar_width, 20)  # Maximale Breite erhöht für Prozent-Anzeige
        max_height = self.height() - 40  # Platz für Labels

        # Bestimme Farbe basierend auf Auslastung
        def get_color(usage):
            if usage < 30:
                return QColor("#4CAF50")  # Grün
            elif usage < 70:
                return QColor("#FF9800")  # Orange
            else:
                return QColor("#F44336")  # Rot

        for i, usage in enumerate(self.usages):
            # Balken-Position berechnen
            x = margin + i * (bar_width + spacing)
            height = max(2, max_height * usage / 100)
            y = self.height() - height - 25

            # Hintergrund-Balken (dunkel)
            painter.setBrush(QColor("#2a2a2a"))
            painter.setPen(Qt.NoPen)
            painter.drawRect(int(x), margin, int(bar_width), max_height)

            # Fortschritts-Balken (farbig)
            painter.setBrush(get_color(usage))
            painter.drawRect(int(x), int(y), int(bar_width), int(height))

            # Core-Nummer als Label (bei 1 anfangen)
            painter.setPen(QColor("#ffffff"))
            font = QFont("Segoe UI", 8)
            painter.setFont(font)
            core_text = f"{i + 1}"
            text_rect = painter.fontMetrics().boundingRect(core_text)
            text_x = x + (bar_width - text_rect.width()) / 2
            text_y = self.height() - 10
            painter.drawText(int(text_x), int(text_y), core_text)

            # Prozent-Wert über dem Balken
            percent_text = f"{usage:.0f}%"
            painter.setPen(QColor("#ffffff"))
            font_small = QFont("Segoe UI", 7)
            painter.setFont(font_small)
            percent_rect = painter.fontMetrics().boundingRect(percent_text)
            percent_x = x + (bar_width - percent_rect.width()) / 2
            percent_y = max(15, y - 5)
            painter.drawText(int(percent_x), int(percent_y), percent_text)

        painter.end()


class CpuHistoryWidget(QWidget):
    """Ein Widget für die CPU-Verlaufsgrafik"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = []  # Liste der letzten CPU-Werte
        self.max_points = 60  # 60 Sekunden History
        self.setMinimumSize(300, 150)

    def add_value(self, value: float):
        """Fügt einen neuen CPU-Wert zur History hinzu"""
        self.history.append(value)
        if len(self.history) > self.max_points:
            self.history.pop(0)
        self.update()

    def paintEvent(self, event):
        if len(self.history) < 2:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Margins für Achsen-Labels
        left_margin = 35
        bottom_margin = 25
        top_margin = 10
        right_margin = 10

        # Verfügbare Zeichenfläche
        graph_width = self.width() - left_margin - right_margin
        graph_height = self.height() - top_margin - bottom_margin

        # Hintergrund
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        # Gitter-Linien und Y-Achse Beschriftung (0-100%)
        painter.setPen(QPen(QColor("#333333"), 1))
        font = QFont("Segoe UI", 8)
        painter.setFont(font)

        for i in range(6):  # 0, 20, 40, 60, 80, 100
            percent = i * 20
            y = top_margin + graph_height - (graph_height * percent / 100)

            # Horizontale Gitter-Linie
            painter.drawLine(left_margin, int(y),
                             left_margin + graph_width, int(y))

            # Y-Achse Beschriftung
            painter.setPen(QColor("#ffffff"))
            painter.drawText(5, int(y + 4), f"{percent}%")
            painter.setPen(QPen(QColor("#333333"), 1))

        # X-Achse Beschriftung (Zeit - aktueller Wert links)
        painter.setPen(QColor("#ffffff"))
        num_time_labels = 5
        for i in range(num_time_labels):
            # Zeit von 0s (links/jetzt) bis 60s (rechts/alt)
            seconds = i * 15  # 0, 15, 30, 45, 60
            x = left_margin + (graph_width * i / (num_time_labels - 1))

            if seconds == 0:
                label = "0s"
            else:
                label = f"{seconds}s"

            text_width = painter.fontMetrics().boundingRect(label).width()
            painter.drawText(int(x - text_width / 2), self.height() - 5, label)

        # CPU-Linie zeichnen (neuer Wert links, alte nach rechts)
        if len(self.history) > 1:
            painter.setPen(QPen(QColor("#29b6f6"), 2))

            points = []
            for i, value in enumerate(self.history):
                # Neuester Wert (letzter in der Liste) erscheint links
                # Ältere Werte wandern nach rechts
                reversed_index = len(self.history) - 1 - i
                x = left_margin + (graph_width * reversed_index / (self.max_points - 1))
                y = top_margin + graph_height - (graph_height * value / 100)
                points.append((int(x), int(y)))

            # Punkte sind jetzt in umgekehrter Reihenfolge, also umkehren für korrekte Linien
            points.reverse()

            # Linie zwischen den Punkten zeichnen
            for i in range(len(points) - 1):
                painter.drawLine(points[i][0], points[i][1],
                                 points[i + 1][0], points[i + 1][1])

        painter.end()

class RamWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.usage_percent = 0.0
        self.used_text = "0 GB"
        self.total_text = "0 GB"
        self.setMinimumSize(200, 80)

    def set_ram_data(self, ram_data):
        self.usage_percent = ram_data["auslastung"]
        self.used_text = ram_data["genutzt_unit"]
        self.total_text = ram_data["gesamt_unit"]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Hintergrund
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        # RAM-Balken
        bar_height = 20
        bar_y = 30
        bar_width = self.width() - 20

        # Hintergrund-Balken
        painter.setBrush(QColor("#2a2a2a"))
        painter.setPen(Qt.NoPen)
        painter.drawRect(10, bar_y, bar_width, bar_height)

        # Fortschritts-Balken
        progress_width = int(bar_width * self.usage_percent / 100)
        color = QColor("#FF5722") if self.usage_percent > 80 else QColor("#4CAF50")
        painter.setBrush(color)
        painter.drawRect(10, bar_y, progress_width, bar_height)

        # Text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 20, "RAM")

        font.setBold(False)
        painter.setFont(font)
        text = f"{self.used_text} / {self.total_text} ({self.usage_percent:.1f}%)"
        painter.drawText(10, 70, text)

        painter.end()


class CpuInfoWidget(QWidget):
    """Widget für CPU-Informationen (Kerne und Takt) - ohne Uptime"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.core_count = 0
        self.frequency = 0
        self.frequency_unit = "0 MHz"
        self.setMinimumSize(200, 80)

    def set_cpu_info(self, cpu_data, boot_data):
        self.core_count = cpu_data["kern_anzahl"]
        self.frequency = cpu_data["takt"]
        self.frequency_unit = cpu_data["takt_unit"] or "0 MHz"
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Hintergrund
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        # Text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 20, "CPU Info")

        font.setBold(False)
        painter.setFont(font)
        painter.drawText(10, 40, f"Kerne: {self.core_count}")
        painter.drawText(10, 60, f"Takt: {self.frequency_unit}")

        painter.end()


class NetworkHistoryWidget(QWidget):
    """Widget für Netzwerk-Verlaufsdiagramm mit Zeitachse und Skalierung"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sent_history = deque(maxlen=60)  # 60 Sekunden Verlauf
        self.recv_history = deque(maxlen=60)
        self.last_sent = 0
        self.last_recv = 0
        self.setMinimumSize(300, 160)

    def add_network_data(self, network_data):
        # Berechne Differenz zu letzter Messung für Rate
        current_sent = network_data["gesendet_bytes"]
        current_recv = network_data["empfangen_bytes"]

        if self.last_sent > 0:
            sent_rate = max(0, current_sent - self.last_sent)
            recv_rate = max(0, current_recv - self.last_recv)
        else:
            sent_rate = 0
            recv_rate = 0

        self.sent_history.append(sent_rate)
        self.recv_history.append(recv_rate)
        self.last_sent = current_sent
        self.last_recv = current_recv
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Hintergrund
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        # Titel
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 15, "Netzwerk Verlauf")

        if len(self.sent_history) < 2:
            painter.end()
            return

        # Diagramm-Bereich
        graph_x = 40
        graph_y = 25
        graph_width = self.width() - 60
        graph_height = 80

        # Hintergrund des Diagramms
        painter.setBrush(QColor("#2a2a2a"))
        painter.setPen(Qt.NoPen)
        painter.drawRect(graph_x, graph_y, graph_width, graph_height)

        # Maximale Werte finden für Skalierung
        max_sent = max(self.sent_history) if self.sent_history else 1
        max_recv = max(self.recv_history) if self.recv_history else 1
        max_value = max(max_sent, max_recv, 1)

        # Y-Achse Skalierung zeichnen
        painter.setPen(QColor("#555555"))
        font_small = QFont("Segoe UI", 8)
        painter.setFont(font_small)

        # Y-Achse Labels (0%, 50%, 100%)
        painter.drawText(5, graph_y + graph_height, "0")
        painter.drawText(5, graph_y + graph_height // 2, self._format_bytes(max_value // 2))
        painter.drawText(5, graph_y + 10, self._format_bytes(max_value))

        # Horizontale Gitterlinien
        painter.setPen(QPen(QColor("#333333"), 1))
        painter.drawLine(graph_x, graph_y + graph_height // 2, graph_x + graph_width, graph_y + graph_height // 2)

        # Linien zeichnen
        if len(self.sent_history) > 1:
            # Gesendet (rot)
            painter.setPen(QPen(QColor("#FF5722"), 2))
            points = []
            for i, value in enumerate(self.sent_history):
                x = graph_x + int(i * graph_width / max(len(self.sent_history) - 1, 1))
                y = graph_y + graph_height - int(value * graph_height / max_value)
                points.append((x, y))

            for i in range(len(points) - 1):
                painter.drawLine(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])

            # Empfangen (grün)
            painter.setPen(QPen(QColor("#4CAF50"), 2))
            points = []
            for i, value in enumerate(self.recv_history):
                x = graph_x + int(i * graph_width / max(len(self.recv_history) - 1, 1))
                y = graph_y + graph_height - int(value * graph_height / max_value)
                points.append((x, y))

            for i in range(len(points) - 1):
                painter.drawLine(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])

        # Zeitachse Labels
        painter.setPen(QColor("#555555"))
        painter.setFont(font_small)
        painter.drawText(graph_x, graph_y + graph_height + 15, "-60s")
        painter.drawText(graph_x + graph_width // 2 - 10, graph_y + graph_height + 15, "-30s")
        painter.drawText(graph_x + graph_width - 15, graph_y + graph_height + 15, "0s")

        # Mehr Platz vor den Labels
        y_labels = graph_y + graph_height + 35

        # Legende mit mehr Abstand
        painter.setPen(QColor("#FF5722"))
        painter.drawText(10, y_labels, "↑ Gesendet")
        painter.setPen(QColor("#4CAF50"))
        painter.drawText(100, y_labels, "↓ Empfangen")

        # Aktuelle Werte
        if self.sent_history and self.recv_history:
            current_sent = self.sent_history[-1]
            current_recv = self.recv_history[-1]
            font.setBold(False)
            painter.setFont(font)

            # ↑ Gesendet in orange
            painter.setPen(QColor("#FF5722"))
            painter.drawText(self.width() - 120, y_labels,
                             f"↑{self._format_bytes(current_sent)}/s")

            # ↓ Empfangen in grün
            painter.setPen(QColor("#4CAF50"))
            painter.drawText(self.width() - 120, y_labels + 15,
                             f"↓{self._format_bytes(current_recv)}/s")

        painter.end()

    def _format_bytes(self, bytes_val):
        """Formatiert Bytes in lesbare Einheiten"""
        if bytes_val >= 1024 ** 3:
            return f"{bytes_val / 1024 ** 3:.1f}GB"
        elif bytes_val >= 1024 ** 2:
            return f"{bytes_val / 1024 ** 2:.1f}MB"
        elif bytes_val >= 1024:
            return f"{bytes_val / 1024:.1f}KB"
        else:
            return f"{bytes_val}B"


class DiskWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.usage_percent = 0.0
        self.used_text = "0 GB"
        self.total_text = "0 GB"
        self.setMinimumSize(200, 80)

    def set_disk_data(self, disk_data):
        self.usage_percent = disk_data["percent"]
        self.used_text = disk_data["used_unit"]
        self.total_text = disk_data["total_unit"]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Hintergrund
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        # Disk-Balken
        bar_height = 20
        bar_y = 30
        bar_width = self.width() - 20

        # Hintergrund-Balken
        painter.setBrush(QColor("#2a2a2a"))
        painter.setPen(Qt.NoPen)
        painter.drawRect(10, bar_y, bar_width, bar_height)

        # Fortschritts-Balken
        progress_width = int(bar_width * self.usage_percent / 100)
        color = QColor("#FF5722") if self.usage_percent > 85 else QColor("#2196F3")
        painter.setBrush(color)
        painter.drawRect(10, bar_y, progress_width, bar_height)

        # Text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 20, "Festplatte")

        font.setBold(False)
        painter.setFont(font)
        text = f"{self.used_text} / {self.total_text} ({self.usage_percent:.1f}%)"
        painter.drawText(10, 70, text)

        painter.end()


class NetworkWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.sent_text = "0 B"
        self.recv_text = "0 B"
        self.is_connected = False
        self.interfaces = {}
        self.setMinimumSize(300, 120)

    def set_network_data(self, network_data, internet_data, interfaces_data):
        self.sent_text = network_data["gesendet_unit"]
        self.recv_text = network_data["empfangen_unit"]
        self.is_connected = internet_data["connection"]
        self.interfaces = interfaces_data
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Hintergrund
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        # Internet-Status-Indikator
        status_color = QColor("#4CAF50") if self.is_connected else QColor("#F44336")
        painter.setBrush(status_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(self.width() - 20, 10, 12, 12)

        # Text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 20, "Netzwerk")

        # Internet-Status
        font.setBold(False)
        painter.setFont(font)
        status_text = "Online" if self.is_connected else "Offline"
        painter.drawText(self.width() - 70, 20, status_text)

        # Traffic
        #painter.setPen(QColor("#ffffff"))

        painter.setPen(QColor("#FFF59D"))
        painter.drawText(10, 40, f"Gesendet / Empfangen seit Boot:")

        painter.setPen(QColor("#4CAF50"))
        painter.drawText(10, 60, f"     ↑ Gesendet: {self.sent_text}")

        painter.setPen(QColor("#FF5722"))
        painter.drawText(10, 80, f"     ↓ Empfangen: {self.recv_text}")

        painter.setPen(QColor("#ffffff"))

        # Aktive Interfaces
        y_offset = 100
        active_interfaces = [name for name, info in self.interfaces.items()
                             if info["is_up"] and info["addresses"]]
        if active_interfaces:
            interface_text = f"Aktiv:"
            for item in active_interfaces:
                ip = self.interfaces[item]["addresses"][0]
                interface_text += f" {item} ({ip}),"
            interface_text = interface_text[:-1]

            painter.setPen(QColor("#FFF59D"))
            painter.drawText(10, y_offset, interface_text)
            painter.setPen(QColor("#FFFFFF"))

        painter.end()


class DiskIOWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.read_text = "0 B"
        self.write_text = "0 B"
        self.read_count = 0
        self.write_count = 0
        self.setMinimumSize(280, 100)

    def set_disk_io_data(self, io_data):
        self.read_text = io_data["read_unit"]
        self.write_text = io_data["write_unit"]
        self.read_count = io_data["read_count"]
        self.write_count = io_data["write_count"]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Hintergrund
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        # Text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 20, "Disk I/O")

        font.setBold(False)
        painter.setFont(font)

        painter.setPen(QColor("#FFF59D"))
        painter.drawText(10, 40, f"Gelesen / Geschrieben seit Boot:")

        painter.setPen(QColor("#4CAF50"))
        painter.drawText(10, 60, f"     Gelesen: {self.read_text}")

        painter.setPen(QColor("#FF5722"))
        painter.drawText(10, 80, f"     Geschrieben: {self.write_text}")

        painter.setPen(QColor("#ffffff"))
        painter.drawText(10, 100, f"Ops: {self.read_count:,} / {self.write_count:,}")


        painter.end()


class BatteryWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.percent = 0.0
        self.plugged = False
        self.has_battery = False
        self.setMinimumSize(200, 80)

    def set_battery_data(self, battery_data):
        if battery_data:
            self.has_battery = True
            self.percent = battery_data["percent"]
            self.plugged = battery_data["power_plugged"]
        else:
            self.has_battery = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Hintergrund
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        if not self.has_battery:
            painter.setPen(QColor("#ffffff"))
            font = QFont("Segoe UI", 10)
            painter.setFont(font)
            painter.drawText(10, 40, "Kein Akku vorhanden")
            painter.end()
            return

        # Akku-Symbol zeichnen
        battery_width = 60
        battery_height = 30
        battery_x = 10
        battery_y = 25

        # Akku-Rahmen
        painter.setPen(QPen(QColor("#ffffff"), 2))
        painter.setBrush(QColor("#2a2a2a"))
        painter.drawRect(battery_x, battery_y, battery_width, battery_height)

        # Akku-Spitze
        painter.drawRect(battery_x + battery_width, battery_y + 8, 4, 14)

        # Akku-Füllung
        fill_width = int((battery_width - 4) * self.percent / 100)
        if self.percent > 20:
            fill_color = QColor("#4CAF50")
        elif self.percent > 10:
            fill_color = QColor("#FF9800")
        else:
            fill_color = QColor("#F44336")

        painter.setBrush(fill_color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(battery_x + 2, battery_y + 2, fill_width, battery_height - 4)

        # Text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(80, 35, f"{self.percent:.0f}%")

        font.setBold(False)
        painter.setFont(font)
        status = "Lädt" if self.plugged else "Entlädt"
        painter.drawText(80, 50, status)

        painter.end()


class SystemInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hostname = ""
        self.system = ""
        self.uptime = ""
        self.boot_time = ""
        self.setMinimumSize(300, 120)

    def set_system_data(self, system_data, boot_data):
        self.hostname = system_data["hostname"]
        self.system = f"{system_data['system']} {system_data['release']}"
        self.uptime = boot_data["uptime"]
        self.boot_time = boot_data["boot_string"]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Hintergrund
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        # Text
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 20, "System Info")

        font.setBold(False)
        painter.setFont(font)
        painter.drawText(10, 40, f"Host: {self.hostname}")
        painter.drawText(10, 60, f"OS: {self.system}")
        painter.drawText(10, 80, f"Uptime: {self.uptime}")
        painter.drawText(10, 100, f"Boot: {self.boot_time}")

        painter.end()


class ProcessListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.processes = []
        self.setMinimumSize(300, 200)

    def set_processes(self, processes):
        # Nur die Top 10 Prozesse anzeigen
        self.processes = processes[:10]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Hintergrund
        painter.fillRect(self.rect(), QColor("#1a1a1a"))

        # Header
        painter.setPen(QColor("#ffffff"))
        font = QFont("Segoe UI", 10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(10, 20, "Top CPU Prozesse")

        # Prozesse auflisten
        font.setBold(False)
        painter.setFont(font)
        y_offset = 40

        for i, (name, cpu_usage) in enumerate(self.processes):
            if y_offset > self.height() - 20:
                break

            # Prozessname (gekürzt falls zu lang)
            display_name = name[:25] + "..." if len(name) > 25 else name
            painter.drawText(10, y_offset, display_name)

            # CPU-Nutzung
            painter.setPen(QColor("#F44336"))
            painter.drawText(self.width() - 60, y_offset, f"{cpu_usage:.1f}%")
            painter.setPen(QColor("#ffffff"))


            y_offset += 18

        painter.end()