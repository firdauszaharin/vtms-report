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

# --- 2. KELAS PDF ---
class VTMS_Full_Report(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('Arial', 'I', 8)
            self.cell(0, 5, 'VTMS LPJ-PTP MAINTENANCE REPORT - JPA/IP/PA(S)01-222', 0, 1, 'R')

    def cover_page(self, data, logo_input):
        self.add_page()
        self.rect(5, 5, 200, 287) 
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            self.image(logo_path, x=75, y=20, w=60)
        elif logo_input:
            logo_input.save("temp_logo.jpg")
            self.image("temp_logo.jpg", x=75, y=20, w=60)
            if os.path.exists("temp_logo.jpg"): os.remove("temp_logo.jpg")
        
        self.set_font('Arial', 'B', 11); self.ln(60)
        self.cell(0, 5, "SYSTEM OWNER", 0, 1, 'C')
        self.set_font('Arial', 'B', 14); self.cell(0, 7, "LEMBAGA PELABUHAN JOHOR", 0, 1, 'C')
        self.ln(10); self.set_font('Arial', 'B', 10); self.cell(0, 5, "PROJECT REFERENCE NO:", 0, 1, 'C')
        self.set_font('Arial', '', 10); self.multi_cell(0, 5, "JPA/IP/PA(S)01-222\nTENDER FOR DEVELOPMENT AND MAINTENANCE SERVICES\n'VESSEL TRAFFIC MANAGEMENT SYSTEM (VTMS)'", 0, 'C')
        self.ln(20); self.set_font('Arial', 'B', 16); self.cell(0, 10, "DOCUMENT TITLE:", 0, 1, 'C')
        self.set_font('Arial', 'B', 20); self.multi_cell(0, 10, data['title'].upper(), 0, 'C')
        self.ln(30); self.set_font('Arial', 'B', 11)
        for k, v in [("LOCATION", data['loc']), ("DOCUMENT ID", data['id']), ("DATE", data['dt'])]:
            self.set_x(35); self.cell(50, 12, k, 1, 0, 'L'); self.cell(90, 12, v, 1, 1, 'L')

    def site_info_table(self, dt, tm, team):
        self.add_page()
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, "1.0    SITE MAINTENANCE INFORMATION", 0, 1, 'L')
        self.ln(2)
        x, y = self.get_x(), self.get_y()
        w_label, w_data, h_row, h_team = 60, 120, 10, 40
        
        self.set_font('Arial', 'B', 10)
        self.cell(w_label, h_row, " DATE", 1, 0, 'L'); self.set_font('Arial', '', 10); self.cell(w_data, h_row, f" {dt}", 1, 1, 'L')
        self.set_font('Arial', 'B', 10)
        self.cell(w_label, h_row, " TIME", 1, 0, 'L'); self.set_font('Arial', '', 10); self.cell(w_data, h_row, f" {tm}", 1, 1, 'L')
        
        y_team = self.get_y()
        self.set_font('Arial', 'B', 10); self.cell(w_label, h_team, " TEAM DETAIL", 1, 0, 'L')
        self.rect(x + w_label, y_team, w_data, h_team)
        self.set_xy(x + w_label, y_team + 2)
        self.set_font('Arial', '', 10); self.multi_cell(w_data, 8, f"{team}", 0, 'L')
        self.set_y(y_team + h_team + 10)

# --- 3. DATABASE SN & TEMPLATES ---
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

templates = {
    "OPERATOR MAINTENANCE REPORT (PM)": [
        ("1.0 HP Z2 TWR Workstation", ["1.1 No physical defect, equipment operation without error/alarm", "1.2 Check SN :", "1.3 Network test, check IP address:(Note In Remark)", "1.4 Check system"]),
        ("2.0 HP Wireless Keyboard & Mouse Set", ["2.1 No physical defect, equipment operation without error/alarm"]),
        ("3.0 Coastwatch Dongle", ["3.1 No physical defect, equipment operation without error/alarm", "3.2 Check ID :"]),
        ("4.0 Monitor HP P34hc G4 WQHD USBC Curved", ["4.1 No physical defect, equipment operation without error/alarm", "4.2 Monitor 1 Check SN :", "4.3 Monitor 2 Check SN :"]),
        ("5.0 UPS ENPLUSEVOIIX-2KTS:2KVA", ["5.1 No physical defect, equipment operation without error/alarm", "5.2 Check SN :", "5.3 Check UPS output = 230 VAC", "5.4 Battery test /remarks time backup hour"]),
        ("6.0 Coastwatch Software", ["6.1 Make sure Coastwatch dongle & Software are properly Install.", "6.2 To make sure Coastwatch Software can functioning properly.", "6.3 To verify that the CoastWatch are receiving AIS data", "6.4 Search test in database", "6.5 Check 3D GeoVS dongle & Software"]),
        ("7.0 Operator terminal CYS1702", ["7.1 No physical defect, equipment operation without error/alarm", "7.2 Check SN :", "7.3 Network test, check IP address:(Note In Remark)", "7.4 Check system Transmitter and Receiver", "7.5 Check system Playback voice", "7.6 Check event log"]),
        ("8.0 Monitor JIYAMA PROLITE", ["8.1 No physical defect, equipment operation without error/alarm", "8.2 Check SN :"]),
        ("9.0 Headset -PLATORA", ["9.1 No physical defect, equipment operation without error/alarm"]),
        ("10.0 Microphone with ptt -CYS1102", ["10.1 No physical defect, equipment operation without error/alarm", "10.2 Check SN :"]),
        ("11.0 Foot pedal long -CYS1315", ["11.1 No physical defect, equipment operation without error/alarm", "11.2 Check SN :"]),
        ("12.0 Handset with ptt -CYS1313", ["12.1 No physical defect, equipment operation without error/alarm", "12.2 Check SN :"]),
        ("13.0 Bluetooth headset -AINA", ["13.1 No physical defect, equipment operation without error/alarm", "13.2 Check ID: Note in remark", "13.3 Check SN:"]),
        ("14.0 Housekeeping", ["14.1 Remove dust on cable terminal points and fans."])
    ],
    "Installation Report": [
        ("1.0 Equipment Installation", ["1.1 Unpacking equipment", "1.2 Mounting/Placement", "1.3 Power cable connection", "1.4 Network cabling"]),
        ("2.0 Configuration", ["2.1 IP Address setting", "2.2 Software installation", "2.3 System integration test"]),
    ],
    "MET Report": [
        ("1.0 MET Sensor", ["1.1 Visual inspection", "1.2 Clean sensor surface", "1.3 Check mounting bracket", "1.4 Verify data accuracy"]),
    ],
    "PTP SERVER": [
        ("1.0 Server Hardware", ["1.1 Check HDD Status (LED)", "1.2 Check Power Supply Redundancy", "1.3 Dust cleaning fans"]),
    ],
    "PTP Floor 8 VHF Basestation": [
        ("1.0 Radio Unit", ["1.1 Check TX/RX Signal", "1.2 Frequency accuracy check"]),
    ],
    "PTP Wall Display": [
        ("1.0 Display Panel", ["1.1 Visual check dead pixel", "1.2 Bezel alignment"]),
    ],
    "LPJ Server": [
        ("1.0 LPJ Rack Hardware", ["1.1 Server health status", "1.2 Network Switch port status"]),
    ]
}

# --- 4. UI STREAMLIT ---
st.set_page_config(page_title="VTMS Report System", layout="wide")

with st.sidebar:
    st.title("📂 CONFIGURATION")
    selected_template = st.selectbox("Pilih Template Laporan:", list(templates.keys()))
    st.divider()
    doc_id = st.text_input("Document ID", f"LPJPTP/VTMS/{selected_template[:3].upper()}/2026")
    loc = st.text_input("Location", "VTMS CONTROL ROOM")
    report_time = st.text_input("Time", "0900H - 1700H")
    team_members = st.text_area("Team Detail", "1. Firdaus\n2. Technician B")
    tech_name = st.text_input("Technician Name", "Daus Works")
    client_name = st.text_input("Client Name", "En. Azman")
    logo_file = st.file_uploader("Logo Backup", type=['png', 'jpg'])

# --- 5. LOGIK TEMPLATE & SN DROPDOWN ---
st.title(f"📋 {selected_template}")
results = []
current_checklist = templates[selected_template]

for section, tasks in current_checklist:
    # Simpan nama section sebagai 'tajuk' dalam senarai keputusan
    results.append({"task": section, "res": "TITLE", "com": ""})
    
    with st.expander(section):
        for task in tasks:
            c1, c2, c3 = st.columns([1, 1, 2])
            res = c1.radio(f"{task}", ["PASS", "FAIL", "N/A"], key=f"r_{task}_{section}")
            
            if task in sn_database:
                options = ["Lain-lain / Taip Sendiri"] + sn_database[task]
                selected_sn = c3.selectbox(f"Pilih SN untuk {task}", options, key=f"sel_{task}")
                com = c3.text_input("Taip SN Manual", key=f"c_man_{task}") if selected_sn == "Lain-lain / Taip Sendiri" else selected_sn
            else:
                com = c3.text_input("Remarks / SN", key=f"c_{task}_{section}")
            
            results.append({"task": task, "res": res, "com": com})

# --- 6. ATTACHMENT & SIGNATURE ---
st.header("🖼️ Attachments & Approval")
uploaded_imgs = st.file_uploader("Upload Bukti Gambar", accept_multiple_files=True)
captions = []
if uploaded_imgs:
    cols = st.columns(3)
    for i, f in enumerate(uploaded_imgs):
        with cols[i % 3]:
            st.image(f, width=150)
            cap = st.text_input(f"Label {i+1}", f"Evidence {i+1}", key=f"cap_{i}")
            captions.append({"file": f, "label": cap})

col_s1, col_s2 = st.columns(2)
with col_s1:
    st.write("Prepared By:")
    sig1 = st_canvas(stroke_width=2, stroke_color="#000", background_color="#eee", height=120, width=250, key="s1")
with col_s2:
    st.write("Verified By:")
    sig2 = st_canvas(stroke_width=2, stroke_color="#000", background_color="#eee", height=120, width=250, key="s2")

# --- 7. GENERATE PDF ---
if st.button("🚀 GENERATE PDF REPORT", type="primary", use_container_width=True):
    p_img = process_image(sig1.image_data, (300, 150))
    v_img = process_image(sig2.image_data, (300, 150))
    
    if p_img is None or v_img is None:
        st.error("Tandatangan diperlukan!")
    else:
        pdf = VTMS_Full_Report()
        pdf.cover_page({"title": selected_template, "id": doc_id, "loc": loc, "dt": datetime.now().strftime("%d/%m/%Y")}, logo_file)
        
        pdf.site_info_table(datetime.now().strftime("%d/%m/%Y"), report_time, team_members)
        
        # 2.0 MAINTENANCE DETAILS
        pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "2.0    MAINTENANCE DETAILS", 0, 1)
        pdf.set_font('Arial', 'B', 8); pdf.set_fill_color(230, 230, 230)
        pdf.cell(10, 8, "NO", 1, 0, 'C', True); pdf.cell(110, 8, "ITEM / ACTIVITY", 1, 0, 'C', True)
        pdf.cell(15, 8, "PASS", 1, 0, 'C', True); pdf.cell(15, 8, "FAIL", 1, 0, 'C', True); pdf.cell(40, 8, "REMARK / SN", 1, 1, 'C', True)
        
        no_counter = 1
        for r in results:
            if pdf.get_y() > 275: pdf.add_page()
            
            # Jika ia adalah tajuk (Section), ubah format baris
            if r['res'] == "TITLE":
                pdf.set_font('Arial', 'B', 8); pdf.set_fill_color(245, 245, 245)
                pdf.cell(10, 6, "", 1, 0, 'C', True)
                pdf.cell(110, 6, f" {r['task']}", 1, 0, 'L', True)
                pdf.cell(15, 6, "", 1, 0, 'C', True)
                pdf.cell(15, 6, "", 1, 0, 'C', True)
                pdf.cell(40, 6, "", 1, 1, 'L', True)
            else:
                pdf.set_font('Arial', '', 7)
                pdf.cell(10, 6, str(no_counter), 1, 0, 'C')
                pdf.cell(110, 6, f" {r['task']}", 1, 0, 'L')
                pdf.cell(15, 6, "X" if r['res'] == "PASS" else "", 1, 0, 'C')
                pdf.cell(15, 6, "X" if r['res'] == "FAIL" else "", 1, 0, 'C')
                pdf.cell(40, 6, f" {r['com']}", 1, 1, 'L')
                no_counter += 1

        # 4.0 ATTACHMENTS
        if captions:
            pdf.add_page(); pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "4.0    ATTACHMENTS", 0, 1)
            img_w = 110
            x_center = (210 - img_w) / 2
            for item in captions:
                if pdf.get_y() > 200: pdf.add_page()
                img_p = process_image(item['file'], (800, 600))
                img_p.save("tmp.jpg")
                pdf.image("tmp.jpg", x=x_center, w=img_w)
                pdf.set_font('Arial', 'I', 9); pdf.cell(0, 8, f"Figure: {item['label']}", 0, 1, 'C')
                pdf.ln(5); os.remove("tmp.jpg")

        # 5.0 APPROVAL
        if pdf.get_y() > 200: pdf.add_page()
        pdf.ln(10); pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "5.0    APPROVAL", 0, 1)
        pdf.set_font('Arial', '', 10); pdf.multi_cell(0, 5, "Work completed satisfactorily.")
        y_sig = pdf.get_y() + 10
        p_img.save("p.jpg"); v_img.save("v.jpg")
        pdf.image("p.jpg", x=35, y=y_sig, w=50); pdf.image("v.jpg", x=125, y=y_sig, w=50)
        pdf.set_y(y_sig + 35); pdf.set_font('Arial', 'B', 10)
        pdf.cell(90, 10, f"Prepared By: {tech_name}", 0, 0, 'C'); pdf.cell(90, 10, f"Verified By: {client_name}", 0, 1, 'C')
        os.remove("p.jpg"); os.remove("v.jpg")

        pdf_out = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 DOWNLOAD REPORT", data=pdf_out, file_name=f"Report_{selected_template}.pdf", mime="application/pdf", use_container_width=True)
