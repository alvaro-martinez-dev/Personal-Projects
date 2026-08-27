import yaml
from pathlib import Path

from src.serial_reader import SerialReader
from src.signal_processing import PulseProcessor


def load_config(path="config.yml"):
    config_path = Path(__file__).parent / path
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


config = load_config()

serial_cfg = config["serial"]
sp_cfg = config["signal_processing"]
cross_cfg = config["cross_sensor"]

MAX_CROSS_SENSOR_DELAY = cross_cfg["max_delay"]

reader = SerialReader(
    baudrate=serial_cfg["baudrate"],
    timeout=serial_cfg["timeout"],
    port_keywords=serial_cfg["port_keywords"],
)
reader.connect()

processor_1 = PulseProcessor(
    window_size=sp_cfg["window_size"],
    baseline_window=sp_cfg["baseline_window"],
    min_peak_interval=sp_cfg["min_peak_interval"],
    rise_threshold_ratio=sp_cfg["rise_threshold_ratio"],
    min_bpm=sp_cfg["min_bpm"],
    max_bpm=sp_cfg["max_bpm"],
    bpm_history_size=sp_cfg["bpm_history_size"],
)
processor_2 = PulseProcessor(
    window_size=sp_cfg["window_size"],
    baseline_window=sp_cfg["baseline_window"],
    min_peak_interval=sp_cfg["min_peak_interval"],
    rise_threshold_ratio=sp_cfg["rise_threshold_ratio"],
    min_bpm=sp_cfg["min_bpm"],
    max_bpm=sp_cfg["max_bpm"],
    bpm_history_size=sp_cfg["bpm_history_size"],
)

pending_peak_1 = None
pending_peak_2 = None

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
            print(f"  [Sensor 1] pico individual, BPM={result_1['bpm']:.1f}")
            pending_peak_1 = result_1

        if result_2 is not None:
            print(f"  [Sensor 2] pico individual, BPM={result_2['bpm']:.1f}")
            pending_peak_2 = result_2

        if pending_peak_1 is not None and pending_peak_2 is not None:
            delay = abs(pending_peak_1["peak_time"] - pending_peak_2["peak_time"])
            print(f"  → delay entre sensores: {delay*1000:.0f}ms")
            if delay <= MAX_CROSS_SENSOR_DELAY:
                bpm_avg = (pending_peak_1["bpm"] + pending_peak_2["bpm"]) / 2
                print(f"✔ Latido confirmado en ambos sensores — BPM: {bpm_avg:.1f}")
                pending_peak_1 = None
                pending_peak_2 = None
            elif delay > MAX_CROSS_SENSOR_DELAY * 3:
                if pending_peak_1["peak_time"] < pending_peak_2["peak_time"]:
                    pending_peak_1 = None
                else:
                    pending_peak_2 = None

except KeyboardInterrupt:
    print("\nDeteniendo...")
    reader.close()