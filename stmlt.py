import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import pandas as pd
from io import BytesIO
import zipfile
from fpdf import FPDF
import time

st.title("QR CODE GENERATOR - PL")
st.write("")

st.subheader("Upload Excel / CSV File")
uploaded_file = st.file_uploader("File harus memiliki kolom Item Code, Item Desc, Lot No", type=["xlsx", "xls", "csv"])

st.markdown(
    """
    <style>
    .stButton>button {
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.header("Masukkan Data Manual")
item_code = st.sidebar.text_input("Item Code")
item_desc = st.sidebar.text_input("Item Description")
lot_no = st.sidebar.text_input("Lot Number")

st.sidebar.write("")

if st.sidebar.button("Generate QR Code Manual"):
    if item_code and item_desc and lot_no:
        text = f"{item_code}\t{item_desc}\t{lot_no}"
        text_below = f"{item_desc}\t{lot_no}".replace("\t", ", ")
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=15,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype("arial.ttf", 25)
        text_bbox = draw.textbbox((0, 0), text_below, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        extra_width = max(0, text_width - img.width + 20)
        new_img_width = img.width + extra_width
        new_img = Image.new('RGB', (new_img_width, img.height + text_height + 30), color=(255, 255, 255))
        new_img.paste(img, ((new_img_width - img.width) // 2, 5))
        draw = ImageDraw.Draw(new_img)
        draw.text(((new_img_width - text_width) // 2, img.height+10), text_below, font=font, fill="black")
        
        img_path = "temp_qr.png"
        new_img.save(img_path)
        
        pdf = FPDF(unit="cm", format=(16, 7))
        pdf.add_page()
        pdf.set_font("Arial", size=17)
        pdf.image(img_path, x=1, y=0.1, w=6)
        pdf.set_xy(8.1, 2.7)
        pdf.cell(10, 1.5, "Quantity: __________", ln=True)
        
        pdf_filename = f"{item_desc}_{lot_no}.pdf"
        pdf.output(pdf_filename)
        os.remove(img_path)
        
        with open(pdf_filename, "rb") as file:
            st.download_button(
                label="Download QR Code PDF",
                data=file,
                file_name=pdf_filename,
                mime="application/pdf"
            )
        os.remove(pdf_filename)
    else:
        st.sidebar.error("Harap isi semua field sebelum mengenerate QR Code")



if uploaded_file:
    df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith(('xlsx', 'xls')) else pd.read_csv(uploaded_file)
    required_columns = {"Item Code", "Item Desc", "Lot No"}
    
    if not required_columns.issubset(df.columns):
        st.error("File yang diunggah harus memiliki kolom: Item Code, Item Desc, dan Lot No")
    else:
        if st.button("Generate QR Code dari File"):
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                st.write("")
                loading = st.empty()
                loading.markdown(
                    """
                    <div style="text-align: center;">
                        <p>Generate QR Code Sedang dalam proses...</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                progress_bar = st.progress(0)
                total_rows = len(df)
                
                for i, row in df.iterrows():
                    text = f"{row['Item Code']}\t{row['Item Desc']}\t{row['Lot No']}"
                    text_below = f"{row['Item Desc']}\t{row['Lot No']}".replace("\t", ", ")
                    
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=15,
                        border=4,
                    )
                    qr.add_data(text)
                    qr.make(fit=True)
                    img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
                    
                    draw = ImageDraw.Draw(img)
                    font = ImageFont.truetype("arial.ttf", 25)
                    text_bbox = draw.textbbox((0, 0), text_below, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1]
                    
                    extra_width = max(0, text_width - img.width + 20)
                    new_img_width = img.width + extra_width
                    new_img = Image.new('RGB', (new_img_width, img.height + text_height + 30), color=(255, 255, 255))
                    new_img.paste(img, ((new_img_width - img.width) // 2, 5))
                    draw = ImageDraw.Draw(new_img)
                    draw.text(((new_img_width - text_width) // 2, img.height+10), text_below, font=font, fill="black")
                    
                    img_path = "temp_qr.png"
                    new_img.save(img_path)
                    
                    pdf = FPDF(unit="cm", format=(16, 7))
                    pdf.add_page()
                    pdf.set_font("Arial", size=17)
                    pdf.image(img_path, x=1, y=0.1, w=6)
                    pdf.set_xy(8.1, 2.7)
                    pdf.cell(10, 1.5, "Quantity: __________", ln=True)
                    
                    pdf_filename = f"{i}. {row['Item Desc']}_{row['Lot No']}.pdf"
                    pdf.output(pdf_filename)
                    os.remove(img_path)
                    
                    with open(pdf_filename, "rb") as file:
                        zip_file.writestr(pdf_filename, file.read())
                    os.remove(pdf_filename)
                    
                    progress_bar.progress((i + 1) / total_rows)
            
            loading.empty()
            loading.write("Proses sudah selesai")

            st.download_button(
                label="Download ZIP with QR Code PDFs",
                data=zip_buffer.getvalue(),
                file_name="qr_codes.zip",
                mime="application/zip"
            )
