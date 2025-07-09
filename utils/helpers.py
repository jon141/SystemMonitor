
import os

def print_dict(d, indent=0):
    """
    Gibt ein Dictionary schön formatiert aus, auch mit verschachtelten dicts oder Listen.
    """
    for key, value in d.items():
        prefix = "  " * indent + f"- {key}: "

        if isinstance(value, dict):
            print(prefix)
            print_dict(value, indent + 1)

        elif isinstance(value, list):
            print(prefix + "[")
            for item in value:
                if isinstance(item, dict):
                    print_dict(item, indent + 2)
                else:
                    print("  " * (indent + 2) + f"- {item}")
            print("  " * indent + "]")

        else:
            print(prefix + str(value))


def format_bytes(size, unit='auto', precision=2):
    if unit == 'auto':
        if size >= 1024**3:
            unit = 'GB'
        elif size >= 1024**2:
            unit = 'MB'
        else:
            unit = 'KB'

    if unit == 'GB':
        return f"{size / 1024**3:.{precision}f} GB"
    elif unit == 'MB':
        return f"{size / 1024**2:.{precision}f} MB"
    elif unit == 'KB':
        return f"{size / 1024:.{precision}f} KB"
    else:
        return f"{size} B"


def clear_console_1():
    os.system('cls' if os.name == 'nt' else 'clear')

def clear_console_2():
    print("\033c", end="")
