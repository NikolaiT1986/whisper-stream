/**
 * Creates a WebSocket and attaches callbacks.
 * @param {Object} callbacks
 * @param {Function} callbacks.onText
 * @param {Function} callbacks.onOpen
 * @param {Function} callbacks.onClose
 * @param {Function} callbacks.onError
 */
export function createAudioWebSocket(callbacks) {
    const {onText, onOpen, onClose, onError} = callbacks;

    const protocol = location.protocol === "https:" ? "wss" : "ws";
    const ws = new WebSocket(`${protocol}://${location.host}/ws/audio`);
    ws.binaryType = "arraybuffer";

    ws.onopen = () => {
        if (onOpen) onOpen(ws);
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (onText) {
            onText(data.text);
        }
    };

    ws.onclose = () => {
        if (onClose) onClose();
    };

    ws.onerror = (e) => {
        if (onError) onError(e);
    };

    return ws;
}
