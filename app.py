import streamlit as st
from fpdf import FPDF
import os
from datetime import datetime
from PIL import Image, ImageOps
import numpy as np
from streamlit_drawable_canvas import st_canvas

# --- 1. FUNGSI PROSES IMEJ ---
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

# --- 2. KELAS PDF CUSTOM ---
class VTMS_Full_Report(FPDF):
    def __init__(self, header_title=""):
        super().__init__()
        self.header_title = header_title
        self.section_pages = {}

    def header(self):
        if self.page_no() > 1:
            self.set_font('Arial', 'I', 8)
            self.set_text_color(100)
            self.cell(0, 5, self.header_title, 0, 1, 'R')
            self.line(10, 15, 200, 15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def cover_page(self, data, logo_path=None):
        self.add_page()
        self.rect(5, 5, 200, 287)
        if logo_path:
            self.image(logo_path, x=75, y=20, w=60)
        
        self.set_font('Arial', 'B', 12); self.ln(65)
        self.cell(0, 5, "SYSTEM OWNER", 0, 1, 'C')
        self.set_font('Arial', 'B', 16); self.multi_cell(0, 8, data['owner'].upper(), 0, 'C')
        self.ln(10); self.set_font('Arial', 'B', 10); self.cell(0, 5, "PROJECT REFERENCE NO:", 0, 1, 'C')
        self.set_font('Arial', '', 10); self.multi_cell(0, 5, data['ref'], 0, 'C')
        self.ln(25); self.set_font('Arial', 'B', 18); self.cell(0, 10, "DOCUMENT TITLE:", 0, 1, 'C')
        self.set_font('Arial', 'B', 22); self.multi_cell(0, 12, data['title'].upper(), 0, 'C')
        self.ln(35)
        for k, v in [("LOCATION", data['loc']), ("DOCUMENT ID", data['id']), ("DATE", data['dt'])]:
            self.set_x(35)
            self.set_font('Arial', 'B', 11); self.cell(50, 12, k, 1, 0, 'L')
            self.set_font('Arial', '', 11); self.cell(90, 12, v, 1, 1, 'L')

# --- 3. PANGKALAN DATA ---
sn_database = {
    "1.2 Check SN :": ["4CE442B8B8", "4CE442B8B7", "4CE442B8BD", "4CE442B8BB", "4CE442B8BC", "4CE442B8B9"],
    "3.2 Check ID :": ["1563220541", "75770141", "689509092", "1151380960", "2048014076", "338176953"],
    "4.2 Monitor 1 Check SN :": ["CNC4431M34", "CNC4431M33", "CNC4431M32", "CNC4431M39", "CNC4431M36", "CNC4431M38"],
    "4.3 Monitor 2 Check SN :": ["CNC4431M34", "CNC4431M33", "CNC4431M32", "CNC4431M39", "CNC4431M36", "CNC4431M38"],
    "5.2 Check SN :": ["UI01245140306", "UI01245140305", "UI01245140309"],
    "7.2 Check SN :": ["VHF-A-9921", "VHF-A-9922"],
    "8.2 Check SN :": ["VHF-B-8831", "VHF-B-8832"],
    "13.3 Check SN:": ["AW121390192", "AW122210344", "AW119430008"]
}

templates = {
    "OPERATOR MAINTENANCE REPORT (PM)": [
        ("1.0 HP Z2 TWR Workstation", ["1.1 No physical defect", "1.2 Check SN :", "1.3 Network test", "1.4 Check system health status"]),
        ("2.0 HP Wireless Keyboard & Mouse", ["2.1 No physical defect", "2.2 Battery status/Operation check"]),
        ("3.0 Coastwatch Dongle", ["3.1 No physical defect", "3.2 Check ID :"]),
        ("4.0 Monitor HP P34hc G4", ["4.1 No physical defect", "4.2 Monitor 1 Check SN :", "4.3 Monitor 2 Check SN :"]),
        ("5.0 UPS ENPLUSEVOIIX-2KTS", ["5.1 No physical defect", "5.2 Check SN :", "5.3 Check output VAC"]),
        ("6.0 Network Switch", ["6.1 Port status check", "6.2 Cable integrity"]),
        ("7.0 VHF Radio 1", ["7.1 Visual check", "7.2 Check SN :"]),
        ("8.0 VHF Radio 2", ["8.1 Visual check", "8.2 Check SN :"]),
        ("9.0 AIS Base Station", ["9.1 Signal status"]),
        ("10.0 Radar System", ["10.1 Rotation check", "10.2 Check SN :"]),
        ("11.0 CCTV System", ["11.1 Camera feed", "11.2 Check SN :"]),
        ("12.0 Server Rack", ["12.1 Fan operation", "12.2 Check SN :"]),
        ("13.0 Power Management", ["13.1 Distribution box", "13.2 Voltage reading", "13.3 Check SN:"]),
        ("14.0 Housekeeping", ["14.1 Remove dust on cable terminal points.", "14.2 Clean workstation area."])
    ],
    "Installation Report": [
        ("1.0 Equipment Installation", ["Type equipment", "SN of equipment", "IP Address if available"]),
        ("2.0 Configuration", ["2.1 IP Address setting", "2.2 Software installation", "2.3 System integration test"])
    ]
}

# --- 4. STREAMLIT INTERFACE ---
st.set_page_config(page_title="VTMS Reporting System", layout="wide")

with st.sidebar:
    st.header("🏢 COMPANY ASSETS")
    logo_file = st.file_uploader("Upload Company Logo (PNG/JPG)", type=['png', 'jpg', 'jpeg'])
    
    st.header("⚙️ REPORT CONFIG")
    sys_owner = st.text_area("System Owner", "LEMBAGA PELABUHAN JOHOR")
    proj_ref = st.text_area("Project Reference", "JPA/IP/PA(S)01-222\n'VESSEL TRAFFIC MANAGEMENT SYSTEM (VTMS)'")
    header_txt = st.text_input("Header Title", "VTMS REPORT - JPA/IP/PA(S)01-222")
    selected_template = st.selectbox("Template Type:", list(templates.keys()))
    doc_id = st.text_input("Document ID", "LPJPTP/VTMS/2026")
    loc = st.text_input("Location", "VTS TOWER, TANJUNG PELEPAS")
    tech_name = st.text_input("Technician Name", "Daus Works")
    client_name = st.text_input("Client Name", "En. Azman")
    report_dt = st.date_input("Date", datetime.now()).strftime("%d/%m/%Y")

# Render Checklist Dinamik
checklist_results = []
st.header(f"📋 {selected_template}")
for sec, tasks in templates[selected_template]:
    checklist_results.append({"task": sec, "res": "TITLE", "com": ""})
    with st.expander(sec, expanded=True):
        for t in tasks:
            c1, c2, c3 = st.columns([1,1,2])
            res = c1.radio(t, ["PASS", "FAIL", "N/A"], key=f"r_{t}")
            if t in sn_database:
                sel = c3.selectbox("Select SN", ["Manual Input"] + sn_database[t], key=f"s_{t}")
                rem = c3.text_input("Input SN", key=f"m_{t}") if sel == "Manual Input" else sel
            else:
                rem = c3.text_input("Remarks", key=f"c_{t}")
            checklist_results.append({"task": t, "res": res, "com": rem})

# Issues Section
if 'issue_list' not in st.session_state: st.session_state['issue_list'] = []
st.divider()
st.header("⚠️ SUMMARY & ISSUES")
for i, item in enumerate(st.session_state['issue_list']):
    c1, c2 = st.columns(2)
    st.session_state['issue_list'][i]['issue'] = c1.text_area(f"Issue {i+1}", item['issue'], key=f"is_{i}")
    st.session_state['issue_list'][i]['Remarks'] = c2.text_area(f"Remarks {i+1}", item['Remarks'], key=f"ac_{i}")
if st.button("➕ Add Issue"): st.session_state['issue_list'].append({'issue':'','Remarks':''})

# Evidence Section
st.divider()
st.header("🖼️ 5.0 EVIDENCE / ATTACHMENTS")
u_files = st.file_uploader("Upload Evidence Photos", accept_multiple_files=True, type=['png','jpg','jpeg'])
evidence_data = []
if u_files:
    cols = st.columns(4)
    for idx, f in enumerate(u_files):
        with cols[idx % 4]:
            st.image(f, use_container_width=True)
            cap = st.text_input(f"Caption {idx+1}", f"Evidence {idx+1}", key=f"cap_{idx}")
            evidence_data.append({"file": f, "label": cap})

# Approval Section
st.divider()
st.header("✍️ 4.0 APPROVAL")
ca, cb = st.columns(2)
with ca: st.write("Prepared By:"); sig1 = st_canvas(stroke_width=2, height=150, width=300, key="sig1", background_color="#eee")
with cb: st.write("Verified By:"); sig2 = st_canvas(stroke_width=2, height=150, width=300, key="sig2", background_color="#eee")

# --- 5. PDF GENERATION LOGIC ---
if st.button("🚀 GENERATE FINAL REPORT", type="primary", use_container_width=True):
    p_img, v_img = process_image(sig1.image_data), process_image(sig2.image_data)
    
    if not p_img or not v_img:
        st.error("Please provide both signatures!")
    else:
        pdf = VTMS_Full_Report(header_title=header_txt)
        
        # Simpan Logo jika ada
        l_path = "temp_logo.png" if logo_file else None
        if logo_file:
            with open(l_path, "wb") as f: f.write(logo_file.getbuffer())

        # 1. Cover
        pdf.cover_page({"owner":sys_owner, "ref":proj_ref, "title":selected_template, "loc":loc, "id":doc_id, "dt":report_dt}, logo_path=l_path)
        
        # 2. Table of Contents
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "1.0    TABLE OF CONTENTS", 0, 1); pdf.ln(5)
        pdf.set_font('Arial', '', 11)
        sections = [("2.0", "DETAILS / CHECKLIST", 3), ("3.0", "SUMMARY & ISSUES", 4), ("4.0", "APPROVAL", 5), ("5.0", "ATTACHMENTS", 6)]
        for n, t, p in sections:
            pdf.cell(15, 10, n, 0, 0); pdf.cell(145, 10, t, 0, 0); pdf.cell(0, 10, "Page " + str(p), 0, 1, 'R')

        # 3. Details (Seksyen 2.0)
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "2.0    DETAILS / CHECKLIST", 0, 1)
        pdf.set_font('Arial', 'B', 8); pdf.set_fill_color(230, 230, 230)
        pdf.cell(10, 8, "NO", 1, 0, 'C', 1); pdf.cell(110, 8, "ITEM / ACTIVITY", 1, 0, 'C', 1)
        pdf.cell(15, 8, "PASS", 1, 0, 'C', 1); pdf.cell(15, 8, "FAIL", 1, 0, 'C', 1); pdf.cell(40, 8, "REMARK", 1, 1, 'C', 1)
        
        cnt = 1
        for row in checklist_results:
            if pdf.get_y() > 265: pdf.add_page()
            if row['res'] == "TITLE":
                # SETIAP KALI JUMPA TITLE, KITA RESET BALIK CNT KEPADA 1
                cnt = 1
                
                pdf.set_font('Arial', 'B', 8); pdf.set_fill_color(245, 245, 245)
                pdf.cell(190, 7, f" {row['task']}", 1, 1, 'L', 1)
            else:
                pdf.set_font('Arial', '', 7)
                # Sekarang str(cnt) akan bermula dari 1 untuk setiap seksyen
                pdf.cell(10, 6, str(cnt), 1, 0, 'C')
                pdf.cell(110, 6, f" {row['task']}", 1, 0, 'L')
                pdf.cell(15, 6, "X" if row['res'] == "PASS" else "", 1, 0, 'C')
                pdf.cell(15, 6, "X" if row['res'] == "FAIL" else "", 1, 0, 'C')
                pdf.cell(40, 6, f" {row['com']}", 1, 1, 'L'); cnt += 1

        # 4. Issues (Seksyen 3.0)
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "3.0    SUMMARY & ISSUES", 0, 1)
        pdf.set_font('Arial', 'B', 9); pdf.set_fill_color(230, 230, 230)
        pdf.cell(15, 10, "NO", 1, 0, 'C', 1); pdf.cell(85, 10, "SUMMARY /ISSUES / FINDINGS", 1, 0, 'C', 1); pdf.cell(90, 10, "Remarks", 1, 1, 'C', 1)
        pdf.set_font('Arial', '', 8)
        for idx, item in enumerate(st.session_state['issue_list']):
            if pdf.get_y() > 250: pdf.add_page()
            y_s = pdf.get_y()
            pdf.set_xy(25, y_s); pdf.multi_cell(85, 5, item['issue'] if item['issue'] else "-", 0, 'L'); y1 = pdf.get_y()
            pdf.set_xy(110, y_s); pdf.multi_cell(90, 5, item['Remarks'] if item['Remarks'] else "-", 0, 'L'); y2 = pdf.get_y()
            h = max(y1, y2, y_s + 10) - y_s
            pdf.set_xy(10, y_s); pdf.cell(15, h, str(idx+1), 1, 0, 'C')
            pdf.set_xy(25, y_s); pdf.cell(85, h, "", 1); pdf.set_xy(110, y_s); pdf.cell(90, h, "", 1, 1)

        # 5. Approval (Seksyen 4.0)
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "4.0    APPROVAL & ACCEPTANCE", 0, 1); pdf.ln(5)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 7, "Confirmation Statement:", 0, 1)
        pdf.set_font('Arial', '', 10)
        stmt = "The undersigned hereby confirms that the maintenance and inspection services detailed in this report have been carried out and completed in accordance with the project specifications and requirements. All findings and Remarkss have been noted and verified."
        pdf.multi_cell(0, 6, stmt, 0, 'L')
        
        p_img.save("p.png"); v_img.save("v.png")
        y_pos = pdf.get_y() + 15
        pdf.image("p.png", x=30, y=y_pos, w=50); pdf.image("v.png", x=120, y=y_pos, w=50)
        pdf.set_y(y_pos + 35); pdf.set_font('Arial', 'B', 10)
        pdf.cell(95, 8, f"PREPARED BY: {tech_name}", 0, 0, 'L')
        pdf.cell(95, 8, f"VERIFIED BY: {client_name}", 0, 1, 'L')

        # 6. Evidence (Seksyen 5.0)
        if evidence_data:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "5.0    ATTACHMENTS / EVIDENCE", 0, 1); pdf.ln(5)
            for i, ev in enumerate(evidence_data):
                if i > 0 and i % 4 == 0: pdf.add_page()
                col, row = (i % 4) % 2, (i % 4) // 2
                x, y = 15 + (col * 95), 35 + (row * 80)
                img = Image.open(ev['file']); img = ImageOps.fit(img, (800, 600))
                img.save(f"temp_ev_{i}.jpg")
                pdf.image(f"temp_ev_{i}.jpg", x=x, y=y, w=85, h=65)
                pdf.set_xy(x, y + 67); pdf.set_font('Arial', 'I', 8); pdf.cell(85, 5, f"Figure {i+1}: {ev['label']}", 0, 0, 'C')
                os.remove(f"temp_ev_{i}.jpg")

        # Final Output
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 DOWNLOAD REPORT", pdf_bytes, f"VTMS_REPORT_{doc_id.replace('/','_')}.pdf", "application/pdf", use_container_width=True)

        # Cleanup
        for f in ["p.png", "v.png", "temp_logo.png"]:
            if os.path.exists(f): os.remove(f)
