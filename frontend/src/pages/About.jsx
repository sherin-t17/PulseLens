export default function About() {
  return (
    <>
      <h1>About PulseLens</h1>

      <div className="card">
        <h3>What is PPG?</h3>
        <p>Photoplethysmography (PPG) is an optical technique that detects small changes
          in light absorption caused by blood-volume changes. With a fingertip over a
          camera and flash, each heartbeat slightly changes the brightness of the video.</p>
      </div>

      <div className="card">
        <h3>How PulseLens works</h3>
        <ol className="steps">
          <li>Capture fingertip video.</li>
          <li>Extract green-channel intensity.</li>
          <li>Create a time-based pulse signal.</li>
          <li>Remove slow trends.</li>
          <li>Apply band-pass filtering (0.7-4.0 Hz).</li>
          <li>Perform FFT.</li>
          <li>Identify the dominant frequency.</li>
          <li>Convert frequency to BPM.</li>
        </ol>
        <p className="formula">BPM = frequency (Hz) x 60</p>
        <p className="small">Example: a pulse of 1.2 Hz means 1.2 beats per second = 72 beats per minute.</p>
      </div>

      <div className="card">
        <h3>Future improvements</h3>
        <ul className="steps">
          <li>Native Android application</li>
          <li>Direct rear-camera access and flash control</li>
          <li>Real-time BPM estimation</li>
          <li>Improved motion-artifact removal</li>
          <li>Better ROI detection</li>
          <li>Machine-learning-based signal refinement</li>
          <li>More extensive validation</li>
          <li>Better signal-quality assessment</li>
        </ul>
      </div>

      <p className="notice">
        This application is a student research prototype and is not a medical device.
        Results may be affected by movement, lighting, camera quality, recording conditions
        and other factors. The results should not be used for medical diagnosis or treatment
        decisions.
      </p>
    </>
  );
}