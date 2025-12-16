console.log("Face Security System Loaded");

let lastDetectionTime = "";

function addLogEntry(detection) {
    const list = document.getElementById('alerts-list');

    // Create new item
    const item = document.createElement('div');
    const typeClass = detection.type === 'known' ? 'success' : 'danger';
    item.className = `alert-item ${typeClass}`;

    item.innerHTML = `
        <span class="time">${detection.time}</span>
        <span class="msg">Detected: <strong>${detection.name}</strong></span>
    `;

    // Add to top
    list.prepend(item);

    // Keep only last 10 items
    if (list.children.length > 10) {
        list.removeChild(list.lastElementChild);
    }
}

function checkDetections() {
    fetch('/api/last_detection')
        .then(response => response.json())
        .then(data => {
            if (data && data.time !== lastDetectionTime) {
                lastDetectionTime = data.time;
                addLogEntry(data);
            }
        })
        .catch(err => console.error("Error fetching detections:", err));
}

// Poll every 1 second
setInterval(checkDetections, 1000);


