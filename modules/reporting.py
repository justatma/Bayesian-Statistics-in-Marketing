import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import beta as beta_dist
import tempfile

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

def create_posterior_plot(alpha, beta, ad_name, output_dir):
    """
    Generate and save a posterior plot as a PNG image.
    """
    x = np.linspace(0, 1, 200)
    y = beta_dist.pdf(x, alpha, beta)
    plt.figure(figsize=(6, 3))
    plt.plot(x, y, label=f"{ad_name} Posterior")
    plt.title(f"Posterior Distribution for {ad_name}")
    plt.xlabel("CTR")
    plt.ylabel("Density")
    plt.legend()
    plot_path = os.path.join(output_dir, f"{ad_name}_posterior.png")
    plt.savefig(plot_path, bbox_inches="tight")
    plt.close()
    return plot_path

def create_pdf_report(data_frame, posteriors, narrative, output_path):
    """
    Generate a PDF report with a title, narrative, data table, and posterior plots.
    """
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("Client Marketing Report", styles['Title']))
    story.append(Spacer(1, 12))

    # Narrative
    story.append(Paragraph(narrative, styles['BodyText']))
    story.append(Spacer(1, 12))

    # Data Table
    table_data = [list(data_frame.columns)] + data_frame.values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND',(0,1),(-1,-1),colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 24))

    # Posterior Plots
    with tempfile.TemporaryDirectory() as tmpdir:
        for ad_name, (alpha, beta) in posteriors.items():
            plot_path = create_posterior_plot(alpha, beta, ad_name, tmpdir)
            story.append(Paragraph(f"Posterior Plot: {ad_name}", styles['Heading2']))
            story.append(Image(plot_path, width=400, height=200))
            story.append(Spacer(1, 24))
        # Build the PDF while images still exist
        doc.build(story)
