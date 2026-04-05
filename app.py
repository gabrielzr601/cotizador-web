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

empresa_global = ""
cliente_global = ""
notas_global = ""

@app.route("/", methods=["GET", "POST"])
def index():

    global productos
    global empresa_global, cliente_global, notas_global

    if request.method == "POST":

        action = request.form.get("action")

        # 🔥 guardar datos SIEMPRE
        empresa_global = request.form.get("empresa", empresa_global)
        cliente_global = request.form.get("cliente", cliente_global)
        notas_global = request.form.get("notas", notas_global)

        # ===== AGREGAR =====
        if action == "agregar":
            servicio = request.form.get("servicio", "")
            desc = request.form.get("desc", "")
            qty = request.form.get("qty", "0")
            precio = request.form.get("precio", "0")

            try:
                total = float(qty) * float(precio)
                productos.append([servicio, desc, qty, precio, total])
            except:
                pass

        # ===== ELIMINAR =====
        elif action == "eliminar":
            try:
                i = int(request.form.get("index"))
                productos.pop(i)
            except:
                pass

        # ===== NUEVO =====
        elif action == "nuevo":
            productos = []
            empresa_global = ""
            cliente_global = ""
            notas_global = ""

        # ===== PDF =====
        elif action == "pdf":

            fecha = datetime.datetime.now().strftime("%Y-%m-%d")
            nombre_archivo = "cotizacion.pdf"

            pdf = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # ================= HEADER (IGUAL TKINTER) =================
            header_data = [
                [Paragraph(f"<b>{empresa_global}</b>", styles['Heading1'])],
                ['', '', Paragraph('Phone number: 432-232-4434', styles['Normal'])],
                ['', '', Paragraph('Email: ottovasquez19@gmail.com', styles['Normal'])],
                ['', '', Paragraph('Address: 1720 Triumph Trl, Arlington, TX 76002', styles['Normal'])],
            ]

            header = Table(header_data, colWidths=[250, 50, 200])
            header.setStyle(TableStyle([
                ("ALIGN", (0,0), (0,-1), "LEFT"),
                ("ALIGN", (2,0), (2,-1), "RIGHT"),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ]))

            elements.append(header)
            elements.append(Spacer(1, 20))

            # ================= CLIENT INFO (IGUAL TKINTER) =================
            client_data = [
                [Paragraph('<b>Quote Subject</b>', styles['Heading3']), '', Paragraph('<b>Quote</b>', styles['Heading3'])],
                [Paragraph(cliente_global, styles['Normal']), '', ''],
                ['', '', Paragraph('<b>Quote Sent</b>', styles['Heading3'])],
                ['', '', Paragraph(fecha, styles['Normal'])],
            ]

            client_table = Table(client_data, colWidths=[250, 50, 200])
            client_table.setStyle(TableStyle([
                ("ALIGN", (0,0), (0,-1), "LEFT"),
                ("ALIGN", (2,0), (2,-1), "RIGHT"),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ]))

            elements.append(client_table)
            elements.append(Spacer(1, 30))

            # ================= PRODUCT TABLE =================
            data = [["Service/Product", "Description", "Qty", "Unit Cost", "Total"]]

            for p in productos:
                data.append([
                    Paragraph(p[0], styles['Normal']),
                    Paragraph(p[1], styles['Normal']),
                    p[2],
                    f"${float(p[3]):.2f}",
                    f"${p[4]:.2f}"
                ])

            table = Table(data, colWidths=[115, 165, 60, 65, 65], hAlign='RIGHT')
            table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("ALIGN", (2,1), (-1,-1), "CENTER"),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 20))

            # ================= TOTALS =================
            subtotal = sum([p[4] for p in productos])
            rough = subtotal * 0.60
            final = subtotal * 0.40

            totals_data = [
                ["Total", f"${subtotal:.2f}"],
                ["Rough-in (60%)", f"${rough:.2f}"],
                ["Final (40%)", f"${final:.2f}"],
            ]

            totals_table = Table(totals_data, colWidths=[150, 100], hAlign='RIGHT')
            totals_table.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
                ("ALIGN", (1,0), (-1,-1), "RIGHT"),
            ]))

            elements.append(totals_table)
            elements.append(Spacer(1, 20))

            # ================= NOTES (IGUAL TKINTER) =================
            notes_title_style = ParagraphStyle(
                name="NotesTitle",
                parent=styles["Heading3"],
                alignment=TA_LEFT
            )

            notes_content_style = ParagraphStyle(
                name="NotesContent",
                parent=styles["Normal"],
                alignment=TA_LEFT
            )

            elements.append(Paragraph("Notes", notes_title_style))

            if notas_global:
                elements.append(Paragraph(notas_global, notes_content_style))

            elements.append(Spacer(1, 12))

            # ================= BUILD =================
            pdf.build(elements)

            return send_file(nombre_archivo, as_attachment=True)

    return render_template(
        "index.html",
        productos=productos,
        empresa=empresa_global,
        cliente=cliente_global,
        notas=notas_global
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
