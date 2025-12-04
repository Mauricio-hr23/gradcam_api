# Gradcam API para AgroIA

API Flask para generar mapas de calor (Grad-CAM) que visualizan qué regiones de una imagen de hoja influencian la predicción del modelo de clasificación de enfermedades.

## Características

- **Grad-CAM en tiempo real**: Genera mapas de calor para explicar decisiones del modelo
- **Soporte multi-especie**: Corn, Grape, Peach, Pepper, Potato, Strawberry, Tomato
- **API simple**: Endpoint POST `/gradcam` con imagen y especie
- **Optimizado para deployment**: Configurado para Railway/Render

## Estructura

```
gradcam_api/
├── app.py              # API Flask principal
├── gradcam.py          # Lógica de Grad-CAM
├── models/             # Modelos .h5 y labels.json
├── requirements.txt    # Dependencias Python
├── Procfile           # Configuración gunicorn
└── railway.json       # Configuración Railway
```

## Deploy en Railway

1. Conectar repo a Railway
2. Railway detecta Flask automáticamente  
3. Deploy automático en cada push

Ver URL: `https://tu-proyecto.up.railway.app`

## API Usage

### Health Check
```bash
GET /health
```

### Generate Grad-CAM
```bash
POST /gradcam
Content-Type: multipart/form-data

Fields:
- species: string (e.g., "Tomato")
- image: file (imagen de hoja)
- target_label: string (opcional - enfermedad específica)
```

**Response:**
```json
{
  "species": "Tomato",
  "predicted_label": "Tomato___Late_blight",
  "target_label": null,
  "topk": [
    {"label": "Tomato___Late_blight", "prob": 0.95},
    ...
  ],
  "image_gradcam_b64": "base64_encoded_image..."
}
```

## Local Development

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python app.py

# Servidor en http://localhost:5000
```

## Modelos

Los modelos fueron entrenados con:
- ✅ Imágenes a color
- ✅ Imágenes en escala de grises  
- ✅ Imágenes sin fondo

Esto garantiza consistencia con la app Flutter que usa preprocesamiento mixto.

## Tecnologías

- **Flask** 3.0.3 - Web framework
- **TensorFlow** 2.16.1 - ML inference
- **OpenCV** 4.10 - Procesamiento de imágenes
- **Gunicorn** 21.2 - Production server
