let audioContext = null;
let mediaStream = null;
let workletNode = null;

export async function initDevices(micSelect) {
    await navigator.mediaDevices.getUserMedia({audio: true});

    const devices = await navigator.mediaDevices.enumerateDevices();
    const audioInputs = devices.filter(d => d.kind === "audioinput");

    micSelect.innerHTML = "";

    let defaultIndex = 0;

    audioInputs.forEach((dev, i) => {
        const option = document.createElement("option");
        option.value = dev.deviceId;
        option.textContent = dev.label || `Микрофон ${i + 1}`;
        micSelect.appendChild(option);

        const label = (dev.label || "").toLowerCase();
        if (
            dev.deviceId === "default" ||
            label.includes("default") ||
            label.includes("communication")
        ) {
            defaultIndex = i;
        }
    });

    micSelect.selectedIndex = defaultIndex;
}

export async function startAudioCapture(deviceId, onChunk) {
    audioContext = new AudioContext({sampleRate: 16000});

    mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
            deviceId: deviceId ? {exact: deviceId} : undefined,
            sampleRate: 16000,
            channelCount: 1,
        },
    });

    await audioContext.audioWorklet.addModule("/static/js/worklets/pcm-sender.js");

    const source = audioContext.createMediaStreamSource(mediaStream);
    workletNode = new AudioWorkletNode(audioContext, "pcm-sender");

    workletNode.port.onmessage = (event) => {
        if (onChunk) {
            onChunk(event.data);
        }
    };

    source.connect(workletNode);
}

export function stopAudioCapture() {
    if (workletNode) {
        workletNode.disconnect();
        workletNode = null;
    }

    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }

    if (mediaStream) {
        mediaStream.getTracks().forEach(t => t.stop());
        mediaStream = null;
    }
}
