class PcmSenderProcessor extends AudioWorkletProcessor {
    process(inputs) {
        const input = inputs[0][0];
        if (input) {
            const copy = new Float32Array(input.length);
            copy.set(input);
            this.port.postMessage(copy.buffer, [copy.buffer]);
        }
        return true;
    }
}

registerProcessor("pcm-sender", PcmSenderProcessor);
