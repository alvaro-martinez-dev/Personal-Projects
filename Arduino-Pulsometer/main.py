from src.serial_reader import SerialReader
from src.signal_processing import PulseProcessor

MAX_CROSS_SENSOR_DELAY = 0.15  # segundos de margen para considerar que es el "mismo" latido

reader = SerialReader()
reader.connect()

processor_1 = PulseProcessor()
processor_2 = PulseProcessor()

pending_peak_1 = None  # último pico de sensor 1 aún no confirmado por sensor 2
pending_peak_2 = None  # último pico de sensor 2 aún no confirmado por sensor 1

print("Leyendo... pon los dedos en los sensores y espera unos segundos (calibración).")

try:
    while True:
        values = reader.read_values()
        if values is None:
            continue

        v1, v2 = values
        result_1 = processor_1.process_sample(v1)
        result_2 = processor_2.process_sample(v2)

        if result_1 is not None:
            pending_peak_1 = result_1

        if result_2 is not None:
            pending_peak_2 = result_2

        # Comprobar si hay confirmación cruzada
        if pending_peak_1 is not None and pending_peak_2 is not None:
            delay = abs(pending_peak_1["peak_time"] - pending_peak_2["peak_time"])
            if delay <= MAX_CROSS_SENSOR_DELAY:
                bpm_avg = (pending_peak_1["bpm"] + pending_peak_2["bpm"]) / 2
                print(f"✔ Latido confirmado en ambos sensores — BPM: {bpm_avg:.1f}")
                pending_peak_1 = None
                pending_peak_2 = None
            elif delay > MAX_CROSS_SENSOR_DELAY * 3:
                # Demasiado desfasados como para ser el mismo latido, descarta el más antiguo
                if pending_peak_1["peak_time"] < pending_peak_2["peak_time"]:
                    pending_peak_1 = None
                else:
                    pending_peak_2 = None

except KeyboardInterrupt:
    print("\nDeteniendo...")
    reader.close()