import time
from audio_capture import ReSpeakerCapture
from direction_estimator import DirectionEstimator

def main():
    sample_rate = 16000
    history_size = 10

    # Init capture + estimator
    capture = ReSpeakerCapture(sample_rate=sample_rate)
    estimator = DirectionEstimator(sample_rate=sample_rate)

    print("Starting ReSpeaker stream...")
    capture.start_stream()
    time.sleep(0.5)

    angle_history = []

    print("\nMove around the mics and clap / talk.")
    print("Positive angle = sound from the RIGHT")
    print("Negative angle = sound from the LEFT")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            # Get a chunk of audio
            left, right = capture.read_chunk()

            # Raw angle estimate from this chunk
            angle = estimator.estimate_angle(left, right)

            if angle is not None:
                angle_history.append(angle)
                if len(angle_history) > history_size:
                    angle_history.pop(0)

                smoothed = estimator.smooth_angle(angle_history)

                if smoothed is not None:
                    print(f"Raw: {angle:7.2f}° | Smoothed: {smoothed:7.2f}°")
                else:
                    print(f"Raw: {angle:7.2f}° | Smoothed: N/A")
            else:
                print("No valid angle (signal below threshold)")

            # Don’t spam too fast
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping...")
        capture.cleanup()

if __name__ == "__main__":
    main()
