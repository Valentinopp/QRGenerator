import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageFont
import os
import pandas as pd
from io import BytesIO
import zipfile
import re

# Fungsi untuk membersihkan nama file
def clean_filename(filename):
    # Menghapus karakter yang tidak valid
    cleaned = re.sub(r'[\\/*?:"<>|]', "_", filename)
    return cleaned

# Judul aplikasi
st.title("QR CODE GENERATOR - PCI")

# Opsi upload file Excel
st.sidebar.header("Upload Excel/CSV File")
uploaded_file = st.sidebar.file_uploader("Upload Disini", type=["xlsx", "xls", "csv"])

# Input data manual dari pengguna
st.sidebar.header("Masukkan Data Manual")
item_code = st.sidebar.text_input("Item Code", "F1P.04000406.L")
item_desc = st.sidebar.text_input("Item Description", "GY_CASA_A")
lot_no = st.sidebar.text_input("Lot Number", "L SALSA GREY 40.00X40.00 (A)")

# Tombol untuk generate QR code manual
if st.sidebar.button("Generate QR Code Manual"):
    # Membuat teks untuk QR code
    text = f"{item_code}\t{item_desc}\t{lot_no}"

    text_below = f"{item_desc}\t{lot_no}".replace("\t", ", ")  # Mengganti tab dengan koma untuk teks di bawah QR code

    # Membuat QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Mengkonversi gambar QR code ke mode RGB
    img = img.convert('RGB')

    # Menambahkan teks di bawah QR code
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()  # Anda bisa mengganti ini dengan font yang diinginkan

    # Menghitung ukuran teks menggunakan textbbox
    text_bbox = draw.textbbox((0, 0), text_below, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1] - 15

    # Menentukan posisi teks
    img_width, img_height = img.size
    x = (img_width - text_width) // 2
    y = img_height - 20  # Jarak antara QR code dan teks

    # Membuat gambar baru dengan ruang untuk teks
    new_img = Image.new('RGB', (img_width, img_height + text_height + 20), color=(255, 255, 255))
    new_img.paste(img, (0, 0))

    # Menambahkan teks ke gambar baru
    draw = ImageDraw.Draw(new_img)
    draw.text((x, y), text_below, font=font, fill="black")

    # Membersihkan nama file
    clean_item_code = clean_filename(item_code)
    save_path = f"qr_code_{clean_item_code}.png"
    new_img.save(save_path)

    # Menampilkan gambar QR code di aplikasi Streamlit
    st.image(save_path, caption="Generated QR Code", use_column_width=True)

    # Menyediakan tombol untuk mengunduh gambar
    with open(save_path, "rb") as file:
        btn = st.download_button(
            label="Download QR Code",
            data=file,
            file_name=save_path,
            mime="image/png"
        )

    # Menghapus file sementara setelah diunduh
    os.remove(save_path)

# Jika file Excel/CSV diupload
if uploaded_file is not None:
    # Membaca file Excel atau CSV
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Memastikan kolom yang diperlukan ada
    required_columns = ["Item Code", "Item Desc", "Lot No"]
    if all(column in df.columns for column in required_columns):
        st.success("File berhasil diupload!")
        st.write("Data dari File:")
        st.dataframe(df)

        # Tombol untuk generate QR code dari file
        if st.button("Generate QR Code dari File"):
            # Membuat buffer untuk file ZIP
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                loading = st.empty()
                loading.write("Generate QR Code Sedang dalam proses...")
                # Menambahkan loading bar
                progress_bar = st.progress(0)
                total_rows = len(df)

                for i, row in df.iterrows():
                    # Membuat teks untuk QR code
                    text = f"{row['Item Code']}\t{row['Item Desc']}\t{row['Lot No']}"
                    text_below = f"{row['Item Desc']}\t{row['Lot No']}".replace("\t", ", ")  # Mengganti tab dengan koma untuk teks di bawah QR code

                    # Membuat QR code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_L,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(text)
                    qr.make(fit=True)

                    img = qr.make_image(fill_color="black", back_color="white")

                    # Mengkonversi gambar QR code ke mode RGB
                    img = img.convert('RGB')

                    # Menambahkan teks di bawah QR code
                    draw = ImageDraw.Draw(img)
                    font = ImageFont.load_default()  # Anda bisa mengganti ini dengan font yang diinginkan

                    # Menghitung ukuran teks menggunakan textbbox
                    text_bbox = draw.textbbox((0, 0), text_below, font=font)
                    text_width = text_bbox[2] - text_bbox[0]
                    text_height = text_bbox[3] - text_bbox[1] - 15

                    # Menentukan posisi teks
                    img_width, img_height = img.size
                    x = (img_width - text_width) // 2
                    y = img_height - 20  # Jarak antara QR code dan teks

                    # Membuat gambar baru dengan ruang untuk teks
                    new_img = Image.new('RGB', (img_width, img_height + text_height + 20), color=(255, 255, 255))
                    new_img.paste(img, (0, 0))

                    # Menambahkan teks ke gambar baru
                    draw = ImageDraw.Draw(new_img)
                    draw.text((x, y), text_below, font=font, fill="black")

                    # Membersihkan nama file
                    clean_item_code = clean_filename(row['Item Code'])
                    save_path = f"qr_code_{clean_item_code}_{i+1}.png"

                    # Menyimpan gambar ke buffer
                    img_bytes = BytesIO()
                    new_img.save(img_bytes, format="PNG")
                    img_bytes.seek(0)

                    # Menambahkan file ke ZIP
                    zip_file.writestr(save_path, img_bytes.getvalue())

                    # Memperbarui loading bar
                    progress = (i + 1) / total_rows
                    progress_bar.progress(progress)
            
            loading.empty()
            loading.write("Proses sudah selesai")

            # Menyediakan tombol untuk mengunduh semua QR code dalam bentuk zip
            zip_buffer.seek(0)
            st.download_button(
                label="Download Semua QR Code (ZIP)",
                data=zip_buffer,
                file_name="qr_codes.zip",
                mime="application/zip"
            )

    else:
        st.sidebar.error("File harus memiliki kolom: Item Code, Item Desc, Lot No")