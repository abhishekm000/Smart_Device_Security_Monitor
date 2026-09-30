/* ================================================================
   SMART DEVICE SECURITY MONITOR — MAIN APPLICATION LOGIC
   ================================================================ */

const API = 'http://127.0.0.1:5000/api';
let threatChart = null;
let refreshTimer = null;
let simRunning   = false;

/* ── CLOCK ── */
function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toLocaleTimeString('en-GB', {hour:'2-digit', minute:'2-digit', second:'2-digit'});
}
setInterval(updateClock, 1000);
updateClock();

/* ── TOAST ── */
function showToast(msg, type='') {
  const tc = document.getElementById('toastContainer');
  const t  = document.createElement('div');
  t.className = `toast ${type ? 'toast-' + type : ''}`;
  t.textContent = msg;
  tc.appendChild(t);
  setTimeout(() => t.remove(), 3100);
}

/* ── MODAL ── */
function closeModal() {
  document.getElementById('alertModal').classList.remove('open');
}
document.getElementById('alertModal').addEventListener('click', e => {
  if (e.target === document.getElementById('alertModal')) closeModal();
});

/* ── PAGE ROUTER ── */
function showPage(page, btn) {
  clearInterval(refreshTimer);
  if (btn) {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }
  const c = document.getElementById('mainContent');
  c.innerHTML = '';
  c.style.animation = 'none';
  void c.offsetWidth;
  c.style.animation = 'fadeIn 0.3s ease';

  const pages = { dashboard, alerts, devices, models, simulation };
  if (pages[page]) pages[page]();
}

/* ════════════════════════════════════════
   PAGE: DASHBOARD
   ════════════════════════════════════════ */
async function dashboard() {
  const c = document.getElementById('mainContent');
  c.innerHTML = `
    <div class="page-title"><span class="title-bar"></span> THREAT OVERVIEW</div>

    <div class="stat-cards">
      <div class="stat-card card-total">
        <div class="stat-label">Total Alerts</div>
        <div class="stat-value" id="st-total">…</div>
        <span class="stat-icon">📡</span>
      </div>
      <div class="stat-card card-high">
        <div class="stat-label">High Risk</div>
        <div class="stat-value" id="st-high">…</div>
        <span class="stat-icon">🔴</span>
      </div>
      <div class="stat-card card-devices">
        <div class="stat-label">Active Devices</div>
        <div class="stat-value" id="st-dev">…</div>
        <span class="stat-icon">📶</span>
      </div>
      <div class="stat-card card-benign">
        <div class="stat-label">Normal Traffic</div>
        <div class="stat-value" id="st-benign">…</div>
        <span class="stat-icon">✅</span>
      </div>
    </div>

    <div class="panel-grid">
      <div class="panel">
        <div class="panel-header"><span class="ph-dot"></span> THREAT DISTRIBUTION</div>
        <div class="panel-body"><div class="chart-wrap"><canvas id="threatChart"></canvas></div></div>
      </div>
      <div class="panel">
        <div class="panel-header"><span class="ph-dot"></span> RECENT ALERTS</div>
        <div class="panel-body" style="padding:0">
          <table class="cyber-table">
            <thead><tr><th>Time</th><th>Threat</th><th>Risk</th><th>Device</th></tr></thead>
            <tbody id="recentAlerts"></tbody>
          </table>
        </div>
      </div>
    </div>
  `;

  await loadDashboardData();
  refreshTimer = setInterval(loadDashboardData, 4000);
}

async function loadDashboardData() {
  try {
    const [alertsRes, devRes] = await Promise.all([
      fetch(API + '/alerts?limit=100'),
      fetch(API + '/devices')
    ]);
    const alerts  = await alertsRes.json();
    const devices = await devRes.json();

    animateNumber('st-total',  alerts.length);
    animateNumber('st-high',   alerts.filter(a => a.risk_level === 'HIGH').length);
    animateNumber('st-dev',    devices.length);
    animateNumber('st-benign', alerts.filter(a => a.prediction === 'Benign').length);

    // Donut chart
    const counts = {};
    alerts.forEach(a => counts[a.prediction] = (counts[a.prediction]||0)+1);
    const colors = ['#00f5ff','#ff2255','#ff8800','#00ff88','#bf00ff','#0080ff','#ffdd00','#ff66cc'];
    const el = document.getElementById('threatChart');
    if (el) {
      if (threatChart) threatChart.destroy();
      threatChart = new Chart(el, {
        type: 'doughnut',
        data: {
          labels: Object.keys(counts),
          datasets: [{ data: Object.values(counts), backgroundColor: colors, borderColor: '#040d1a', borderWidth: 3 }]
        },
        options: {
          cutout: '70%',
          animation: { animateScale: true },
          plugins: {
            legend: { position:'right', labels: { color:'#e8f4fd', font:{ family:'Rajdhani', size:13, weight:'600' }, padding:16 } }
          }
        }
      });
    }

    // Recent alerts table
    const tbody = document.getElementById('recentAlerts');
    if (tbody) {
      tbody.innerHTML = '';
      alerts.slice(0,8).forEach(a => {
        const dev = devices.find(d => d.id === a.device_id);
        const devName = dev ? dev.name : (a.device_id||'—');
        
        const row = document.createElement('tr');
        row.onclick = () => showAlertModal(a.id);
        row.innerHTML = `
          <td style="font-family:'Share Tech Mono',monospace;font-size:0.75rem">${new Date(a.timestamp).toLocaleTimeString()}</td>
          <td style="color:var(--accent-cyan);font-weight:700">${a.prediction}</td>
          <td><span class="badge-risk badge-${a.risk_level}">${a.risk_level}</span></td>
          <td style="color:var(--text-dim)">${devName}</td>`;
        tbody.appendChild(row);
      });
    }
  } catch(e) {
    showToast('API unreachable — start python run.py', 'red');
  }
}

function animateNumber(id, target) {
  const el = document.getElementById(id);
  if (!el) return;
  const start = parseInt(el.textContent) || 0;
  const dur = 600, steps = 20;
  let i = 0;
  const tick = setInterval(() => {
    i++;
    el.textContent = Math.round(start + (target - start) * (i / steps));
    if (i >= steps) clearInterval(tick);
  }, dur / steps);
}

/* ════════════════════════════════════════
   AUDIO ALARM SYSTEM
   ════════════════════════════════════════ */
const AudioContext = window.AudioContext || window.webkitAudioContext;
let audioCtx;
function playAlarm() {
  if (!audioCtx) audioCtx = new AudioContext();
  if (audioCtx.state === 'suspended') audioCtx.resume();
  
  const osc = audioCtx.createOscillator();
  const gainNode = audioCtx.createGain();
  
  osc.type = 'square';
  osc.frequency.setValueAtTime(880, audioCtx.currentTime); // High pitch A5
  osc.frequency.exponentialRampToValueAtTime(440, audioCtx.currentTime + 0.1);
  
  gainNode.gain.setValueAtTime(0.1, audioCtx.currentTime);
  gainNode.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
  
  osc.connect(gainNode);
  gainNode.connect(audioCtx.destination);
  
  osc.start();
  osc.stop(audioCtx.currentTime + 0.15);
}

/* ════════════════════════════════════════
   GEO IP TRACKER MOCK
   ════════════════════════════════════════ */
const GEO_LOCATIONS = ["🇷🇺 Russia", "🇨🇳 China", "🇺🇸 USA", "🇧🇷 Brazil", "🇮🇷 Iran", "🇰🇵 North Korea", "🇩🇪 Germany", "🌍 External"];
function getGeoForIp(ip) {
  if (ip === "External") return GEO_LOCATIONS[Math.floor(Math.random() * GEO_LOCATIONS.length)];
  return "🏠 Internal LAN";
}

/* ════════════════════════════════════════
   PAGE: ALERTS
   ════════════════════════════════════════ */
async function alerts() {
  document.getElementById('mainContent').innerHTML = `
    <div class="page-title" style="display:flex; justify-content:space-between; width:100%">
      <div style="display:flex; align-items:center; gap:14px">
        <span class="title-bar"></span> ALERT LOG
      </div>
      <div style="display:flex; gap:10px">
        <button class="btn-cyber btn-red" onclick="clearAlerts()"><span>🗑 CLEAR ALERTS</span></button>
        <button class="btn-cyber btn-green" onclick="exportCSV()"><span>📥 EXPORT CSV</span></button>
      </div>
    </div>
    <div class="panel">
      <div class="panel-header"><span class="ph-dot"></span> ALL SECURITY EVENTS</div>
      <div class="panel-body" style="padding:0;overflow-x:auto">
        <table class="cyber-table">
          <thead><tr><th>#</th><th>Timestamp</th><th>Device</th><th>Source</th><th>Threat</th><th>Risk</th><th>Status</th></tr></thead>
          <tbody id="alertsTable"></tbody>
        </table>
      </div>
    </div>`;
  try {
    const res    = await fetch(API + '/alerts');
    const devRes = await fetch(API + '/devices');
    const data   = await res.json();
    const devices= await devRes.json();
    
    // Save data globally for CSV export
    window._currentAlertsData = data;
    window._currentDevicesData = devices;
    
    const tbody  = document.getElementById('alertsTable');
    data.forEach(a => {
      const dev = devices.find(d => d.id === a.device_id);
      const devName = dev ? dev.name : (a.device_id||'—');
      const geoLoc = getGeoForIp(a.source_ip);
      
      const row = document.createElement('tr');
      row.onclick = () => showAlertModal(a.id);
      row.innerHTML = `
        <td style="font-family:'Share Tech Mono',monospace;color:var(--text-dim)">${a.id}</td>
        <td style="font-family:'Share Tech Mono',monospace;font-size:0.75rem">${new Date(a.timestamp).toLocaleString()}</td>
        <td>${devName}</td>
        <td style="color:var(--text-dim); font-size:0.75rem">${geoLoc}</td>
        <td style="color:var(--accent-cyan);font-weight:700">${a.prediction}</td>
        <td><span class="badge-risk badge-${a.risk_level}">${a.risk_level} (${a.risk_score})</span></td>
        <td style="font-size:0.75rem;color:var(--text-dim)">${a.status}</td>`;
      tbody.appendChild(row);
    });
    if (!data.length) tbody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--text-dim);padding:40px">No alerts yet — run the Simulation!</td></tr>`;
  } catch(e) { showToast('Failed to load alerts', 'red'); }
}

/* ════════════════════════════════════════
   CLEAR ALERTS
   ════════════════════════════════════════ */
window.clearAlerts = async function() {
  if (confirm("Are you sure you want to permanently delete all alerts from the database?")) {
    try {
      const res = await fetch(API + '/alerts', { method: 'DELETE' });
      if (res.ok) {
        showToast('All alerts cleared successfully', 'green');
        alerts(); // Reload the alerts page UI
      } else {
        showToast('Failed to clear alerts', 'red');
      }
    } catch(e) {
      showToast('Error clearing alerts', 'red');
    }
  }
};

/* ════════════════════════════════════════
   CSV EXPORT
   ════════════════════════════════════════ */
window.exportCSV = function() {
  if (!window._currentAlertsData || !window._currentAlertsData.length) {
    showToast('No data to export', 'red');
    return;
  }
  let csv = "ID,Timestamp,Device,Source IP,Threat,Confidence,Risk Score,Risk Level,Status\n";
  window._currentAlertsData.forEach(a => {
    const dev = window._currentDevicesData.find(d => d.id === a.device_id);
    const devName = dev ? dev.name : a.device_id;
    csv += `${a.id},"${a.timestamp}","${devName}","${a.source_ip}","${a.prediction}",${a.confidence},${a.risk_score},${a.risk_level},${a.status}\n`;
  });
  
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.setAttribute('href', url);
  a.setAttribute('download', `Security_Audit_${new Date().getTime()}.csv`);
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  showToast('Security Audit Exported!', 'green');
};

/* ════════════════════════════════════════
   ALERT MODAL
   ════════════════════════════════════════ */
async function showAlertModal(id) {
  try {
    const res = await fetch(`${API}/alerts/${id}`);
    const a   = await res.json();
    let shapHtml = '<p style="color:var(--text-dim);font-size:0.8rem">No SHAP data.</p>';
    if (a.explanation && a.explanation.length) {
      const maxImp = Math.max(...a.explanation.map(e => e.importance));
      shapHtml = a.explanation.map(e => `
        <div class="shap-row">
          <span class="shap-feature">${e.feature}</span>
          <div class="shap-bar-wrap"><div class="shap-bar" style="width:${Math.round(e.importance/maxImp*100)}%"></div></div>
          <span style="font-family:'Orbitron',monospace;font-size:0.7rem;color:var(--accent-blue)">${e.importance.toFixed(4)}</span>
        </div>`).join('');
    }

    document.getElementById('modalBody').innerHTML = `
      <div class="detail-grid">
        <div class="detail-item"><label>Threat Class</label><div class="detail-val" style="color:var(--accent-cyan);font-family:'Orbitron',monospace">${a.prediction}</div></div>
        <div class="detail-item"><label>Risk</label><div class="detail-val"><span class="badge-risk badge-${a.risk_level}">${a.risk_level} — ${a.risk_score}/100</span></div></div>
        <div class="detail-item"><label>Confidence</label><div class="detail-val" style="font-family:'Orbitron',monospace">${(a.confidence*100).toFixed(2)}%</div></div>
        <div class="detail-item"><label>Anomaly</label><div class="detail-val" style="color:${a.anomaly_score<0?'var(--accent-red)':'var(--accent-green)'}">${a.anomaly_score<0?'⚠ YES':'✓ NO'}</div></div>
        <div class="detail-item"><label>Source IP</label><div class="detail-val">${a.source_ip||'—'}</div></div>
        <div class="detail-item"><label>Destination IP</label><div class="detail-val">${a.destination_ip||'—'}</div></div>
        <div class="detail-item"><label>Device</label><div class="detail-val">${a.device_id||'—'}</div></div>
        <div class="detail-item"><label>Time</label><div class="detail-val">${new Date(a.timestamp).toLocaleString()}</div></div>
      </div>
      <div style="margin-top:16px">
        <div style="font-family:'Orbitron',monospace;font-size:0.65rem;letter-spacing:2px;color:var(--text-dim);margin-bottom:10px">WHY WAS THIS DETECTED? (SHAP)</div>
        ${shapHtml}
      </div>
      <div style="margin-top:20px; border: 1px solid var(--accent-orange); border-radius: 4px; padding: 10px; background: rgba(255, 165, 0, 0.05);">
        <div style="font-family:'Orbitron',monospace;font-size:0.75rem;letter-spacing:2px;color:var(--accent-orange);margin-bottom:6px">🤖 GEMINI AI SECURITY COPILOT</div>
        <div id="aiAnalysisText" style="font-size:0.85rem; color:var(--text-bright); line-height:1.5; font-family:'Share Tech Mono', monospace;">
           <span class="spinner" style="display:inline-block; border-color:var(--accent-orange); border-bottom-color:transparent; width:12px; height:12px; border-width:2px; margin-right:8px;"></span> Analyzing threat data...
        </div>
      </div>`;
    document.getElementById('alertModal').classList.add('open');

    // Fetch AI Analysis in background
    fetch(`${API}/alerts/${id}/analysis`)
      .then(r => r.json())
      .then(data => {
        const el = document.getElementById('aiAnalysisText');
        if (el) el.innerHTML = data.ai_report.replace(/\n/g, '<br>');
      })
      .catch(e => {
        const el = document.getElementById('aiAnalysisText');
        if (el) el.innerHTML = '<span style="color:var(--accent-red)">AI Analysis failed or timed out.</span>';
      });

  } catch(e) { showToast('Could not load alert details','red'); }
}

/* ════════════════════════════════════════
   PAGE: DEVICES
   ════════════════════════════════════════ */
async function devices() {
  document.getElementById('mainContent').innerHTML = `
    <div class="page-title"><span class="title-bar"></span> DEVICE INVENTORY</div>
    <div class="panel">
      <div class="panel-header"><span class="ph-dot"></span> REGISTERED DEVICES</div>
      <div class="panel-body" style="padding:0">
        <table class="cyber-table">
          <thead><tr><th>ID</th><th>Name</th><th>Type</th><th>IP Address</th><th>Status</th></tr></thead>
          <tbody id="devTable"></tbody>
        </table>
      </div>
    </div>`;
  try {
    const devs = await (await fetch(API + '/devices')).json();
    const tbody = document.getElementById('devTable');
    devs.forEach(d => {
      tbody.innerHTML += `
        <tr>
          <td style="font-family:'Share Tech Mono',monospace;color:var(--text-dim)">${d.id}</td>
          <td style="font-weight:700">${d.name}</td>
          <td style="color:var(--text-dim)">${d.device_type}</td>
          <td style="font-family:'Share Tech Mono',monospace;color:var(--accent-blue)">${d.ip_address}</td>
          <td><span class="device-status ${d.status==='Online'?'online':'offline'}">● ${d.status}</span></td>
        </tr>`;
    });
  } catch(e) { showToast('Failed to load devices', 'red'); }
}

/* ════════════════════════════════════════
   PAGE: MODELS
   ════════════════════════════════════════ */
async function models() {
  document.getElementById('mainContent').innerHTML = `
    <div class="page-title"><span class="title-bar"></span> ML MODEL PERFORMANCE</div>
    <div class="panel-grid" id="modelsGrid">
      <div style="color:var(--text-dim);padding:40px;font-family:'Share Tech Mono',monospace">
        <span class="spinner"></span> Loading metrics…
      </div>
    </div>`;
  try {
    const m = await (await fetch(API + '/metrics')).json();
    let html = '';
    for (const [name, met] of Object.entries(m)) {
      html += `
        <div class="panel">
          <div class="panel-header"><span class="ph-dot"></span> ${name.toUpperCase()}</div>
          <div class="panel-body">
            ${metricRow('Accuracy',        met.accuracy)}
            ${metricRow('Precision',       met.precision)}
            ${metricRow('Recall',          met.recall)}
            ${metricRow('F1 Score',        met.f1_score)}
            ${metricRow('Detection Rate',  met.detection_rate)}
            ${metricRow('False Positive Rate', met.fpr, false)}
            ${metricRow('False Negative Rate', met.fnr, false)}
          </div>
        </div>`;
    }
    document.getElementById('modelsGrid').innerHTML = html;
    // Animate bars after render
    setTimeout(() => {
      document.querySelectorAll('.metric-bar').forEach(b => {
        b.style.width = b.dataset.w + '%';
      });
    }, 100);
  } catch(e) {
    document.getElementById('modelsGrid').innerHTML =
      `<div style="color:var(--accent-red);padding:30px;font-family:'Share Tech Mono',monospace">
        Models not trained yet.<br>Run: <code style="color:var(--accent-cyan)">python ml/train.py</code></div>`;
  }
}

function metricRow(label, val, higherBetter=true) {
  const pct = Math.round(val * 100);
  const color = higherBetter
    ? (pct > 80 ? 'var(--accent-green)' : pct > 50 ? 'var(--accent-orange)' : 'var(--accent-red)')
    : (pct < 20 ? 'var(--accent-green)' : 'var(--accent-orange)');
  return `
    <div class="metric-row">
      <span class="metric-label">${label}</span>
      <div class="metric-bar-wrap"><div class="metric-bar" data-w="${pct}" style="width:0;background:${color}"></div></div>
      <span class="metric-value" style="color:${color}">${(val*100).toFixed(1)}%</span>
    </div>`;
}

/* ════════════════════════════════════════
   PAGE: SIMULATION
   ════════════════════════════════════════ */
async function simulation() {
  document.getElementById('mainContent').innerHTML = `
    <div class="page-title"><span class="title-bar"></span> LIVE TRAFFIC SIMULATION</div>

    <div class="panel-grid">
      <!-- Manual Injection (Full Width or Half Width) -->
      <div class="panel" style="margin-bottom:20px; grid-column: 1 / -1;">
        <div class="panel-header"><span class="ph-dot"></span> MANUAL PACKET INJECTION</div>
        <div class="panel-body">
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px; margin-bottom:15px;">
            <div>
              <label style="font-size:0.7rem; color:var(--text-dim);">TARGET DEVICE</label>
              <select id="inj-device" class="speed-selector" style="width:100%; margin-top:4px; padding:5px;"></select>
            </div>
            <div>
              <label style="font-size:0.7rem; color:var(--text-dim);">PROTOCOL</label>
              <select id="inj-proto" class="speed-selector" style="width:100%; margin-top:4px; padding:5px;">
                <option value="6">TCP (6)</option>
                <option value="17">UDP (17)</option>
                <option value="1">ICMP (1)</option>
              </select>
            </div>
            <div>
              <label style="font-size:0.7rem; color:var(--text-dim);">PACKET COUNT (Rate)</label>
              <input type="number" id="inj-rate" class="speed-selector" style="width:100%; margin-top:4px; padding:5px;" value="10">
            </div>
            <div>
              <label style="font-size:0.7rem; color:var(--text-dim);">TOTAL SIZE (Bytes)</label>
              <input type="number" id="inj-size" class="speed-selector" style="width:100%; margin-top:4px; padding:5px;" value="500">
            </div>
          </div>
          <button class="btn-cyber btn-green" style="width:100%" onclick="injectPacket()"><span>⚡ INJECT PACKET</span></button>
        </div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-header"><span class="ph-dot"></span> LIVE ALERT FEED</div>
      <div class="panel-body" style="padding:12px">
        <div class="alert-feed" id="alertFeed">
          <div style="color:var(--text-dim);padding:8px">Start simulation or inject packets to see live alerts…</div>
        </div>
      </div>
    </div>`;

  // Load devices for injection dropdown
  try {
    const devs = await (await fetch(API + '/devices')).json();
    const sel = document.getElementById('inj-device');
    devs.forEach(d => {
      sel.innerHTML += `<option value="${d.id}">${d.name} (${d.ip_address})</option>`;
    });
  } catch(e) {}

  refreshTimer = setInterval(async () => {
    try {
      const res  = await fetch(API + '/alerts?limit=30');
      const devRes = await fetch(API + '/devices');
      const data = await res.json();
      const devices = await devRes.json();
      
      const feed = document.getElementById('alertFeed');
      if (!feed) return;
      
      // Check if we have new HIGH risk alerts to play a sound
      if (window._lastAlertId !== undefined && data.length > 0) {
        const newAlerts = data.filter(a => a.id > window._lastAlertId);
        if (newAlerts.some(a => a.risk_level === 'HIGH')) {
            playAlarm();
        }
      }
      if (data.length > 0) window._lastAlertId = data[0].id;
      
      feed.innerHTML = '';
      data.forEach(a => {
        const dev = devices.find(d => d.id === a.device_id);
        const devName = dev ? dev.name : (a.device_id||'');
        
        const line = document.createElement('div');
        line.className = 'feed-line';
        line.innerHTML = `
          <span class="feed-time">${new Date(a.timestamp).toLocaleTimeString()}</span>
          <span class="feed-threat ${a.risk_level}" onclick="showAlertModal(${a.id})" style="cursor:pointer">
            [${a.risk_level}] ${a.prediction} (${(a.confidence*100).toFixed(1)}%) -> ${devName}
          </span>`;
        feed.appendChild(line);
      });
      // Do not auto scroll if user is scrolling up
    } catch(e){}
  }, 2000);
}

// Global function to handle injection
window.injectPacket = async function() {
  const devId = document.getElementById('inj-device').value;
  const proto = parseFloat(document.getElementById('inj-proto').value);
  const rate = parseFloat(document.getElementById('inj-rate').value);
  const size = parseFloat(document.getElementById('inj-size').value);
  
  // Find device IP for simulation
  let ip = "192.168.1.100";
  try {
    const devs = await (await fetch(API + '/devices')).json();
    const dev = devs.find(d => d.id === devId);
    if (dev) ip = dev.ip_address;
  } catch(e){}

  const payload = {
    "device_id": devId,
    "destination_ip": ip,
    "source_ip": "External",
    "Protocol Type": proto,
    "Rate": rate,
    "Tot size": size,
    // Add default values for ML model
    "flow_duration": 1.0, "Header_Length": 60, "Duration": 0.5,
    "Srate": rate, "Drate": 0, "fin_flag_number": 0, "syn_flag_number": 1,
    "rst_flag_number": 0, "psh_flag_number": 0, "ack_flag_number": 0,
    "ece_flag_number": 0, "cwr_flag_number": 0, "ack_count": 0,
    "syn_count": 1, "fin_count": 0, "urg_count": 0, "rst_count": 0,
    "HTTP": 0, "HTTPS": 0, "DNS": proto===17?1:0, "Telnet": 0, "SMTP": 0, "SSH": 0, "IRC": 0, 
    "TCP": proto===6?1:0, "UDP": proto===17?1:0, "DHCP": 0, "ARP": 0, "ICMP": proto===1?1:0, 
    "IPv": 1, "LLC": 1, "Tot sum": size, "Min": size, "Max": size, "AVG": size, "Std": 0, 
    "IAT": 0.1, "Number": 1, "Magnitue": size, "Radius": 0, "Covariance": 0, "Variance": 0, "Weight": 1.0
  };

  try {
    const res = await fetch(API + '/predict', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    showToast(`Injected! Prediction: ${result.prediction}`, result.risk_level === 'HIGH' ? 'red' : 'green');
  } catch(e) {
    showToast('Failed to inject packet', 'red');
  }
};

async function ctrlSim(action) {
  const speed = parseFloat(document.getElementById('speedSel')?.value||1);
  try {
    await fetch(`${API}/simulation/${action}`, {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ speed })
    });
    if (action === 'start') showToast('Simulation started ▶', 'green');
    else                    showToast('Simulation stopped ■', 'red');
    updateSimStatus();
  } catch(e){ showToast('Server not reachable', 'red'); }
}

async function updateSimStatus() {
  try {
    const s    = await (await fetch(API + '/simulation/status')).json();
    const line = document.getElementById('simStatusLine');
    const text = document.getElementById('simStatusText');
    const spin = document.getElementById('simSpinner');
    if (!line) return;
    if (s.is_running) {
      line.classList.add('running');
      if(text) text.textContent = `RUNNING — Record ${s.current_index} / ${s.total_records}`;
      if(spin) spin.style.display = 'inline-block';
    } else {
      line.classList.remove('running');
      if(text) text.textContent = 'Idle';
      if(spin) spin.style.display = 'none';
    }
  } catch(e){}
}

/* ── INIT ── */
window.onload = () => showPage('dashboard', document.querySelector('.nav-btn'));
