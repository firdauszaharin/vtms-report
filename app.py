import streamlit as st
from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image, ImageOps
import numpy as np
from streamlit_drawable_canvas import st_canvas

# --- 1. FUNGSI PEMPROSESAN IMEJ ---
def process_image(img_input, target_size=(800, 600)):
    if img_input is None: return None
    try:
        if isinstance(img_input, np.ndarray):
            if not np.any(img_input[:, :, 3] > 0): return None
            img = Image.fromarray(img_input.astype('uint8')).convert("RGBA")
        else:
            img = Image.open(img_input).convert("RGBA")
        white_bg = Image.new("RGB", img.size, (255, 255, 255))
        white_bg.paste(img, mask=img.split()[3])
        return ImageOps.fit(white_bg, target_size, Image.Resampling.LANCZOS)
    except:
        return None

# --- 2. KELAS PDF (FRONT PAGE LENGKAP) ---
class VTMS_Full_Report(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Arial', 'I', 8)
            self.cell(0, 5, 'VTMS LPJ-PTP PREVENTIVE MAINTENANCE - JPA/IP/PA(S)01-222', 0, 1, 'R')

    def cover_page(self, data, logo):
        self.add_page()
        self.rect(5, 5, 200, 287) # Border Luar
        if logo:
            logo.save("temp_logo.jpg")
            self.image("temp_logo.jpg", x=80, y=20, w=50)
            os.remove("temp_logo.jpg")
        
        self.set_font('Arial', 'B', 10); self.ln(55)
        self.cell(0, 5, "SYSTEM OWNER", 0, 1, 'C')
        self.cell(0, 5, "LEMBAGA PELABUHAN JOHOR", 0, 1, 'C')
        self.ln(10); self.cell(0, 5, "PROJECT REFERENCE NO:", 0, 1, 'C')
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 5, "JPA/IP/PA(S)01-222\nTENDER FOR DEVELOPMENT AND MAINTENANCE SERVICES 'VESSEL TRAFFIC MANAGEMENT SYSTEM (VTMS)'", 0, 'C')
        
        self.ln(20); self.set_font('Arial', 'B', 16); self.cell(0, 10, "DOCUMENT TITLE", 0, 1, 'C')
        self.set_font('Arial', 'B', 20); self.multi_cell(0, 10, data['title'], 0, 'C')
        
        self.ln(30); self.set_font('Arial', 'B', 11)
        for k, v in [("LOCATION", data['loc']), ("DOCUMENT ID", data['id']), ("DATE", data['dt'])]:
            self.set_x(35); self.cell(50, 12, k, 1, 0, 'L')
            self.cell(90, 12, v, 1, 1, 'L')

# --- 3. DATA CHECKLIST PENUH (1.0 - 14.0) ---
checklist_items = [
    ("1.0 HP Z2 TWR Workstation", ["1.1 Physical Check", "1.2 Check SN", "1.3 Network/IP", "1.4 System Check"]),
    ("2.0 Keyboard & Mouse", ["2.1 Physical Check"]),
    ("3.0 Coastwatch Dongle", ["3.1 Physical Check", "3.2 Check ID"]),
    ("4.0 Monitor HP P34hc G4", ["4.1 Physical Check", "4.2 Monitor 1 SN", "4.3 Monitor 2 SN"]),
    ("5.0 UPS System", ["5.1 Physical Check", "5.2 Check SN", "5.3 Output 230 VAC", "5.4 Battery Test"]),
    ("6.0 Coastwatch Software", ["6.1 Installation", "6.2 Functioning", "6.3 AIS Data", "6.4 Search", "6.5 3D GeoVS"]),
    ("7.0 Operator Terminal CYS1702", ["7.1 Physical Check", "7.2 Check SN", "7.3 Network/IP", "7.4 TX/RX", "7.5 Playback", "7.6 Event Log"]),
    ("8.0 Monitor JIYAMA", ["8.1 Physical Check", "8.2 Check SN"]),
    ("9.0 Headset - PLATORA", ["9.1 Physical Check"]),
    ("10.0 Microphone - CYS1102", ["10.1 Physical Check", "10.2 Check SN"]),
    ("11.0 Foot Pedal - CYS1315", ["11.1 Physical Check", "11.2 Check SN"]),
    ("12.0 Handset - CYS1313", ["12.1 Physical Check", "12.2 Check SN"]),
    ("13.0 Bluetooth Headset - AINA", ["13.1 Physical Check", "13.2 Check ID", "13.3 Check SN"]),
    ("14.0 Housekeeping", ["14.1 Remove Dust"])
]

# --- 4. UI STREAMLIT ---
st.set_page_config(page_title="VTMS Report System", layout="wide")

with st.sidebar:
    st.title("📂 NAVIGASI TEMPLATE")
    jenis_laporan = st.radio("Pilih Jenis Laporan:", ["Preventive Maintenance (PM)", "Corrective Maintenance (CM)"])
    st.divider()
    logo_file = st.file_uploader("Logo Syarikat", type=['png', 'jpg'])
    doc_id = st.text_input("Document ID", "LPJPTP/VTMS/PM/Q1/2026")
    loc = st.text_input("Location", "VTMS CONTROL, PTP WISMA A")
    tech_name = st.text_input("Technician Name", "Daus Works")
    client_name = st.text_input("Client Name", "En. Azman")

# --- 5. LOGIK TEMPLATE PM ---
if jenis_laporan == "Preventive Maintenance (PM)":
    st.title("🚢 2.0 Maintenance Activities (PM)")
    pm_results = []
    for section, tasks in checklist_items:
        with st.expander(section):
            for task in tasks:
                col1, col2 = st.columns([1, 2])
                res = col1.radio(f"{task}", ["PASS", "FAIL", "N/A"], key=f"p_{task}", horizontal=True)
                com = col2.text_input(f"Komen", key=f"c_{task}")
                pm_results.append({"sec": section, "task": task, "res": res, "com": com})

# --- 6. LOGIK TEMPLATE CM ---
else:
    st.title("🔧 2.0 Repair Details (CM)")
    fault_desc = st.text_area("Deskripsi Kerosakan (Faulty Description)")
    action_taken = st.text_area("Tindakan Pembaikan (Action Taken)")
    spareparts = st.text_input("Alat Ganti", "N/A")

# --- 7. LAMPIRAN & SIGNATURE (KONGSI) ---
st.header("🖼️ 4.0 Attachments")
uploaded_imgs = st.file_uploader("Upload Bukti Gambar", accept_multiple_files=True)
captions = []
if uploaded_imgs:
    for i, f in enumerate(uploaded_imgs):
        cap = st.text_input(f"Kapsyen Gambar {i+1}", f"Evidence {i+1}", key=f"cap_{i}")
        captions.append({"file": f, "label": cap})

st.header("✍️ 5.0 Approval")
c1, c2 = st.columns(2)
with c1:
    st.write("Prepared By:")
    sig1 = st_canvas(stroke_width=2, height=150, width=300, key="s1")
with c2:
    st.write("Verified By:")
    sig2 = st_canvas(stroke_width=2, height=150, width=300, key="s2")

# --- 8. PENJANAAN PDF ---
if st.button("🚀 GENERATE PDF REPORT", type="primary", use_container_width=True):
    p_img = process_image(sig1.image_data, (300, 150))
    v_img = process_image(sig2.image_data, (300, 150))
    
    if p_img is None or v_img is None:
        st.error("Tandatangan diperlukan!")
    else:
        pdf = VTMS_Full_Report()
        report_title = "VTMS LPJ-PTP PREVENTIVE MAINTENANCE" if jenis_laporan == "Preventive Maintenance (PM)" else "VTMS LPJ-PTP CORRECTIVE MAINTENANCE"
        
        # Cover Page
        cover_data = {"title": report_title, "id": doc_id, "loc": loc, "dt": datetime.now().strftime("%d/%m/%Y")}
        pdf.cover_page(cover_data, process_image(logo_file) if logo_file else None)
        
        # Page 2: Maintenance Content
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "2.0 MAINTENANCE DETAILS", 0, 1)
        
        if jenis_laporan == "Preventive Maintenance (PM)":
            pdf.set_font('Arial', 'B', 8); pdf.set_fill_color(230, 230, 230)
            pdf.cell(10, 8, "NO", 1, 0, 'C', True); pdf.cell(110, 8, "ITEM / ACTIVITY", 1, 0, 'C', True)
            pdf.cell(15, 8, "PASS", 1, 0, 'C', True); pdf.cell(15, 8, "FAIL", 1, 0, 'C', True); pdf.cell(40, 8, "COMMENT", 1, 1, 'C', True)
            
            pdf.set_font('Arial', '', 7)
            for i, r in enumerate(pm_results):
                pdf.cell(10, 6, str(i+1), 1, 0, 'C')
                pdf.cell(110, 6, f"{r['sec']} - {r['task']}", 1, 0, 'L')
                pdf.cell(15, 6, "X" if r['res'] == "PASS" else "", 1, 0, 'C')
                pdf.cell(15, 6, "X" if r['res'] == "FAIL" else "", 1, 0, 'C')
                pdf.cell(40, 6, r['com'], 1, 1, 'L')
                if pdf.get_y() > 270: pdf.add_page()
        else:
            pdf.set_font('Arial', 'B', 10); pdf.cell(0, 8, "Faulty Description:", 0, 1)
            pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 6, fault_desc, 1)
            pdf.ln(5); pdf.cell(0, 8, "Action Taken:", 0, 1)
            pdf.multi_cell(0, 6, action_taken, 1)

        # Page 3: Attachments
        if captions:
            pdf.add_page(); pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "4.0 ATTACHMENTS", 0, 1)
            for item in captions:
                img_p = process_image(item['file'], (800, 600))
                img_p.save("tmp.jpg")
                pdf.image("tmp.jpg", x=55, w=100); pdf.ln(2)
                pdf.set_font('Arial', 'I', 9); pdf.cell(0, 8, f"Figure: {item['label']}", 0, 1, 'C')
                pdf.ln(10); os.remove("tmp.jpg")
                if pdf.get_y() > 230: pdf.add_page()

        # Page 4: Approval
        if pdf.get_y() > 200: pdf.add_page()
        pdf.ln(10); pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "5.0 APPROVAL", 0, 1)
        pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, "Upon signing this Letter of Acceptance, the Client hereby confirms that the maintenance work has been completed satisfactorily.")
        y_sig = pdf.get_y() + 10
        p_img.save("p.jpg"); v_img.save("v.jpg")
        pdf.image("p.jpg", x=30, y=y_sig, w=50); pdf.image("v.jpg", x=120, y=y_sig, w=50)
        pdf.set_y(y_sig + 35); pdf.set_font('Arial', 'B', 10)
        pdf.cell(90, 10, f"Prepared By: {tech_name}", 0, 0, 'C'); pdf.cell(90, 10, f"Verified By: {client_name}", 0, 1, 'C')
        os.remove("p.jpg"); os.remove("v.jpg")

        # Download
        pdf_out = pdf.output(dest='S').encode('latin-1')
        st.success("Laporan Lengkap Berjaya!")
        st.download_button("📥 MUAT TURUN PDF", data=pdf_out, file_name=f"VTMS_Report_{doc_id.replace('/','_')}.pdf", mime="application/pdf", use_container_width=True)