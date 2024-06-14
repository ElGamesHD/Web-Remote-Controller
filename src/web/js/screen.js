const wsUrl = 'ws://192.168.1.141:8765';
const screenshotImg = document.getElementById('screen_share');
const socket = new WebSocket(wsUrl);

socket.onmessage = function (event) {
    screenshotImg.src = 'data:image/jpeg;base64,' + event.data;
};

socket.onerror = function (error) {
    console.error('WebSocket error:', error);
};

socket.onclose = function (event) {
    console.log('WebSocket connection closed:', event);
};

screenshotImg.addEventListener('click', function (event) {
    console.log("click");
    const x = event.clientX;
    const y = event.clientY;
    const message = JSON.stringify({
        x: x,
        y: y,
        img_w: screenshotImg.offsetWidth,
        img_h: screenshotImg.offsetHeight
    });
    socket.send(message);
});

function openFullscreen() {
    const elem = document.getElementById("screenshot");

    if (elem.requestFullscreen) {
        elem.requestFullscreen();
    } else if (elem.webkitRequestFullscreen) { /* Safari */
        elem.webkitRequestFullscreen();
    } else if (elem.msRequestFullscreen) { /* IE11 */
        elem.msRequestFullscreen();
    }
}