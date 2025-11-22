const express = require('express');
const requestIp = require('request-ip');
const geoip = require('geoip-lite');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();
const borderLine = '\x1b[34;1;4m----------------------------------------\x1b[0m';

// Middleware to parse JSON bodies
app.use(express.json());
app.use(cors({ origin: '*' }));


const dotenv = require('dotenv');
const envFilePath = path.resolve(__dirname, './.env');
dotenv.config({ path: envFilePath });
const PORT = parseInt(process.env.SERVER_PORT);


// Middleware to detect client IP
app.use(requestIp.mw());

app.get("/convert", (req, res) => {
    console.log(`${borderLine}\n${req.body.url} | ${req.body.format} converted and downloading successfully\n${borderLine}`);
    res.send(`${req.body.url} | ${req.body.format} converted and downloaded successfully`)
});


app.post('/download', (req, res) => {
    const clientIp = req.clientIp;
    const filename = req.body.filename;
    const format = req.body.format;
    const geo = geoip.lookup(clientIp);
    const country = geo ? geo.country : 'Unknown';
    let timestamp =  new Date().toISOString();    
    const downloadInfo = {
        ip: clientIp,
        country: country,
        timestamp: timestamp,
        filename: filename,
        format: format
    };
    console.log(
        `${borderLine}
        \x1b[32mIP: ${downloadInfo.ip}
        Country: ${downloadInfo.country}
        Timestamp: ${downloadInfo.timestamp}
        File: ${downloadInfo.filename}
        Format: ${downloadInfo.format}
        Port: ${PORT}\n
        \x1b[0m${borderLine}`
    );
    res.json({})
});

// Start the server

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});