import queue
import threading
import time
from pathlib import Path

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

try:
    import numpy as np
except ImportError:
    np = None

try:
    import sounddevice as sd
except ImportError:
    sd = None

try:
    import whisper
except ImportError:
    whisper = None


class SpeechToTextNode(Node):
    def __init__(self) -> None:
        super().__init__("speech_to_text_node")
        self.voice_pub = self.create_publisher(String, "/voice_text", 10)
        self.declare_parameter("model_name", "base")
        self.declare_parameter("sample_rate", 16000)
        self.declare_parameter("audio_device_index", -1)
        self.declare_parameter("chunk_seconds", 4.0)
        self.declare_parameter("language", "en")
        self.declare_parameter("energy_threshold", 0.0005)
        self.declare_parameter("poll_interval_seconds", 0.25)
        self.declare_parameter("audio_device", "")
        self.declare_parameter("auto_listen", True)
        self.declare_parameter("push_to_talk", False)
        self.declare_parameter("list_audio_devices", False)
        self.declare_parameter("audio_file", "")
        self.declare_parameter("transcribe_file_on_startup", True)
        self.declare_parameter("fallback_to_device_sample_rate", True)
        self.declare_parameter("log_audio_levels", False)
        self.declare_parameter("debug_capture", False)
        self.declare_parameter("debug_every_n_chunks", 1)
        self.declare_parameter("auto_calibrate", False)
        self.declare_parameter("calibration_seconds", 2.0)
        self.declare_parameter("calibration_multiplier", 3.0)
        self.declare_parameter("minimum_energy_threshold", 0.001)

        self.model_name = self.get_parameter("model_name").get_parameter_value().string_value
        self.sample_rate = (
            self.get_parameter("sample_rate").get_parameter_value().integer_value
        )
        self.audio_device_index = (
            self.get_parameter("audio_device_index").get_parameter_value().integer_value
        )
        self.chunk_seconds = (
            self.get_parameter("chunk_seconds").get_parameter_value().double_value
        )
        self.language = self.get_parameter("language").get_parameter_value().string_value
        self.energy_threshold = (
            self.get_parameter("energy_threshold").get_parameter_value().double_value
        )
        self.poll_interval_seconds = (
            self.get_parameter("poll_interval_seconds").get_parameter_value().double_value
        )
        self.audio_device = (
            self.get_parameter("audio_device").get_parameter_value().string_value or None
        )
        self.auto_listen = (
            self.get_parameter("auto_listen").get_parameter_value().bool_value
        )
        self.push_to_talk = (
            self.get_parameter("push_to_talk").get_parameter_value().bool_value
        )
        self.list_audio_devices = (
            self.get_parameter("list_audio_devices").get_parameter_value().bool_value
        )
        self.audio_file = (
            self.get_parameter("audio_file").get_parameter_value().string_value or None
        )
        self.transcribe_file_on_startup = (
            self.get_parameter("transcribe_file_on_startup").get_parameter_value().bool_value
        )
        self.fallback_to_device_sample_rate = (
            self.get_parameter("fallback_to_device_sample_rate")
            .get_parameter_value()
            .bool_value
        )
        self.log_audio_levels = (
            self.get_parameter("log_audio_levels").get_parameter_value().bool_value
        )
        self.debug_capture = (
            self.get_parameter("debug_capture").get_parameter_value().bool_value
        )
        self.debug_every_n_chunks = max(
            1, self.get_parameter("debug_every_n_chunks").get_parameter_value().integer_value
        )
        self.auto_calibrate = (
            self.get_parameter("auto_calibrate").get_parameter_value().bool_value
        )
        self.calibration_seconds = (
            self.get_parameter("calibration_seconds").get_parameter_value().double_value
        )
        self.calibration_multiplier = (
            self.get_parameter("calibration_multiplier").get_parameter_value().double_value
        )
        self.minimum_energy_threshold = (
            self.get_parameter("minimum_energy_threshold")
            .get_parameter_value()
            .double_value
        )

        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.listening_enabled = self.auto_listen and not self.push_to_talk
        self.capture_thread = None
        self.transcribe_thread = None
        self.model = None
        self.resolved_audio_device = None
        self.capture_sample_rate = self.sample_rate
        self.capture_chunk_count = 0
        self._destroyed = False

        self.create_subscription(String, "/speech_to_text/control", self.handle_control, 10)
        self._load_model()
        self._log_audio_devices()
        self._resolve_audio_device()
        self._validate_audio_input()
        self._calibrate_audio_threshold()
        self._transcribe_startup_file()
        self._start_workers()

        self.get_logger().info(
            f"speech_to_text_node ready with local Whisper model '{self.model_name}'"
        )
        if self.debug_capture:
            self.get_logger().info(
                "debug_capture enabled; microphone capture loop will log chunk statistics"
            )

    def _load_model(self) -> None:
        if whisper is None:
            self.get_logger().error(
                "whisper is not installed. Install 'openai-whisper' to enable speech-to-text."
            )
            return

        try:
            self.model = whisper.load_model(self.model_name)
        except Exception as exc:
            self.get_logger().error(f"failed to load Whisper model '{self.model_name}': {exc}")

    def _log_audio_devices(self) -> None:
        if not self.list_audio_devices:
            return
        if sd is None:
            self.get_logger().warning("sounddevice is unavailable; cannot list audio devices")
            return
        try:
            devices = sd.query_devices()
        except Exception as exc:
            self.get_logger().warning(f"failed to query audio devices: {exc}")
            return

        for index, device in enumerate(devices):
            self.get_logger().info(
                f"audio_device[{index}] name='{device['name']}' "
                f"in={device['max_input_channels']} out={device['max_output_channels']}"
            )

    def _resolve_audio_device(self) -> None:
        if sd is None:
            return
        if self.audio_device_index >= 0:
            self.resolved_audio_device = int(self.audio_device_index)
            self.get_logger().info(f"using audio device index {self.resolved_audio_device}")
            return
        if self.audio_device is None:
            self.resolved_audio_device = None
            self.get_logger().info("using default input audio device")
            return
        if self.audio_device.isdigit():
            self.resolved_audio_device = int(self.audio_device)
            self.get_logger().info(f"using audio device index {self.resolved_audio_device}")
            return
        self.resolved_audio_device = self.audio_device
        self.get_logger().info(f"using audio device name '{self.resolved_audio_device}'")

    def _validate_audio_input(self) -> None:
        if sd is None:
            return

        try:
            sd.check_input_settings(
                device=self.resolved_audio_device,
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
            )
            self.capture_sample_rate = self.sample_rate
            self.get_logger().info(
                f"audio input validated at {self.capture_sample_rate} Hz"
            )
            return
        except Exception as exc:
            self.get_logger().warning(
                f"audio input validation failed at {self.sample_rate} Hz: {exc}"
            )

        if not self.fallback_to_device_sample_rate:
            return

        try:
            device_info = sd.query_devices(self.resolved_audio_device, "input")
            fallback_rate = int(device_info["default_samplerate"])
            sd.check_input_settings(
                device=self.resolved_audio_device,
                samplerate=fallback_rate,
                channels=1,
                dtype="float32",
            )
            self.capture_sample_rate = fallback_rate
            self.get_logger().warning(
                f"falling back to device default sample rate {self.capture_sample_rate} Hz"
            )
        except Exception as exc:
            self.get_logger().error(f"audio input could not be validated: {exc}")

    def _transcribe_startup_file(self) -> None:
        if not self.audio_file or not self.transcribe_file_on_startup:
            return
        path = Path(self.audio_file)
        if not path.exists():
            self.get_logger().error(f"audio_file does not exist: {path}")
            return
        if self.model is None:
            self.get_logger().warning("Whisper model unavailable; cannot transcribe audio file")
            return
        self._transcribe_file(path)

    def _start_workers(self) -> None:
        if not self.auto_listen and not self.push_to_talk:
            self.get_logger().info("microphone capture is disabled")
            return

        if np is None or sd is None:
            self.get_logger().error(
                "numpy and sounddevice are required for microphone capture."
            )
            return

        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.transcribe_thread = threading.Thread(target=self._transcribe_loop, daemon=True)
        self.capture_thread.start()
        self.transcribe_thread.start()
        if self.debug_capture:
            self.get_logger().info("capture and transcription worker threads started")

    def _calibrate_audio_threshold(self) -> None:
        if not self.auto_calibrate:
            self.get_logger().info(
                f"auto calibration disabled; using energy_threshold={self.energy_threshold:.5f}"
            )
            return

        if np is None or sd is None:
            self.get_logger().warning(
                "cannot auto-calibrate without numpy and sounddevice; "
                f"using energy_threshold={self.energy_threshold:.5f}"
            )
            return

        frames = max(1, int(self.capture_sample_rate * self.calibration_seconds))
        self.get_logger().info(
            "calibrating microphone noise floor for %.2f seconds; keep the room quiet"
            % self.calibration_seconds
        )

        try:
            audio = sd.rec(
                frames,
                samplerate=self.capture_sample_rate,
                channels=1,
                dtype="float32",
                device=self.resolved_audio_device,
            )
            sd.wait()
        except Exception as exc:
            self.get_logger().warning(
                f"audio calibration failed: {exc}; using energy_threshold={self.energy_threshold:.5f}"
            )
            return

        audio = np.squeeze(audio)
        if audio.size == 0:
            self.get_logger().warning(
                "audio calibration captured no samples; "
                f"using energy_threshold={self.energy_threshold:.5f}"
            )
            return

        rms = float(np.sqrt(np.mean(np.square(audio))))
        peak = float(np.max(np.abs(audio)))
        calibrated = max(
            self.minimum_energy_threshold,
            rms * self.calibration_multiplier,
        )
        self.energy_threshold = calibrated
        self.get_logger().info(
            "audio calibration complete: noise_rms=%.5f peak=%.5f "
            "multiplier=%.2f -> energy_threshold=%.5f"
            % (rms, peak, self.calibration_multiplier, self.energy_threshold)
        )

    def _capture_loop(self) -> None:
        frames_per_chunk = max(1, int(self.capture_sample_rate * self.chunk_seconds))
        while not self.stop_event.is_set():
            if not self.listening_enabled:
                if self.debug_capture:
                    self.get_logger().info("capture loop idle because listening is disabled")
                time.sleep(self.poll_interval_seconds)
                continue
            try:
                start_time = time.time()
                audio = sd.rec(
                    frames_per_chunk,
                    samplerate=self.capture_sample_rate,
                    channels=1,
                    dtype="float32",
                    device=self.resolved_audio_device,
                )
                sd.wait()
                elapsed = time.time() - start_time
            except Exception as exc:
                self.get_logger().error(f"microphone capture failed: {exc}")
                time.sleep(2.0)
                continue

            self.capture_chunk_count += 1
            audio = np.squeeze(audio)
            if audio.size == 0:
                if self.debug_capture:
                    self.get_logger().warning(
                        f"capture chunk {self.capture_chunk_count}: empty audio buffer"
                    )
                time.sleep(self.poll_interval_seconds)
                continue

            rms = float(np.sqrt(np.mean(np.square(audio))))
            peak = float(np.max(np.abs(audio)))
            should_log_chunk = (
                self.debug_capture
                and self.capture_chunk_count % self.debug_every_n_chunks == 0
            )
            if should_log_chunk:
                self.get_logger().info(
                    "capture chunk %d: samples=%d rms=%.5f peak=%.5f "
                    "queue=%d capture_dt=%.3fs sample_rate=%d device=%s"
                    % (
                        self.capture_chunk_count,
                        int(audio.size),
                        rms,
                        peak,
                        self.audio_queue.qsize(),
                        elapsed,
                        self.capture_sample_rate,
                        str(self.resolved_audio_device),
                    )
                )
            if self.log_audio_levels:
                self.get_logger().info(f"audio rms={rms:.5f}")
            if rms < self.energy_threshold:
                if should_log_chunk:
                    self.get_logger().info(
                        f"capture chunk {self.capture_chunk_count}: below energy threshold "
                        f"{self.energy_threshold:.5f}, dropping"
                    )
                time.sleep(self.poll_interval_seconds)
                continue

            self.audio_queue.put(audio.copy())
            if should_log_chunk:
                self.get_logger().info(
                    f"capture chunk {self.capture_chunk_count}: queued for transcription"
                )
            time.sleep(self.poll_interval_seconds)

    def _transcribe_loop(self) -> None:
        while not self.stop_event.is_set():
            try:
                audio = self.audio_queue.get(timeout=0.5)
            except queue.Empty:
                if self.debug_capture:
                    self.get_logger().info("transcribe loop waiting for audio chunk")
                continue

            if self.model is None:
                self.get_logger().warning("Whisper model is unavailable; dropping audio chunk")
                continue

            try:
                if self.debug_capture:
                    self.get_logger().info(
                        f"transcribe loop: starting Whisper on chunk with {len(audio)} samples"
                    )
                result = self.model.transcribe(
                    audio.astype(np.float32),
                    language=self.language or None,
                    fp16=False,
                    verbose=False,
                )
            except Exception as exc:
                self.get_logger().error(f"transcription failed: {exc}")
                continue

            text = result.get("text", "").strip()
            if not text:
                if self.debug_capture:
                    self.get_logger().info("transcribe loop: Whisper returned empty text")
                continue

            self.voice_pub.publish(String(data=text))
            self.get_logger().info(f"transcribed: {text}")

    def _transcribe_file(self, path: Path) -> None:
        try:
            result = self.model.transcribe(
                str(path),
                language=self.language or None,
                fp16=False,
                verbose=False,
            )
        except Exception as exc:
            self.get_logger().error(f"file transcription failed for '{path}': {exc}")
            return

        text = result.get("text", "").strip()
        if not text:
            self.get_logger().info(f"no speech detected in file '{path}'")
            return

        self.voice_pub.publish(String(data=text))
        self.get_logger().info(f"transcribed file '{path}': {text}")

    def handle_control(self, msg: String) -> None:
        command = msg.data.strip().lower()
        if command == "start":
            self.listening_enabled = True
            self.get_logger().info("speech capture started")
            return
        if command == "stop":
            self.listening_enabled = False
            self.get_logger().info("speech capture stopped")
            return
        if command == "toggle":
            self.listening_enabled = not self.listening_enabled
            state = "started" if self.listening_enabled else "stopped"
            self.get_logger().info(f"speech capture {state}")
            return
        if command.startswith("file:"):
            path = Path(command.split(":", 1)[1]).expanduser()
            if self.model is None:
                self.get_logger().warning("Whisper model unavailable; cannot transcribe file")
                return
            self._transcribe_file(path)
            return
        self.get_logger().warning(
            "unknown STT control command; expected start, stop, toggle, or file:/path"
        )

    def destroy_node(self):
        if self._destroyed:
            return
        self._destroyed = True
        self.stop_event.set()
        self.listening_enabled = False
        if sd is not None:
            try:
                sd.stop()
            except Exception as exc:
                self.get_logger().warning(f"failed to stop audio backend cleanly: {exc}")
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=max(1.0, self.chunk_seconds + 1.0))
            if self.capture_thread.is_alive():
                self.get_logger().warning("capture thread did not exit before timeout")
        if self.transcribe_thread and self.transcribe_thread.is_alive():
            self.transcribe_thread.join(timeout=2.0)
            if self.transcribe_thread.is_alive():
                self.get_logger().warning("transcribe thread did not exit before timeout")
        super().destroy_node()


def main() -> None:
    rclpy.init()
    node = SpeechToTextNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("keyboard interrupt received, shutting down speech_to_text_node")
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
