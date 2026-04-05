from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import io

app = Flask(__name__)

productos = []

@app.route("/", methods=["GET", "POST"])
def index():

    global productos

    empresa = ""
    cliente = ""
    notas = ""

    if request.method == "POST":

        # 🔥 SIEMPRE CAPTURAR CAMPOS
        empresa = request.form.get("empresa", "")
        cliente = request.form.get("cliente", "")
        notas = request.form.get("notas", "")

        servicio = request.form.get("servicio", "")
        desc = request.form.get("desc", "")
        qty = request.form.get("qty", "")
        precio = request.form.get("precio", "")

        # BOTÓN AGREGAR
        if "agregar" in request.form:
            if servicio and qty and precio:
                total = float(qty) * float(precio)
                productos.append([servicio, desc, qty, precio, total])

        # BOTÓN ELIMINAR
        if "eliminar" in request.form:
            idx = int(request.form["eliminar"])
            if 0 <= idx < len(productos):
                productos.pop(idx)

        # BOTÓN NUEVO
        if "nuevo" in request.form:
            productos = []
            empresa = ""
            cliente = ""
            notas = ""

        # BOTÓN PDF
        if "pdf" in request.form:
            return generar_pdf(empresa, cliente, notas, productos)

    return render_template(
        "index.html",
        productos=productos,
        empresa=empresa,
        cliente=cliente,
        notas=notas
    )


def generar_pdf(empresa, cliente, notas, productos):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    # 🟢 ENCABEZADO
    elements.append(Paragraph(f"<b>Company:</b> {empresa}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Quote Subject:</b> {cliente}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Notes:</b> {notas}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    # 🟢 TABLA
    data = [["Service", "Description", "Qty", "Price", "Total"]]

    for p in productos:
        data.append(p)

    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="quote.pdf")


if __name__ == "__main__":
    app.run(debug=True)
