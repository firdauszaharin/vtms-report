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
    except: return None

# --- 2. KELAS PDF ---
class VTMS_Full_Report(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Arial', 'I', 8)
            self.cell(0, 5, 'VTMS LPJ-PTP MAINTENANCE REPORT - JPA/IP/PA(S)01-222', 0, 1, 'R')

    def cover_page(self, data):
        self.add_page()
        self.rect(5, 5, 200, 287) 
        logo_path = "logo.png" 
        if os.path.exists(logo_path):
            self.image(logo_path, x=75, y=20, w=60)
        self.set_font('Arial', 'B', 11); self.ln(60)
        self.cell(0, 5, "SYSTEM OWNER", 0, 1, 'C')
        self.set_font('Arial', 'B', 14); self.cell(0, 7, "LEMBAGA PELABUHAN JOHOR", 0, 1, 'C')
        self.ln(10); self.set_font('Arial', 'B', 10); self.cell(0, 5, "PROJECT REFERENCE NO:", 0, 1, 'C')
        self.set_font('Arial', '', 10); self.multi_cell(0, 5, "JPA/IP/PA(S)01-222\nTENDER FOR DEVELOPMENT AND MAINTENANCE SERVICES\n'VESSEL TRAFFIC MANAGEMENT SYSTEM (VTMS)'", 0, 'C')
        self.ln(20); self.set_font('Arial', 'B', 16); self.cell(0, 10, "DOCUMENT TITLE:", 0, 1, 'C')
        self.set_font('Arial', 'B', 20); self.multi_cell(0, 10, data['title'].upper(), 0, 'C')
        self.ln(30)
        for k, v in [("LOCATION", data['loc']), ("DOCUMENT ID", data['id']), ("DATE", data['dt'])]:
            self.set_x(35)
            self.set_font('Arial', 'B', 11); self.cell(50, 12, k, 1, 0, 'L')
            self.set_font('Arial', '', 11); self.cell(90, 12, v, 1, 1, 'L')

# --- 3. DATABASE SN ---
sn_database = {
    "1.2 Check SN :": ["4CE442B8B8", "4CE442B8B7", "4CE442B8BD", "4CE442B8BB", "4CE442B8BC", "4CE442B8B9"],
    "3.2 Check ID :": ["1563220541", "75770141", "689509092", "1151380960", "2048014076", "338176953"],
    "4.2 Monitor 1 Check SN :": ["CNC4431M34", "CNC4431M33", "CNC4431M32", "CNC4431M39", "CNC4431M36", "CNC4431M38", "CNC4431M2X", "CNC4431M2Y", "CNC4431M15", "CNC4431M30", "CNC4431M31", "CNC4431M35"],
    "4.3 Monitor 2 Check SN :": ["CNC4431M34", "CNC4431M33", "CNC4431M32", "CNC4431M39", "CNC4431M36", "CNC4431M38", "CNC4431M2X", "CNC4431M2Y", "CNC4431M15", "CNC4431M30", "CNC4431M31", "CNC4431M35"],
    "5.2 Check SN :": ["UI01245140306", "UI01245140305", "UI01245140309", "UI01245140308", "UI01245140310", "UI01243060100"],
    "7.2 Check SN :": ["0164", "0165", "0166", "0167", "0168", "0169"],
    "8.2 Check SN :": ["11815345B0174", "11815345B0183", "11815345B0160", "11815203A0383", "11815345B0187", "11815345B0164"],
    "10.2 Check SN :": ["0200", "0201", "0202", "0203", "0204", "0205"],
    "11.2 Check SN :": ["0145", "0146", "0147", "0148", "0149", "0150"],
    "12.2 Check SN :": ["3050", "3033", "3030", "3035", "3036", "3031"],
    "13.3 Check SN:": ["AW121390192", "AW122210344", "AW119430008", "AW122240324", "AW122320273", "AW122080141"]
}

# --- 4. TEMPLATE LENGKAP ---
templates = {
    "OPERATOR MAINTENANCE REPORT (PM)": [
        ("1.0 HP Z2 TWR Workstation", ["1.1 No physical defect", "1.2 Check SN :", "1.3 Network test", "1.4 Check system health status"]),
        ("2.0 HP Wireless Keyboard & Mouse", ["2.1 No physical defect", "2.2 Battery status/Operation check"]),
        ("3.0 Coastwatch Dongle", ["3.1 No physical defect", "3.2 Check ID :"]),
        ("4.0 Monitor HP P34hc G4", ["4.1 No physical defect", "4.2 Monitor 1 Check SN :", "4.3 Monitor 2 Check SN :"]),
        ("5.0 UPS ENPLUSEVOIIX-2KTS", ["5.1 No physical defect", "5.2 Check SN :", "5.3 Check output VAC", "5.4 Battery load test"]),
        ("6.0 Network Switch", ["6.1 Port status check", "6.2 Cable integrity"]),
        ("7.0 VHF Radio 1", ["7.1 Visual check", "7.2 Check SN :"]),
        ("8.0 VHF Radio 2", ["8.1 Visual check", "8.2 Check SN :"]),
        ("9.0 AIS Base Station", ["9.1 Signal status"]),
        ("10.0 Radar System", ["10.1 Rotation check", "10.2 Check SN :"]),
        ("11.0 CCTV System", ["11.1 Camera feed", "11.2 Check SN :"]),
        ("12.0 Server Rack", ["12.1 Fan operation", "12.2 Check SN :"]),
        ("13.0 Power Management", ["13.1 Distribution box", "13.2 Voltage reading", "13.3 Check SN:"]),
        ("14.0 Housekeeping", ["14.1 Remove dust on cable terminal points and fans.", "14.2 Clean workstation area."])
    ],
    "Installation Report": [("1.0 Equipment Installation", ["1.1 Mounting", "1.2 Cabling", "1.3 Configuration"])],
    "MET Report": [("1.0 MET Sensor", ["1.1 Visual check", "1.2 Data verify"])],
    "PTP SERVER": [("1.0 Server", ["1.1 Health status", "1.2 Disk LED"])],
    "LPJ Server": [("1.0 LPJ Rack", ["1.1 Port status", "1.2 UPS Check"])]
}

# --- 5. UI STREAMLIT ---
st.set_page_config(page_title="VTMS Maintenance System", layout="wide")
with st.sidebar:
    st.header("📂 CONFIGURATION")
    selected_template = st.selectbox("Pilih Template:", list(templates.keys()))
    doc_id = st.text_input("Document ID", "LPJPTP/VTMS/2026")
    loc = st.text_input("Location", "VTMS CONTROL ROOM")
    tech_name = st.text_input("Technician", "Daus Works")
    client_name = st.text_input("Client", "En. Azman")
    report_date = st.date_input("Date", datetime.now()).strftime("%d/%m/%Y")

st.title(f"📋 {selected_template}")
results = []
for section, tasks in templates[selected_template]:
    results.append({"task": section, "res": "TITLE", "com": ""})
    with st.expander(section, expanded=True):
        for task in tasks:
            c1, c2, c3 = st.columns([1, 1, 2])
            res = c1.radio(task, ["PASS", "FAIL", "N/A"], key=f"r_{task}")
            if task in sn_database:
                opt = ["Taip Sendiri"] + sn_database[task]
                sel_sn = c3.selectbox(f"Pilih SN", opt, key=f"s_{task}")
                com = c3.text_input("Manual SN", key=f"m_{task}") if sel_sn == "Taip Sendiri" else sel_sn
            else:
                com = c3.text_input("Remarks", key=f"c_{task}")
            results.append({"task": task, "res": res, "com": com})

st.divider()
st.header("⚠️ 3.0 ISSUES & CORRECTIVE ACTIONS")
c_iss1, c_act1 = st.columns(2)
iss1 = c_iss1.text_area("Issue 1", height=80)
act1 = c_act1.text_area("Action Taken 1", height=80)
c_iss2, c_act2 = st.columns(2)
iss2 = c_iss2.text_area("Issue 2", height=80)
act2 = c_act2.text_area("Action Taken 2", height=80)

st.header("🖼️ Attachments & Approval")
uploaded_imgs = st.file_uploader("Upload Gambar Evidence", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
captions = []
if uploaded_imgs:
    cols = st.columns(3)
    for i, f in enumerate(uploaded_imgs):
        with cols[i % 3]:
            st.image(f, width=150)
            cap = st.text_input(f"Label Gambar {i+1}", f"Evidence {i+1}", key=f"cap_{i}")
            captions.append({"file": f, "label": cap})

st.divider()
col_s1, col_s2 = st.columns(2)
with col_s1:
    st.write("Prepared By:")
    sig1 = st_canvas(stroke_width=2, height=120, width=250, key="s1", background_color="#eee")
with col_s2:
    st.write("Verified By:")
    sig2 = st_canvas(stroke_width=2, height=120, width=250, key="s2", background_color="#eee")

# --- 6. GENERATE PDF ---
if st.button("🚀 GENERATE PDF REPORT", type="primary", use_container_width=True):
    p_img, v_img = process_image(sig1.image_data), process_image(sig2.image_data)
    if not p_img or not v_img:
        st.error("Tandatangan diperlukan!")
    else:
        pdf = VTMS_Full_Report()
        pdf.cover_page({"title": selected_template, "id": doc_id, "loc": loc, "dt": report_date})
        
        # Maintenance Details
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "2.0    MAINTENANCE DETAILS", 0, 1)
        pdf.set_font('Arial', 'B', 8); pdf.set_fill_color(230, 230, 230)
        pdf.cell(10, 8, "NO", 1, 0, 'C', True); pdf.cell(110, 8, "ITEM / ACTIVITY", 1, 0, 'C', True)
        pdf.cell(15, 8, "PASS", 1, 0, 'C', True); pdf.cell(15, 8, "FAIL", 1, 0, 'C', True); pdf.cell(40, 8, "REMARK", 1, 1, 'C', True)
        
        cnt = 1
        for r in results:
            if pdf.get_y() > 270: pdf.add_page()
            if r['res'] == "TITLE":
                pdf.set_font('Arial', 'B', 8); pdf.set_fill_color(245, 245, 245)
                pdf.cell(190, 7, f" {r['task']}", 1, 1, 'L', True)
            else:
                pdf.set_font('Arial', '', 7)
                pdf.cell(10, 6, str(cnt), 1, 0, 'C'); pdf.cell(110, 6, f" {r['task']}", 1, 0, 'L')
                pdf.cell(15, 6, "X" if r['res']=="PASS" else "", 1, 0, 'C')
                pdf.cell(15, 6, "X" if r['res']=="FAIL" else "", 1, 0, 'C')
                pdf.cell(40, 6, f" {r['com']}", 1, 1, 'L'); cnt += 1

        # Issues Table
        pdf.ln(10); pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "3.0    ISSUES & CORRECTIVE ACTIONS", 0, 1)
        pdf.set_font('Arial', 'B', 9); pdf.set_fill_color(230, 230, 230)
        pdf.cell(15, 10, "NO", 1, 0, 'C', True); pdf.cell(85, 10, "ISSUES / FINDINGS", 1, 0, 'C', True); pdf.cell(90, 10, "CORRECTIVE ACTION", 1, 1, 'C', True)
        pdf.set_font('Arial', '', 8)
        for i, (iss, act) in enumerate([(iss1, act1), (iss2, act2)], 1):
            curr_y = pdf.get_y()
            pdf.set_xy(10, curr_y); pdf.multi_cell(15, 5, str(i), 0, 'C')
            h1 = pdf.get_y() - curr_y
            pdf.set_xy(25, curr_y); pdf.multi_cell(85, 5, iss if iss else "-", 0, 'L')
            h2 = pdf.get_y() - curr_y
            pdf.set_xy(110, curr_y); pdf.multi_cell(90, 5, act if act else "-", 0, 'L')
            h3 = pdf.get_y() - curr_y
            max_h = max(h1, h2, h3, 10)
            pdf.set_xy(10, curr_y); pdf.cell(15, max_h, "", 1); pdf.cell(85, max_h, "", 1); pdf.cell(90, max_h, "", 1)
            pdf.set_y(curr_y + max_h)

        # Signature Box
        pdf.ln(10); p_img.save("p.jpg"); v_img.save("v.jpg")
        y_sig = pdf.get_y()
        pdf.image("p.jpg", x=35, y=y_sig, w=50); pdf.image("v.jpg", x=125, y=y_sig, w=50)
        pdf.set_y(y_sig + 35); pdf.set_font('Arial', 'B', 10)
        pdf.cell(90, 10, f"Prepared: {tech_name}", 0, 0, 'C'); pdf.cell(90, 10, f"Verified: {client_name}", 0, 1, 'C')

        # Attachments Page
        if captions:
            pdf.add_page(); pdf.set_font('Arial', 'B', 14); pdf.cell(0, 10, "4.0    ATTACHMENTS", 0, 1)
            for idx, item in enumerate(captions):
                if idx > 0 and idx % 2 == 0: pdf.add_page()
                img_pil = Image.open(item['file'])
                img_pil.save(f"temp_{idx}.jpg")
                pdf.image(f"temp_{idx}.jpg", x=30, w=150)
                pdf.set_font('Arial', 'I', 10); pdf.cell(0, 10, f"Figure {idx+1}: {item['label']}", 0, 1, 'C')
                pdf.ln(5)

        st.download_button("📥 DOWNLOAD REPORT", pdf.output(dest='S').encode('latin-1'), "VTMS_Report.pdf", "application/pdf", use_container_width=True)
