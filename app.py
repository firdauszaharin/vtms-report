import streamlit as st
from fpdf import FPDF
import os
import json
from datetime import datetime
from PIL import Image, ImageOps
import numpy as np
from streamlit_drawable_canvas import st_canvas

# --- 1. SECURITY CHECK (Sistem Password) ---
def check_password():
    """Returns True if the user had the correct password."""
    def password_entered():
        if st.session_state["password"] == "DausVTMS2026": 
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.header("🔒 Akses Terhad")
        st.text_input("Sila Masukkan Password Akses", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.header("🔒 Akses Terhad")
        st.text_input("Sila Masukkan Password Akses", type="password", on_change=password_entered, key="password")
        st.error("😕 Password salah. Sila hubungi pentadbir sistem.")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- 1. PENGURUSAN TEMPLATE ---
TEMPLATE_FILE = 'templates.json'
TAMBAHAN_FILE = 'templates_tambahan.json' # Fail simpanan untuk perubahan (Add/Delete)

def load_templates():
    # 1. Load default dari kod jika fail templates.json tak wujud
    defaults = {
       "MET REPORT": {
            "headers": ["NO", "ITEM / ACTIVITY", "PASS", "FAIL", "REMARK"],
            "widths": [10, 110, 15, 15, 40],
            "type": "checkbox",
            "content": [
                ["1.0 Anderaa Smartguard Datalogger", ["No physical defect, no error/alarm", "Check SN :1182", "Sensor detection check", "Data Storage Capacity/Backup check"]],
                ["2.0 AMEC Mando 303 Transponder", ["No physical defect, no error/alarm", "Transmit AIS msg8 check", "Check SN :B4K300007", "Verify data at VTS Control(Coastwatch)"]],
                ["3.0 Vaisala PWD20 Visibility Sensor", ["No physical defect, no error/alarm", "Check SN :W4017603", "Monitor Data Output", "Inspect Cables", "Cleaning sensor"]],
                ["4.0 Vaisala WXT536 Weather Sensor", ["No physical defect, no error/alarm", "Check SN : W4045971", "Monitor Data Output", "Inspect Cables", "Cleaning sensor"]],
                ["5.0 Solar Panel 12V 100Watt", ["No physical defect", "Voltage Output check (Remaks voltage)", "Cleaning"]],
                ["6.0 Phocos Solar Charger Controller", ["No physical defect, no error/alarm"]],
                ["7.0 MSB 12V 100Ah AGM Battery", ["No physical defect", "Voltage Output check (Remarks voltage)"]],
                ["8.0 VHF Antenna", ["No physical defect"]],
                ["9.0 GPS Antenna", ["No physical defect"]],
                ["10.0 Stainless Equipment Enclosure", ["No physical defect"]],
                ["11.0 Housekeeping", ["Remove dust on cable terminals"]]
            ]
        },
        "OPERATOR WORKSTATION REPORT": {
            "headers": ["NO", "ITEM / ACTIVITY", "PASS", "FAIL", "REMARK"],
            "widths": [10, 110, 15, 15, 40],
            "type": "checkbox",
            "content": [
                ["1.0 HP Z2 TWR Workstation", ["No physical defect", "Check SN :", "Network test (Note IP in Remark)", "Check system/Windows update"]],
                ["2.0 Monitor HP P34hc G4", ["No physical defect", "Monitor 1 Check SN :", "Monitor 2 Check SN :"]],
                ["3.0 HP Wireless Keyboard & Mouse", ["No physical defect","Function test"]],
                ["4.0 Coastwatch Dongle", ["No physical defect", "Check ID(*localhost 127.0.0.1 1947) :"]],
                ["5.0 UPS ENPLUSEVOIIX-2KTS", ["No physical defect", "Check SN :", "Check output 230 VAC", "Battery test / Backup time"]],
                ["6.0 Operator Terminal CYS1702", ["No physical defect", "Check SN :", "Network test (Note IP in Remark)", "TX/RX Check (Radio test)", "Playback voice check", "Event log record"]],
                ["7.0 Monitor LIYAMA PROLITE", ["No physical defect", "Check SN :"]],
                ["8.0 Headset - PLATORA", ["No physical defect"]],
                ["9.0 Microphone PTT CYS1102", ["No physical defect", "Check SN :"]],
                ["10.0 Foot Pedal CYS1315", ["No physical defect", "Check SN :"]],
                ["11.0 Handset PTT CYS1313", ["No physical defect", "Check SN :"]],
                ["12.0 Bluetooth Headset AINA", ["No physical defect", "Check ID (Note in Remark)", "Check SN:"]],
                ["13.0 Software Check", ["Coastwatch properly installed", "Software functioning", "Receiving AIS data", "Database/Playback search test", "Check 3D GeoVS (PTP 3D only)"]],
                ["14.0 Housekeeping", ["Remove dust on cables/fans"]]
            ]
        },
        "WALL DISPLAY REPORT": {
            "headers": ["NO", "ITEM / ACTIVITY", "PASS", "FAIL", "REMARK"],
            "widths": [10, 110, 15, 15, 40],
            "type": "checkbox",
            "content": [
                ["Displays", [f"Wall Display-{i}" for i in range(1, 16)]],
                ["Housekeeping", ["Remove dust on cables"]]
            ]
        },
        "VHF PTP FLOOR 8": {
            "headers": ["NO", "ITEM / ACTIVITY", "PASS", "FAIL", "REMARK"],
            "widths": [10, 110, 15, 15, 40],
            "type": "checkbox",
            "content": [
                ["Passive Components", ["Antenna Omnidirectional", "Lightning protector", "Coaxial cable", "Check VSWR (Note in remark)", "VHF splitter", "VHF Combiner"]],
                ["VHF Basestation", ["VHF 1 Check SN : 0001", "VHF 2 Check SN : 0002", "VHF 3 Check SN : 0003", "VHF 4 Check SN : 0004", "VHF 5 Check SN : 0005", "VHF 6 Check SN : 0006"]],
                ["Network ", ["Switch Cisco Catalyst", "NTP Time Server", "Check NTP Monitoring Web", "Lease line & SDWAN Equipment"]],
                ["Housekeeping", ["Remove dust on terminals"]]
            ]
        },
        "PTP SERVER REPORT": {
            "headers": ["NO", "ITEM / ACTIVITY", "PASS", "FAIL", "REMARK"],
            "widths": [10, 110, 15, 15, 40],
            "type": "checkbox",
            "content": [
                ["PTP PPB Servers", ["App Server VTSA SN: SGH443KXBB", "Database Server SN: SGH443KXBN", "Sensor Server SN: SGH443KX9Z", "VHF Server 1 SN: 8CJX034", "VHF Server 2 SN: 2JNX034"]],
                ["Storage & Switch", ["SAN Switch SN: CZC4329XHM/XHP", "SAN Storage MSA SN: ACV411W1WL", "KVM LCD8500 SN: 2C4426BADY"]],
                ["Server Tasks", ["Equipment operate without alarm", "Check system health and hardware status (CPU, RAM, disk usage)", "Check application and system logs for errors", "Check Windows update", "Verify archived data make sure 3 month previous data available", " Restart services or applications if necessary"]],
                ["Housekeeping", ["Remove dust on terminals"]]
            ]
        },
            "LPJ SERVER REPORT": {
            "headers": ["NO", "ITEM / ACTIVITY", "PASS", "FAIL", "REMARK"],
            "widths": [10, 110, 15, 15, 40],
            "type": "checkbox",
            "content": [
                ["LPJ Servers", ["App/DB Server SN: SGH441G81Z"]],
                ["Storage & Switch", [ "SAN Switch SN: CZC4329XF8/XHT", "SAN Storage MSA SN: ACV411W1LS", "NTP Time Server and GPS Antenna check"]],
                ["Server Tasks", ["Equipment operate without alarm", "Check system health and hardware status (CPU, RAM, disk usage)", "Check application and system logs for errors", "Check Windows update", "Verify archived data make sure 3 month previous data available", " Restart services or applications if necessary"]],
                ["Housekeeping", ["Remove dust on terminals"]]
            ]
        },
        "INSTALLATION REPORT": {
            "headers": ["NO", "ITEM / ACTIVITY", "PASS", "FAIL", "REMARK"],
            "widths": [10, 110, 15, 15, 40],
            "type": "checkbox",
            "content": [
                ["1. Pre-Installation", ["Site readiness", "Tools available", "Specs reviewed", "Materials verified", "Safety briefing"]],
                ["2. Installation", ["Equipment installed", "Cabling completed", "Power connected", "Network connected", "Grounding completed"]],
                ["3. Testing", ["System configured", "Software installed", "Functional testing", "Operating normally"]]
            ]
        },
        "KEROSAKAN TEMPLATE": {
            "headers": ["NO", "ITEM / ACTIVITY","PASS", "FAIL", "REMARK"],
            "widths": [10, 110, 15, 15, 40],
            "type": "checkbox",
            "content": [
                ["1. Inspection", ["Visual inspection", "Physical check", "Power Status"]],
                ["2. Analysis", ["Root Cause (Hardware/Network)", "External Factors"]],
                ["3. Action Taken", ["Repair / Replacement", "Configuration / Restoration", "System Testing"]]
            ]
        }
    }

    # Cipta fail asal jika tiada (untuk rujukan sahaja)
    if not os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, 'w') as f:
            json.dump(defaults, f, indent=4)

    # 2. Keutamaan: Baca fail TAMBAHAN jika wujud (ini mengandungi Add/Delete terbaru)
    if os.path.exists(TAMBAHAN_FILE):
        with open(TAMBAHAN_FILE, 'r') as f:
            return json.load(f)
    
    # 3. Jika fail tambahan tiada, guna defaults
    return defaults

if 'all_templates' not in st.session_state:
    st.session_state['all_templates'] = load_templates()

def save_templates_to_file():
    # HANYA simpan ke fail tambahan. Fail asal (TEMPLATE_FILE) tidak akan disentuh.
    with open(TAMBAHAN_FILE, 'w') as f:
        json.dump(st.session_state['all_templates'], f, indent=4)

# --- 2. DATABASE S/N ASAL ---
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

# --- 3. PROSES IMEJ & PDF CLASS ---
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

class VTMS_Full_Report(FPDF):
    def __init__(self, header_title=""):
        super().__init__()
        self.header_title = header_title
    def header(self):
        if self.page_no() > 1:
            self.set_font('Arial', 'I', 8); self.set_text_color(100)
            self.cell(0, 5, self.header_title, 0, 1, 'R')
            self.line(10, 15, 200, 15)
    def footer(self):
        self.set_y(-15); self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    def cover_page(self, data, logo_path=None):
        self.add_page(); self.rect(5, 5, 200, 287)
        if logo_path: self.image(logo_path, x=75, y=20, w=60)
        self.set_font('Arial', 'B', 12); self.ln(65); self.cell(0, 5, "SYSTEM OWNER", 0, 1, 'C')
        self.set_font('Arial', 'B', 16); self.multi_cell(0, 8, data['owner'].upper(), 0, 'C'); self.ln(10)
        self.set_font('Arial', 'B', 10); self.cell(0, 5, "PROJECT REFERENCE NO:", 0, 1, 'C')
        self.set_font('Arial', '', 10); self.multi_cell(0, 5, data['ref'], 0, 'C'); self.ln(25)
        self.set_font('Arial', 'B', 18); self.cell(0, 10, "DOCUMENT TITLE:", 0, 1, 'C')
        self.set_font('Arial', 'B', 22); self.multi_cell(0, 12, data['title'].upper(), 0, 'C'); self.ln(35)
        for k, v in [("LOCATION", data['loc']), ("DOCUMENT ID", data['id']), ("DATE", data['dt'])]:
            self.set_x(35); self.set_font('Arial', 'B', 11); self.cell(50, 12, k, 1, 0, 'L')
            self.set_font('Arial', '', 11); self.cell(90, 12, v, 1, 1, 'L')

# --- 4. INTERFACE ---
st.set_page_config(page_title="VTMS Reporting System", layout="wide")

with st.sidebar:
    st.header("🏢 COMPANY ASSETS")
    logo_file = st.file_uploader("Upload Company Logo", type=['png', 'jpg', 'jpeg'])
    
    with st.expander("✨ CREATE NEW TEMPLATE"):
        n_name = st.text_input("Template Name")
        n_type = st.radio("Format", ["checkbox", "technical"])
        if st.button("Build Template"):
            if n_name:
                h_l = ["NO", "ITEM / ACTIVITY", "PASS", "FAIL", "REMARK"] if n_type=="checkbox" else ["NO", "ITEM", "SPEC", "ACTUAL", "RESULT"]
                w_l = [10, 110, 15, 15, 40] if n_type=="checkbox" else [10, 75, 40, 40, 25]
                st.session_state['all_templates'][n_name] = {"headers": h_l, "widths": w_l, "type": n_type, "content": [["1.0 DETAILS", ["First Item"]]]}
                save_templates_to_file(); st.rerun()

    st.divider()
    selected_template = st.selectbox("Template Type:", list(st.session_state['all_templates'].keys()))
    
    with st.expander("📝 EDIT SECTION / TASKS"):
        st.subheader("Manage Sections")
        new_sec = st.text_input("New Section Name")
        col1, col2 = st.columns(2)
        if col1.button("➕ Add Section"):
            if new_sec:
                st.session_state['all_templates'][selected_template]["content"].append([new_sec, ["New Item"]])
                save_templates_to_file(); st.rerun()
            
        sec_names = [s[0] for s in st.session_state['all_templates'][selected_template]["content"]]
        target_sec_del = st.selectbox("Select Section to Delete", sec_names)
        if col2.button("🗑️ Delete Section", type="secondary"):
            st.session_state['all_templates'][selected_template]["content"] = [s for s in st.session_state['all_templates'][selected_template]["content"] if s[0] != target_sec_del]
            save_templates_to_file(); st.rerun()

        st.divider()
        st.subheader("Manage Tasks")
        target_sec = st.selectbox("Select Target Section", sec_names)
        
        current_tasks = []
        for s in st.session_state['all_templates'][selected_template]["content"]:
            if s[0] == target_sec: current_tasks = s[1]; break

        new_t_name = st.text_input("New Task Name")
        col3, col4 = st.columns(2)
        if col3.button("➕ Add Task"):
            if new_t_name:
                for item in st.session_state['all_templates'][selected_template]["content"]:
                    if item[0] == target_sec: item[1].append(new_t_name); break
                save_templates_to_file(); st.rerun()
            
        target_task_del = st.selectbox("Select Task to Delete", current_tasks)
        if col4.button("🗑️ Delete Task"):
            for item in st.session_state['all_templates'][selected_template]["content"]:
                if item[0] == target_sec:
                    if target_task_del in item[1]:
                        item[1].remove(target_task_del); break
            save_templates_to_file(); st.rerun()

    if st.sidebar.button("♻️ Reset to Original Template", type="secondary"):
        if os.path.exists(TAMBAHAN_FILE):
            os.remove(TAMBAHAN_FILE)
            del st.session_state['all_templates']
            st.rerun()

    st.divider()
    sys_owner = st.text_area("System Owner", "LEMBAGA PELABUHAN JOHOR")
    proj_ref = st.text_area("Project Reference", "JPA/IP/PA(S)01-222\n'VESSEL TRAFFIC MANAGEMENT SYSTEM (VTMS)'")
    header_txt = st.text_input("Header Title", "VTMS REPORT - JPA/IP/PA(S)01-222")
    doc_id = st.text_input("Document ID", "LPJPTP/VTMS/2026")
    loc = st.text_input("Location", "VTS TOWER, TANJUNG PELEPAS")
    tech_name = st.text_input("Team Details", "Daus Works")
    client_name = st.text_input("Client Name", "En. Azman")
    report_dt = st.date_input("Date", datetime.now()).strftime("%d/%m/%Y")

# --- Render Checklist ---
config = st.session_state['all_templates'][selected_template]
checklist_results = []
st.header(f"📋 {selected_template}")

for sec_idx, (sec, tasks) in enumerate(config["content"]):
    checklist_results.append({"task": sec, "res": "TITLE", "com": ""})
    with st.expander(sec, expanded=True):
        for t_idx, t in enumerate(tasks):
            u_key = f"{sec_idx}_{t_idx}"
            
            if config["type"] == "technical":
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
                c1.write(f"**{t}**")
                spec = c2.text_input("Spec", key=f"s_{u_key}")
                act = c3.text_input("Actual", key=f"a_{u_key}")
                res = c4.selectbox("Result", ["PASS", "FAIL", "N/A"], key=f"r_{u_key}")
                checklist_results.append({"task": t, "res": res, "spec": spec, "actual": act})
            else:
                c1, c2, c3 = st.columns([1, 1, 2])
                res = c1.radio(t, ["PASS", "FAIL", "N/A"], key=f"rad_{u_key}", horizontal=True)
                if t in sn_database:
                    sel = c3.selectbox("Select SN", ["Manual Input"] + sn_database[t], key=f"sel_{u_key}")
                    rem = c3.text_input("Input SN", key=f"inp_{u_key}") if sel == "Manual Input" else sel
                else:
                    rem = c3.text_input("Remarks", key=f"rem_{u_key}")
                checklist_results.append({"task": t, "res": res, "com": rem})

# --- SUMMARY, EVIDENCE & SIG ---
if 'issue_list' not in st.session_state: st.session_state['issue_list'] = []
st.divider(); st.header("⚠️ SUMMARY & ISSUES")
for i, item in enumerate(st.session_state['issue_list']):
    c1, c2 = st.columns(2)
    st.session_state['issue_list'][i]['issue'] = c1.text_area(f"Issue {i+1}", item['issue'], key=f"is_{i}")
    st.session_state['issue_list'][i]['Remarks'] = c2.text_area(f"Remarks {i+1}", item['Remarks'], key=f"ac_{i}")
if st.button("➕ Add Issue"): st.session_state['issue_list'].append({'issue':'','Remarks':''}); st.rerun()

st.divider(); st.header("🖼️ EVIDENCE")
u_files = st.file_uploader("Upload Evidence", accept_multiple_files=True, type=['png','jpg','jpeg'])
evidence_data = []
if u_files:
    cols = st.columns(4)
    for idx, f in enumerate(u_files):
        with cols[idx % 4]:
            st.image(f, use_container_width=True)
            cap = st.text_input(f"Caption {idx+1}", f"Evidence {idx+1}", key=f"cap_{idx}")
            evidence_data.append({"file": f, "label": cap})

st.divider(); st.header("✍️ APPROVAL")
ca, cb = st.columns(2)
with ca: st.write("Prepared By:"); sig1 = st_canvas(stroke_width=2, height=150, width=300, key="sig1", background_color="#ffffff")
with cb: st.write("Verified By:"); sig2 = st_canvas(stroke_width=2, height=150, width=300, key="sig2", background_color="#ffffff")

# --- 5. PDF GENERATION ---
if st.button("🚀 GENERATE FINAL REPORT", type="primary", use_container_width=True):
    p_img, v_img = process_image(sig1.image_data), process_image(sig2.image_data)
    if not p_img or not v_img: st.error("Please provide both signatures!")
    else:
        pdf = VTMS_Full_Report(header_title=header_txt)
        l_path = "temp_logo.png" if logo_file else None
        if logo_file: 
            with open(l_path, "wb") as f: f.write(logo_file.getbuffer())

        pdf.cover_page({"owner":sys_owner, "ref":proj_ref, "title":selected_template, "loc":loc, "id":doc_id, "dt":report_dt}, logo_path=l_path)
        
# --- 1.0 TABLE OF CONTENTS ---
        pdf.add_page()
        # Set Bold untuk tajuk utama sahaja
        pdf.set_font('Arial', 'B', 14) 
        pdf.cell(0, 10, "TABLE OF CONTENTS", 0, 1)
        pdf.ln(5)

        # Set Normal untuk senarai di bawahnya
        pdf.set_font('Arial', '', 10.5) 
        for n, t, p in [("2.0", "DETAILS / CHECKLIST", 3), ("3.0", "SUMMARY & ISSUES", 4), ("4.0", "APPROVAL", 5), ("5.0", "ATTACHMENTS", 6)]:
            pdf.cell(10, 10, n, 0, 0)
            pdf.cell(145, 10, t, 0, 0)
            pdf.cell(0, 10, "Page " + str(p), 0, 1, 'R')

        pdf.add_page(); pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "2.0    DETAILS / CHECKLIST", 0, 1)
        h_l, w_l = config["headers"], config["widths"]
        pdf.set_font('Arial', 'B', 8); pdf.set_fill_color(230, 230, 230)
        for i, h in enumerate(h_l): pdf.cell(w_l[i], 8, h, 1, 0, 'C', 1)
        pdf.ln()

        cnt = 1
        for row in checklist_results:
            if pdf.get_y() > 265:
                pdf.add_page()
                for i, h in enumerate(h_l): pdf.cell(w_l[i], 8, h, 1, 0, 'C', 1)
                pdf.ln()
            if row['res'] == "TITLE":
                cnt = 1; pdf.set_font('Arial', 'B', 8); pdf.set_fill_color(245, 245, 245)
                pdf.cell(sum(w_l), 7, f" {row['task']}", 1, 1, 'L', 1)
            else:
                pdf.set_font('Arial', '', 7)
                pdf.cell(w_l[0], 6, str(cnt), 1, 0, 'C')
                pdf.cell(w_l[1], 6, f" {row['task']}", 1, 0, 'L')
                if config["type"] == "technical":
                    pdf.cell(w_l[2], 6, str(row.get('spec','-')), 1, 0, 'C')
                    pdf.cell(w_l[3], 6, str(row.get('actual','-')), 1, 0, 'C')
                    pdf.cell(w_l[4], 6, row['res'], 1, 1, 'C')
                else:
                    pdf.cell(w_l[2], 6, "X" if row['res'] == "PASS" else "", 1, 0, 'C')
                    pdf.cell(w_l[3], 6, "X" if row['res'] == "FAIL" else "", 1, 0, 'C')
                    pdf.cell(w_l[4], 6, f" {row.get('com','')}", 1, 1, 'L')
                cnt += 1

        pdf.add_page(); pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "3.0    SUMMARY & ISSUES", 0, 1)
        pdf.set_font('Arial', 'B', 9); pdf.set_fill_color(230, 230, 230)
        pdf.cell(15, 10, "NO", 1, 0, 'C', 1); pdf.cell(85, 10, "SUMMARY / ISSUES", 1, 0, 'C', 1); pdf.cell(90, 10, "REMARKS", 1, 1, 'C', 1)
        pdf.set_font('Arial', '', 8)
        for idx, item in enumerate(st.session_state['issue_list']):
            pdf.cell(15, 10, str(idx+1), 1, 0, 'C'); pdf.cell(85, 10, item['issue'], 1, 0, 'L'); pdf.cell(90, 10, item['Remarks'], 1, 1, 'L')

        pdf.add_page(); pdf.set_font('Arial', 'B', 12); pdf.cell(0, 10, "4.0    APPROVAL & ACCEPTANCE", 0, 1); pdf.ln(5)
        pdf.set_font('Arial', 'B', 10); pdf.cell(0, 7, "Confirmation Statement:", 0, 1)
        pdf.set_font('Arial', '', 10)
        stmt = "The undersigned hereby confirms that the works described in this report have been carried out in accordance with the agreed scope, specifications, and requirements. All findings and remarks have been documented and verified accordingly."
        pdf.multi_cell(0, 6, stmt, 0, 'L')
        
        p_img.save("p.png"); v_img.save("v.png")
        pdf.image("p.png", x=30, y=pdf.get_y()+10, w=50); pdf.image("v.png", x=120, y=pdf.get_y()+10, w=50)
        pdf.ln(45); pdf.cell(95, 8, f"PREPARED BY: {tech_name}", 0, 0, 'L'); pdf.cell(95, 8, f"VERIFIED BY: {client_name}", 0, 1, 'L')

        if evidence_data:
            pdf.add_page()
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, "5.0    ATTACHMENTS", 0, 1)
            
            # Tetapan Grid (2 imej sebaris, maks 4 imej semuka surat)
            x_start = 20
            y_start = 40
            curr_y = y_start
            
            for i, ev in enumerate(evidence_data):
                # 1. Buka muka surat baru selepas setiap 4 gambar
                if i > 0 and i % 4 == 0:
                    pdf.add_page()
                    curr_y = y_start 

                # 2. Tentukan X: Imej genap di kiri (20), ganjil di kanan (110)
                x_pos = x_start if i % 2 == 0 else 110
                
                # 3. Proses imej (Gunakan Pillow untuk resize)
                img = ImageOps.fit(Image.open(ev['file']), (800, 600))
                temp_filename = f"tmp_ev_{i}.jpg" # Nama unik untuk setiap fail sementara
                img.save(temp_filename)
                
                # 4. Masukkan imej ke PDF
                pdf.image(temp_filename, x=x_pos, y=curr_y, w=80)
                
                # 5. Masukkan Kapsyen/Label di bawah imej
                pdf.set_xy(x_pos, curr_y + 62)
                pdf.set_font('Arial', 'I', 8)
                pdf.cell(80, 5, ev['label'], 0, 0, 'C')
                
                # 6. Update koordinat Y: Turunkan baris selepas imej kedua diletakkan
                if i % 2 != 0:
                    curr_y += 75 # Jarak antara baris atas dan bawah
                
                # Padam fail sementara
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

        st.download_button("📥 DOWNLOAD REPORT", pdf.output(dest='S').encode('latin-1'), f"VTMS_REPORT.pdf", "application/pdf", use_container_width=True)
        for f in ["p.png", "v.png", "temp_logo.png"]: 
            if os.path.exists(f): os.remove(f)
