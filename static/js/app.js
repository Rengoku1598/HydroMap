document.addEventListener("DOMContentLoaded", function() {
    // 1. Initialize Map
    const map = L.map('map', { 
        zoomControl: false,
        attributionControl: false 
    }).setView([41.35, 64.3], 6);
    
    window.map = map; // For global access

    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // 2. Map Layers
    const layers = {
        geo: L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; OpenStreetMap &copy; CARTO'
        }),
        sat: L.layerGroup([
            L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'),
            L.tileLayer('https://services.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}')
        ]),
        topo: L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png')
    };
    
    layers.geo.addTo(map);
    let currentLayer = 'geo';

    function switchLayer(type) {
        map.removeLayer(layers[currentLayer]);
        layers[type].addTo(map);
        currentLayer = type;
        
        // Apply or remove dark filter based on type
        const pane = map.getPane('tilePane');
        if (type === 'geo') {
            pane.style.filter = 'invert(100%) hue-rotate(180deg) brightness(95%) contrast(85%) grayscale(20%)';
        } else {
            pane.style.filter = 'none';
        }
    }

    document.getElementById('map-sat')?.addEventListener('click', () => switchLayer('sat'));
    document.getElementById('map-geo')?.addEventListener('click', () => switchLayer('geo'));
    document.getElementById('map-topo')?.addEventListener('click', () => switchLayer('topo'));

    const depositMarkers = {};

    // 2.5 Load and Render Major Waterways (Uzbekistan)
    fetch('/static/js/uz_water.geojson')
        .then(response => response.json())
        .then(data => {
            // Render Waterways (Optimized single pass)
            L.geoJSON(data, {
                style: function (feature) {
                    if (feature.properties.type === 'waterbody') {
                        return {
                            color: '#00f3ff', // Bright neon outline
                            weight: 2,
                            fillColor: '#0055ff',
                            fillOpacity: 0.15,
                            opacity: 0.9,
                            className: 'neon-waterbody',
                            interactive: false
                        };
                    } else {
                        return {
                            color: '#00f3ff', // Bright neon river
                            weight: 1.5,
                            opacity: 0.8,
                            className: 'flowing-water',
                            interactive: false
                        };
                    }
                }
            }).addTo(map);
        })
        .catch(err => console.error("Could not load Uzbekistan waterways:", err));

    // 3. Load & Render Water Deposits
    async function updateDeposits() {
        try {
            const response = await fetch('/api/v1/water-deposits/');
            const deposits = await response.json();

            deposits.forEach(deposit => {
                const { latitude, longitude, id, status } = deposit;
                
                const color = status === 'critical' ? '#ef4444' : 
                              status === 'warning' ? '#f59e0b' : '#10b981';

                const markerOptions = {
                    radius: 8000,
                    fillColor: color,
                    color: color,
                    weight: 2,
                    opacity: 0.8,
                    fillOpacity: 0.4,
                };

                if (depositMarkers[id]) {
                    depositMarkers[id].setLatLng([latitude, longitude]);
                    depositMarkers[id].setStyle(markerOptions);
                } else {
                    const marker = L.circle([latitude, longitude], markerOptions).addTo(map);
                    depositMarkers[id] = marker;
                    
                    marker.on('click', () => {
                        showDepositInfo(id);
                    });
                }
            });
        } catch (error) {
            console.error('Error loading deposits:', error);
        }
    }

    updateDeposits();
    setInterval(updateDeposits, 10000); // 10s updates
});

function focusOnDeposit(id, lat, lng) {
    if (window.map) {
        window.map.setView([lat, lng], 10, { animate: true, duration: 1.5 });
        showDepositInfo(id);
    }
}

function showDepositInfo(id) {
    const lang = new URLSearchParams(window.location.search).get('lang') || 'uz';
    const detailUrl = `/details/${id}/?lang=${lang}`;
    
    fetch(detailUrl)
        .then(response => response.text())
        .then(html => {
            const modal = document.getElementById('details-modal');
            const content = document.getElementById('details-content');
            if (modal && content) {
                content.innerHTML = html;
                modal.classList.remove('hidden');
                modal.classList.add('flex');
            }
        });
}

function closeDetails() {
    const modal = document.getElementById('details-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}

// ─────────────────────────────────────────────────────────
//  AquaAI Chatbot Logic
// ─────────────────────────────────────────────────────────

let aquaaiOpen = false;

function toggleAquaAI() {
    const panel = document.getElementById('aquaai-panel');
    aquaaiOpen = !aquaaiOpen;
    if (aquaaiOpen) {
        panel.classList.remove('hidden');
        panel.classList.add('flex');
        // Animate in
        panel.style.animation = 'aquaPanelIn 0.35s cubic-bezier(0.34,1.56,0.64,1) both';
        document.getElementById('aquaai-input')?.focus();
        scrollAquaToBottom();
    } else {
        panel.style.animation = 'aquaPanelOut 0.25s ease-in both';
        setTimeout(() => {
            panel.classList.add('hidden');
            panel.classList.remove('flex');
        }, 220);
    }
}

function scrollAquaToBottom() {
    const msgs = document.getElementById('aquaai-messages');
    if (msgs) msgs.scrollTop = msgs.scrollHeight;
}

function aquaaiAppendUser(text) {
    const msgs = document.getElementById('aquaai-messages');
    const div = document.createElement('div');
    div.className = 'flex justify-end';
    div.innerHTML = `
        <div class="max-w-[75%] bg-gradient-to-br from-cyan-600/30 to-blue-600/30 border border-cyan-500/20
                    rounded-2xl rounded-tr-sm px-4 py-2.5 text-[12px] text-slate-100 leading-relaxed">
            ${escapeHtml(text)}
        </div>`;
    msgs.appendChild(div);
    scrollAquaToBottom();
}

function aquaaiAppendBot(html) {
    const msgs = document.getElementById('aquaai-messages');
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    const node = tmp.firstElementChild;
    if (node) {
        msgs.appendChild(node);
        scrollAquaToBottom();
    }
}

function setTyping(show) {
    const t = document.getElementById('aquaai-typing');
    if (t) t.classList.toggle('hidden', !show);
    if (show) scrollAquaToBottom();
}

function escapeHtml(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

async function aquaaiSend() {
    const input = document.getElementById('aquaai-input');
    const message = (input?.value || '').trim();
    if (!message) return;

    input.value = '';
    input.disabled = true;

    aquaaiAppendUser(message);
    setTyping(true);

    const lang = new URLSearchParams(window.location.search).get('lang') || 'uz';
    const csrfToken = getCookie('csrftoken');

    try {
        const resp = await fetch(`/ai-chat/?lang=${lang}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken,
                'HX-Request': 'true',
            },
            body: `message=${encodeURIComponent(message)}`,
        });
        const html = await resp.text();
        setTyping(false);
        aquaaiAppendBot(html);
    } catch (err) {
        setTyping(false);
        aquaaiAppendBot(`<div class="flex items-start gap-2.5">
            <div class="flex-1 bg-red-900/30 border border-red-500/20 rounded-2xl px-4 py-3 text-[12px] text-red-300">
                ⚠️ Xatolik yuz berdi. Qayta urinib ko'ring.
            </div></div>`);
    } finally {
        input.disabled = false;
        input?.focus();
    }
}

// Quick actions map
const QUICK_MESSAGES = {
    'theft': {
        'uz': "suv o'g'irlanishi haqida ma'lumot bering",
        'ru': "расскажите о краже воды",
        'en': "tell me about water theft"
    },
    'forecast': {
        'uz': "24 soatlik bashorat",
        'ru': "прогноз на 24 часа",
        'en': "24 hour forecast"
    },
    'weather': {
        'uz': "ob-havo holati",
        'ru': "погода",
        'en': "weather status"
    },
    'critical': {
        'uz': "kritik holatlar haqida ayt",
        'ru': "расскажите о критических ситуациях",
        'en': "tell me about critical situations"
    },
};

function aquaaiQuick(type) {
    const lang = new URLSearchParams(window.location.search).get('lang') || 'uz';
    const msg = QUICK_MESSAGES[type]?.[lang] || QUICK_MESSAGES[type]?.['uz'] || type;
    const input = document.getElementById('aquaai-input');
    if (input) {
        input.value = msg;
        aquaaiSend();
    }
}

// Enter key support
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('aquaai-input');
    input?.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            aquaaiSend();
        }
    });
});

function getCookie(name) {
    const v = document.cookie.match('(^|;) ?' + name + '=([^;]*)(;|$)');
    return v ? v[2] : '';
}

// Panel animation keyframes (injected once)
(function() {
    const style = document.createElement('style');
    style.textContent = `
        @keyframes aquaPanelIn {
            from { opacity:0; transform: scale(0.85) translateY(20px); transform-origin: bottom right; }
            to   { opacity:1; transform: scale(1)    translateY(0);    transform-origin: bottom right; }
        }
        @keyframes aquaPanelOut {
            from { opacity:1; transform: scale(1)    translateY(0);    transform-origin: bottom right; }
            to   { opacity:0; transform: scale(0.88) translateY(12px);  transform-origin: bottom right; }
        }
    `;
    document.head.appendChild(style);
})();

