from collections import deque
import time


class PulseProcessor:
    def __init__(self, window_size=5, baseline_window=50, min_peak_interval=0.3,
                 rise_threshold_ratio=0.5, min_bpm=40, max_bpm=180, bpm_history_size=5):
        self.window_size = window_size
        self.min_peak_interval = min_peak_interval
        self.rise_threshold_ratio = rise_threshold_ratio
        self.min_bpm = min_bpm
        self.max_bpm = max_bpm

        self.buffer = deque(maxlen=window_size)
        self.recent_values = deque(maxlen=baseline_window)
        self.last_peak_time = None
        self.bpm_history = deque(maxlen=bpm_history_size)
        self.last_smoothed = None

    def _smooth(self, value):
        self.buffer.append(value)
        return sum(self.buffer) / len(self.buffer)

    def process_sample(self, raw_value):
        """
        Devuelve un dict {'bpm': float, 'peak_time': float} si se confirma un latido,
        o None si no hay nada nuevo que reportar.
        """
        smoothed = self._smooth(raw_value)
        self.recent_values.append(smoothed)
        now = time.time()

        if len(self.recent_values) < 10:
            self.last_smoothed = smoothed
            return None

        local_min = min(self.recent_values)
        local_max = max(self.recent_values)
        local_range = local_max - local_min

        if local_range < 3:
            self.last_smoothed = smoothed
            return None

        dynamic_threshold = local_min + local_range * self.rise_threshold_ratio

        was_below = self.last_smoothed is not None and self.last_smoothed <= dynamic_threshold
        is_above = smoothed > dynamic_threshold
        enough_time_passed = (
            self.last_peak_time is None
            or (now - self.last_peak_time) > self.min_peak_interval
        )

        result = None
        if was_below and is_above and enough_time_passed:
            if self.last_peak_time is not None:
                interval = now - self.last_peak_time
                bpm = 60 / interval

                if self.min_bpm <= bpm <= self.max_bpm:
                    self.bpm_history.append(bpm)
                    self.last_peak_time = now
                    result = {"bpm": self._average_bpm(), "peak_time": now}
            else:
                self.last_peak_time = now

        self.last_smoothed = smoothed
        return result

    def _average_bpm(self):
        return sum(self.bpm_history) / len(self.bpm_history)