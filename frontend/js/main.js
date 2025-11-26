import { initUI } from "./ui.js";
import { initDevices, startAudioCapture, stopAudioCapture } from "./audio.js";
import { createAudioWebSocket } from "./ws.js";

let isRecording = false;
let ws = null;

document.addEventListener("DOMContentLoaded", async () => {
    const ui = initUI();

    await initDevices(ui.micSelect).catch(err => {
        console.error(err);
        ui.setStatus("Ошибка доступа к микрофону");
    });

    ui.recordBtn.addEventListener("click", () => {
        if (!isRecording) {
            startRecording(ui).catch(err => console.error(err));
        } else {
            stopRecording(ui);
        }
    });
});

export async function startRecording(ui) {
    ui.setStatus("Подключение к серверу...");
    ui.clearTranscript();

    ws = createAudioWebSocket({
        onText: (text) => {
            ui.appendTranscript(text + " ");
        },
        onOpen: async () => {
            ui.setStatus("Запрос к микрофону...");

            const deviceId = ui.micSelect.value;

            await startAudioCapture(deviceId, (chunk) => {
                if (ws && ws.readyState === WebSocket.OPEN) {
                    ws.send(chunk);
                }
            });

            isRecording = true;
            ui.setRecording(true);
            ui.setStatus("Идёт прослушивание...");
        },
        onClose: () => {
            stopRecording(ui, true);
        },
        onError: (e) => {
            console.error("WebSocket error", e);
            ui.setStatus("Ошибка соединения");
            stopRecording(ui, true);
        },
    });
}

function stopRecording(ui, fromWS = false) {
    if (!isRecording && !fromWS) {
        return;
    }

    isRecording = false;
    ui.setRecording(false);

    stopAudioCapture();

    if (!fromWS && ws && ws.readyState === WebSocket.OPEN) {
        ws.send("stop");
    }

    ui.setStatus("Прослушивание остановлено");
}
