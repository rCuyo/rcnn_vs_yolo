# Guía de Instalación y Configuración

## Tabla de Contenidos

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación Paso a Paso](#instalación-paso-a-paso)
3. [Configuración Inicial](#configuración-inicial)
4. [Ejecución](#ejecución)
5. [Verificación](#verificación)
6. [Troubleshooting](#troubleshooting)

---

## Requisitos del Sistema

### Software Obligatorio

- **Python 3.11+** (3.12 recomendado)
- **pip** (administrador de paquetes)
- **Git** (opcional, para clonar el repositorio)

### Hardware Recomendado

#### Mínimo:
- CPU: Intel i5 / AMD Ryzen 5 (4 núcleos)
- RAM: 8 GB
- Espacio en disco: 5 GB

#### Recomendado:
- CPU: Intel i7/i9 o AMD Ryzen 7/9 (8+ núcleos)
- RAM: 16-32 GB
- GPU: NVIDIA RTX 3060+ (12 GB VRAM)
- Espacio en disco: 20 GB

### GPU (Opcional pero Recomendado)

**Para NVIDIA GPU:**
- CUDA 11.8+ 
- cuDNN 8.6+
- Driver NVIDIA actualizado

**Verificar CUDA:**
```bash
nvidia-smi
```

**Verificar CUDA en Python:**
```bash
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name())"
```

---

## Instalación Paso a Paso

### Paso 1: Descargar el Proyecto

**Opción A: Con Git**
```bash
git clone https://github.com/username/rcnn_vs_yolo.git
cd rcnn_vs_yolo
```

**Opción B: Descargar ZIP**
1. Descargar ZIP desde GitHub
2. Extraer en carpeta deseada
3. Abrir terminal en la carpeta

### Paso 2: Crear Entorno Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Verificar activación:**
- Debe aparecer `(venv)` al inicio de la línea de comando

### Paso 3: Actualizar pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

### Paso 4: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Esto instalará:**
- FastAPI y Uvicorn
- PyTorch y TorchVision
- Ultralytics YOLO
- OpenCV
- SQLAlchemy
- Y más...

**Tiempo estimado:** 5-15 minutos (depende de internet)

### Paso 5: Descargar Modelos (Opcional)

Los modelos se descargan automáticamente en la primera ejecución. Si prefieres descargarlos manualmente:

```bash
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

---

## Configuración Inicial

### Crear Archivo .env (Opcional)

En la raíz del proyecto, crear `.env`:

```env
# Debug mode
DEBUG=True

# Device: 'cpu' o 'cuda'
DEVICE=cuda

# RCNN settings
RCNN_CONFIDENCE_THRESHOLD=0.5

# YOLO settings  
YOLO_MODEL_PATH=yolov8n.pt
YOLO_CONFIDENCE_THRESHOLD=0.5

# Upload limits
MAX_IMAGE_SIZE=1920
MAX_VIDEO_DURATION=600
MAX_UPLOAD_SIZE=104857600
```

### Crear Directorios (Si no Existen)

```bash
# Windows
mkdir uploads\images
mkdir uploads\videos
mkdir uploads\results

# macOS/Linux
mkdir -p uploads/images
mkdir -p uploads/videos
mkdir -p uploads/results
```

---

## Ejecución

### Opción 1: Comando Directo

```bash
cd app/backend
python main.py
```

### Opción 2: Con Uvicorn

```bash
cd app/backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Opción 3: En Puerto Diferente

```bash
uvicorn main:app --port 8001
```

### Esperado en la Consola:

```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Waiting for application startup.
Loading Faster R-CNN model on cuda...
✓ RCNN model loaded
Loading YOLO model (yolov8n.pt) on cuda...
✓ YOLO model loaded
INFO:     Application startup complete
```

### Acceder a la Aplicación

Abrir navegador web:

1. **Interfaz Web**: http://localhost:8000/
2. **API Swagger Docs**: http://localhost:8000/docs
3. **API ReDoc**: http://localhost:8000/redoc

---

## Verificación

### Verificar Instalación

```bash
# Verificar Python
python --version

# Verificar entorno virtual
where python  # Windows
which python  # macOS/Linux

# Verificar PyTorch
python -c "import torch; print(f'PyTorch: {torch.__version__}')"

# Verificar CUDA
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}')"

# Verificar Ultralytics
python -c "from ultralytics import YOLO; print('YOLO ready')"

# Verificar FastAPI
python -c "import fastapi; print(f'FastAPI: {fastapi.__version__}')"
```

### Test de Funcionalidad

1. Abrir http://localhost:8000/api/v1/health
2. Debe retornar:
```json
{
  "status": "healthy",
  "rcnn_available": true,
  "yolo_available": true
}
```

### Test de Detección

1. Ir a http://localhost:8000/
2. Subir una imagen de prueba
3. Esperar resultados

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'torch'"

**Solución:**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Error: "CUDA out of memory"

**Soluciones:**
1. Usar GPU más pequeña:
   ```python
   # En config.py, cambiar a:
   YOLO_MODEL_PATH = "yolov8n.pt"  # nano en vez de small
   ```

2. Usar CPU:
   ```env
   DEVICE=cpu
   ```

3. Reducir tamaño de imagen:
   ```python
   MAX_IMAGE_SIZE=1280
   ```

### Error: "Port 8000 already in use"

**Solución:**
```bash
# Usar puerto diferente
uvicorn main:app --port 8001

# O matar proceso en puerto 8000:
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

### Error: "No module named 'uvicorn'"

**Solución:**
```bash
pip install uvicorn
```

### No hay aceleración GPU

**Verificar:**
```bash
python -c "import torch; print(torch.cuda.is_available())"
```

**Si es False:**
1. Verificar driver NVIDIA: `nvidia-smi`
2. Reinstalar PyTorch con CUDA:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

### Videos no se procesan

**Verificar formato:**
```bash
# Soportados: MP4, AVI, MOV, FLV, MKV
# Convertir con ffmpeg:
ffmpeg -i input.avi -c:v libx264 -crf 23 output.mp4
```

### Errores de permisos en uploads/

**Solución Windows:**
```bash
icacls uploads /grant:r %username%:F /t
```

**Solución macOS/Linux:**
```bash
chmod -R 755 uploads/
```

### Imagen del resultado no se ve

**Verificar:**
1. Carpeta `uploads/results/` existe
2. Permisos de lectura/escritura
3. Espacio en disco disponible

### Frontend no carga

**Solución:**
1. Verificar que FastAPI está corriendo: http://localhost:8000/api/v1/health
2. Limpiar caché: Ctrl+Shift+R en navegador
3. Verificar archivos en `/app/frontend/static/`

---

## Configuración Avanzada

### Cambiar Modelos YOLO

En `app/backend/config.py`:

```python
# Opciones disponibles:
# yolov8n.pt - Nano (más rápido)
# yolov8s.pt - Small
# yolov8m.pt - Medium
# yolov8l.pt - Large
# yolov8x.pt - Extra Large (más preciso)

YOLO_MODEL_PATH = "yolov8n.pt"
```

### Usar CPU vs GPU

En `app/backend/config.py`:

```python
# Automático (recomendado):
DEVICE = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu"

# Forzar CPU:
DEVICE = "cpu"

# Forzar GPU específica:
os.environ["CUDA_VISIBLE_DEVICES"] = "0"  # GPU 0
DEVICE = "cuda"
```

### Aumentar Límites de Upload

En `app/backend/config.py`:

```python
MAX_IMAGE_SIZE = 2560  # píxeles
MAX_VIDEO_DURATION = 1200  # segundos (20 minutos)
MAX_UPLOAD_SIZE = 500 * 1024 * 1024  # 500 MB
```

### Base de Datos Remota

En `app/backend/config.py`:

```python
# SQLite (predeterminado)
DATABASE_URL = "sqlite:///./detection.db"

# PostgreSQL
DATABASE_URL = "postgresql://user:password@localhost/dbname"

# MySQL
DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
```

---

## Producción

### Instalación de Supervisor (Linux)

```bash
sudo apt install supervisor
```

Crear archivo `/etc/supervisor/conf.d/yolo-detection.conf`:

```ini
[program:yolo-detection]
directory=/home/user/rcnn_vs_yolo/app/backend
command=/home/user/rcnn_vs_yolo/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
autostart=true
autorestart=true
stderr_logfile=/var/log/yolo-detection.err.log
stdout_logfile=/var/log/yolo-detection.out.log
```

Iniciar:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start yolo-detection
```

### Usar Nginx como Reverse Proxy

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Desinstalación

### Desactivar Entorno Virtual

```bash
deactivate
```

### Eliminar Entorno Virtual

```bash
# Windows
rmdir /s venv

# macOS/Linux
rm -rf venv
```

### Limpiar Caché de Python

```bash
# Windows
for /d /r . %d in (__pycache__) do @if exist "%d" (echo "%d" && rmdir /s /q "%d")

# macOS/Linux
find . -type d -name __pycache__ -exec rm -rf {} +
```

---

## Soporte y Ayuda

Para problemas adicionales:

1. Ver logs: `uploads/logs/` (si existen)
2. Revisar GitHub Issues
3. Contactar al desarrollador

---

**Documento de Instalación v1.0**
**Última actualización: 2024**
