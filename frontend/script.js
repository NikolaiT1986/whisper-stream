const recordBtn = document.getElementById('recordBtn');
const statusDiv = document.getElementById('status');
const transcriptDiv = document.getElementById('transcript');
const micSelect = document.getElementById('micSelect');

let isRecording = false;
let ws = null;
let audioContext = null;
let mediaStream = null;
let workletNode = null;

// ============================ AUDIO WORKLET ВНУТРИ SCRIPT ============================

// Создаём JS-код процессора в виде строки
const workletCode = `
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
`;

// Создаём Blob → URL для загрузки в audioContext
const workletBlob = new Blob([workletCode], { type: "application/javascript" });
const workletUrl = URL.createObjectURL(workletBlob);

// =============================== ИНИЦИАЛИЗАЦИЯ МИКРОФОНОВ ===============================

async function initDevices() {
    await navigator.mediaDevices.getUserMedia({ audio: true });

    const devices = await navigator.mediaDevices.enumerateDevices();
    const audioInputs = devices.filter(d => d.kind === 'audioinput');

    micSelect.innerHTML = "";

    let defaultIndex = 0;

    audioInputs.forEach((dev, i) => {
        const option = document.createElement("option");
        option.value = dev.deviceId;

        option.textContent = dev.label || `Микрофон ${i + 1}`;
        micSelect.appendChild(option);

        if (
            dev.deviceId === "default" ||
            dev.label.toLowerCase().includes("default") ||
            dev.label.toLowerCase().includes("communication")
        ) {
            defaultIndex = i;
        }
    });

    micSelect.selectedIndex = defaultIndex;
}

initDevices().catch(console.error);

// =============================== СТАРТ ЗАПИСИ ===============================

recordBtn.addEventListener("click", () => {
    if (!isRecording) {
        startRecording().catch(err => console.error(err));
    } else {
        stopRecording();
    }
});

async function startRecording() {
    statusDiv.textContent = "Подключение к серверу...";

    const protocol = location.protocol === "https:" ? "wss" : "ws";
    ws = new WebSocket(`${protocol}://${location.host}/ws/audio`);
    ws.binaryType = "arraybuffer";

    ws.onopen = async () => {
        statusDiv.textContent = "Запрос к микрофону...";

        const deviceId = micSelect.value;

        mediaStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                deviceId: deviceId ? { exact: deviceId } : undefined,
                sampleRate: 16000,
                channelCount: 1
            }
        });

        audioContext = new AudioContext({ sampleRate: 16000 });

        // Загружаем worklet
        await audioContext.audioWorklet.addModule(workletUrl);

        const source = audioContext.createMediaStreamSource(mediaStream);

        workletNode = new AudioWorkletNode(audioContext, "pcm-sender");

        // Получаем PCM из worklet и отправляем в WebSocket
        workletNode.port.onmessage = (event) => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(event.data);
            }
        };

        source.connect(workletNode);

        isRecording = true;
        recordBtn.textContent = "Остановить";
        statusDiv.textContent = "Запись идёт...";
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        transcriptDiv.textContent += data.text + " ";
    };

    ws.onclose = () => stopRecording(true);
}

// =============================== ОСТАНОВКА ЗАПИСИ ===============================

function stopRecording(fromWS = false) {
    isRecording = false;
    recordBtn.textContent = "Начать запись";

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

    if (!fromWS && ws && ws.readyState === WebSocket.OPEN) {
        ws.close();
    }

    statusDiv.textContent = "Запись остановлена";
}
