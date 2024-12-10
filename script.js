
window.onload = function () {
    const client = mqtt.connect('ws://localhost:9001'); // Connect to the local MQTT broker

    client.on('connect', () => {
        console.log('Connected to MQTT broker');

        // Subscribe to relevant topics
        const topics = [
            'hmi/pcm/battery_soc',
            'hmi/pcm/hv_battery_pack_temp',
            'hmi/pcm/cacc_mileage_accumulation',
            'hmi/pcm/drive_mode_active',
            'hmi/pcm/distance_to_lead_vehicle',
            'hmi/pcm/front_edu_reported_temp',
            'hmi/pcm/back_edu_reported_temp',
            'hmi/pcm/front_axle_power',
            'hmi/pcm/rear_axle_power',
            'hmi/pcm/traffic_light_state',
        ];

        client.subscribe(topics, (err) => {
            if (err) {
                console.error('Failed to subscribe to topics:', err);
            } else {
                console.log('Subscribed to topics:', topics.join(', '));
            }
        });
    });

    client.on('message', (topic, message) => {
        const data = message.toString();
        console.log(`Message received on ${topic}: ${data}`);

        switch (topic) {
            case 'hmi/pcm/battery_soc':
                document.getElementById('fuel-percentage').innerText = `${data}%`;
                document.getElementById('fuel-level').style.width = `${data}%`;
                break;
            case 'hmi/pcm/hv_battery_pack_temp':
                document.getElementById('battery-temp').innerText = `${data}°C`;
                break;
            case 'hmi/pcm/cacc_mileage_accumulation':
                document.getElementById('cacc-mileage').innerText = `${data} mi`;
                break;
            case 'hmi/pcm/drive_mode_active':
                let driveModeText = 'Drive Mode: ';
                if (data === 0) {
                    driveModeText += 'Default Drive';
                } else if (data === 1) {
                    driveModeText += 'Performance Drive';
                } else if (data === 2) {
                    driveModeText += 'ECO Drive';
                }
                document.getElementById('drive-mode-status').innerText = driveModeText;
                break;
            case 'hmi/pcm/distance_to_lead_vehicle':
                document.getElementById('distance').innerText = `Distance: ${data}m`;
                break;
            case 'hmi/pcm/front_edu_reported_temp':
                document.getElementById('front-motor-temp').innerText = `Front Motor Temp: ${data}°C`;
                break;
            case 'hmi/pcm/back_edu_reported_temp':
                document.getElementById('rear-motor-temp').innerText = `Rear Motor Temp: ${data}°C`;
                break;
            case 'hmi/pcm/front_axle_power':
                const frontWheels = document.querySelectorAll('.wheel.front-left, .wheel.front-right');
                frontWheels.forEach(wheel => {
                    wheel.style.backgroundColor = data === '0' ? 'red' : 'green';
                });
                break;
            case 'hmi/pcm/rear_axle_power':
                const rearWheels = document.querySelectorAll('.wheel.rear-left, .wheel.rear-right');
                rearWheels.forEach(wheel => {
                    wheel.style.backgroundColor = data === '0' ? 'red' : 'green';
                });
                break;
            case 'hmi/pcm/traffic_light_state':
                updateTrafficLightState(Number(data));
                break;
        }
    });

    client.on('error', (err) => {
        console.error('MQTT client error:', err);
    });

    function updateTrafficLightState(state) {
        console.log('Updating traffic light with state:', state);

        const redLight = document.querySelector('.red-light');
        const yellowLight = document.querySelector('.yellow-light');
        const greenLight = document.querySelector('.green-light');

        // Clear active class from all lights
        redLight.classList.remove('active');
        yellowLight.classList.remove('active');
        greenLight.classList.remove('active');

        // Add active class based on traffic light state
        if (state === 0) {
            redLight.classList.add('active');
        } else if (state === 1) {
            yellowLight.classList.add('active');
        } else if (state === 2) {
            greenLight.classList.add('active');
        }
    }
};
