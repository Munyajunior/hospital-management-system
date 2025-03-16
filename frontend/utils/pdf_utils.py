from fpdf import FPDF

def generate_pdf(patient_info, file_path):
    """
    Generate a PDF form with patient information and medical records.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add patient information
    pdf.cell(200, 10, txt="Patient Information", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Name: {patient_info['full_name']}", ln=True)
    pdf.cell(200, 10, txt=f"Date of Birth: {patient_info['date_of_birth']}", ln=True)
    pdf.cell(200, 10, txt=f"Gender: {patient_info['gender']}", ln=True)
    pdf.cell(200, 10, txt=f"Contact Number: {patient_info['contact_number']}", ln=True)
    pdf.cell(200, 10, txt=f"Email: {patient_info['email']}", ln=True)
    pdf.cell(200, 10, txt=f"Address: {patient_info['address']}", ln=True)
    pdf.cell(200, 10, txt=f"Category: {patient_info['category']}", ln=True)
    pdf.cell(200, 10, txt=f"Emergency: {'Yes' if patient_info['emergency'] else 'No'}", ln=True)

    # Add medical records section
    pdf.cell(200, 10, txt="Medical Records", ln=True, align="C")
    pdf.cell(200, 10, txt="Diagnosis: ___________________________", ln=True)
    pdf.cell(200, 10, txt="Treatment Plan: ___________________________", ln=True)
    pdf.cell(200, 10, txt="Prescription: ___________________________", ln=True)
    pdf.cell(200, 10, txt="Lab Tests: ___________________________", ln=True)
    pdf.cell(200, 10, txt="Scan Results: ___________________________", ln=True)
    pdf.cell(200, 10, txt="Notes: ___________________________", ln=True)

    # Save the PDF
    pdf.output(file_path)