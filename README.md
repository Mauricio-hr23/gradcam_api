# 🌿 GradCAM API - AgroIA

API backend para generar mapas de calor Grad-CAM de diagnósticos de enfermedades en plantas usando modelos de Deep Learning.

## 🚀 Deployment en Railway

### Requisitos Previos
- Cuenta en [Railway](https://railway.app)
- Repositorio conectado: `https://github.com/Mauricio-hr23/gradcam_api`

### Pasos para Desplegar

1. **Crear Nuevo Proyecto en Railway**
   - Ve a [railway.app](https://railway.app)
   - Click en "New Project"
   - Selecciona "Deploy from GitHub repo"
   - Conecta el repositorio `Mauricio-hr23/gradcam_api`

2. **Configuración Automática**
   Railway detectará automáticamente:
   - Python como lenguaje (via `requirements.txt`)
   - Comando de inicio (via `Procfile`)
   - Versión de Python 3.11 (via `.python-version`)

3. **Variables de Entorno** (Opcional)
   No se requieren variables de entorno para la configuración básica.

4. **Deploy**
   Railway desplegará automáticamente. El proceso incluye:
   - Instalación de dependencias desde `requirements.txt`
   - Inicio del servidor con gunicorn (2 workers, timeout 120s)

5. **Obtener URL**
   Una vez desplegado, Railway te proporcionará una URL pública como:
   ```
   https://gradcam-api-production.up.railway.app
   ```

## 📡 API Endpoints

### Health Check
```bash
GET /health
```
Respuesta:
```json
{"ok": true}
```

### Generar Grad-CAM
```bash
POST /gradcam
```

**Parámetros (multipart/form-data):**
- `species` (string, requerido): Especie de la planta (`corn`, `grape`, `peach`, `pepper`, `potato`, `strawberry`, `tomato`)
- `image` (file, requerido): Imagen de la hoja en formato JPG/PNG
- `target_label` (string, opcional): Clase específica para generar el Grad-CAM

**Respuesta:**
```json
{
  "species": "tomato",
  "predicted_label": "Tomato_Late_blight",
  "target_label": null,
  "topk": [
    {"label": "Tomato_Late_blight", "prob": 0.95},
    {"label": "Tomato_Early_blight", "prob": 0.03},
    ...
  ],
  "image_gradcam_b64": "base64_encoded_image..."
}
```

## 🔧 Desarrollo Local

### Instalación
```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecutar Localmente
```bash
python app.py
```
El servidor estará disponible en `http://localhost:5000`

### Probar API
```bash
# Health check
curl http://localhost:5000/health

# Generar Grad-CAM
curl -X POST http://localhost:5000/gradcam \
  -F "species=tomato" \
  -F "image=@path/to/leaf.jpg"
```

## 📦 Estructura del Proyecto

```
gradcam_api/
├── app.py              # API Flask principal
├── gradcam.py          # Funciones de Grad-CAM
├── fix_labels.py       # Utilidad para corregir labels
├── models/             # Modelos .h5 y labels.json
├── requirements.txt    # Dependencias Python
├── Procfile           # Configuración Railway
├── .python-version    # Versión de Python
└── README.md          # Esta documentación
```

## 🧠 Modelos Soportados

Los modelos deben estar en la carpeta `models/` con el formato:
- `{species}_model.h5` - Modelo de TensorFlow/Keras
- `{species}_labels.json` - Etiquetas de clases

Especies soportadas:
- `corn` - Maíz
- `grape` - Uva
- `peach` - Durazno
- `pepper` - Pimiento
- `potato` - Papa
- `strawberry` - Fresa
- `tomato` - Tomate

## ⚡ Optimizaciones para Railway

- **Gunicorn Workers**: 2 workers para balance entre memoria y rendimiento
- **Timeout**: 120 segundos para permitir generación de mapas de calor complejos
- **Liberación de Memoria**: Limpieza automática de memoria TensorFlow después de cada request
- **Python 3.11**: Versión optimizada compatible con TensorFlow 2.16.1

## 🔄 Actualizar Deployment

Railway se actualiza automáticamente con cada push a la rama principal:
```bash
git add .
git commit -m "Update API"
git push origin main
```

## 📱 Integración con Flutter App

Actualiza la URL del servidor en tu app Flutter:
```dart
// Antes (Render)
const String serverUrl = 'https://gradcam-api.onrender.com';

// Después (Railway)
const String serverUrl = 'https://tu-app.up.railway.app';
```

## 📝 Notas

- **Performance**: Railway ofrece mejor rendimiento que Render Free tier para generación de mapas de calor
- **Cold Starts**: Railway mantiene las instancias activas, reduciendo tiempos de espera
- **Escalabilidad**: Fácil escalado vertical/horizontal según necesidades

## 🐛 Troubleshooting

### Error: "Model not found"
Verifica que los archivos `.h5` y `_labels.json` estén en la carpeta `models/`

### Error: "Timeout"
Aumenta el timeout en `Procfile` si los mapas de calor tardan más de 120s

### Error: "Out of memory"
Reduce el número de workers en `Procfile` de 2 a 1

## 📄 Licencia

Proyecto AgroIA - Universidad Técnica de Cotopaxi
