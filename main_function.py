# app.py
import json
import re
import base64
import tempfile

import streamlit as st
import PyPDF2
import os

# Optional: PDF image preview using PyMuPDF (if installed)
try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except Exception:
    HAS_PYMUPDF = False

# ==== OpenRouter (OpenAI-compatible client) ====
from openai import OpenAI

@st.cache_resource
def get_openrouter_client(OPENROUTER_API_KEY):
    if not OPENROUTER_API_KEY:
        st.error(" Please put your OpenRouter API key in the code.")
        st.stop()
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    return client

def generate_json_section(prompt: str, client) -> str:
    sys_msg = (
        "You are a careful data extraction engine. "
        "Reply with ONLY valid JSON or arrays matching the user's requested structure. "
        "No explanations, no markdown fences."
    )
    resp = client.chat.completions.create(
        model="openai/gpt-4o-mini",   # 👈 Fixed model
        messages=[
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
    )
    return (resp.choices[0].message.content or "").strip()


# ========== CONFIG ==========
st.set_page_config(page_title="NEVE JEWEL GROUP • Invoice → JSON", page_icon="🧾", layout="wide")


# ========== PDF HELPERS ==========
def file_to_text(file_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    text = ""
    with open(tmp_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    print(text)
    return text 

def to_b64_pdf(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode("utf-8")


# ========== PROMPTS (UNCHANGED) ==========
def build_prompt_vendor(raw_text):
    return fr"""
Extract structured JSON data from the following invoice text which is extracted from image passed of invoice

--- START ---
{raw_text}
--- END ---


    "generalDetailsRequest": {{
        "sezUnitCode": This is fixed value as "BOM6Z227",
        "sezUnitName": This is fixed value as "Navgrahaa Gems Pvt Ltd",
        "sezIecCode": This is fixed value as "AAHCN5216B",
        "sezUnitAddress": This is fixed value as "4th Floor, Unit No. 404 Multistoried Building, SEEPZ SEZ , Andheri-East, Mumbai 400096"
        "sezCity": This is fixed value as "Mumbai",
        "sezState": This is fixed value as "MAHARASHTRA",
        "sezPinCode": This is fixed value as "400096",
        "sezGstin": This is fixed value as "27AANCN5216B2ZR",
        "dtaUnitGstin": this is seller gstin number ,
        "dtaUnitName": this is seller name,  
        "dtaUnitAddressLine1": seller  address if present else blank string remove the special character like / , & and replace it with - if there. sometimes it is given at top of pdf. Strictly limit the adrress lenth upto 50 character, 
        "dtaUnitCity": seller City from address,
        "dtaUnitState": This is always fixed as  "MAHARASHTRA",
        "dtaUnitPinCode": this is always fixed as "400051",
        "igstDeclaration": this is always fixed as "LUT"
        "lutNumber": lut number or bond number if present else blank string it always start with AD and ends with an Alphabet and contains fifteen character,
        "lutDate": last date of lut block if present else blank string in DD-MM-YYYY for example "2025-08-27T00:00:00.000Z" in this format,
        "areDetailsToBeFilled": this is always fixed as "N",
        "areNumber": this is fixed as null,
        "areDate": this is fixed as null,
        "range": this is fixed as null,
        "division": this is fixed as null,
        "address": this is fixed as null,
        "commissionerate": this is fixed as null,
        "dutyAmountAsPerAre": this is fixed as null,
        "availingFacilityOfCenvatCreditUnderCenvatCreditRules": this is fixed as null,
        "availingFacilityUnderNotification41": this is fixed as null,
        "availingFacilityUnderNotification43": this is fixed as null,
        "generalRemarks": this is always blank as ""
    }},
Note: this is the detail of sender/vendor/owner of invoice and details. 
STRICTLY FOLLOW GIVEN STRUCTURE
"""

def build_prompt_invoice(raw_text):
    return fr"""
Extract structured JSON data from the following invoice text which is extracted from image passed of invoice

--- START ---
{raw_text}
--- END ---


   "invoiceDetailsRequest": [
        {{
            "invoiceNumber": Invoice Number of the invoice.  and if special character like / are there then replce it with -.IF invoice number followed by date or have year like 25-26/ in starting then ommit date like S00672/09-09-2025 or 25-26/S00672 then take the invoice number as S00672 only,
            "invoiceValue": Invoice value is given as Invoice Total or total if not then blank. Do not seperate the digit by comma(,),
            "invoiceValueInr": This is same as invoiceValue. Do not seperate the digit by comma(,), 
            "invoiceDate": invoice date in ISO 8601 format if not then blank string for example "2025-08-21T00:00:00.000" in this format only,
            "natureOfTransaction": This is fixed value as "Sale",
            "natureOfSupply": This is fixed value as "Supply under LUT",
            "invoiceCurrency": This is fixed value as "INR",
            "exchangeRate": This is fixed value as "1",
            "igstAmount": This is fixed value as "0.00",
            "cessAmount": This is fixed value as "0.00",
            "invoiceFileIrn": This is always blank as "",
            "invoiceFileName":This is always blank as  "",
            "dutyAmountasPer": This is Fixed value as"0",
            "fobValue": This is always blank as "",
            "freight": This is always blank as "",
            "insurance": This is always blank as"",
            "commission": This is always blank as"",
            "discount": This is always blank as"",
            "otherDeduction": This is always blank as"",
            "incoterm": This is always blank as""
        }}
    ],
STRICTLY FOLLOW GIVEN STRUCTURE
"""

def build_prompt_products(raw_text):
    return fr"""
Extract structured JSON data from the following invoice text which is extracted from image passed of invoice

--- START ---
{raw_text}
--- END ---

    "itemDetailsRequest": [
        {{
            "invoiceNumber": Invoice Number of the invoice.  and if special character like / are there then replce it with -.IF invoice number followed by date or have year like 25-26/ in starting then ommit date like S00672/09-09-2025 or 25-26/S00672 then take the invoice number as S00672 only ,
            "invoiceDate": invoice date in ISO 8601 time format if not then blank string for example "2025-08-21T00:00:00.000" in this format only, 
            "itemDescription1": item_description no special characters are allowed like "()","/" ,"&" if special character are there then do not take special character words and replace & with -, 
            "itemDescription2": this is always blank as "",
            "itemDescription3": this is always blank as "",
            "itemAccessories": this is always blank as "",
            "hsCode": hsn or hsn like product code if preset  else blank string, 
            "quantity": quantity of products if present else blank string. If Qty and Wt both column are there then take quantity from Wt column, 
            "unitOfMeasurement":Given under PER or UOM Column. If the PER OR UOM Column value is "Cts" then replace with "CTM" and If the PER OR UOM Column value is "PKT" then replace it with "PAC".Strictly follow this. Else if itemDescription1 contains "cam pisce" set "GMS", otherwise set "CTM". Do not combine Description and UOM column value strictly follow this rule,
            "unitPrice": unit price if present else blank string,  
            "productValue": total product value if present else 0.00,
            "presentMarketValue": this is always fixed as "0",
            "rebateClaimed": this is always blank as"",
            "itemType": "if item description OR description of goods contains anywhere like cam pisce then Consumables and if item description OR description of goods contains anywhere like Lab Grown Diamond, Cut & Polished Diamonds,Precious Stone,Pearl,Semi Precious Stone, CZ Diamond then Raw Material else Others, 
            "taxableValue":  total product value if present else 0.00,
            "igstNotificationNumber": this is always fixed "001/2017",
            "igstNotificationSerialNumber": if description1 is contains like "Semi Precious Stone" then "VI2" , contains like "Lab Grown Diamonds" then "VII1" ,contains like "Cut & Polished Diamonds" then "VII1",contains like "Precious Stone" then"VI2", contains like "Pearl" then"VI2", contains like "CZ Diamond" then "VII1", contains like "Cam pisce" then "III111".
            "isGstExempt": this is always fixed as "Y",
            "igstRate":this is always fixed as 0,
            "igstAmount": this is always fixed as "0.00",
            "cessNotificationNumber": This is always blank as "",
            "cessNotificationSerialNumber": This is always blank as "",
            "cessRate": This is always fixed as 0,
            "cessAmount": This is always fixed as "0.00"
        }}
    ]
Note : this is the details of product listed in invoice. provide json for each product then list of jsons under the key itemDetailsRequest
STRICTLY FOLLOW GIVEN STRUCTURE
"""


# ========== JSON HELPERS ==========
def clean_llm_fragment(s: str) -> str:
    if not s:
        return ""
    s = s.strip()
    if s.startswith("```"):
        parts = s.split("```")
        if len(parts) >= 2:
            inner = parts[1]
            if inner.lower().startswith("json"):
                inner = inner.split("\n", 1)[1] if "\n" in inner else ""
            s = inner
    return s.strip().rstrip(",")

def extract_json_like(text: str) -> str:
    text = (text or "").strip()
    obj_matches = list(re.finditer(r"\{[\s\S]*\}", text))
    arr_matches = list(re.finditer(r"\[[\s\S]*\]", text))
    if obj_matches:
        m = obj_matches[0]
        return text[m.start():m.end()]
    if arr_matches:
        m = arr_matches[0]
        return text[m.start():m.end()]
    return text

def coerce_fragment_to_value(fragment: str, expected_key: str):
    frag = clean_llm_fragment(fragment)
    frag = extract_json_like(frag)
    try:
        parsed = json.loads(frag)
        if isinstance(parsed, dict):
            if expected_key in parsed:
                return parsed[expected_key]
            return parsed
        if isinstance(parsed, list):
            return parsed
    except Exception:
        pass
    if frag.strip().startswith(f'"{expected_key}"'):
        try:
            wrapped = "{" + frag + "}"
            parsed = json.loads(wrapped)
            return parsed.get(expected_key, {})
        except Exception:
            pass
    inner = extract_json_like(frag)
    try:
        return json.loads(inner)
    except Exception:
        if expected_key in ("invoiceDetailsRequest", "itemDetailsRequest"):
            return []
        return {}

def pretty_json_text(obj_or_text) -> str:
    if isinstance(obj_or_text, (dict, list)):
        return json.dumps(obj_or_text, indent=2, ensure_ascii=False)
    try:
        return json.dumps(json.loads(obj_or_text), indent=2, ensure_ascii=False)
    except Exception:
        return str(obj_or_text)






def getDetails(OPENROUTER_API_KEY):
        # ========== SESSION STATE ==========
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = False
    if "json_text" not in st.session_state:
        st.session_state.json_text = ""
    if "original_json_text" not in st.session_state:
        st.session_state.original_json_text = ""
    if "json_error" not in st.session_state:
        st.session_state.json_error = ""

    # ========== UI ==========
    st.markdown("""
    <style>
    .fixed-header {
        position: fixed;
        top: 22px;
        left: 0;
        width: 100%;
        background-color: white;
        z-index: 9999;
        padding: 10px 0;
        text-align: center;
        border-bottom: 1px solid #e5e7eb;
    }
    .main-content {
        margin-top: 120px;
    }
    .json-preview-container {
        height: 80vh;
        border: 1px solid #ddd;
        border-radius: 8px;
        overflow-y: auto;
        padding: 10px;
        background-color: #f8f9fa;
        font-family: 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.4;
    }
    .json-preview-container pre {
        margin: 0;
        padding: 0;
        background: transparent;
        border: none;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    </style>

    <div class="fixed-header">
    <h1 style="margin-bottom:0">NEVE JEWELS GROUP</h1>
    <p style="color:#6b7280; margin-top:-10px">Invoice → JSON</p>
    </div>
    <div class="main-content">
    """, unsafe_allow_html=True)


    uploaded = st.file_uploader("Upload an Invoice PDF", type=["pdf"])

    if uploaded is None:
        st.info("Upload a PDF to begin.")
    else:
        file_bytes = uploaded.read()
        col_left, col_right = st.columns(2, gap="large")

        with col_left:
            st.subheader("PDF Preview")
            try:
                b64 = to_b64_pdf(file_bytes)
                st.markdown(
                    f"""
                    <div style="height:80vh; border:1px solid #ddd; border-radius:8px; overflow:hidden">
                    <embed src="data:application/pdf;base64,{b64}#toolbar=0&navpanes=0&scrollbar=0&zoom=page-width"
                            type="application/pdf" width="100%" height="100%">
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            except Exception:
                st.caption("Embedded PDF preview not supported.")

        with col_right:
            st.subheader("JSON Output")
            if "last_filename" not in st.session_state or st.session_state.last_filename != uploaded.name:
                st.session_state.last_filename = uploaded.name
                with st.spinner("Generating JSON…"):
                    raw_text = file_to_text(file_bytes)
                    client = get_openrouter_client(get_openrouter_client)
                    vendor_str = generate_json_section(build_prompt_vendor(raw_text), client)
                    invoice_str = generate_json_section(build_prompt_invoice(raw_text), client)
                    item_str = generate_json_section(build_prompt_products(raw_text), client)
                    general = coerce_fragment_to_value(vendor_str, "generalDetailsRequest")
                    invoices = coerce_fragment_to_value(invoice_str, "invoiceDetailsRequest")
                    items = coerce_fragment_to_value(item_str, "itemDetailsRequest")
                    final_obj = {
                        "generalDetailsRequest": general if isinstance(general, dict) else {},
                        "invoiceDetailsRequest": invoices if isinstance(invoices, list) else [],
                        "itemDetailsRequest": items if isinstance(items, list) else [],
                    }
                pretty = pretty_json_text(final_obj)
                st.session_state.original_json_text = pretty
                st.session_state.json_text = pretty
                st.session_state.json_error = ""
                st.session_state.edit_mode = False

            json_filename = uploaded.name.rsplit(".", 1)[0] + ".json"

            if not st.session_state.edit_mode:
                try:
                    parsed = json.loads(st.session_state.json_text)
                    pretty_json = json.dumps(parsed, indent=4, ensure_ascii=False)
                    import html
                    escaped_json = html.escape(pretty_json)
                    st.markdown(
                        f"""
                        <div class="json-preview-container">
                            <pre><code>{escaped_json}</code></pre>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                except Exception:
                    import html
                    escaped_text = html.escape(st.session_state.json_text)
                    st.markdown(
                        f"""
                        <div class="json-preview-container">
                            <pre><code>{escaped_text}</code></pre>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                if st.button("Edit", use_container_width=True):
                    st.session_state.edit_mode = True
            else:
                st.session_state.json_text = st.text_area(
                    "Edit JSON",
                    value=st.session_state.json_text,
                    height=650
                )
                col_a, col_b, col_c, col_d = st.columns([1, 1, 1, 1])
                with col_a:
                    if st.button("Validate & Save", use_container_width=True):
                        try:
                            parsed = json.loads(st.session_state.json_text)
                            st.session_state.json_text = pretty_json_text(parsed)
                            st.session_state.json_error = ""
                            st.success("JSON is valid and saved (pretty-formatted).")
                        except Exception as e:
                            st.session_state.json_error = str(e)
                            st.error(f"Invalid JSON: {st.session_state.json_error}")
                with col_b:
                    if st.button("Pretty Format", use_container_width=True):
                        try:
                            st.session_state.json_text = pretty_json_text(st.session_state.json_text)
                            st.session_state.json_error = ""
                        except Exception as e:
                            st.session_state.json_error = str(e)
                            st.error(f"Cannot format: {e}")
                with col_c:
                    if st.button("Revert to Original", use_container_width=True):
                        st.session_state.json_text = st.session_state.original_json_text
                        st.session_state.json_error = ""
                        st.info("Reverted to original JSON (pretty).")
                with col_d:
                    if st.button("Exit Edit Mode", use_container_width=True):
                        st.session_state.edit_mode = False
                if st.session_state.json_error:
                    st.code(st.session_state.json_error, language="text")

            pretty_for_download = pretty_json_text(st.session_state.json_text)
            st.download_button(
                "Download JSON",
                data=pretty_for_download.encode("utf-8"),
                file_name=json_filename,
                mime="application/json",
                use_container_width=True
            )
