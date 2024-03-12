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
    let url = document.querySelector('meta[name="help"]')?.content
    if (!url) {
        url = "plugin"
    }

    window.xtWindow = window.open(
        `https://docs.f10.dev/streamdeckintegration/manual/${url}.html`,
        "Plugin Help"
    );
}

function filterChars(event) {
    const forbiddenChars = ['"'];
    let keyPressed = String.fromCharCode(event.keyCode || event.which);

    if (forbiddenChars.includes(keyPressed)) {
        event.preventDefault();
    }
}

// https://github.com/LexmarkWeb/csi.js under MIT
window.onload = function() {
	var elements = document.getElementsByTagName('*'),
		i;
	for (i in elements) {
		if (elements[i].hasAttribute && elements[i].hasAttribute('data-include')) {
			fragment(elements[i], elements[i].getAttribute('data-include'));
		}
	}
	function fragment(el, url) {
		var localTest = /^(?:file):/,
			xmlhttp = new XMLHttpRequest(),
			status = 0;

		xmlhttp.onreadystatechange = function() {
			/* if we are on a local protocol, and we have response text, we'll assume
 *  				things were sucessful */
			if (xmlhttp.readyState == 4) {
				status = xmlhttp.status;
			}
			if (localTest.test(location.href) && xmlhttp.responseText) {
				status = 200;
			}
			if (xmlhttp.readyState == 4 && status == 200) {
				el.outerHTML = xmlhttp.responseText;
			}
		}

		try { 
			xmlhttp.open("GET", url, true);
			xmlhttp.send();
		} catch(err) {
			/* todo catch error */
		}
	}
}