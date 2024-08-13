import base64
from io import BytesIO
from barcode import EAN13
from barcode.writer import ImageWriter

def generate_barcode(barcode_value):
    from io import BytesIO
    from barcode import EAN13
    from barcode.writer import ImageWriter

    buffer = BytesIO()
    EAN13(barcode_value, writer=ImageWriter()).write(buffer)

    return base64.b64encode(buffer.getvalue())
