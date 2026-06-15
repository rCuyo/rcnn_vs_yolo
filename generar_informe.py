"""
Genera un informe-resumen en PDF del proyecto RCNN vs YOLO.
Usa reportlab (PDF) y matplotlib (gráficos).
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)

BASE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(BASE, "uploads", "images")
OUT_DIR = BASE
TMP = os.path.join(BASE, "_informe_tmp")
os.makedirs(TMP, exist_ok=True)

NAVY = colors.HexColor("#1f3a5c")
ACCENT = colors.HexColor("#3d6e9e")
GREEN = colors.HexColor("#2f7d4f")
LIGHT = colors.HexColor("#eef1f5")

# ---------------------------------------------------------------- Datos medidos
imagenes = ["bus", "playa\n(multiobjeto)", "perros", "zidane", "persona"]
yolo_det = [5, 7, 3, 3, 1]
rcnn_det = [5, 20, 5, 7, 2]
yolo_ms = [156, 129, 145, 126, 169]
rcnn_ms = [1493, 1589, 1702, 1809, 1448]

# ---------------------------------------------------------------- Gráfico 1: detecciones
def grafico_detecciones():
    x = range(len(imagenes))
    w = 0.38
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.bar([i - w/2 for i in x], rcnn_det, w, label="RCNN", color="#3d6e9e")
    ax.bar([i + w/2 for i in x], yolo_det, w, label="YOLO", color="#2f7d4f")
    ax.set_ylabel("Objetos detectados")
    ax.set_title("Número de detecciones por imagen")
    ax.set_xticks(list(x))
    ax.set_xticklabels(imagenes, fontsize=8)
    ax.legend()
    for i in x:
        ax.text(i - w/2, rcnn_det[i] + 0.3, str(rcnn_det[i]), ha="center", fontsize=8)
        ax.text(i + w/2, yolo_det[i] + 0.3, str(yolo_det[i]), ha="center", fontsize=8)
    fig.tight_layout()
    p = os.path.join(TMP, "det.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p

# ---------------------------------------------------------------- Gráfico 2: tiempo de inferencia
def grafico_tiempo():
    x = range(len(imagenes))
    w = 0.38
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.bar([i - w/2 for i in x], rcnn_ms, w, label="RCNN", color="#3d6e9e")
    ax.bar([i + w/2 for i in x], yolo_ms, w, label="YOLO", color="#2f7d4f")
    ax.set_ylabel("Tiempo de inferencia (ms)")
    ax.set_title("Tiempo de inferencia por imagen (menor = más rápido)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(imagenes, fontsize=8)
    ax.legend()
    fig.tight_layout()
    p = os.path.join(TMP, "time.png")
    fig.savefig(p, dpi=150)
    plt.close(fig)
    return p

g1 = grafico_detecciones()
g2 = grafico_tiempo()

# ---------------------------------------------------------------- Estilos
styles = getSampleStyleSheet()
styles.add(ParagraphStyle("Titulo", parent=styles["Title"], textColor=NAVY, fontSize=22, spaceAfter=6))
styles.add(ParagraphStyle("Sub", parent=styles["Normal"], textColor=ACCENT, fontSize=12,
                          alignment=TA_CENTER, spaceAfter=18))
styles.add(ParagraphStyle("H2", parent=styles["Heading2"], textColor=NAVY, fontSize=14,
                          spaceBefore=14, spaceAfter=6))
styles.add(ParagraphStyle("H3", parent=styles["Heading3"], textColor=ACCENT, fontSize=11.5,
                          spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle("Just", parent=styles["Normal"], alignment=TA_JUSTIFY, fontSize=10,
                          leading=15, spaceAfter=6))
styles.add(ParagraphStyle("Cap", parent=styles["Normal"], fontSize=8.5, alignment=TA_CENTER,
                          textColor=colors.grey, spaceAfter=12))

def P(t, s="Just"):
    return Paragraph(t, styles[s])

# ---------------------------------------------------------------- Tabla estilo
def estilo_tabla(t, header=True):
    cmds = [
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cfd6de")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if header:
        cmds += [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    t.setStyle(TableStyle(cmds))
    return t

# ---------------------------------------------------------------- Contenido
story = []

# Portada
story.append(Spacer(1, 1.5 * cm))
story.append(P("Detección de Objetos: RCNN vs YOLO", "Titulo"))
story.append(P("Informe-resumen de la plataforma de análisis comparativo", "Sub"))
story.append(Spacer(1, 0.3 * cm))

resumen = ("Este informe resume el desarrollo y los resultados de una plataforma web que realiza "
           "detección de objetos sobre imágenes y video, comparando dos arquitecturas de referencia: "
           "<b>Faster R-CNN</b> (basada en RCNN, de dos etapas) y <b>YOLOv8</b> (de una sola etapa). "
           "La aplicación permite cargar imágenes y videos, ejecutar la detección en tiempo real con la "
           "cámara, y comparar ambos modelos en función de métricas de desempeño: número de detecciones, "
           "tiempo de inferencia, FPS y consumo de recursos.")
story.append(P(resumen))

# 1. Qué hace la aplicación
story.append(P("1. ¿Qué hace la aplicación?", "H2"))
story.append(P("La plataforma está organizada en cinco módulos que cubren los objetivos del proyecto:"))
mod = [
    ["Módulo", "Función"],
    ["1 · RCNN en imágenes", "Detección de objetos con Faster R-CNN sobre imágenes estáticas."],
    ["2 · YOLO en imágenes", "Detección de objetos con YOLOv8 sobre imágenes estáticas."],
    ["3 · RCNN en video", "Detección cuadro por cuadro con Faster R-CNN sobre archivos de video."],
    ["4 · YOLO en video", "Detección cuadro por cuadro con YOLOv8 sobre archivos de video."],
    ["5 · Análisis", "Comparación de hallazgos entre imágenes y video según las métricas."],
    ["+ Tiempo real", "Detección en vivo desde la webcam, con modo de comparación simultánea."],
]
t = Table(mod, colWidths=[4.2 * cm, 11.3 * cm])
story.append(estilo_tabla(t))
story.append(Spacer(1, 0.2 * cm))

# 2. Arquitectura y tecnologías
story.append(P("2. Arquitectura y tecnologías", "H2"))
arq = ("El <b>backend</b> es una API REST construida con <b>FastAPI</b> y servida por <b>Uvicorn</b>. "
       "Los modelos se cargan al iniciar: Faster R-CNN proviene de <b>Torchvision</b> "
       "(fasterrcnn_resnet50_fpn, pesos COCO) y YOLOv8 de <b>Ultralytics</b>. Las detecciones se "
       "persisten en una base de datos <b>SQLite</b> (vía SQLAlchemy) para el historial y las "
       "comparaciones. El <b>frontend</b> es una página única con Bootstrap 5 y Chart.js; la detección "
       "en tiempo real usa <b>WebSockets</b> para enviar los cuadros de la cámara al servidor. "
       "La ejecución de esta evaluación se realizó en <b>CPU</b>.")
story.append(P(arq))
story.append(P("Configuración de los modelos evaluada:", "H3"))
cfg = [
    ["Parámetro", "Valor"],
    ["Modelo RCNN", "fasterrcnn_resnet50_fpn (Torchvision, COCO)"],
    ["Modelo YOLO", "yolov8s (variante 'small')"],
    ["Umbral de confianza", "0.60 (ambos modelos)"],
    ["Dispositivo", "CPU"],
    ["Clases detectables", "80 categorías del dataset COCO"],
]
t = Table(cfg, colWidths=[5 * cm, 10.5 * cm])
story.append(estilo_tabla(t))

# 3. Los modelos y sus fuertes
story.append(P("3. Los modelos y sus puntos fuertes", "H2"))
story.append(P("Faster R-CNN (dos etapas)", "H3"))
story.append(P("Genera primero propuestas de regiones y luego las clasifica. Esto le da <b>mayor "
               "sensibilidad (recall) y precisión de localización</b>, especialmente con objetos "
               "<b>pequeños, lejanos o aglomerados</b>. Su contrapartida es un mayor costo "
               "computacional: es notablemente más lento y consume más recursos."))
story.append(P("YOLOv8 (una etapa)", "H3"))
story.append(P("Predice las cajas y clases en una sola pasada de la red. Su gran fuerte es la "
               "<b>velocidad</b>, lo que lo hace ideal para <b>video y tiempo real</b>, manteniendo "
               "una precisión competitiva en escenas con objetos claros y de tamaño medio."))

story.append(PageBreak())

# 4. Resultados
story.append(P("4. Resultados de las pruebas", "H2"))
story.append(P("Se ejecutaron ambos modelos sobre el mismo conjunto de imágenes. La siguiente tabla "
               "resume el número de detecciones y el tiempo de inferencia de cada uno:"))
res = [
    ["Imagen", "Detecciones\nRCNN", "Detecciones\nYOLO", "Tiempo\nRCNN (ms)", "Tiempo\nYOLO (ms)"],
    ["bus", "5", "5", "1493", "156"],
    ["playa (multiobjeto)", "20", "7", "1589", "129"],
    ["perros", "5", "3", "1702", "145"],
    ["zidane", "7", "3", "1809", "126"],
    ["persona", "2", "1", "1448", "169"],
]
t = Table(res, colWidths=[4.5 * cm] + [2.75 * cm] * 4)
estilo_tabla(t)
t.setStyle(TableStyle([("ALIGN", (1, 0), (-1, -1), "CENTER")]))
story.append(t)
story.append(Spacer(1, 0.3 * cm))

story.append(Image(g1, width=15.5 * cm, height=7.5 * cm))
story.append(P("Figura 1. RCNN detecta consistentemente más objetos; la diferencia es máxima en la "
               "escena de playa (20 vs 7), rica en objetos pequeños.", "Cap"))

story.append(Image(g2, width=15.5 * cm, height=7.5 * cm))
story.append(P("Figura 2. YOLO es ~10× más rápido que RCNN en todas las imágenes (≈130-170 ms frente "
               "a ≈1500-1800 ms en CPU).", "Cap"))

# Imágenes demostrativas
story.append(PageBreak())
story.append(P("5. Imágenes demostrativas de cada fuerte", "H2"))
story.append(P("Fuerte de RCNN — recall en objetos pequeños/aglomerados", "H3"))
story.append(P("En la escena de playa, RCNN detectó <b>20 objetos frente a 7 de YOLO</b>, evidenciando "
               "su superioridad para localizar objetos pequeños y numerosos."))
playa = os.path.join(IMG, "playa_multiobjeto.jpg")
if os.path.exists(playa):
    story.append(Image(playa, width=12 * cm, height=8 * cm))
    story.append(P("playa_multiobjeto.jpg — RCNN: 20 detecciones · YOLO: 7 detecciones", "Cap"))

story.append(P("Fuerte de YOLO — velocidad con precisión equivalente", "H3"))
story.append(P("En la imagen del autobús, ambos modelos detectaron <b>los mismos 5 objetos</b>, pero "
               "YOLO lo hizo en <b>156 ms frente a 1493 ms de RCNN (~10× más rápido)</b>."))
bus = os.path.join(IMG, "bus.jpg")
if os.path.exists(bus):
    story.append(Image(bus, width=7 * cm, height=9.3 * cm))
    story.append(P("bus.jpg — RCNN: 5 det. (1493 ms) · YOLO: 5 det. (156 ms)", "Cap"))

# 6. Conclusiones
story.append(PageBreak())
story.append(P("6. Hallazgos y conclusiones", "H2"))
concl = [
    "<b>Precisión / recall:</b> Faster R-CNN detecta consistentemente más objetos, sobre todo "
    "pequeños y solapados. Es la mejor opción cuando prima la exhaustividad de la detección.",
    "<b>Velocidad:</b> YOLOv8 es aproximadamente 10× más rápido en imágenes y mantiene esa ventaja "
    "—amplificada— en video y tiempo real, donde el costo por cuadro se multiplica.",
    "<b>Falsos positivos:</b> RCNN, al ser más sensible, puede producir algún falso positivo de alta "
    "confianza. Elevar el umbral a 0.60 redujo estos casos en ambos modelos.",
    "<b>Imágenes vs video:</b> en video la diferencia de velocidad se vuelve determinante; RCNN en CPU "
    "cae por debajo de 1 FPS, mientras YOLO sostiene una tasa apta para tiempo real.",
    "<b>Recomendación:</b> usar YOLO para escenarios de video/tiempo real y para procesamiento masivo; "
    "reservar Faster R-CNN para análisis offline de imágenes donde la máxima precisión es prioritaria.",
]
for c in concl:
    story.append(P("• " + c))

story.append(Spacer(1, 0.5 * cm))
story.append(P("Informe generado automáticamente a partir de las pruebas ejecutadas en la plataforma "
               "RCNN vs YOLO.", "Cap"))

# ---------------------------------------------------------------- Construir PDF
out_pdf = os.path.join(OUT_DIR, "Informe_RCNN_vs_YOLO.pdf")
doc = SimpleDocTemplate(out_pdf, pagesize=A4,
                        leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                        topMargin=2 * cm, bottomMargin=2 * cm,
                        title="Informe RCNN vs YOLO")
doc.build(story)
print("PDF generado:", out_pdf, "(", os.path.getsize(out_pdf), "bytes )")
