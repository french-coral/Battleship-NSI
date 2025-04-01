import serial.tools.list_ports

# Cherche tous les ports disponibles
ports = list(serial.tools.list_ports.comports())

feathers = []  # Stocke les objets serial.Serial pour chaque Feather trouvée

for port in ports:
    if "Feather" in port.description:  # Filtre les périphériques Adafruit
        try:
            ser = serial.Serial(port.device, 115200, timeout=1)
            feathers.append(ser)
            print(f"Connecté à {port.device}")
        except Exception as e:
            print(f"Erreur avec {port.device}: {e}")

# Maintenant, "feathers" contient toutes les Feather connectées
