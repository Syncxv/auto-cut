import ffmpeg from 'fluent-ffmpeg';
import fs from 'node:fs';
import path from 'node:path';

const inputFile = 'S07E08.mp4';
const outputDirectory = `out/${inputFile.split('.')[0]}`;

if (!fs.existsSync('out')) fs.mkdirSync('out');
if (!fs.existsSync(outputDirectory)) fs.mkdirSync(outputDirectory);

ffmpeg(`videos/${inputFile}`)
    .on('filenames', (filenames) => {
        console.log('Frames:', filenames);
    })
    .on('end', () => {
        console.log('Frame extraction finished.');

        // Now, you can analyze the frames and audio
        // analyzeFramesAndAudio();
    })
    .on('error', (err) => {
        console.error('Error:', err);
    })
    .audioCodec('pcm_s16le')
    .audioChannels(1)
    .audioFrequency(44100)
    .audioQuality(0)
    .audioBitrate(96)
    .audioFilters('volume=1.0')
    .output(path.join(outputDirectory, 'audio.wav'))
    .run();
