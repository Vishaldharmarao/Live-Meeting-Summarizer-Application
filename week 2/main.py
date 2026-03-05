"""
Ultra-Optimized CPU Real-Time Speech-to-Text
Whisper Tiny Model (CPU Only - Intel Iris Optimized)
Stable, clean, non-blocking architecture.
"""

import numpy as np
import sounddevice as sd
import queue
import threading
import sys
import time
from faster_whisper import WhisperModel

# ============================================================================
# CONFIGURATION (CPU OPTIMIZED)
# ============================================================================
SAMPLE_RATE = 16000
CHUNK_DURATION = 0.5                     # 0.5 sec chunks
CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION)

ROLLING_BUFFER_DURATION = 1.5            # 1.5 sec buffer (small for CPU)
ROLLING_BUFFER_SIZE = int(SAMPLE_RATE * ROLLING_BUFFER_DURATION)

MODEL_NAME = "tiny"
COMPUTE_TYPE = "int8"                    # Best for CPU
BEAM_SIZE = 1

PROCESS_INTERVAL = 0.8                   # seconds
BATCH_SIZE = 2                           # 2 chunks = 1 second

LOG_FILE = "transcription_log.txt"

# ============================================================================
# REAL-TIME TRANSCRIBER CLASS
# ============================================================================
class RealtimeTranscriber:
    def __init__(self):
        print("\n[INFO] Loading Whisper 'tiny' model (CPU optimized)...")
        print("[INFO] This may take 10-20 seconds on first run...\n")

        self.model = WhisperModel(
            MODEL_NAME,
            device="cpu",
            compute_type=COMPUTE_TYPE,
            num_workers=1,
            cpu_threads=4,
        )

        print("[INFO] Model loaded successfully.\n")

        self.audio_queue = queue.Queue(maxsize=50)
        self.is_running = False
        self.stream = None
        self.worker_thread = None

        self.rolling_buffer = np.zeros(ROLLING_BUFFER_SIZE, dtype=np.float32)
        self.buffer_pos = 0

        self.full_text = ""

    # ------------------------------------------------------------------------
    # AUDIO CALLBACK (NON-BLOCKING)
    # ------------------------------------------------------------------------
    def audio_callback(self, indata, frames, time_info, status):
        if status:
            print(f"[WARNING] {status}")

        audio_data = indata[:, 0].astype(np.float32)

        try:
            self.audio_queue.put_nowait(audio_data.copy())
        except queue.Full:
            pass  # Drop chunk if queue full (avoid blocking)

    # ------------------------------------------------------------------------
    # UPDATE ROLLING BUFFER
    # ------------------------------------------------------------------------
    def update_rolling_buffer(self, chunk):
        chunk_len = len(chunk)

        if self.buffer_pos + chunk_len <= ROLLING_BUFFER_SIZE:
            self.rolling_buffer[self.buffer_pos:self.buffer_pos + chunk_len] = chunk
            self.buffer_pos += chunk_len
        else:
            overlap = self.buffer_pos + chunk_len - ROLLING_BUFFER_SIZE
            self.rolling_buffer = np.roll(self.rolling_buffer, -overlap)
            self.rolling_buffer[-chunk_len:] = chunk
            self.buffer_pos = ROLLING_BUFFER_SIZE

    # ------------------------------------------------------------------------
    # WORKER THREAD (GRACEFUL SHUTDOWN)
    # ------------------------------------------------------------------------
    def worker_process(self):
        batch_audio = []
        chunk_count = 0
        last_process_time = time.time()

        print("-" * 60)
        print("LIVE TRANSCRIPTION:")
        print("-" * 60)

        while self.is_running:
            try:
                # Check shutdown flag at each iteration
                if not self.is_running:
                    break

                try:
                    chunk = self.audio_queue.get(timeout=0.2)
                    batch_audio.append(chunk)
                    chunk_count += 1
                    self.update_rolling_buffer(chunk)
                except queue.Empty:
                    pass

                if (
                    chunk_count >= BATCH_SIZE
                    or (time.time() - last_process_time) > PROCESS_INTERVAL
                ):
                    if batch_audio and self.is_running:
                        self.transcribe_batch(np.concatenate(batch_audio))
                        batch_audio = []
                        chunk_count = 0
                        last_process_time = time.time()

            except Exception as e:
                if self.is_running:
                    print(f"\n[ERROR] Worker error: {e}\n")
                break
        
        # Clean exit
        print("[INFO] Worker thread shutting down.")
        return

    # ------------------------------------------------------------------------
    # TRANSCRIBE
    # ------------------------------------------------------------------------
    def transcribe_batch(self, audio_np):
        try:
            segments, _ = self.model.transcribe(
                audio_np,
                language="en",
                beam_size=BEAM_SIZE,
                best_of=1,
                vad_filter=True,
                condition_on_previous_text=False
            )

            current_text = "".join([segment.text for segment in segments]).strip()

            if current_text != self.full_text:
                print("\r" + current_text, end="", flush=True)
                self.full_text = current_text

        except Exception as e:
            print(f"\n[ERROR] Transcription error: {e}\n")

    # ------------------------------------------------------------------------
    # START
    # ------------------------------------------------------------------------
    def start(self):
        self.is_running = True

        self.worker_thread = threading.Thread(
            target=self.worker_process,
            daemon=True
        )
        self.worker_thread.start()

        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            blocksize=CHUNK_SIZE,
            callback=self.audio_callback,
            latency="low"
        )
        self.stream.start()

        print(f"[INFO] Listening... Press Ctrl+C to stop.\n")

    # ------------------------------------------------------------------------
    # STOP (GRACEFUL SHUTDOWN)
    # ------------------------------------------------------------------------
    def stop(self):
        """
        Gracefully shutdown transcription with proper resource cleanup.
        - Stops stream immediately
        - Sets shutdown flag
        - Doesn't block on threads
        - Saves transcript
        - Exits cleanly
        """
        print("\n[INFO] Shutting down...")

        # 1. Stop audio stream IMMEDIATELY (highest priority)
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception as e:
                print(f"[WARNING] Error closing stream: {e}")

        # 2. Set flag to stop worker thread
        self.is_running = False

        # 3. Wait briefly for worker to finish (timeout, don't block forever)
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)

        # 4. Save transcript
        if self.full_text:
            try:
                with open(LOG_FILE, "w", encoding="utf-8") as f:
                    f.write(self.full_text.strip())
                print(f"[INFO] Transcript saved to {LOG_FILE}")
            except Exception as e:
                print(f"[ERROR] Failed to save transcript: {e}")

        print("[INFO] Shutdown complete.")
        sys.exit(0)  # Exit immediately


# ============================================================================
# MAIN (GRACEFUL SHUTDOWN)
# ============================================================================
def main():
    """
    Main entry point with proper Ctrl+C handling.
    - Starts transcriber
    - Catches KeyboardInterrupt
    - Triggers graceful shutdown
    - Exits immediately
    """
    transcriber = RealtimeTranscriber()

    try:
        transcriber.start()

        # Keep main thread alive
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        # Ctrl+C pressed - initiate shutdown
        transcriber.stop()

    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        transcriber.stop()

    finally:
        # Ensure exit (in case stop() doesn't call sys.exit)
        sys.exit(0)


if __name__ == "__main__":
    main()