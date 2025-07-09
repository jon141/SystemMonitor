import psutil
import datetime
from utils.helpers import format_bytes
from collections import defaultdict
import time
import socket
import platform


def get_cpu():
    usage = psutil.cpu_percent(interval=0.2)
    core_usages = psutil.cpu_percent(interval=0.2, percpu=True)
    freq = psutil.cpu_freq()
    takt_current = freq.current if freq else 0
    return {
        "auslastung_prozent": usage,
        "alle_kerne": core_usages,
        "kern_anzahl": len(core_usages),
        "takt": takt_current,  # in MHz
        "takt_unit": f"{takt_current:.0f} MHz" if freq else None
    }



def get_ram():
    ram = psutil.virtual_memory()
    return {
        "genutzt_bytes": ram.used,
        "gesamt_bytes": ram.total,
        "frei_bytes": ram.available,

        "genutzt_unit": format_bytes(ram.used),
        "gesamt_unit": format_bytes(ram.total),
        "frei_unit": format_bytes(ram.available),

        "auslastung": ram.percent  # in %
    }

def get_netzwerk():
    net = psutil.net_io_counters()
    return {
        "gesendet_bytes": net.bytes_sent,
        "empfangen_bytes": net.bytes_recv,

        "gesendet_unit": format_bytes(net.bytes_sent),
        "empfangen_unit": format_bytes(net.bytes_recv)
    }

def get_boot():
    boot_timestamp = psutil.boot_time()
    boot_time = datetime.datetime.fromtimestamp(boot_timestamp)
    uptime = datetime.datetime.now() - boot_time
    return {
        "timestamp": boot_timestamp,
        "boot_string": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": str(uptime).split('.')[0],  # z. B. "3:12:45"
        "uptime_seconds": uptime.total_seconds()
    }


def get_active_cpu_processes(wait=0.2):
    stats = defaultdict(float)

    # 1. Initialisieren der CPU-Messung
    for proc in psutil.process_iter():
        try:
            proc.cpu_percent(interval=None)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # 2. Kurze Pause für Messung
    time.sleep(wait)

    # 3. Aktuelle CPU-Werte abfragen und nur Prozesse mit CPU > 0 speichern
    for proc in psutil.process_iter(['name', 'cpu_percent']):
        try:
            info = proc.info
            name = info['name'] or "unbekannt"
            cpu = info['cpu_percent'] or 0.0

            if cpu > 0:
                stats[name] += cpu
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # 4. Sortieren nach CPU-Auslastung absteigend
    sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)

    #print(sorted_stats)
    # 5. Ausgabe
    #for name, cpu in sorted_stats:
    #    print(f"{name}: CPU {cpu}%")
    #print(sorted_stats)
    return sorted_stats


def get_disk_usage():

    betriebssystem = platform.system().lower()
    if betriebssystem == 'linux' or betriebssystem == 'darwin':  # macOS ist 'Darwin'
        path = "/"
    elif betriebssystem == 'windows':
        path = "C:\\"
    else:
        path = "/"  # Fallback

    usage = psutil.disk_usage(path)
    return {
        "total_bytes": usage.total,
        "used_bytes": usage.used,
        "free_bytes": usage.free,

        "total_unit": format_bytes(usage.total),
        "used_unit": format_bytes(usage.used),
        "free_unit": format_bytes(usage.free),

        "percent": usage.percent
    }

def get_battery_info():
    battery = psutil.sensors_battery()
    if battery.secsleft == -2:
        secs_left = None
    else:
        secs_left = battery.secsleft
    if battery:
        return {
            "percent": battery.percent,
            "secsleft": secs_left,  # Sekunden bis leer/voll
            "power_plugged": battery.power_plugged
        }
    else:
        return None  # Akku nicht vorhanden

def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor()
    }

def get_disk_io():
    io = psutil.disk_io_counters()
    return {
        "read_bytes": io.read_bytes,
        "write_bytes": io.write_bytes,

        "read_unit": format_bytes(io.read_bytes),
        "write_unit": format_bytes(io.write_bytes),

        "read_count": io.read_count,
        "write_count": io.write_count
    }

def get_internet_connection(host="8.8.8.8", port=53, timeout=1):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return {"connection": True}
    except socket.error:
        return {"connection": False}


def get_network_interfaces():
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    interfaces = {}
    for intf, addr_list in addrs.items():
        ipv4_addresses = []
        for a in addr_list:
            if hasattr(a.family, 'name'):
                if a.family.name == 'AF_INET':
                    ipv4_addresses.append(str(a.address))
            else:
                # fallback für Windows (a.family ist int)
                if a.family == socket.AF_INET:
                    ipv4_addresses.append(str(a.address))

        interfaces[intf] = {
            "is_up": stats[intf].isup if intf in stats else None,
            "addresses": ipv4_addresses,
            "speed": stats[intf].speed if intf in stats else None
        }
    return interfaces



def get_all_system_stats():
    cpu = get_cpu()
    cpu_processes = get_active_cpu_processes()
    ram = get_ram()
    netzwerk = get_netzwerk()
    boot = get_boot()
    usage = get_disk_usage()
    battery = get_battery_info()
    system_info = get_system_info()
    time_jetzt = datetime.datetime.now()
    internet = get_internet_connection()
    io = get_disk_io()
    network_interfaces = get_network_interfaces()

    return {
        "cpu": cpu,
        "ram": ram,
        "boot": boot,
        "usage": usage,
        "battery": battery,
        "system_info": system_info,
        "cpu_prozesses": cpu_processes,
        "time_jetzt": time_jetzt,
        "time_jetzt_str": time_jetzt.strftime("%Y-%m-%d %H:%M:%S"),
        "io": io,
        "netzwerk": netzwerk,
        "internet": internet,
        "network_interfaces": network_interfaces,
    }


