// script.js


let audioContext;
let mediaStream;
let audioBufferSourceNode;
let gainNode;

// Create a new MediaStream and get the user's microphone input
navigator.mediaDevices.getUserMedia({ audio: true })
  .then(stream => {
    mediaStream = stream;
    createAudioContext();
    startRecording();
  })
  .catch(err => console.error(err));

function createAudioContext() {
  audioContext = new AudioContext();
  audioBufferSourceNode = audioContext.createBufferSource();

  // Create a gain node to adjust the volume
  gainNode = audioContext.createGain();
  gainNode.gain.value = -20;

  // Connect the gain node to the audio context
  audioBufferSourceNode.connect(gainNode);
  gainNode.connect(audioContext.destination);

  // Set up event listeners for start and stop recording
  document.getElementById('start-button').addEventListener('click', startRecording);
  document.getElementById('stop-button').addEventListener('click', stopRecording);
}

function startRecording() {
  mediaStream.getAudioTracks()[0].applyConstraints({
    bitrate: 128,
    sampleRate: 44100,
  });

  audioBufferSourceNode.connect(audioContext.destination);
  audioBufferSourceNode.start();

  document.getElementById('audio').play();
}

function stopRecording() {
  // Stop the recording
  mediaStream.getAudioTracks()[0].stop();
  audioBufferSourceNode.stop();

  // Release the gain node and disconnect it from the audio context
  gainNode.disconnect(audioContext.destination);
}
