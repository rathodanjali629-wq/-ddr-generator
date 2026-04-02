from flask import Flask, request, render_template, send_file
import os
from extractor import extract_text, extract_images
from report_generator import generate_ddr
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from PIL import Image as PILImage

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        inspection_pdf = request.files["inspection"]
        thermal_pdf = request.files["thermal"]

        insp_path = f"{UPLOAD_FOLDER}/inspection.pdf"
        therm_path = f"{UPLOAD_FOLDER}/thermal.pdf"
        inspection_pdf.save(insp_path)
        thermal_pdf.save(therm_path)

        inspection_text = extract_text(insp_path)
        thermal_text = extract_text(therm_path)

        insp_images = extract_images(insp_path, "uploads/insp_images")

        ddr_content = generate_ddr(inspection_text, thermal_text)

        output_path = "uploads/DDR_Report.pdf"
        create_pdf(ddr_content, insp_images, output_path)

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"<h2>Error:</h2><pre>{str(e)}</pre>", 500


def create_pdf(content, images, output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("Detailed Diagnostic Report (DDR)", styles["Title"]))
    story.append(Spacer(1, 20))

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            story.append(Spacer(1, 6))
        elif line.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.")):
            clean = line.replace("**", "")
            story.append(Paragraph(clean, styles["Heading2"]))
            story.append(Spacer(1, 8))
        else:
            clean = line.replace("**", "")
            story.append(Paragraph(clean, styles["Normal"]))
            story.append(Spacer(1, 4))

    story.append(Paragraph("Supporting Images", styles["Heading2"]))
    story.append(Spacer(1, 10))

    added = 0
    for img_path in images:
        try:
            img = PILImage.open(img_path)
            img_array = list(img.getdata())
            dark_pixels = sum(1 for p in img_array
                            if isinstance(p, tuple) and sum(p[:3]) < 30)
            total = len(img_array)
            if total > 0 and dark_pixels / total > 0.5:
                continue
            story.append(RLImage(img_path, width=4*inch, height=3*inch))
            story.append(Spacer(1, 12))
            added += 1
            if added >= 15:
                break
        except:
            pass

    doc.build(story)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)