const express = require('express');
const app = express();
const port = 3000;

// Set up middlewares
app.use(express.static('public'));
app.use(express.json());

// API endpoint configuration
const internalApiUrl = 'http://192.168.1.88:5000';

app.get('/', (req, res) => {
    res.sendFile(__dirname + '/index.html');
});

app.post('/generate-audio', (req, res) => {
    const audioValue = req.body.audio;
    fetch(internalApiUrl, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: audioValue }),
    })
    .then(response => response.json())
    .then(data => {
        const audioBlob = data.audio;
        const url = URL.createObjectURL(audioBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'audio.mp3';
        link.click();
    })
    .catch(error => console.error('Error:', error));

    res.send('Audio generated successfully!');
});

// Start server
app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});