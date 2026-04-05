from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import datetime
import os

app = Flask(__name__)

productos = []

@app.route("/", methods=["GET", "POST"])
def index():
    global productos

    if request.method == "POST":

        # ===== AGREGAR =====
        if "agregar" in request.form:
            servicio = request.form.get("servicio")
            desc = request.form.get("desc")
            qty = request.form.get("qty")
            precio = request.form.get("precio")

            if servicio and qty and precio:
                try:
                    total = float(qty) * float(precio)
                    productos.append([servicio, desc, qty, precio, total])
                except:
                    pass

        # ===== ELIMINAR =====
        elif "eliminar" in request.form:
            try:
                i = int(request.form.get("eliminar"))
                productos.pop(i)
            except:
                pass

        # ===== NUEVO =====
        elif "nuevo" in request.form:
            productos = []

        # ===== PDF =====
        elif "pdf" in request.form:
            empresa = request.form.get("empresa")
            cliente = request.form.get("cliente")
            notas = request.form.get("notas")

            fecha = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"cotizacion_{fecha}.pdf"

            pdf = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # HEADER
            elements.append(Paragraph(f"<b>{empresa}</b>", styles['Heading1']))
            elements.append(Paragraph("Phone: 432-232-4434", styles['Normal']))
            elements.append(Paragraph("Email: empresa@email.com", styles['Normal']))
            elements.append(Paragraph("Address: Arlington, TX", styles['Normal']))
            elements.append(Spacer(1, 15))

            # CLIENTE
            elements.append(Paragraph(f"<b>Quote Subject:</b> {cliente}", styles['Normal']))
            elements.append(Spacer(1, 15))

            # TABLA
            data = [["Service", "Description", "Qty", "Price", "Total"]]

            for p in productos:
                data.append([
                    p[0],
                    p[1],
                    p[2],
                    f"${float(p[3]):.2f}",
                    f"${p[4]:.2f}"
                ])

            table = Table(data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 15))

            # TOTALES
            subtotal = sum([p[4] for p in productos])
            rough = subtotal * 0.60
            final = subtotal * 0.40

            totals = [
                ["Total", f"${subtotal:.2f}"],
                ["Rough-in (60%)", f"${rough:.2f}"],
                ["Final (40%)", f"${final:.2f}"],
            ]

            t = Table(totals)
            t.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ]))

            elements.append(t)

            # NOTES
            elements.append(Spacer(1, 15))
            elements.append(Paragraph("<b>Notes</b>", styles['Heading3']))
            elements.append(Paragraph(notas if notas else "", styles['Normal']))

            pdf.build(elements)

            return send_file(nombre_archivo, as_attachment=True)

    return render_template("index.html", productos=productos)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
