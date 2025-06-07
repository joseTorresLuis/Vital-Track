<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VitalTrack - Panel de Monitoreo</title>
    <link rel="stylesheet" href="{{ asset('css/dashboard.css') }}">
    <link rel="stylesheet" href="{{ asset('css/status.css') }}">
</head>
<body>
<header class="main-header">
    <div class="container header-container">
        <div class="logo-container">
            <img src="{{ secure_asset('/icons/vitaltrack-white.png') }}" alt="VitalTrack">
        </div>

        <nav class="main-nav">
            <a href="#" class="nav-link active">Resumen</a>
            <a href="#" class="nav-link">Reportes</a>
            <a href="#" class="nav-link">Alertas</a>
            <a href="#" class="nav-link">Ajustes</a>
            <a href="#" class="nav-link">Perfil Paciente</a>
            <a href="#" class="nav-link">Perfil Usuario</a>
            <a href="#" class="nav-link">Cerrar Sesión</a>
        </nav>

        <button class="mobile-menu-button" id="mobile-menu-button">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
        </button>
    </div>

    <div class="mobile-menu hidden" id="mobile-menu">
        <div class="container mobile-menu-content">
            <a href="#" class="mobile-nav-link active">Resumen</a>
            <a href="#" class="mobile-nav-link">Reportes</a>
            <a href="#" class="mobile-nav-link">Alertas</a>
            <a href="#" class="mobile-nav-link">Ajustes</a>
            <a href="#" class="mobile-nav-link">Perfil Paciente</a>
            <a href="#" class="mobile-nav-link">Perfil Usuario</a>
            <a href="#" class="nav-link">Cerrar Sesión</a>
        </div>
    </div>
</header>

<div class="main-content">
    <header class="secondary-header">
        <div class="container secondary-header-container">
            <h1 class="page-title">Monitoreo en tiempo real</h1>

            <div class="user-info">
                <div class="user-text">
                    <p class="user-label">Usuario Conectado</p>
                    <p class="user-name">John Doe</p>
                </div>

                <button class="notification-button" id="notification-button">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path>
                    </svg>
                    <span class="notification-badge hidden" id="notification-badge"></span>
                </button>
            </div>
        </div>
    </header>

    <main class="content-container">
        <div class="container">
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-header">
                        <h3 class="metric-title">Ritmo cardíaco</h3>
                        <span class="metric-status status-normal" id="heart-rate-status">Cargando...</span>
                    </div>
                    <div>
                        <p class="metric-description">Lectura actual</p>
                        <p class="metric-value" id="heart-rate-value">-- <span class="metric-unit">lpm</span></p>
                        <p class="metric-description">60 min. - 110 max</p>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-header">
                        <h3 class="metric-title">Temperatura</h3>
                        <span class="metric-status status-normal" id="temperature-status">Cargando...</span>
                    </div>
                    <div>
                        <p class="metric-description">Lectura actual</p>
                        <p class="metric-value" id="temperature-value">--° <span class="metric-unit">C</span></p>
                        <p class="metric-description">36.0° - 37.5° normal</p>
                    </div>
                </div>

                <div class="metric-card">
                    <div class="metric-header">
                        <h3 class="metric-title">Nivel de oxígeno</h3>
                        <span class="metric-status status-normal" id="oxygen-status">Cargando...</span>
                    </div>
                    <div>
                        <p class="metric-value" id="oxygen-value">--%</p>
                        <p class="metric-description">95% - 100% normal</p>
                    </div>
                </div>
            </div>

            <div class="charts-grid">
                <div class="chart-card">
                    <div class="chart-header">
                        <h2 class="chart-title">Ritmo cardíaco</h2>
                        <span class="chart-unit">Latidos por minuto</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="heartRateChart"></canvas>
                    </div>
                </div>

                <div class="chart-card">
                    <div class="chart-header">
                        <h2 class="chart-title">Temperatura</h2>
                        <span class="chart-unit">°C</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="temperatureChart"></canvas>
                    </div>
                </div>

                <div class="chart-card">
                    <div class="chart-header">
                        <h2 class="chart-title">Nivel de oxígeno</h2>
                        <span class="chart-unit">%</span>
                    </div>
                    <div class="chart-container">
                        <canvas id="oxygenLevelChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="alerts-grid">
                <div class="alert-card">
                    <h2 class="alert-title">Alertas Registradas</h2>
                    <div class="alert-list" id="alert-list">
                    </div>
                </div>

                <div class="recommendation-card">
                    <h2 class="recommendation-title">Recomendaciones</h2>
                    <div class="recommendation-list" id="recommendation-list">
                    </div>
                </div>
            </div>
        </div>
    </main>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://js.pusher.com/7.0/pusher.min.js"></script>
{{-- <script src="{{ asset('js/app.js') }}"></script> --}}
<script>
    // Configuración de Pusher
    window.pusherConfig = {
        key: '{{ config('broadcasting.connections.pusher.key') }}',
        cluster: '{{ config('broadcasting.connections.pusher.options.cluster') }}'
    };

    // Variables globales para los gráficos de Chart.js
    let heartRateChart, temperatureChart, oxygenLevelChart;

    // Función para actualizar el estado visual (Normal, Alto, Bajo)
    function updateStatus(elementId, value, normalMin, normalMax, unit) {
        const statusElement = document.getElementById(elementId + '-status');
        const valueElement = document.getElementById(elementId + '-value');

        // Manejo de valores undefined o nulos
        if (value === undefined || value === null || value === '') {
            valueElement.textContent = '--' + (unit || '');
            statusElement.textContent = 'Sin datos';
            statusElement.classList.remove('status-normal', 'status-high', 'status-low'); // Asegurarse de quitar clases
            statusElement.classList.add('status-normal'); // O una clase para 'sin datos' si la tienes
            return; // Salir de la función si no hay valor válido
        }

        valueElement.textContent = value + (unit || ''); // Actualiza el valor

        // Elimina clases de estado anteriores
        statusElement.classList.remove('status-normal', 'status-high', 'status-low');

        // Asigna la clase de estado según el valor
        if (value >= normalMin && value <= normalMax) {
            statusElement.textContent = 'Normal';
            statusElement.classList.add('status-normal');
        } else if (value > normalMax) {
            statusElement.textContent = 'Alto';
            statusElement.classList.add('status-high');
        } else { // value < normalMin
            statusElement.textContent = 'Bajo';
            statusElement.classList.add('status-low');
        }
    }

    // Función para añadir nuevos datos a un gráfico
    function addDataToChart(chart, label, newData) {
        if (!chart) return; // Asegúrate de que el gráfico esté inicializado

        chart.data.labels.push(label);
        chart.data.datasets.forEach((dataset) => {
            dataset.data.push(newData);
        });
        // Limita el número de puntos en el gráfico para mantenerlo legible
        const maxDataPoints = 15; // Coincide con el take(15) de tu API
        if (chart.data.labels.length > maxDataPoints) {
            chart.data.labels.shift(); // Elimina el primer elemento
            chart.data.datasets.forEach((dataset) => {
                dataset.data.shift(); // Elimina el primer dato del dataset
            });
        }
        chart.update(); // Actualiza el gráfico
    }

    // Función para inicializar los gráficos
    function initializeCharts(labels, heartRateData, temperatureData, oxygenLevelData) {
        const ctxHeartRate = document.getElementById('heartRateChart').getContext('2d');
        heartRateChart = new Chart(ctxHeartRate, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Ritmo Cardíaco (lpm)',
                    data: heartRateData,
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, // Permite que el gráfico se ajuste al contenedor
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'LPM'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Tiempo'
                        }
                    }
                }
            }
        });

        const ctxTemperature = document.getElementById('temperatureChart').getContext('2d');
        temperatureChart = new Chart(ctxTemperature, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Temperatura (°C)',
                    data: temperatureData,
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false, // La temperatura no empieza en 0
                        title: {
                            display: true,
                            text: '°C'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Tiempo'
                        }
                    }
                }
            }
        });

        const ctxOxygenLevel = document.getElementById('oxygenLevelChart').getContext('2d');
        oxygenLevelChart = new Chart(ctxOxygenLevel, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Nivel de Oxígeno (%)',
                    data: oxygenLevelData,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    fill: true,
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100, // El nivel de oxígeno no puede ser más del 100%
                        title: {
                            display: true,
                            text: '%'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Tiempo'
                        }
                    }
                }
            }
        });
    }

    // Función principal para cargar y mostrar los datos
    document.addEventListener('DOMContentLoaded', function() {
        // URL de tu API para obtener los datos
        const apiUrl = 'http://127.0.0.1:8000/api/datos';

        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Error HTTP: ${response.status} ${response.statusText}`);
                }
                return response.json();
            })
            .then(apiResponse => {
                const data = apiResponse.data; // Accede al array de datos dentro del objeto 'data'

                if (data && data.length > 0) {
                    // Ordenar los datos por created_at en orden ascendente para los gráficos
                    data.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

                    // Obtener el último dato para los valores actuales
                    const latestData = data[data.length - 1];

                    // Actualizar los valores actuales en las tarjetas (Usando heart_rate, temperature, oxygen_level)
                    updateStatus('heart-rate', latestData.heart_rate, 60, 100, ' lpm');
                    updateStatus('temperature', latestData.temperature, 36.0, 37.5, '° C');
                    updateStatus('oxygen', latestData.oxygen_level, 95, 100, '%');

                    // Preparar datos para los gráficos (Usando heart_rate, temperature, oxygen_level)
                    const labels = data.map(item => new Date(item.created_at).toLocaleTimeString());
                    const heartRateData = data.map(item => item.heart_rate);
                    const temperatureData = data.map(item => item.temperature);
                    const oxygenLevelData = data.map(item => item.oxygen_level);

                    // Inicializar los gráficos
                    initializeCharts(labels, heartRateData, temperatureData, oxygenLevelData);

                } else {
                    console.warn('No hay datos disponibles de la API.');
                    // Mostrar "No hay datos" o mantener "--"
                    updateStatus('heart-rate', undefined, 60, 100, ' lpm');
                    updateStatus('temperature', undefined, 36.0, 37.5, '° C');
                    updateStatus('oxygen', undefined, 95, 100, '%');
                }
            })
            .catch(error => {
                console.error('Error al cargar los datos iniciales:', error);
                document.getElementById('heart-rate-status').textContent = 'Error';
                document.getElementById('temperature-status').textContent = 'Error';
                document.getElementById('oxygen-status').textContent = 'Error';
            });

        // --- Integración con Pusher para actualizaciones en tiempo real ---
        if (window.pusherConfig && window.pusherConfig.key && window.pusherConfig.cluster) {
            try {
                Pusher.logToConsole = true; // Solo para depuración

                const pusher = new Pusher(window.pusherConfig.key, {
                    cluster: window.pusherConfig.cluster,
                    encrypted: true
                });

                // ¡CORREGIDO: Nombre del evento y acceso a los datos!
                const channel = pusher.subscribe('sensor-data');
                channel.bind('SensorDataUpdated', function(eventData) { // <-- Cambiado 'data' a 'eventData' para evitar conflictos
                    console.log('Nuevo dato recibido de Pusher:', eventData);

                    // Acceder al objeto 'data' dentro de 'eventData'
                    const newDato = eventData.data;

                    if (newDato) {
                        // Actualizar los valores actuales en las tarjetas
                        updateStatus('heart-rate', newDato.BPM, 60, 100, ' lpm');
                        updateStatus('temperature', newDato.TEMP, 36.0, 37.5, '° C');
                        updateStatus('oxygen', newDato.SPO2, 95, 100, '%');

                        // Actualizar los gráficos si están inicializados
                        const newLabel = new Date(newDato.created_at).toLocaleTimeString();
                        if (heartRateChart) addDataToChart(heartRateChart, newLabel, newDato.BPM);
                        if (temperatureChart) addDataToChart(temperatureChart, newLabel, newDato.TEMP);
                        if (oxygenLevelChart) addDataToChart(oxygenLevelChart, newLabel, newDato.SPO2);

                        // Lógica para alertas y recomendaciones
                        if (newDato.BPM > 100 || newDato.BPM < 60) {
                            const alertList = document.getElementById('alert-list');
                            const alertItem = document.createElement('p');
                            alertItem.className = 'alert-item';
                            alertItem.textContent = `Alerta: Ritmo cardíaco ${newDato.BPM} lpm (${newLabel})`;
                            alertList.prepend(alertItem);
                        }
                        if (newDato.TEMP > 37.5 || newDato.TEMP < 36.0) {
                            const alertList = document.getElementById('alert-list');
                            const alertItem = document.createElement('p');
                            alertItem.className = 'alert-item';
                            alertItem.textContent = `Alerta: Temperatura ${newDato.TEMP}°C (${newLabel})`;
                            alertList.prepend(alertItem);
                        }
                        if (newDato.SPO2 < 95) {
                            const alertList = document.getElementById('alert-list');
                            const alertItem = document.createElement('p');
                            alertItem.className = 'alert-item';
                            alertItem.textContent = `Alerta: Nivel de oxígeno ${newDato.SPO2}% (${newLabel})`;
                            alertList.prepend(alertItem);
                        }
                    }
                });

            } catch (e) {
                console.error('Error inicializando Pusher:', e);
            }
        } else {
            console.warn('Pusher no se ha configurado correctamente. Las actualizaciones en tiempo real no funcionarán.');
        }
    });
</script>
{{-- <script src="{{asset('js/dashboard.js')}}"></script> --}}
</body>
</html>
