import wav from 'node-wav';
import path from 'node:path';
import fs from 'node:fs';

const inputFile = 'S07E08.mp4';
const outputDirectory = `out/${inputFile.split('.')[0]}`;

const audioFilePath = path.join(outputDirectory, 'audio.wav');
const audioData = fs.readFileSync(audioFilePath);
const audioInfo = wav.decode(audioData);
const audioSamples = audioInfo.channelData[0];

const frameRate = 24;
const samplesPerFrame = audioInfo.sampleRate / frameRate;

const SILENCE_THRESHOLD = 0.1;
// Loop through the audio by the specified frame rate
for (let frameNumber = 0; frameNumber < audioSamples.length / samplesPerFrame; frameNumber++) {
    const startSample = frameNumber * samplesPerFrame;
    const endSample = (frameNumber + 1) * samplesPerFrame;

    const currentFrameAudioData = audioSamples.slice(startSample, endSample);

    const isSilent = currentFrameAudioData.every((sample) => Math.abs(sample) < SILENCE_THRESHOLD);

    if (isSilent) {
        const nextFramesSample = frameNumber * samplesPerFrame;
        const endNextFrameSamples = (frameNumber + 4) * samplesPerFrame;

        const data = audioSamples.slice(nextFramesSample, endNextFrameSamples);
        if (data.every((s) => Math.abs(s) < SILENCE_THRESHOLD)) {
            console.log(`Cut at Frame ${frameNumber + 1}`);
        }
    }
}
