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

            empresa = request.form.get("empresa", "")
            quote_subject = request.form.get("cliente", "")
            notas = request.form.get("notas", "")

            fecha = datetime.datetime.now().strftime("%Y-%m-%d")
            nombre_archivo = "cotizacion.pdf"

            pdf = SimpleDocTemplate(nombre_archivo, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []

            # ================= HEADER =================
            header_data = [
                [
                    Paragraph(f"<b>{empresa}</b>", styles["Heading1"]),
                    Paragraph("""
                    <para align=right>
                    432-232-4434<br/>
                    ottovasquez19@gmail.com<br/>
                    1720 Triumph Trl, Arlington, TX 76002
                    </para>
                    """, styles["Normal"])
                ]
            ]

            header_table = Table(header_data, colWidths=[300, 250])
            header_table.setStyle(TableStyle([
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("ALIGN", (1,0), (1,0), "RIGHT"),
                ("BOTTOMPADDING", (0,0), (-1,-1), 20),
            ]))

            elements.append(header_table)

            # ================= QUOTE INFO =================
            info_data = [
                [
                    Paragraph("<b>Company</b>", styles["Heading3"]),
                    "",
                    Paragraph("<b>Quote Subject</b>", styles["Heading3"])
                ],
                [
                    Paragraph(empresa, styles["Normal"]),
                    "",
                    Paragraph(quote_subject, styles["Normal"])
                ],
                [
                    "",
                    "",
                    Paragraph("<b>Quote Date</b>", styles["Heading3"])
                ],
                [
                    "",
                    "",
                    fecha
                ]
            ]

            info_table = Table(info_data, colWidths=[200, 200, 150])
            info_table.setStyle(TableStyle([
                ("ALIGN", (0,0), (-1,-1), "LEFT"),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("BOTTOMPADDING", (0,0), (-1,-1), 8),
            ]))

            elements.append(info_table)
            elements.append(Spacer(1, 20))

            # ================= PRODUCT TABLE =================
            data = [["Service/Product", "Description", "Qty", "Unit Cost", "Total"]]

            for p in productos:
                data.append([
                    p[0],
                    p[1],
                    p[2],
                    f"${float(p[3]):.2f}",
                    f"${p[4]:.2f}"
                ])

            table = Table(data, colWidths=[120, 180, 50, 80, 80])

            table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("ALIGN", (2,1), (-1,-1), "CENTER"),
                ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
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

            totals_table = Table(totals_data, colWidths=[150, 100])

            totals_table.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
                ("ALIGN", (1,0), (-1,-1), "RIGHT"),
            ]))

            wrapper = Table([[totals_table]], colWidths=[500])
            wrapper.setStyle(TableStyle([
                ("ALIGN", (0,0), (-1,-1), "RIGHT"),
            ]))

            elements.append(wrapper)
            elements.append(Spacer(1, 20))

            # ================= NOTES =================
            elements.append(Paragraph("<b>Notes</b>", styles["Heading3"]))
            elements.append(Paragraph(notas, styles["Normal"]))

            pdf.build(elements)
            print("FORM COMPLETO:", request.form.to_dict())

            return send_file(nombre_archivo, as_attachment=True)

    return render_template("index.html", productos=productos)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
