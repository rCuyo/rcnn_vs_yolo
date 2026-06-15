// API base URL
const API_URL = '/api/v1';

// Store results IDs for comparison
let rcnnImageResultId = null;
let yoloImageResultId = null;
let comparisonCharts = {};

// ==================== INITIALIZATION ====================

document.addEventListener('DOMContentLoaded', function() {
    initializeUploadAreas();
    loadStatistics();
    loadHistory();
    setInterval(loadStatistics, 30000);
});

// ==================== UPLOAD AREA INITIALIZATION ====================

function initializeUploadAreas() {
    const uploadAreas = ['rcnn-image', 'yolo-image'];
    
    uploadAreas.forEach(prefix => {
        const uploadArea = document.getElementById(`${prefix}-upload`);
        const fileInput = document.getElementById(`${prefix}-input`);
        
        if (!uploadArea || !fileInput) return;
        
        // Click to upload
        uploadArea.addEventListener('click', () => fileInput.click());
        
        // File input change
        fileInput.addEventListener('change', (e) => {
            handleFileSelect(e, prefix);
        });
        
        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#667eea';
            uploadArea.style.backgroundColor = '#f0f0ff';
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.style.borderColor = '#ddd';
            uploadArea.style.backgroundColor = 'transparent';
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.style.borderColor = '#ddd';
            uploadArea.style.backgroundColor = 'transparent';
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                fileInput.files = files;
                handleFileSelect({target: {files: files}}, prefix);
            }
        });
    });
}

// ==================== FILE HANDLING ====================

function handleFileSelect(event, prefix) {
    const files = event.target.files;
    if (files.length === 0) return;
    
    const file = files[0];
    
    // Validate file type
    if (!file.type.startsWith('image/')) {
        showError(`${prefix}: Please select an image file`);
        return;
    }
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        const preview = document.getElementById(`${prefix}-preview`);
        const previewImg = document.getElementById(`${prefix}-preview-img`);
        
        previewImg.src = e.target.result;
        preview.style.display = 'block';
        
        // Upload file
        uploadFile(file, prefix);
    };
    reader.readAsDataURL(file);
}

function uploadFile(file, prefix) {
    const [model, type] = prefix.split('-');
    const endpoint = `${API_URL}/detect/${type}/${model}`;
    
    const formData = new FormData();
    formData.append('file', file);
    
    // Show loading
    const loading = document.getElementById(`${prefix}-loading`);
    const results = document.getElementById(`${prefix}-results`);
    loading.style.display = 'block';
    results.style.display = 'none';
    
    fetch(endpoint, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        loading.style.display = 'none';
        
        if (data.result_id) {
            // Store result ID for comparison
            if (model === 'rcnn' && type === 'image') {
                rcnnImageResultId = data.result_id;
            } else if (model === 'yolo' && type === 'image') {
                yoloImageResultId = data.result_id;
            }
            
            displayResults(data, prefix);
            
            // Try to auto-compare
            if (rcnnImageResultId && yoloImageResultId && type === 'image') {
                compareResults(rcnnImageResultId, yoloImageResultId);
            }
        }
        
        loadStatistics();
    })
    .catch(error => {
        loading.style.display = 'none';
        showError(`${prefix}: ${error.message}`);
    });
}

// ==================== RESULTS DISPLAY ====================

function displayResults(data, prefix) {
    const results = document.getElementById(`${prefix}-results`);
    const resultImg = document.getElementById(`${prefix}-result`);
    const metrics = document.getElementById(`${prefix}-metrics`);
    const detections = document.getElementById(`${prefix}-detections`);
    
    // Display result image
    if (data.output_image) {
        resultImg.src = data.output_image;
    }
    
    // Display metrics
    const metricsHtml = `
        <li>
            <span class="metric-label">Detecciones:</span>
            <span class="metric-value">${data.detections_count}</span>
        </li>
        <li>
            <span class="metric-label">Tiempo de Inferencia:</span>
            <span class="metric-value">${(data.inference_time * 1000).toFixed(2)} ms</span>
        </li>
        <li>
            <span class="metric-label">CPU Usage:</span>
            <span class="metric-value">${data.system_metrics.cpu_percent.toFixed(1)}%</span>
        </li>
        <li>
            <span class="metric-label">Memory Usage:</span>
            <span class="metric-value">${data.system_metrics.memory_mb.toFixed(0)} MB</span>
        </li>
    `;
    
    if (data.system_metrics.gpu_available) {
        metricsHtml += `
            <li>
                <span class="metric-label">GPU Usage:</span>
                <span class="metric-value">${data.system_metrics.gpu_percent.toFixed(1)}%</span>
            </li>
        `;
    }
    
    metrics.innerHTML = metricsHtml;
    
    // Display detections
    let detectionsHtml = '';
    if (data.detections && data.detections.length > 0) {
        data.detections.forEach((det, idx) => {
            detectionsHtml += `
                <div class="detection-item">
                    <div class="detection-item-title">
                        ${det.class_name}
                        <span class="confidence-badge">${(det.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div class="detection-item-meta">
                        Position: (${Math.round(det.bbox.x1)}, ${Math.round(det.bbox.y1)}) - 
                        Size: ${Math.round(det.bbox.width)}x${Math.round(det.bbox.height)}
                    </div>
                </div>
            `;
        });
    } else {
        detectionsHtml = '<p class="text-muted">No detections found</p>';
    }
    
    detections.innerHTML = detectionsHtml;
    results.style.display = 'block';
}

// ==================== COMPARISON ====================

function compareResults(rcnnId, yoloId) {
    fetch(`${API_URL}/compare?rcnn_result_id=${rcnnId}&yolo_result_id=${yoloId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        displayComparison(data);
        generateAnalysis(data);
    })
    .catch(error => {
        console.error('Comparison error:', error);
    });
}

function displayComparison(data) {
    const rcnnStats = document.getElementById('rcnn-comparison-stats');
    const yoloStats = document.getElementById('yolo-comparison-stats');
    
    const rcnnHtml = `
        <div class="comparison-stat">
            <p><strong>Tiempo de Inferencia:</strong> ${(data.rcnn.inference_time * 1000).toFixed(2)} ms</p>
            <p><strong>Detecciones:</strong> ${data.rcnn.detections}</p>
            <p><strong>Memoria:</strong> ${data.rcnn.memory_mb ? data.rcnn.memory_mb.toFixed(0) + ' MB' : 'N/A'}</p>
        </div>
    `;
    
    const yoloHtml = `
        <div class="comparison-stat">
            <p><strong>Tiempo de Inferencia:</strong> ${(data.yolo.inference_time * 1000).toFixed(2)} ms</p>
            <p><strong>Detecciones:</strong> ${data.yolo.detections}</p>
            <p><strong>Memoria:</strong> ${data.yolo.memory_mb ? data.yolo.memory_mb.toFixed(0) + ' MB' : 'N/A'}</p>
        </div>
    `;
    
    rcnnStats.innerHTML = rcnnHtml;
    yoloStats.innerHTML = yoloHtml;
    
    // Create comparison charts
    createComparisonCharts(data);
}

function createComparisonCharts(data) {
    // Inference Time Chart
    const inferenceTimeCtx = document.getElementById('inferenceTimeChart')?.getContext('2d');
    if (inferenceTimeCtx && !comparisonCharts.inferenceTime) {
        comparisonCharts.inferenceTime = new Chart(inferenceTimeCtx, {
            type: 'bar',
            data: {
                labels: ['RCNN', 'YOLO'],
                datasets: [{
                    label: 'Tiempo de Inferencia (ms)',
                    data: [
                        data.rcnn.inference_time * 1000,
                        data.yolo.inference_time * 1000
                    ],
                    backgroundColor: ['#667eea', '#ffc107'],
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Memory Chart
    const memoryCtx = document.getElementById('memoryChart')?.getContext('2d');
    if (memoryCtx && !comparisonCharts.memory) {
        comparisonCharts.memory = new Chart(memoryCtx, {
            type: 'bar',
            data: {
                labels: ['RCNN', 'YOLO'],
                datasets: [{
                    label: 'Uso de Memoria (MB)',
                    data: [
                        data.rcnn.memory_mb || 0,
                        data.yolo.memory_mb || 0
                    ],
                    backgroundColor: ['#667eea', '#ffc107'],
                    borderRadius: 5
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// ==================== ANALYSIS ====================

function generateAnalysis(data) {
    const analysisContent = document.getElementById('analysis-content');
    
    const fasterModel = data.comparison.faster_model.toUpperCase();
    const speedAdvantage = data.comparison.speed_advantage_percent.toFixed(1);
    const rcnnDetections = data.rcnn.detections;
    const yoloDetections = data.yolo.detections;
    
    let detectionAnalysis = '';
    if (rcnnDetections > yoloDetections) {
        detectionAnalysis = `RCNN detectó ${rcnnDetections - yoloDetections} objetos más que YOLO.`;
    } else if (yoloDetections > rcnnDetections) {
        detectionAnalysis = `YOLO detectó ${yoloDetections - rcnnDetections} objetos más que RCNN.`;
    } else {
        detectionAnalysis = `Ambos modelos detectaron la misma cantidad de objetos.`;
    }
    
    const analysis = `
        <div class="analysis-section mb-4">
            <h5>Resumen Comparativo</h5>
            <p>
                <strong>${fasterModel}</strong> fue <strong>${speedAdvantage}%</strong> más rápido en esta prueba.
                ${detectionAnalysis}
            </p>
        </div>
        
        <div class="analysis-section mb-4">
            <h5>Velocidad de Procesamiento</h5>
            <p>
                RCNN: ${(data.rcnn.inference_time * 1000).toFixed(2)} ms<br>
                YOLO: ${(data.yolo.inference_time * 1000).toFixed(2)} ms
            </p>
            <p class="text-muted">
                ${data.comparison.faster_model === 'yolo' 
                    ? 'YOLO es significativamente más rápido, ideal para aplicaciones en tiempo real.'
                    : 'RCNN ofrece mayor precisión a cambio de más tiempo de procesamiento.'}
            </p>
        </div>
        
        <div class="analysis-section">
            <h5>Consumo de Recursos</h5>
            <p>
                RCNN Memory: ${data.rcnn.memory_mb ? data.rcnn.memory_mb.toFixed(0) + ' MB' : 'N/A'}<br>
                YOLO Memory: ${data.yolo.memory_mb ? data.yolo.memory_mb.toFixed(0) + ' MB' : 'N/A'}
            </p>
        </div>
    `;
    
    analysisContent.innerHTML = analysis;
}

// ==================== HISTORY ====================

async function loadHistory() {
    const modelFilter = document.getElementById('history-filter-model')?.value || '';
    const typeFilter = document.getElementById('history-filter-type')?.value || '';
    
    let url = `${API_URL}/history?skip=0&limit=50`;
    if (modelFilter) url += `&model_type=${modelFilter}`;
    if (typeFilter) url += `&file_type=${typeFilter}`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        const tbody = document.getElementById('history-table-body');
        if (!tbody) return;
        
        if (data.results.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted">No results found</td></tr>';
            return;
        }
        
        let html = '';
        data.results.forEach(result => {
            html += `
                <tr>
                    <td><small>${result.filename}</small></td>
                    <td><span class="badge ${result.model_type === 'rcnn' ? 'bg-primary' : 'bg-warning'}">${result.model_type.toUpperCase()}</span></td>
                    <td><span class="badge bg-secondary">${result.file_type}</span></td>
                    <td>${result.detections_count}</td>
                    <td>${(result.inference_time * 1000).toFixed(2)}</td>
                    <td><small>${new Date(result.created_at).toLocaleString()}</small></td>
                    <td>
                        <button class="btn btn-sm btn-outline-primary" onclick="viewResult(${result.id})">
                            <i class="bi bi-eye"></i>
                        </button>
                    </td>
                </tr>
            `;
        });
        
        tbody.innerHTML = html;
    } catch (error) {
        console.error('History load error:', error);
    }
}

// ==================== STATISTICS ====================

async function loadStatistics() {
    try {
        const response = await fetch(`${API_URL}/statistics`);
        const data = await response.json();
        
        document.getElementById('stat-detections').textContent = data.total_detections;
        document.getElementById('stat-comparisons').textContent = data.comparisons;
    } catch (error) {
        console.error('Statistics load error:', error);
    }
}

// ==================== CAMERA / WEBSOCKET ====================

let cameraStream = null;
let cameraWS = null;
let cameraActive = false;
let cameraAnimId = null;
let waitingWSResponse = false;
let latestDetections = [];
let latestModel = null;
let camFrameCount = 0;
let camFpsTimer = Date.now();
let compareStats = { rcnn: { totalTime: 0, count: 0, totalObjects: 0 }, yolo: { totalTime: 0, count: 0, totalObjects: 0 } };

const captureCanvas = document.createElement('canvas');
captureCanvas.width = 640;
captureCanvas.height = 480;
const captureCtx = captureCanvas.getContext('2d');

function startCamera() {
    const model = document.getElementById('camera-model-select').value;
    const videoEl = document.getElementById('camera-video');
    const displayCanvas = document.getElementById('camera-canvas');
    const displayCtx = displayCanvas.getContext('2d');
    const placeholder = document.getElementById('camera-placeholder');
    const errorEl = document.getElementById('camera-error');
    const startBtn = document.getElementById('camera-start-btn');

    errorEl.style.display = 'none';

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showCameraError('Tu navegador no soporta acceso a cámara. Usa Chrome o Firefox en localhost.');
        return;
    }

    // Feedback inmediato en el botón
    startBtn.disabled = true;
    startBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Conectando...';

    navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } })
        .then(stream => {
            cameraStream = stream;
            videoEl.srcObject = stream;
            videoEl.play();

            const wsProtocol = location.protocol === 'https:' ? 'wss' : 'ws';
            const wsPath = model === 'compare' ? '/api/v1/ws/camera/compare' : `/api/v1/ws/camera/${model}`;
            cameraWS = new WebSocket(`${wsProtocol}://${location.host}${wsPath}`);
            cameraWS.binaryType = 'arraybuffer';

            cameraWS.onopen = () => {
                cameraActive = true;
                waitingWSResponse = false;
                latestDetections = [];
                latestModel = null;
                compareStats = { rcnn: { totalTime: 0, count: 0, totalObjects: 0 }, yolo: { totalTime: 0, count: 0, totalObjects: 0 } };
                placeholder.style.display = 'none';
                document.getElementById('camera-stats').style.display = 'block';
                if (model === 'compare') {
                    document.getElementById('single-model-stats').style.display = 'none';
                    document.getElementById('compare-model-stats').style.display = 'block';
                } else {
                    document.getElementById('single-model-stats').style.display = 'block';
                    document.getElementById('compare-model-stats').style.display = 'none';
                }
                startBtn.innerHTML = '<i class="bi bi-play-fill"></i> Iniciar Cámara';
                document.getElementById('camera-stop-btn').disabled = false;
                document.getElementById('camera-model-select').disabled = true;
                camFpsTimer = Date.now();
                camFrameCount = 0;
                cameraLoop(videoEl, displayCanvas, displayCtx);
            };

            cameraWS.onmessage = (event) => {
                const data = JSON.parse(event.data);
                latestDetections = data.detections || [];
                waitingWSResponse = false;
                if (data.model) {
                    latestModel = data.model;
                    compareStats[data.model].totalTime += data.inference_time;
                    compareStats[data.model].count++;
                    compareStats[data.model].totalObjects += data.count;
                    updateCompareStats();
                } else {
                    document.getElementById('camera-time').textContent = (data.inference_time * 1000).toFixed(0) + ' ms';
                    document.getElementById('camera-count').textContent = data.count;
                }
                updateLiveDetections(latestDetections);
            };

            cameraWS.onerror = (e) => showCameraError('No se pudo conectar al servidor de detección (WebSocket).');
            cameraWS.onclose = (e) => {
                if (cameraActive) showCameraError(`Conexión cerrada inesperadamente (código ${e.code}).`);
            };
        })
        .catch(err => {
            startBtn.disabled = false;
            startBtn.innerHTML = '<i class="bi bi-play-fill"></i> Iniciar Cámara';
            showCameraError('No se pudo acceder a la cámara: ' + err.message);
        });
}

function cameraLoop(videoEl, canvas, ctx) {
    if (!cameraActive) return;

    if (videoEl.readyState >= 2) {
        ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);
        drawCameraDetections(ctx, latestDetections, canvas.width / 640, canvas.height / 480);

        camFrameCount++;
        const elapsed = (Date.now() - camFpsTimer) / 1000;
        if (elapsed >= 1) {
            document.getElementById('camera-fps').textContent = (camFrameCount / elapsed).toFixed(1);
            camFrameCount = 0;
            camFpsTimer = Date.now();
        }

        if (!waitingWSResponse && cameraWS?.readyState === WebSocket.OPEN) {
            captureCtx.drawImage(videoEl, 0, 0, 640, 480);
            captureCanvas.toBlob(blob => {
                if (blob && cameraWS?.readyState === WebSocket.OPEN) {
                    waitingWSResponse = true;
                    blob.arrayBuffer().then(buf => cameraWS.send(buf));
                }
            }, 'image/jpeg', 0.7);
        }
    }

    cameraAnimId = requestAnimationFrame(() => cameraLoop(videoEl, canvas, ctx));
}

function drawCameraDetections(ctx, detections, scaleX, scaleY, offsetX = 0, offsetY = 0) {
    const color = latestModel === 'rcnn' ? '#4d7cf4' : '#00ff41';
    detections.forEach(det => {
        const { x1, y1, x2, y2 } = det.bbox;
        const sx = x1 * scaleX + offsetX, sy = y1 * scaleY + offsetY;
        const sw = (x2 - x1) * scaleX, sh = (y2 - y1) * scaleY;
        const label = `${det.class_name} ${(det.confidence * 100).toFixed(0)}%`;

        ctx.strokeStyle = color;
        ctx.lineWidth = 2;
        ctx.strokeRect(sx, sy, sw, sh);

        const textW = ctx.measureText(label).width + 8;
        ctx.fillStyle = color;
        ctx.fillRect(sx, sy - 20, textW, 20);
        ctx.fillStyle = '#000';
        ctx.font = 'bold 12px monospace';
        ctx.fillText(label, sx + 4, sy - 5);
    });
}

function updateCompareStats() {
    const r = compareStats.rcnn;
    const y = compareStats.yolo;

    if (r.count > 0) {
        document.getElementById('cmp-rcnn-time').textContent = (r.totalTime / r.count * 1000).toFixed(0) + ' ms';
        document.getElementById('cmp-rcnn-count').textContent = (r.totalObjects / r.count).toFixed(1);
    }
    if (y.count > 0) {
        document.getElementById('cmp-yolo-time').textContent = (y.totalTime / y.count * 1000).toFixed(0) + ' ms';
        document.getElementById('cmp-yolo-count').textContent = (y.totalObjects / y.count).toFixed(1);
    }

    document.getElementById('cmp-active-model').textContent = `Ahora: ${latestModel.toUpperCase()}`;

    if (r.count > 0 && y.count > 0) {
        const rAvg = r.totalTime / r.count;
        const yAvg = y.totalTime / y.count;
        if (yAvg < rAvg) {
            const pct = ((rAvg - yAvg) / rAvg * 100).toFixed(0);
            document.getElementById('cmp-advantage').textContent = `YOLO es ${pct}% más rápido`;
        } else {
            const pct = ((yAvg - rAvg) / yAvg * 100).toFixed(0);
            document.getElementById('cmp-advantage').textContent = `RCNN es ${pct}% más rápido`;
        }
    }
}

function updateLiveDetections(detections) {
    const el = document.getElementById('camera-detections-live');
    if (detections.length === 0) { el.innerHTML = ''; return; }
    const counts = {};
    detections.forEach(d => { counts[d.class_name] = (counts[d.class_name] || 0) + 1; });
    el.innerHTML = Object.entries(counts)
        .map(([name, n]) => `<span class="badge bg-success me-1 mb-1">${name}${n > 1 ? ' ×' + n : ''}</span>`)
        .join('');
}

function stopCamera() {
    cameraActive = false;
    if (cameraAnimId) cancelAnimationFrame(cameraAnimId);
    if (cameraWS) { try { cameraWS.close(); } catch (_) {} }
    if (cameraStream) cameraStream.getTracks().forEach(t => t.stop());
    latestDetections = [];
    latestModel = null;
    cameraWS = null;
    cameraStream = null;

    const ctx = document.getElementById('camera-canvas').getContext('2d');
    ctx.clearRect(0, 0, 640, 480);
    document.getElementById('camera-placeholder').style.display = 'flex';
    document.getElementById('camera-stats').style.display = 'none';
    const startBtn = document.getElementById('camera-start-btn');
    startBtn.disabled = false;
    startBtn.innerHTML = '<i class="bi bi-play-fill"></i> Iniciar Cámara';
    document.getElementById('camera-stop-btn').disabled = true;
    document.getElementById('camera-model-select').disabled = false;
}

function showCameraError(msg) {
    const el = document.getElementById('camera-error');
    el.textContent = msg;
    el.style.display = 'block';
    stopCamera();
}

// ==================== UTILITIES ====================

function viewResult(resultId) {
    fetch(`${API_URL}/results/${resultId}`)
        .then(r => r.json())
        .then(data => {
            alert(`Result Details\nFile: ${data.filename}\nModel: ${data.model_type}\nDetections: ${data.detections_count}\nTime: ${(data.inference_time * 1000).toFixed(2)}ms`);
        });
}

function showError(message) {
    alert(`Error: ${message}`);
    console.error(message);
}

// Smooth scroll
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
