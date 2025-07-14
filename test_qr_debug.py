#!/usr/bin/env python3
"""
Script de prueba para debuggear la generación de QR
"""

import qrcode
import base64
from io import BytesIO

def generar_qr_base64(codigo: str) -> str:
    """Genera un código QR y lo convierte a base64"""
    try:
        print(f"🔍 Generando QR para: {codigo}")
        
        # Crear QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(codigo)
        qr.make(fit=True)
        
        # Crear imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        print(f"✅ QR generado exitosamente. Longitud base64: {len(img_str)}")
        print(f"📄 Primeros 50 caracteres: {img_str[:50]}...")
        
        return img_str
        
    except Exception as e:
        print(f"❌ Error generando QR: {e}")
        return ""

if __name__ == "__main__":
    # Probar con el mismo UUID que vimos en el correo
    test_uuid = "bf7499c8-7e49-4a90-8ea7-87b0746ca12b"
    
    print("🧪 Probando generación de QR...")
    qr_base64 = generar_qr_base64(test_uuid)
    
    if qr_base64:
        print("✅ QR generado correctamente")
        print(f"📊 Longitud del base64: {len(qr_base64)}")
        
        # Crear HTML de prueba
        html_test = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test QR</title>
        </head>
        <body>
            <h1>Test QR Code</h1>
            <img src="data:image/png;base64,{qr_base64}" alt="QR Code" width="200" height="200">
            <p>Código: {test_uuid}</p>
        </body>
        </html>
        """
        
        with open("test_qr.html", "w", encoding="utf-8") as f:
            f.write(html_test)
        
        print("📄 Archivo test_qr.html creado. Ábrelo en tu navegador para ver el QR.")
    else:
        print("❌ Error generando QR") 