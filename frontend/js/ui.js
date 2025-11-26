export function initUI() {
    const recordBtn = document.getElementById("recordBtn");
    const statusDiv = document.getElementById("status");
    const transcriptDiv = document.getElementById("transcript");
    const micSelect = document.getElementById("micSelect");

    function setStatus(text) {
        statusDiv.textContent = text;
    }

    function clearTranscript() {
        transcriptDiv.textContent = "";
    }

    function appendTranscript(text) {
        transcriptDiv.textContent += text;
    }

    function setRecording(isRecording) {
        recordBtn.textContent = isRecording ? "Остановить" : "Начать прослушивать";
    }

    return {
        recordBtn,
        micSelect,
        setStatus,
        clearTranscript,
        appendTranscript,
        setRecording,
    };
}
