import ffmpeg from 'fluent-ffmpeg';

ffmpeg('videos/S07E08.mp4')
    .output('videos/audio.mp3')
    .on('end', () => console.log('Finished'))
    .on('error', (err) => console.log('error occoured', err))
    .run();
