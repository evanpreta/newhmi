const mqtt = require('mqtt');

// Connect to the Mosquitto broker
const client = mqtt.connect('mqtt://localhost:1883');

// Subscribe to the desired topic
const topic = 'hmi/pcm/HVBSOC_BatSOC0';
client.on('connect', () => {
    console.log(`Connected to MQTT broker`);
    client.subscribe(topic, (err) => {
        if (err) {
            console.error(`Failed to subscribe to topic ${topic}:`, err);
        } else {
            console.log(`Subscribed to topic: ${topic}`);
        }
    });
});

// Handle incoming messages
client.on('message', (topic, message) => {
    console.log(`Message received on topic ${topic}: ${message.toString()}`);
});

// Handle errors
client.on('error', (err) => {
    console.error(`MQTT client error:`, err);
});
