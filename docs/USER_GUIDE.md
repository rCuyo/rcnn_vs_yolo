# Guía de Uso - RCNN vs YOLO Plataforma de Detección

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Interfaz de Usuario](#interfaz-de-usuario)
3. [Detección en Imágenes](#detección-en-imágenes)
4. [Detección en Videos](#detección-en-videos)
5. [Comparación de Modelos](#comparación-de-modelos)
6. [Historial y Análisis](#historial-y-análisis)
7. [Consejos y Mejores Prácticas](#consejos-y-mejores-prácticas)

---

## Introducción

Esta plataforma te permite:
- Detectar objetos en imágenes usando RCNN o YOLO
- Procesar videos completos
- Comparar el rendimiento de ambos modelos
- Analizar métricas de velocidad y precisión
- Visualizar resultados con gráficos interactivos

---

## Interfaz de Usuario

### Navegación Principal

```
┌──────────────────────────────────────────┐
│  RCNN vs YOLO    [Inicio Imágenes Videos │
│                   Comparación Historial] │
└──────────────────────────────────────────┘
```

### Secciones

1. **Inicio**: Estadísticas generales y resumen
2. **Imágenes**: Carga y detección en imágenes
3. **Videos**: Procesamiento de videos
4. **Comparación**: Análisis lado a lado
5. **Historial**: Resultados anteriores

---

## Detección en Imágenes

### Paso 1: Seleccionar Modelo

Elige entre:
- **RCNN (Faster R-CNN)**: Más preciso, más lento
- **YOLO (YOLOv8)**: Más rápido, buena precisión

### Paso 2: Cargar Imagen

Dos opciones:

**A. Hacer clic en el área de carga**
- Se abrirá un selector de archivos
- Seleccionar imagen (JPG, PNG, BMP, etc.)

**B. Arrastrar y soltar**
- Arrastrar imagen al área de carga
- Soltar para procesar

### Paso 3: Esperar Procesamiento

Durante el procesamiento:
- Se muestra indicador de carga
- Tiempo estimado: RCNN 0.8-1.2s, YOLO 0.05-0.1s

### Paso 4: Revisar Resultados

Resultados mostrados:

```
┌─────────────────────────────────┐
│ MÉTRICAS                        │
├─────────────────────────────────┤
│ Detecciones: 5                  │
│ Tiempo: 150 ms                  │
│ CPU: 25%                        │
│ Memoria: 2048 MB                │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ DETECCIONES                     │
├─────────────────────────────────┤
│ ▸ Persona (0.95)                │
│ ▸ Coche (0.87)                  │
│ ▸ Teléfono (0.72)               │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│      [Imagen con BBox]          │
│  (Cajas verdes = Detecciones)   │
└─────────────────────────────────┘
```

### Elementos de Resultados

- **Imagen Anotada**: Imagen con bounding boxes
- **Bounding Box**: Caja roja o verde alrededor del objeto
- **Etiqueta**: Nombre del objeto + confianza
- **Métricas**: Tiempo, CPU, memoria usados

### Descargar Resultados

- Hacer clic derecho en imagen → "Guardar imagen como"
- O hacer clic en botón de descarga (si disponible)

---

## Detección en Videos

### Paso 1: Cargar Video

- Hacer clic en "Cargar Video"
- Seleccionar archivo (MP4, AVI, MOV, FLV, MKV)
- Máximo: 600 segundos (10 minutos)

### Paso 2: Seleccionar Modelo

- RCNN: Mayor precisión, procesamiento lento
- YOLO: Más rápido, FPS más alto

### Paso 3: Procesar

- El procesamiento puede tardar varios minutos
- Se muestra barra de progreso
- Tiempo estimado se actualiza en vivo

### Paso 4: Ver Resultados

```
Información del Video:
- Resolución: 1920x1080
- FPS Original: 30
- Duración: 2 minutos

Resultados:
- FPS de Procesamiento: 12 (RCNN) / 35 (YOLO)
- Tiempo Total: 120 seg
- Detecciones Totales: 450
- Detecciones/Frame: 3.75
```

### Descargar Video Procesado

- Hacer clic en el video → "Descargar"
- O hacer clic derecho → "Guardar video como"

### Tipos de Video Soportados

| Formato | Códec | Soporte |
|---------|-------|---------|
| MP4     | H.264 | ✓ Recomendado |
| AVI     | MPEG4 | ✓ |
| MOV     | MPEG4 | ✓ |
| MKV     | VP9   | ✓ |
| WebM    | VP8   | ✓ |

---

## Comparación de Modelos

### Paso 1: Procesar la Misma Imagen con Ambos Modelos

1. Ir a "RCNN - Imágenes"
2. Cargar imagen
3. Esperar resultados
4. Ir a "YOLO - Imágenes"
5. Cargar la misma imagen
6. Sistema automáticamente compara

### Paso 2: Ver Comparación

Se mostrarán automáticamente:

**Lado a lado:**
```
RCNN                    YOLO
────────────────────────────────
Tiempo: 150 ms          Tiempo: 50 ms
Detecciones: 5          Detecciones: 4
CPU: 35%                CPU: 28%
Memoria: 2.8 GB         Memoria: 0.8 GB
```

**Gráficos Comparativos:**
- Gráfico de barras: Tiempo de inferencia
- Gráfico de barras: Uso de memoria
- Tabla de detecciones

### Paso 3: Análisis Automático

El sistema genera conclusiones automáticas:

```
"YOLO fue 3x más rápido en esta prueba.
RCNN detectó 1 objeto más.
YOLO es recomendado para aplicaciones en tiempo real."
```

### Interpretar Resultados

**Ventajas RCNN:**
- ✓ Mejor precisión general
- ✓ Menos falsos positivos
- ✓ Mejor con objetos pequeños

**Ventajas YOLO:**
- ✓ 10-15x más rápido
- ✓ Tiempo real a 30+ FPS
- ✓ Menos uso de recursos
- ✓ Funciona bien en CPU

---

## Historial y Análisis

### Acceder al Historial

Navegar a sección "Historial" en el menú principal.

### Tabla de Resultados

Muestra:
- **Archivo**: Nombre de imagen/video
- **Modelo**: RCNN o YOLO
- **Tipo**: Imagen o Video
- **Detecciones**: Número total
- **Tiempo**: Tiempo de procesamiento
- **Fecha**: Cuándo se procesó

### Filtros Disponibles

```
┌─────────────────────────────────────────┐
│ Modelo: [Todos ▼]                       │
│ Tipo:   [Todos ▼]                       │
│ [Actualizar]                            │
└─────────────────────────────────────────┘
```

Opciones de filtro:
- Modelo: Todos, RCNN, YOLO
- Tipo: Todos, Imágenes, Videos

### Acciones

- **Ver detalles**: Botón "ojo"
- **Descargar**: Hacer clic en fila

### Análisis

Sección automática que incluye:
- Hallazgos principales
- Comparación de velocidad
- Consumo de recursos
- Recomendaciones

---

## Consejos y Mejores Prácticas

### Para Mejores Resultados

#### 1. Preparación de Imágenes

- **Resolución**: 640x480 a 1920x1080 (óptimo)
- **Formato**: JPG o PNG
- **Iluminación**: Bien iluminadas
- **Calidad**: Sin compresión excesiva

#### 2. Preparación de Videos

- **Resolución**: 720p a 1080p
- **Códec**: H.264 (MP4)
- **FPS**: 24-60
- **Tamaño**: < 100 MB
- **Duración**: 10 minutos máximo

#### 3. Selección de Modelo

**Usa RCNN si:**
- Necesitas máxima precisión
- Tienes tiempo para procesar
- Hardware potente disponible
- Presupuesto GPU no es problema

**Usa YOLO si:**
- Necesitas tiempo real
- Hardware limitado
- Quieres procesar en CPU
- Presupuesto energético importante

### Optimización

#### Aumentar Velocidad

1. Reducir tamaño de imagen
2. Usar YOLO en lugar de RCNN
3. Usar GPU si disponible
4. Procesar a menor resolución

#### Aumentar Precisión

1. Usar RCNN en lugar de YOLO
2. Usar imágenes de mejor calidad
3. Optimizar iluminación
4. Usar versión YOLO más grande (small/medium)

### Solución de Problemas Comunes

#### Imagen no se procesa

1. Verificar formato (JPG, PNG, BMP, GIF, WebP)
2. Verificar tamaño < 100 MB
3. Intentar imagen diferente
4. Recargar página

#### Resultados imprecisos

1. Verificar calidad de imagen
2. Verificar iluminación
3. Probar con otro modelo
4. Ajustar umbral de confianza

#### Aplicación lenta

1. Verificar disponibilidad de GPU
2. Reducir tamaño de imagen
3. Usar YOLO en lugar de RCNN
4. Cerrar otras aplicaciones

---

## Casos de Uso Recomendados

### Vigilancia en Tiempo Real
- **Modelo**: YOLO
- **Entrada**: Video en vivo
- **Ventaja**: 30+ FPS, CPU viable

### Análisis Médico/Forense
- **Modelo**: RCNN
- **Entrada**: Imágenes de alto valor
- **Ventaja**: Máxima precisión

### Conducción Autónoma
- **Modelo**: YOLO
- **Entrada**: Video en tiempo real
- **Ventaja**: Velocidad crítica, bajo latency

### Catalogación de Imágenes
- **Modelo**: RCNN
- **Entrada**: Batch de imágenes
- **Ventaja**: Precisión, sin restricción temporal

### Aplicaciones Embebidas (IoT)
- **Modelo**: YOLO Nano
- **Entrada**: Video de cámara
- **Ventaja**: Bajo consumo de recursos

---

## FAQ (Preguntas Frecuentes)

### ¿Cuál es la diferencia entre RCNN y YOLO?

RCNN es más preciso pero lento. YOLO es más rápido pero menos preciso. Elige según tus necesidades.

### ¿Necesito GPU?

No es obligatorio. YOLO funciona razonablemente en CPU. RCNN necesita GPU para buenos tiempos.

### ¿Qué tamaño de imagen es óptimo?

640x480 a 1280x720. Imágenes más grandes son más precisas pero más lentas.

### ¿Cuál es el video más largo que puedo procesar?

Máximo 600 segundos (10 minutos). Videos más grandes pueden causar errores de memoria.

### ¿Dónde se guardan los resultados?

En la carpeta `uploads/results/`. Puedes descargarlos desde la interfaz.

### ¿Es seguro cargar mis imágenes/videos?

Sí. El sistema está en localhost. Ningún dato se envía a servidores externos.

### ¿Puedo entrenar modelos personalizados?

En esta versión no, pero la arquitectura permite agregar esa funcionalidad.

### ¿Qué objetos puede detectar?

90 categorías de COCO dataset: personas, animales, vehículos, objetos domésticos, etc.

---

## Exportar y Compartir Resultados

### Exportar Resultados

```
1. Ir a Historial
2. Seleccionar resultado
3. Botón "Descargar"
4. Guardar archivo
```

### Compartir Análisis

1. Ir a sección de Comparación
2. Tomar screenshot
3. Compartir imagen

---

## Contacto y Soporte

Para problemas o sugerencias:
- GitHub Issues: https://github.com/username/rcnn_vs_yolo/issues
- Email: support@example.com
- Documentación: Ver carpeta `/docs`

---

**Guía de Usuario v1.0**
**Última actualización: 2024**
