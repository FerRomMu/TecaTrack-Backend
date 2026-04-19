PATTERNS: dict[str, str] = {
    "amount": r"\$\s?([\d.,]+)|importe[:\s]+([\d.,]+)",
    "date": r"(\d{1,2}\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\s+de\s+\d{4})",
    "time": r"(\d{2}:\d{2}(?::\d{2})?)",
    "cbu_cvu": r"(?:CBU|CVU)[:\s]*([\d]{22})",
    "alias": r"[Aa]lias[:\s]+([\w.]+)",
    "cuit_cuil": r"(?:CUIT|CUIL)[:\s]*(\d{2}-?\d{8}-?\d)",
    "receipt_number": r"(?:N[°º]?|Comprobante|Nro\.?)[:\s#]*(\d+)",
    "destination_bank": r"Entidad\s+([A-Za-zÁÉÍÓÚÑáéíóúñ ]+?)(?=\s+(CBU|CVU|CUIT|Origen|$))",
    "source_bank": r"Banco\s+[A-Za-z]?\s*([A-Za-zÁÉÍÓÚÑáéíóúñ ]+?)(?=\s+(Origen|Titular|Caja|$))",
}