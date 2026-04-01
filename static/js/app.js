document.addEventListener("DOMContentLoaded", function() {
    // 1. Initialize Map (Center on Central Asia: Tashkent area)
    const map = L.map('map', { 
        zoomControl: false,
        attributionControl: false 
    }).setView([41.311081, 69.240562], 7);
    
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // 2. Map Layer (Standard OSM with CSS Dark Filter from base.html)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    const sensorMarkers = {};
    const depositMarkers = {};

    // 3. Load & Render Water Deposits (Reservoirs/Lakes)
    async function updateDeposits() {
        try {
            const response = await fetch('/api/v1/water-deposits/');
            const deposits = await response.json();

            deposits.forEach(deposit => {
                const { latitude, longitude, id, status, name, radius_meters, description, deposit_type } = deposit;
                
                const color = status === 'critical' ? '#ef4444' : 
                              status === 'warning' ? '#f59e0b' : '#34d399';

                // We use L.circle for actual geographic area representation
                const markerOptions = {
                    radius: radius_meters || 5000,
                    fillColor: '#00aaff', // Bright Blue
                    color: color,        // Border status
                    weight: 3,
                    opacity: 0.8,
                    fillOpacity: 0.35,
                };

                if (depositMarkers[id]) {
                    depositMarkers[id].setStyle(markerOptions);
                } else {
                    const marker = L.circle([latitude, longitude], markerOptions).addTo(map);
                    const typeLabel = deposit_type === 'reservoir' ? 'Suv ombori' : 
                                      deposit_type === 'lake' ? 'Ko\'l' : 'Yer osti suvi';
                    
                    marker.bindPopup(`
                        <div class="p-3 min-w-[200px]">
                            <h3 class="font-bold text-lg text-slate-800 border-b border-slate-200 pb-2 mb-2">${name}</h3>
                            <div class="flex items-center gap-2 mb-3">
                                <span class="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-[10px] font-bold uppercase">${typeLabel}</span>
                                <span class="px-2 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px] font-bold uppercase">UZB</span>
                            </div>
                            <p class="text-sm text-slate-600 mb-4">${description || 'Hududiy suv zaxirasi monitoringi.'}</p>
                            <div class="flex items-center justify-between p-2 bg-slate-50 rounded-lg">
                                <span class="text-xs font-semibold text-slate-500">Holat:</span>
                                <div class="flex items-center gap-2">
                                    <span class="w-2 h-2 rounded-full" style="background-color: ${color}"></span>
                                    <span class="text-xs font-bold uppercase" style="color: ${color}">${status}</span>
                                </div>
                            </div>
                        </div>
                    `, { maxWidth: 300 });
                    depositMarkers[id] = marker;
                }
            });
        } catch (err) {
            console.error("Deposits fetch error:", err);
        }
    }

    // 4. Load & Render Sensors from API
    async function updateMarkers() {
        try {
            const response = await fetch('/api/v1/sensors/');
            const sensors = await response.json();
            
            let activeCount = 0;
            let totalFlow = 0;

            sensors.forEach(sensor => {
                const { latitude, longitude, uid, status, name, max_flow_rate } = sensor;
                
                // Color mapping
                const color = status === 'critical' ? '#ef4444' : 
                              status === 'warning' ? '#f59e0b' : '#10b981';

                const markerOptions = {
                    radius: 10,
                    fillColor: color,
                    color: '#fff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 0.9,
                    className: status === 'critical' ? 'animate-pulse' : ''
                };

                if (sensorMarkers[uid]) {
                    sensorMarkers[uid].setStyle(markerOptions);
                } else {
                    const marker = L.circleMarker([latitude, longitude], markerOptions).addTo(map);
                    marker.bindPopup(`
                        <div class="p-2 text-slate-800">
                            <h3 class="font-bold border-b pb-1 mb-1">${name}</h3>
                            <p class="text-xs">UID: ${uid}</p>
                            <p class="text-xs font-bold text-blue-600">Flow: ${max_flow_rate} m³/s</p>
                        </div>
                    `);
                    sensorMarkers[uid] = marker;
                }

                if (sensor.is_active) activeCount++;
                // In production, totalFlow would come from live telemetry aggregation
            });

            // Update UI elements
            document.getElementById('sensor-count').innerText = activeCount;
            document.getElementById('total-flow').innerText = `${totalFlow.toFixed(1)} m³/s`;

        } catch (err) {
            console.error("Map transition error:", err);
        }
    }

    // Initial load and periodic refresh
    updateMarkers();
    updateDeposits();
    setInterval(() => {
        updateMarkers();
        updateDeposits();
    }, 5000); 
});
