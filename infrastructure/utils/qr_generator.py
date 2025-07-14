import qrcode
import base64
from io import BytesIO

class QRGenerator:
    async def generar(self, codigo: str) -> str:
        """
        Genera un código QR en base64 a partir de un string.
        Args:
            codigo (str): El texto/código a codificar en el QR.
        Returns:
            str: Imagen QR en formato base64 (sin prefijo data:image/png;base64,)
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(codigo)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, 'PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return img_str 