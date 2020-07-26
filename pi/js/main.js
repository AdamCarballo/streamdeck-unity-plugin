let socket = null;
let inspector = {};

function connectElgatoStreamDeckSocket(port, uuid, registerEvent, info, actionInfo) {
    inspector.port = port;
    inspector.uuid = uuid;
    inspector.registerEvent = registerEvent;
    inspector.info = info;
    inspector.actionInfo = actionInfo;

    createSocket();
}

function isSocketOpen() {
    return socket && socket.readyState === WebSocket.OPEN;
}

function createSocket() {
    socket = new WebSocket(`ws://127.0.0.1:${inspector.port}`);
    socket.onopen = _ => onOpen();
    socket.onmessage = message => onMessage(message);
    socket.onclose = _ => createSocket();
}

function onOpen() {
    const json = {
        event: inspector.registerEvent,
        uuid: inspector.uuid
    };
    socket.send(JSON.stringify(json));

    getSettings();
    registerChangeDetection();
}

function onMessage(message) {
    const json = JSON.parse(message.data);

    if (json.event === "didReceiveSettings") {
        settingsReceived(json.payload.settings);
    }
}

function registerChangeDetection() {
    getInputs().forEach(element => {
        if (element.tagName === "SELECT") {
            element.addEventListener("change", () => setSettings());
        } else {
            element.addEventListener("input", () => setSettings());
        }
    });
}

function getInputs() {
    return Array.from(document.querySelectorAll(".sdpi-item-value")).filter(element => {
        return element.tagName !== "BUTTON";
    }).map(element => {
        if (element.tagName !== "INPUT" && element.tagName !== "TEXTAREA" && element.tagName !== "SELECT") {
            return element.querySelector("input");
        }
        return element;
    });
}

function getSettings() {
    if (!isSocketOpen()) return;

    const json = {
        event: "getSettings",
        context: inspector.uuid
    };
    socket.send(JSON.stringify(json));
}

function settingsReceived(settings) {
    Object.entries(settings).forEach(([key, value]) => {
        const element = document.getElementById(key);
        if (!element) return;

        if (element.type === "checkbox") {
            element.checked = value;
        } else {
            element.value = value;
        }

    });
}

function setSettings() {
    if (!isSocketOpen()) return;

    let payload = {};

    getInputs().forEach(element => {
        if (element.type === "checkbox") {
            payload[element.id] = element.checked ? true : false;
        } else if (element.tagName === "SELECT") {
            payload[element.id] = element.options[element.selectedIndex].value;
        } else {
            payload[element.id] = element.value;
        }
    });

    const json = {
        event: "setSettings",
        context: inspector.uuid,
        payload
    };
    socket.send(JSON.stringify(json));
}

function openHelp() {
    window.xtWindow = window.open(
        "https://github.com/nicollasricas/streamdeck-unity#execute-menu",
        "Execute Menu Help"
    );
}