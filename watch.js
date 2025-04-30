const { connect } = require('tiktok-live-connector');
const axios = require('axios');

// Replace with your friend's TikTok username (no @)
const username = "qwotuh";
const discordBotEndpoint = "http://localhost:5000/tiktok-live";

// Connect to the TikTok live stream
connect(username).then(connection => {
    console.log(`Connected to TikTok user: ${username}`);

    connection.on('streamStart', async () => {
        console.log(`${username} is now LIVE!`);
        try {
            await axios.post(discordBotEndpoint, {
                username,
                status: 'live'
            });
        } catch (e) {
            console.error("Failed to notify Discord bot:", e.message);
        }
    });

    connection.on('streamEnd', async () => {
        console.log(`${username} has ended the stream.`);
        try {
            await axios.post(discordBotEndpoint, {
                username,
                status: 'offline'
            });
        } catch (e) {
            console.error("Failed to notify Discord bot:", e.message);
        }
    });

}).catch(err => {
    console.error("Failed to connect:", err.message);
});
