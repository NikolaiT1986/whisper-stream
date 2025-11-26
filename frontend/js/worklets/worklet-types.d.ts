declare class AudioWorkletProcessor {
    readonly port: MessagePort;
    constructor();
    process(inputs: Float32Array[][]): boolean;
}

declare function registerProcessor(
    name: string,
    processorCtor: typeof AudioWorkletProcessor
): void;
