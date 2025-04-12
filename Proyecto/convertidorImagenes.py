import base64

def convertirImagen(imagenes):
    imagenes_base64 = []
    for img in imagenes:
        img_id = img[0]
        img_nombre = img[1]
        img_blob = img[2]
        img_base64 = base64.b64encode(img_blob).decode('utf-8')
        imagenes_base64.append({
            'id': img_id,
            'nombre': img_nombre,
            'imagen': img_base64
        })
    return imagenes_base64 