from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

def create_report():
    # Définir le chemin du fichier PDF
    pdf_path = "rapport_niveau1.pdf"
    
    # Créer le document
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    
    # Créer la liste des éléments à ajouter au PDF
    elements = []
    
    # Obtenir les styles
    styles = getSampleStyleSheet()
    
    # Ajouter un titre
    title = Paragraph("Rapport d'Analyse - Niveau 1", styles['Heading1'])
    elements.append(title)
    elements.append(Spacer(1, 30))
    
    # Ajouter la date
    date_str = datetime.now().strftime("%d/%m/%Y")
    date_paragraph = Paragraph(f"Date du rapport: {date_str}", styles['Normal'])
    elements.append(date_paragraph)
    elements.append(Spacer(1, 20))
    
    # Ajouter du contenu
    content = """
    Ceci est un exemple de rapport généré automatiquement.
    Vous pouvez ajouter ici les analyses et résultats spécifiques.
    """
    text = Paragraph(content, styles['Normal'])
    elements.append(text)
    
    # Générer le PDF
    doc.build(elements)
    print(f"Le rapport a été généré avec succès : {pdf_path}")

if __name__ == "__main__":
    create_report()