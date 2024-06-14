document.addEventListener('DOMContentLoaded', function () {
    fetch('/info.json')
        .then(response => response.json())
        .then(data => {
            document.getElementById('ip-address').textContent = data.ip;
            document.getElementById('os').textContent = data.os;
            document.getElementById('python-version').textContent = data.python_version;
        })
        .catch(error => console.error('Error:', error));
});
