import numpy as np
import cv2
import tensorflow as tf
import gc

# ============================================================
# 🔹 Preprocesamiento
# ============================================================

def remove_background(img_rgb, threshold=240):
    """
    Elimina el fondo blanco de la imagen y lo reemplaza con negro.
    """
    # Convertir a escala de grises para detectar fondo blanco
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    # Crear máscara donde píxeles claros (fondo) son 0
    _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)
    # Aplicar la máscara
    result = cv2.bitwise_and(img_rgb, img_rgb, mask=mask)
    return result


def preprocess_bgr_to_model(img_bgr, size=224):
    """
    Recibe imagen en BGR (OpenCV) y genera 3 inputs:
    1. Imagen a color normalizada
    2. Imagen en escala de grises (3 canales)
    3. Imagen sin fondo (fondo blanco → negro)
    
    Retorna: [input_color, input_gray, input_nobg]
    """
    # Convertir BGR a RGB
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_rgb = cv2.resize(img_rgb, (size, size))
    
    # 1. Input a color
    input_color = img_rgb.astype(np.float32) / 255.0
    input_color = np.expand_dims(input_color, axis=0)
    
    # 2. Input en escala de grises (repetir en 3 canales)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    img_gray_3ch = cv2.cvtColor(img_gray, cv2.COLOR_GRAY2RGB)
    input_gray = img_gray_3ch.astype(np.float32) / 255.0
    input_gray = np.expand_dims(input_gray, axis=0)
    
    # 3. Input sin fondo
    img_nobg = remove_background(img_rgb)
    input_nobg = img_nobg.astype(np.float32) / 255.0
    input_nobg = np.expand_dims(input_nobg, axis=0)
    
    return [input_color, input_gray, input_nobg]


# ============================================================
# 🔹 Buscar la última capa convolucional
# ============================================================

def find_last_conv_layer(model):
    """
    Busca la última capa con salida 4D (batch, h, w, channels).
    """
    for layer in reversed(model.layers):
        try:
            if len(layer.output.shape) == 4:
                return layer.name
        except Exception:
            continue
    # Nombre por defecto si no encuentra
    return model.layers[-1].name


# ============================================================
# 🔹 Grad-CAM
# ============================================================

def make_gradcam_heatmap(
    model,
    img_array,
    last_conv_layer_name=None,
    class_idx_override=None,
):
    """
    Genera el heatmap Grad-CAM.

    Parámetros:
      - model: modelo Keras.
      - img_array: lista de tensors [color, gray, nobg] o tensor único.
      - last_conv_layer_name: nombre de la última capa conv (opcional).
      - class_idx_override: si node es None, usa ese índice de clase
        en vez de la clase más probable.

    Retorna:
      - heatmap (2D)
      - class_idx (int usado)
      - preds_np (vector de probabilidades)
    """

    if last_conv_layer_name is None:
        last_conv_layer_name = find_last_conv_layer(model)

    # Control por si el modelo tiene múltiples salidas
    model_output = model.output
    if isinstance(model_output, (list, tuple)):
        model_output = model_output[0]

    grad_model = tf.keras.models.Model(
        [model.inputs],
        [model.get_layer(last_conv_layer_name).output, model_output],
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_array)

        if isinstance(predictions, (list, tuple)):
            predictions = predictions[0]

        predictions = tf.reshape(predictions, [-1])

        # Si nos pasaron una clase específica, usar esa
        if class_idx_override is not None:
            class_idx = tf.constant(class_idx_override, dtype=tf.int32)
        else:
            class_idx = tf.argmax(predictions)

        loss = predictions[class_idx]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_mean(conv_outputs * pooled_grads, axis=-1)

    heatmap = np.maximum(heatmap.numpy(), 0)
    maxv = np.max(heatmap) if np.max(heatmap) > 0 else 1e-7
    heatmap /= maxv

    # Convertir class_idx a entero puro
    class_idx_int = int(class_idx.numpy()) if hasattr(class_idx, "numpy") else int(class_idx)

    # Vector de probabilidades en numpy
    preds_np = predictions.numpy() if hasattr(predictions, "numpy") else np.array(predictions)
    preds_np = np.squeeze(preds_np)

    return heatmap, class_idx_int, preds_np


# ============================================================
# 🔹 Superponer mapa de calor
# ============================================================

def overlay_heatmap_on_image(orig_bgr, heatmap, alpha=0.4):
    """
    Mezcla el mapa de calor con la imagen BGR original.
    """
    h, w = orig_bgr.shape[:2]
    heatmap_resized = cv2.resize(heatmap, (w, h))
    heatmap_resized = np.uint8(255 * heatmap_resized)
    heatmap_color = cv2.applyColorMap(heatmap_resized, cv2.COLORMAP_JET)
    blended = cv2.addWeighted(orig_bgr, 1.0 - alpha, heatmap_color, alpha, 0)
    return blended


# ============================================================
# 🔹 Liberar memoria
# ============================================================

def release_tf_memory(model=None):
    """
    Limpia la sesión de Keras/TensorFlow para liberar RAM
    (especialmente útil en Render Free u otros entornos limitados).
    """
    try:
        tf.keras.backend.clear_session()
        del model
        gc.collect()
    except Exception:
        pass