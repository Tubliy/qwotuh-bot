// watch.js

const TikTokLiveConnection = require('tiktok-live-connector');

const axios = require('axios');

// 🔧 Change this to your friend's TikTok username (no @)
const username = "qwotuh";

// 🔧 This is where your Python bot will be listening
const discordBotEndpoint = "http://localhost:5000/tiktok-live";

// Start connection
const connection = new TikTokLiveConnection(username);

connection.on('streamStart', async () => {
    console.log(`${username} is now LIVE!`);
    try {
        await axios.post(discordBotEndpoint, {
            username: username,
            status: 'live'
        });
    } catch (err) {
        console.error("Failed to notify Discord bot:", err.message);
    }
});

connection.on('streamEnd', async () => {
    console.log(`${username} has ended the stream.`);
    try {
        await axios.post(discordBotEndpoint, {
            username: username,
            status: 'offline'
        });
    } catch (err) {
        console.error("Failed to notify Discord bot:", err.message);
    }
});

connection.connect().catch(console.error);
