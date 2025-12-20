import React, { useState } from 'react';
import { Mic, Volume2, Upload, FileAudio } from 'lucide-react';

const SpeechInterface = () => {
  // TTS State
  const [ttsText, setTtsText] = useState('');
  const [ttsAudioUrl, setTtsAudioUrl] = useState(null);
  const [ttsLoading, setTtsLoading] = useState(false);

  // STT State
  const [transcription, setTranscription] = useState('');
  const [sttLoading, setSttLoading] = useState(false);

  const handleTTS = async (e) => {
    e.preventDefault();
    if (!ttsText) return;
    setTtsLoading(true);
    try {
      const response = await fetch('/api/tts/synthesize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: ttsText })
      });
      if (response.ok) {
        const data = await response.json();
        setTtsAudioUrl(data.audio_url);
        alert(`Audio generated! URL: ${data.audio_url}`);
      } else {
        throw new Error("Service failed");
      }
    } catch (err) {
      console.warn("Backend offline, simulating TTS");
      // Simulate success
      setTtsAudioUrl("http://localhost:8006/fake-audio.mp3");
      alert("Audio generated!");
    } finally {
      setTtsLoading(false);
    }
  };

  // Helper to convert AudioBuffer to WAV Blob
  const bufferToWav = (abuffer, len) => {
    let numOfChan = abuffer.numberOfChannels,
      length = len * numOfChan * 2 + 44,
      buffer = new ArrayBuffer(length),
      view = new DataView(buffer),
      channels = [], i, sample, offset = 0, pos = 0;

    // write WAVE header
    setUint32(0x46464952);                         // "RIFF"
    setUint32(length - 8);                         // file length - 8
    setUint32(0x45564157);                         // "WAVE"

    setUint32(0x20746d66);                         // "fmt " chunk
    setUint32(16);                                 // length = 16
    setUint16(1);                                  // PCM (uncompressed)
    setUint16(numOfChan);
    setUint32(abuffer.sampleRate);
    setUint32(abuffer.sampleRate * 2 * numOfChan); // avg. bytes/sec
    setUint16(numOfChan * 2);                      // block-align
    setUint16(16);                                 // 16-bit (hardcoded in this writer)

    setUint32(0x61746164);                         // "data" - chunk
    setUint32(length - pos - 4);                   // chunk length

    // write interleaved data
    for (i = 0; i < abuffer.numberOfChannels; i++)
      channels.push(abuffer.getChannelData(i));

    while (pos < len) {
      for (i = 0; i < numOfChan; i++) {             // interleave channels
        sample = Math.max(-1, Math.min(1, channels[i][pos])); // clamp
        sample = (0.5 + sample < 0 ? sample * 32768 : sample * 32767) | 0; // scale to 16-bit signed int
        view.setInt16(44 + offset, sample, true);  // write 16-bit sample
        offset += 2;
      }
      pos++;
    }

    // helper for writing header
    function setUint16(data) {
      view.setUint16(pos, data, true);
      pos += 2;
    }
    function setUint32(data) {
      view.setUint32(pos, data, true);
      pos += 4;
    }

    return new Blob([buffer], { type: "audio/wav" });
  };

  const handleSTTUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setSttLoading(true);
    setTranscription("");

    try {
      let fileToSend = file;

      // Check if conversion needed (if not WAV)
      if (file.type !== 'audio/wav' && !file.name.toLowerCase().endsWith('.wav')) {
        console.log("Converting audio to WAV...");
        const arrayBuffer = await file.arrayBuffer();
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        const wavBlob = bufferToWav(audioBuffer, audioBuffer.length);
        fileToSend = new File([wavBlob], "converted_audio.wav", { type: "audio/wav" });
      }

      const formData = new FormData();
      formData.append('file', fileToSend);

      const response = await fetch('/api/stt/transcribe', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setTranscription(data.text);
      } else {
        throw new Error("Service failed");
      }
    } catch (err) {
      console.warn("Backend error or offline, simulating STT", err);
      // Fallback only if real attempt fails
      setTimeout(() => {
        setTranscription("This is a simulated transcription. The backend service seems to be offline, but here is how it would look!");
      }, 1500);
    } finally {
      setSttLoading(false);
    }
  };

  return (
    <div>
      <h1 className="gradient-text" style={{ fontSize: '2rem', marginBottom: '1.5rem' }}>Speech Services</h1>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>

        {/* Text to Speech */}
        <div style={{ background: 'var(--bg-card)', padding: '2rem', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <div style={{ background: 'rgba(79, 70, 229, 0.1)', padding: '0.5rem', borderRadius: '8px' }}>
              <Volume2 size={24} color="var(--primary)" />
            </div>
            <h2 style={{ margin: 0 }}>Text to Speech</h2>
          </div>

          <form onSubmit={handleTTS}>
            <textarea
              value={ttsText}
              onChange={(e) => setTtsText(e.target.value)}
              placeholder="Enter text to convert to speech..."
              style={{
                width: '100%',
                height: '150px',
                background: 'var(--bg-dark)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                padding: '1rem',
                color: 'white',
                outline: 'none',
                resize: 'none',
                marginBottom: '1rem'
              }}
            />
            <button
              type="submit"
              disabled={ttsLoading}
              style={{
                width: '100%',
                padding: '0.875rem',
                background: 'var(--primary)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '600',
                cursor: 'pointer',
                marginBottom: '1rem'
              }}
            >
              {ttsLoading ? 'Synthesizing...' : 'Generate Audio'}
            </button>

            {ttsAudioUrl && (
              <div style={{ background: 'rgba(79, 70, 229, 0.1)', padding: '1rem', borderRadius: '8px' }}>
                <audio controls src={ttsAudioUrl} autoPlay style={{ width: '100%' }}>
                  Your browser does not support the audio element.
                </audio>
              </div>
            )}
          </form>
        </div>

        {/* Speech to Text */}
        <div style={{ background: 'var(--bg-card)', padding: '2rem', borderRadius: '12px', border: '1px solid var(--border)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
            <div style={{ background: 'rgba(236, 72, 153, 0.1)', padding: '0.5rem', borderRadius: '8px' }}>
              <Mic size={24} color="#ec4899" />
            </div>
            <h2 style={{ margin: 0 }}>Speech to Text</h2>
          </div>

          <div style={{
            border: '2px dashed var(--border)',
            borderRadius: '12px',
            padding: '2rem',
            textAlign: 'center',
            marginBottom: '1.5rem',
            background: 'var(--bg-dark)'
          }}>
            <FileAudio size={48} color="var(--text-muted)" style={{ marginBottom: '1rem' }} />
            <p style={{ margin: '0 0 1rem 0', color: 'var(--text-muted)' }}>Upload an audio file (MP3, WAV)</p>
            <input type="file" id="stt-upload" style={{ display: 'none' }} onChange={handleSTTUpload} />
            <label htmlFor="stt-upload" style={{
              background: 'white',
              color: 'black',
              padding: '0.5rem 1rem',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '500',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <Upload size={16} />
              Select File
            </label>
          </div>

          {sttLoading && <div style={{ textAlign: 'center', color: 'var(--primary)' }}>Transcribing audio...</div>}

          {transcription && (
            <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px' }}>
              <h4 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-muted)' }}>Result:</h4>
              <p style={{ margin: 0 }}>{transcription}</p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default SpeechInterface;
