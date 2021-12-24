class PlaybackAudioProcessor extends AudioWorkletProcessor {
    // TODO: Some kinda parameter to control playback

    process (inputs, outputs, parameters) {
        // TODO: Route input to output
        const output = outputs[0]
        output.forEach(channel => {
            for (let i = 0; i < channel.length; i++) {
                channel[i] = Math.random() * 2 - 1
            }
        })
        return true
    }
}

registerProcessor('playback-audio-processor', PlaybackAudioProcessor)
