# Quick Reference Card - RCNN vs YOLO Platform

## 🚀 Quick Start (5 minutos)

```bash
# 1. Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 2. Run
cd app/backend
python main.py

# 3. Open
http://localhost:8000
```

## 📊 Performance Comparison

| Métrica | RCNN | YOLO | Ganador |
|---------|------|------|--------|
| Tiempo (ms) | 800-1200 | 50-100 | 🟨 YOLO |
| Precisión | 0.58 mAP | 0.54 mAP | 🟦 RCNN |
| FPS (Video) | 8 FPS | 40 FPS | 🟨 YOLO |
| Memoria | 2.8 GB | 0.8 GB | 🟨 YOLO |
| CPU Capable | ✗ | ✓ | 🟨 YOLO |

## 📁 Directorio Clave

```
rcnn_vs_yolo/
├── app/backend/           ← Backend FastAPI
├── app/frontend/          ← Interfaz web
├── docs/                  ← Documentación
├── uploads/               ← Datos/resultados
├── requirements.txt       ← Dependencias
└── README.md             ← Información general
```

## 🔌 API Endpoints Principales

```
POST /api/v1/detect/image/rcnn      ← Detectar imagen con RCNN
POST /api/v1/detect/image/yolo      ← Detectar imagen con YOLO
POST /api/v1/detect/video/rcnn      ← Procesar video con RCNN
POST /api/v1/detect/video/yolo      ← Procesar video con YOLO
POST /api/v1/compare                ← Comparar resultados
GET  /api/v1/history                ← Ver historial
GET  /api/v1/statistics             ← Ver estadísticas
```

## 🖥️ Interfaz Web

```
┌─ RCNN vs YOLO ─ [Inicio|Imágenes|Videos|Comparación|Historial]
│
├─ 📸 Imágenes
│  ├─ RCNN: Cargar → Procesar → Ver resultados
│  └─ YOLO: Cargar → Procesar → Ver resultados
│
├─ 🎬 Videos
│  ├─ RCNN: Cargar → Procesar → Descargar
│  └─ YOLO: Cargar → Procesar → Descargar
│
├─ ⚖️ Comparación
│  └─ Análisis lado a lado + Gráficos
│
├─ 📋 Historial
│  └─ Tabla filtrable de resultados
│
└─ 📊 Análisis
   └─ Conclusiones automáticas
```

## 📦 Dependencias Clave

```python
fastapi==0.104.1          # Framework web
torch==2.1.0              # Deep learning
torchvision==0.16.0       # Modelos vision
ultralytics==8.0          # YOLO
opencv-python==4.8.1      # Procesamiento de imágenes
sqlalchemy==2.0           # ORM base de datos
```

## 🎯 Casos de Uso

**Usa RCNN si:**
- ✓ Necesitas máxima precisión
- ✓ Tiempo no es restricción
- ✓ Tienes GPU disponible
- ✓ Objetos pequeños o superpuestos

**Usa YOLO si:**
- ✓ Necesitas tiempo real
- ✓ Hardware limitado
- ✓ Procesamiento en CPU
- ✓ Objetos grandes/medianos

## 🔧 Configuración

Editar `app/backend/config.py`:

```python
DEVICE = "cuda"  # 'cpu' o 'cuda'
YOLO_MODEL_PATH = "yolov8n.pt"  # n/s/m/l/x
RCNN_CONFIDENCE_THRESHOLD = 0.5
```

## ⚠️ Requisitos Mínimos

- Python 3.11+
- 8 GB RAM
- 5 GB espacio en disco
- (Opcional) GPU NVIDIA 12 GB

## 🐛 Troubleshooting

```bash
# Error: ModuleNotFoundError torch
pip install torch torchvision

# Error: Port 8000 en uso
uvicorn main:app --port 8001

# Error: CUDA out of memory
# Cambiar en config.py: YOLO_MODEL_PATH = "yolov8n.pt"
```

## 📖 Documentación

| Documento | Contenido |
|-----------|----------|
| README.md | Visión general |
| TECHNICAL_DOCUMENT.md | Marco teórico + Benchmarks |
| INSTALLATION_GUIDE.md | Instalación paso a paso |
| USER_GUIDE.md | Manual de usuario |
| PROJECT_SUMMARY.md | Resumen completo |

## 🎓 Conceptos Clave

**RCNN (Region-based)**
- Analiza regiones del imagen
- Mayor precisión
- Más lento

**YOLO (Single-shot)**
- Analiza imagen completa
- Más rápido
- Tiempo real

## ✨ Características

✅ Detección en imágenes (JPG, PNG, BMP, GIF)
✅ Detección en videos (MP4, AVI, MOV, MKV)
✅ Comparación automática de modelos
✅ Dashboard con gráficos
✅ Historial almacenado
✅ API REST completa
✅ Interfaz responsive
✅ Métricas de rendimiento
✅ Análisis automático

## 🔗 URLs Importantes

```
http://localhost:8000              ← Interfaz web
http://localhost:8000/docs         ← Swagger UI (API)
http://localhost:8000/redoc        ← ReDoc (API)
http://localhost:8000/api/v1/health ← Health check
```

## 📝 Pasos para Usar

1. **Instalar**: `pip install -r requirements.txt`
2. **Ejecutar**: `python main.py`
3. **Abrir**: http://localhost:8000
4. **Cargar**: Seleccionar imagen o video
5. **Procesar**: Hacer clic en detectar
6. **Comparar**: Procesar con ambos modelos
7. **Analizar**: Ver resultados y conclusiones

## 🎬 Flujo de Trabajo Típico

```
Usuario carga imagen
    ↓
Selecciona RCNN o YOLO
    ↓
Sistema procesa
    ↓
Se muestra resultado con bounding boxes
    ↓
Se guardan métricas en BD
    ↓
Usuario carga misma imagen con otro modelo
    ↓
Sistema automáticamente compara
    ↓
Se muestran gráficos y análisis
```

## 💡 Pro Tips

- Imágenes 640x480-1280x720: Óptimas velocidad/precisión
- YOLO funciona bien en CPU para demostración
- GPU GPU acelera RCNN 10x más que YOLO
- Videos <10 minutos para mejor rendimiento
- Usar formato MP4 para videos

## 📞 Contacto

- Documentación: `/docs`
- Issues: GitHub Issues
- FAQ: Ver USER_GUIDE.md

---

**v1.0 | 2024 | Versión Completa Funcional**
