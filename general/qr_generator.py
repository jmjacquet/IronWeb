# -*- coding: utf-8 -*-
import json
from StringIO import StringIO

import qrcode
# from general.base64 import b64encode
from general.base64 import encodestring
from general.utilidades import URL_API_QR, b64encode


class QRCodeGenerator(object):
    def __init__(
        self,
        qr_ver=1,
        box_size=10,
        border=4,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        data=''
    ):
        self.qr_ver = qr_ver
        self.box_size = box_size
        self.border = border
        self.error_correction = error_correction
        self.data = data

    def _get_img_and_data(self):
        qr = qrcode.QRCode(
            version=self.qr_ver,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(self.data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        return img, self.data

    def get_qrcode(self):
        img, url = self._get_img_and_data()
        output = StringIO()
        img.save(output, format="PNG")
        return format(encodestring(output.getvalue())), url


class AFIPQRGenerator(QRCodeGenerator):
    def __init__(
        self,
        ver=1,
        fecha="2020-10-13",
        cuit=30000000007,
        pto_vta=10,
        tipo_cmp=1,
        nro_cmp=94,
        importe=12100,
        moneda="PES",
        ctz=1.000,
        tipo_doc_rec=80,
        nro_doc_rec=20000000001,
        tipo_cod_aut="E",
        cod_aut=70417054367476,
    ):
        super(AFIPQRGenerator, self).__init__()
        self.ver = ver
        self.fecha = fecha
        self.cuit = cuit
        self.pto_vta = pto_vta
        self.tipo_cmp = tipo_cmp
        self.nro_cmp = nro_cmp
        self.importe = importe
        self.moneda = moneda
        self.ctz = ctz
        self.tipo_doc_rec = tipo_doc_rec
        self.nro_doc_rec = nro_doc_rec
        self.tipo_cod_aut = tipo_cod_aut
        self.cod_aut = cod_aut

    def _convert_to_json(self):
        datos_cmp = {
            "ver": int(self.ver),
            "fecha": self.fecha,
            "cuit": int(self.cuit),
            "ptoVta": int(self.pto_vta),
            "tipoCmp": int(self.tipo_cmp),
            "nroCmp": int(self.nro_cmp),
            "importe": float(self.importe),
            "moneda": self.moneda,
            "ctz": float(self.ctz),
            "tipoDocRec": int(self.tipo_doc_rec),
            "nroDocRec": int(self.nro_doc_rec),
            "tipoCodAut": self.tipo_cod_aut,
            "codAut": int(self.cod_aut),
        }
        # convertir a representación json
        return json.dumps(datos_cmp)

    def _get_encoded_data(self):
        return URL_API_QR % (b64encode(self._convert_to_json()))

    def get_qrcode(self):
        self.data = self._get_encoded_data()
        return self.get_qrcode_img()


if __name__ == '__main__':  # pragma: no cover
    import sys
    data = "www.google.com"
    qrgen = AFIPQRGenerator()
    print qrgen.get_qrcode()
    qrgen2 = QRCodeGenerator(data=data)
    print qrgen2.get_qrcode()
