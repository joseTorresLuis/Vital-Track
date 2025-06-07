document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('mobile-menu-button').addEventListener('click', function() {
        document.getElementById('mobile-menu').classList.toggle('hidden');
    });

    const heartRateChart = initChart('heartRateChart', 'Latidos por minuto', '#3B82F6', {
        min: 40,
        max: 110,
        step: 10
    });

    const temperatureChart = initChart('temperatureChart', 'Temperatura (°C)', '#EF4444', {
        min: 35.5,
        max: 37.5,
        decimals: 1
    });

    const oxygenLevelChart = initChart('oxygenLevelChart', 'Nivel de oxígeno (%)', '#8B5CF6', {
        min: 80,
        max: 100,
        step: 5
    });

    window.Echo = new Echo({
        broadcaster: 'pusher',
        key: window.pusherConfig.key,
        cluster: window.pusherConfig.cluster,
        encrypted: true,
        forceTLS: true
    });

    window.Echo.channel('sensor-data')
        .listen('SensorDataUpdated', (event) => {
            const data = event;
            console.log('Nuevos datos recibidos:', data);
            updateDashboard(data);
            checkForAlerts(data);
        });

    function initChart(elementId, label, color, {min, max, step, decimals} = {}) {
        const ctx = document.getElementById(elementId).getContext('2d');
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: label,
                    data: [],
                    borderColor: color,
                    backgroundColor: hexToRgba(color, 0.1),
                    tension: 0.3,
                    fill: true,
                    borderWidth: 2,
                    pointRadius: 3,
                    pointBackgroundColor: color
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        min: min,
                        max: max,
                        ticks: {
                            stepSize: step,
                            callback: decimals ? function(value) { return value.toFixed(decimals); } : undefined
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                }
            }
        });
    }

    function hexToRgba(hex, alpha) {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    function updateDashboard(data) {
        updateMetric('heart-rate', data.BPM, 'lpm');
        updateMetric('temperature', data.TEMP, '°C');
        updateMetric('oxygen', data.SPO2, '%');

        updateStatus('heart-rate', data.BPM, 60, 100);
        updateStatus('temperature', data.TEMP, 36.0, 37.5);
        updateStatus('oxygen', data.SPO2, 95, 100);

        updateChart(heartRateChart, data.BPM);
        updateChart(temperatureChart, data.TEMP);
        updateChart(oxygenLevelChart, data.SPO2);
    }

    function updateMetric(type, value, unit) {
        const element = document.getElementById(`${type}-value`);
        if (element) {
            const formattedValue = type === 'temperature' ? value.toFixed(1) : Math.round(value);
            element.innerHTML = `${formattedValue}${unit ? ` <span class="metric-unit">${unit}</span>` : ''}`;
        }
    }

    function updateStatus(type, value, min, max) {
        const statusElement = document.getElementById(`${type}-status`);
        if (!statusElement) return;

        if (value < min) {
            statusElement.textContent = 'Bajo';
            statusElement.className = 'metric-status status-moderate';
        } else if (value > max) {
            statusElement.textContent = 'Alto';
            statusElement.className = 'metric-status status-alert';
        } else {
            statusElement.textContent = 'Normal';
            statusElement.className = 'metric-status status-normal';
        }
    }

    function updateChart(chart, value) {
        const now = new Date();
        const time = now.toLocaleTimeString();

        chart.data.labels.push(time);
        chart.data.datasets[0].data.push(value);

        if (chart.data.labels.length > 15) {
            chart.data.labels.shift();
            chart.data.datasets[0].data.shift();
        }

        chart.update();
    }

    function checkForAlerts(data) {
        const alerts = [];
        const recommendations = [];

        if (data.BPM < 60) {
            alerts.push('Ritmo cardíaco bajo detectado');
            recommendations.push('Realizar actividad física moderada');
        } else if (data.BPM > 100) {
            alerts.push('Ritmo cardíaco alto detectado');
            recommendations.push('Descansar y relajarse');
        }

        if (data.TEMP < 36.0) {
            alerts.push('Temperatura corporal baja');
            recommendations.push('Abrigarse y tomar líquidos calientes');
        } else if (data.TEMP > 37.5) {
            alerts.push('Fiebre detectada');
            recommendations.push('Tomar medicamento para la fiebre y descansar');
        }

        if (data.SPO2 < 95) {
            alerts.push('Nivel de oxígeno bajo');
            recommendations.push('Realizar ejercicios de respiración profunda');
            if (data.SPO2 < 92) {
                alerts.push('Nivel de oxígeno crítico');
                recommendations.push('Buscar atención médica inmediata');
            }
        }

        if (alerts.length > 0) {
            showAlerts(alerts);
            showRecommendations(recommendations);
            showNotificationBadge(alerts.length);
        }
    }

    function showAlerts(alerts) {
        const alertList = document.getElementById('alert-list');
        alertList.innerHTML = '';

        alerts.forEach(alert => {
            const alertItem = document.createElement('div');
            alertItem.className = 'alert-item';
            alertItem.innerHTML = `
                <div class="alert-indicator"></div>
                <div class="alert-content">
                    <p class="alert-message">${alert}</p>
                    <p class="alert-time">${new Date().toLocaleString()}</p>
                </div>
            `;
            alertList.appendChild(alertItem);
        });
    }

    function showRecommendations(recommendations) {
        const recList = document.getElementById('recommendation-list');
        recList.innerHTML = '';

        recommendations.forEach(rec => {
            const recItem = document.createElement('div');
            recItem.className = 'recommendation-item';
            recItem.innerHTML = `
                <div class="recommendation-icon">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
                <p class="recommendation-text">${rec}</p>
            `;
            recList.appendChild(recItem);
        });
    }

    function showNotificationBadge(count) {
        const badge = document.getElementById('notification-badge');
        badge.textContent = count;
        badge.classList.remove('hidden');

        document.getElementById('notification-button').addEventListener('click', function() {
            badge.classList.add('hidden');
        }, { once: true });
    }

    fetch('/api/sensor-data')
        .then(response => response.json())
        .then(data => {
            updateDashboard(data);
        })
        .catch(error => console.error('Error al cargar datos iniciales:', error));
});
