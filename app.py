from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
import datetime
import os

app = Flask(__name__)

productos = []

@app.route("/", methods=["GET", "POST"])
def index():
    global productos

    if request.method == "POST":
        if "agregar" in request.form:
            servicio = request.form["servicio"]
            desc = request.form["desc"]
            qty = request.form["qty"]
            precio = request.form["precio"]

            if servicio and qty and precio:
                total = float(qty) * float(precio)
                productos.append([servicio, desc, qty, precio, total])

        elif "eliminar" in request.form:
            index = int(request.form.get("eliminar"))
            productos.pop(index)

        elif "nuevo" in request.form:
            productos = []

        elif "pdf" in request.form:
            empresa = request.form["empresa"]
            cliente = request.form["cliente"]
            notas = request.form["notas"]

            nombre_archivo = "cotizacion.pdf"
            pdf = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # HEADER
            elements.append(Paragraph(f"<b>{empresa}</b>", styles['Heading1']))
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"Cliente: {cliente}", styles['Normal']))
            elements.append(Spacer(1, 20))

            # TABLA
            data = [["Service", "Desc", "Qty", "Price", "Total"]]
            for p in productos:
                data.append([p[0], p[1], p[2], p[3], f"{p[4]:.2f}"])

            table = Table(data)
            table.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 1, colors.black)
            ]))

            elements.append(table)
            elements.append(Spacer(1, 20))

            # TOTAL
            subtotal = sum([p[4] for p in productos])
            elements.append(Paragraph(f"Total: ${subtotal:.2f}", styles['Normal']))

            # NOTAS
            elements.append(Spacer(1, 20))
            elements.append(Paragraph("Notes", styles['Heading3']))

            notes_style = ParagraphStyle(name="Notes", alignment=TA_LEFT)
            elements.append(Paragraph(notas, notes_style))

            pdf.build(elements)

            return send_file(nombre_archivo, as_attachment=True)

    return render_template("/templates/index.html", productos=productos)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

