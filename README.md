# RCNN vs YOLO - Plataforma de Detección de Objetos

Una plataforma web completa para la comparación de modelos de detección de objetos **RCNN (Faster R-CNN)** y **YOLO (YOLOv8)**, con soporte para imágenes, videos y análisis de rendimiento en tiempo real.

## 📋 Descripción General

Este proyecto implementa una aplicación web local que permite:

- **Detección en imágenes**: Carga imágenes y detecta objetos usando RCNN o YOLO
- **Detección en videos**: Procesa videos completos con detección frame-by-frame
- **Comparación de modelos**: Compara métricas de rendimiento entre ambos modelos
- **Análisis de métricas**: Calcula precisión, recall, mAP, tiempo de inferencia, FPS
- **Dashboard de resultados**: Visualiza resultados con gráficos y tablas comparativas
- **Historial de detecciones**: Almacena y recupera resultados anteriores

## 🚀 Características

### 1. Detección con RCNN
- Modelo: Faster R-CNN con ResNet-50 backbone
- Soporte para imágenes y videos
- Métricas: Tiempo de inferencia, número de detecciones, uso de CPU/GPU
- Bounding boxes con etiquetas y confianza

### 2. Detección con YOLO
- Modelo: YOLOv8 Nano (optimizado para velocidad)
- Procesamiento ultrarrápido de imágenes y videos
- FPS en tiempo real
- Visualización de detecciones con colores distintivos

### 3. Análisis Comparativo
- Gráficos comparativos de velocidad y memoria
- Tablas de rendimiento lado a lado
- Análisis automático de ventajas/desventajas
- Recomendaciones de casos de uso

### 4. Base de Datos
- SQLite para almacenamiento de resultados
- Historial completo de detecciones
- Comparaciones guardadas
- Métricas de sistema

## 📦 Tecnologías

- **Backend**: FastAPI, Python 3.11+
- **ML/CV**: PyTorch, Torchvision, Ultralytics YOLO, OpenCV
- **Base de Datos**: SQLite, SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Visualización**: Chart.js
- **Servidor**: Uvicorn

## 📋 Requisitos Previos

- Python 3.11 o superior
- pip (administrador de paquetes Python)
- Opcional: CUDA 11.8+ y cuDNN 8.6+ para aceleración GPU

## 🔧 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd rcnn_vs_yolo
```

### 2. Crear un entorno virtual

```bash
python -m venv venv
```

Activar el entorno virtual:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Nota**: La instalación puede tardar varios minutos, especialmente si se descargan los modelos de PyTorch.

### 4. Configurar variables de entorno (opcional)

Crear un archivo `.env` en la raíz del proyecto:

```env
DEBUG=True
DEVICE=cuda
RCNN_CONFIDENCE_THRESHOLD=0.5
YOLO_CONFIDENCE_THRESHOLD=0.5
```

## 🎯 Ejecución

### Iniciar el servidor

```bash
cd app/backend
python main.py
```

O usando uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Acceder a la aplicación

1. Abrir un navegador web
2. Ir a `http://localhost:8000`
3. La interfaz web cargará automáticamente

### URLs principales

- **Inicio**: http://localhost:8000/
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Alternative (ReDoc)**: http://localhost:8000/redoc

## 📚 Estructura del Proyecto

```
rcnn_vs_yolo/
├── app/
│   ├── backend/
│   │   ├── main.py                 # Aplicación FastAPI principal
│   │   ├── config.py               # Configuración de la app
│   │   ├── database/
│   │   │   ├── models.py           # Modelos SQLAlchemy
│   │   │   └── db.py               # Configuración de BD
│   │   ├── detection/
│   │   │   ├── rcnn_detector.py    # Implementación RCNN
│   │   │   └── yolo_detector.py    # Implementación YOLO
│   │   ├── metrics/
│   │   │   └── calculator.py       # Cálculo de métricas
│   │   └── utils/
│   │       └── file_handler.py     # Manejo de archivos
│   └── frontend/
│       ├── templates/
│       │   └── index.html          # Página principal
│       └── static/
│           ├── css/
│           │   └── styles.css      # Estilos CSS
│           └── js/
│               └── main.js         # JavaScript frontend
├── uploads/
│   ├── images/                     # Imágenes subidas
│   ├── videos/                     # Videos subidos
│   └── results/                    # Imágenes/videos de resultados
├── docs/                           # Documentación
├── requirements.txt                # Dependencias Python
└── README.md                       # Este archivo
```

## 🔌 API Endpoints

### Detección en Imágenes

**RCNN:**
```
POST /api/v1/detect/image/rcnn
Content-Type: multipart/form-data
Body: file (imagen)
```

**YOLO:**
```
POST /api/v1/detect/image/yolo
Content-Type: multipart/form-data
Body: file (imagen)
```

### Detección en Videos

**RCNN:**
```
POST /api/v1/detect/video/rcnn
Content-Type: multipart/form-data
Body: file (video)
```

**YOLO:**
```
POST /api/v1/detect/video/yolo
Content-Type: multipart/form-data
Body: file (video)
```

### Resultados

```
GET /api/v1/results/{result_id}           # Detalles del resultado
GET /api/v1/results/image/{result_id}     # Descargar imagen resultado
GET /api/v1/results/video/{result_id}     # Descargar video resultado
```

### Comparación

```
POST /api/v1/compare?rcnn_result_id=X&yolo_result_id=Y
GET /api/v1/history                        # Historial de detecciones
GET /api/v1/statistics                     # Estadísticas globales
GET /api/v1/health                         # Estado del sistema
```

## 📊 Métricas Calculadas

### Por Detección
- **Tiempo de Inferencia (ms)**: Tiempo total de procesamiento
- **Número de Detecciones**: Objetos encontrados
- **Confianza Promedio**: Score de confianza medio
- **Uso de CPU (%)**: Consumo de CPU durante procesamiento
- **Uso de Memoria (MB)**: RAM utilizada
- **Uso de GPU (%)**: Consumo de GPU (si disponible)

### Para Videos
- **FPS (Frames Per Second)**: Fotogramas procesados por segundo
- **Detecciones por Frame**: Promedio de objetos por fotograma
- **Tiempo Total de Procesamiento**: Duración total del análisis

### Comparativas
- **Ventaja de Velocidad**: Porcentaje de diferencia en tiempo
- **Diferencia en Detecciones**: Variación en número de objetos detectados
- **Eficiencia de Memoria**: Consumo de memoria relativo

## 🖼️ Interfaz de Usuario

### Secciones Principales

1. **Inicio**: Bienvenida y estadísticas generales
2. **Detección RCNN-Imágenes**: Carga y procesamiento con RCNN
3. **Detección YOLO-Imágenes**: Carga y procesamiento con YOLO
4. **Detección RCNN-Videos**: Procesamiento de videos con RCNN
5. **Detección YOLO-Videos**: Procesamiento de videos con YOLO
6. **Comparación**: Análisis lado a lado y gráficos comparativos
7. **Historial**: Tabla de resultados anteriores
8. **Análisis**: Conclusiones y recomendaciones automáticas

## ⚙️ Configuración Avanzada

### Cambiar Modelo YOLO

En `config.py`, modificar:

```python
YOLO_MODEL_PATH: str = "yolov8n.pt"  # nano, small, medium, large, xlarge
```

Opciones disponibles:
- `yolov8n.pt` - Nano (más rápido)
- `yolov8s.pt` - Small
- `yolov8m.pt` - Medium
- `yolov8l.pt` - Large
- `yolov8x.pt` - Extra Large (más preciso)

### Ajustar Umbrales de Confianza

En `config.py`:

```python
RCNN_CONFIDENCE_THRESHOLD: float = 0.5
YOLO_CONFIDENCE_THRESHOLD: float = 0.5
```

### Usar GPU

Asegurarse de que CUDA está disponible:

```bash
python -c "import torch; print(torch.cuda.is_available())"
```

Si está disponible, la app usará automáticamente GPU.

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError: No module named 'torch'"

```bash
pip install --upgrade torch torchvision
```

### Error: "CUDA out of memory"

- Usar un modelo YOLO más pequeño (yolov8n)
- Reducir tamaño de imágenes
- Usar CPU en lugar de GPU (en config.py)

### Error: "Port 8000 already in use"

```bash
uvicorn main:app --port 8001
```

### Videos no se procesan

Asegurarse de que OpenCV puede leer el formato:
- Soportados: MP4, AVI, MOV, FLV, MKV
- Convertir video si es necesario

## 📈 Resultados Típicos

### Tiempo de Inferencia (Imagen 640x480)

| Modelo | CPU | GPU |
|--------|-----|-----|
| RCNN | 800-1200ms | 100-200ms |
| YOLO | 50-100ms | 20-50ms |

### Precisión (COCO Dataset)

| Modelo | mAP50 | mAP95 |
|--------|-------|-------|
| Faster-RCNN | 0.58 | 0.36 |
| YOLOv8n | 0.54 | 0.32 |

**Nota**: Los valores reales dependen del hardware y los datos específicos.

## 📖 Documentación Técnica

Ver la carpeta `docs/` para:
- Marco teórico de RCNN y YOLO
- Arquitectura detallada de la aplicación
- Guía de entrenamiento con modelos personalizados
- Métricas de evaluación

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork del proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para detalles.

## 👨‍💼 Autor

**Tu Nombre**
- GitHub: [@username](https://github.com/username)
- Email: tu.email@example.com

## 🙏 Agradecimientos

- [Ultralytics](https://github.com/ultralytics/ultralytics) por YOLOv8
- [PyTorch](https://pytorch.org/) por los modelos de visión
- [FastAPI](https://fastapi.tiangolo.com/) por el framework web
- [Bootstrap](https://getbootstrap.com/) por el framework CSS

## 📞 Soporte

Para reportar problemas o sugerencias, abre un issue en:
https://github.com/username/rcnn_vs_yolo/issues

---

**Última actualización**: 2024
**Versión**: 1.0.0
