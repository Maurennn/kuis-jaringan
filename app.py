import streamlit as st
import pandas as pd
import time

# Konfigurasi Halaman Web
st.set_page_config(page_title="Kuis Pemrograman Jaringan", page_icon="🖥️", layout="centered")

# Link Export CSV dari Google Sheets Bank Soal V2 (47 Soal)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1ms5wHVYz8vLuOoBZQdSMr449pMw-wIYIqB7slcT4P3A/export?format=csv"

# Fungsi untuk mengambil data (di-cache agar web tidak lambat)
@st.cache_data(ttl=60)
def ambil_data_soal():
    return pd.read_csv(SHEET_CSV_URL)

# Setup state untuk mengingat posisi kuis pengguna
if 'soal_aktif' not in st.session_state:
    st.session_state.soal_aktif = 0
    st.session_state.skor = 0
    st.session_state.selesai = False
    st.session_state.pesan_evaluasi = ""

def reset_kuis():
    st.session_state.soal_aktif = 0
    st.session_state.skor = 0
    st.session_state.selesai = False
    st.session_state.pesan_evaluasi = ""

# --- TAMPILAN WEB ---
st.title("🖥️ Kuis Pemrograman Jaringan")
st.write("Uji pengetahuan Anda dengan 47 soal komprehensif mengenai arsitektur jaringan, protokol transport, dan socket programming.")
st.markdown("---")

try:
    df = ambil_data_soal()
except Exception as e:
    st.error("Gagal terhubung ke Database Soal. Pastikan Google Sheets bisa diakses publik.")
    st.stop()

# Jika kuis belum selesai
if not st.session_state.selesai:
    # Menampilkan pesan benar/salah dari soal sebelumnya
    if st.session_state.pesan_evaluasi:
        if "Benar" in st.session_state.pesan_evaluasi:
            st.success(st.session_state.pesan_evaluasi)
        else:
            st.error(st.session_state.pesan_evaluasi)
            
    # Ambil baris soal saat ini
    idx = st.session_state.soal_aktif
    row = df.iloc[idx]

    st.subheader(f"Soal No. {row['No']} dari {len(df)}")
    st.write(row['Soal'])

    # Menampilkan Pilihan Ganda
    pilihan = [row['Pilihan_A'], row['Pilihan_B'], row['Pilihan_C'], row['Pilihan_D']]
    jawaban_user = st.radio("Pilih jawaban Anda:", pilihan, index=None, key=f"radio_{idx}")

    if st.button("Kirim Jawaban"):
        if jawaban_user:
            # Ambil huruf depan dari jawaban (A, B, C, atau D)
            huruf_jawaban = jawaban_user.split(".")[0].strip().upper()
            kunci_jawaban = str(row['Jawaban']).strip().upper()

            # Evaluasi
            if huruf_jawaban == kunci_jawaban:
                st.session_state.pesan_evaluasi = "✅ Jawaban sebelumnya Benar!"
                st.session_state.skor += 1
            else:
                st.session_state.pesan_evaluasi = f"❌ Jawaban sebelumnya Salah! Kunci: {kunci_jawaban}"

            # Pindah soal atau selesai
            if st.session_state.soal_aktif < len(df) - 1:
                st.session_state.soal_aktif += 1
            else:
                st.session_state.selesai = True
                st.session_state.pesan_evaluasi = ""
            
            # Refresh halaman
            st.rerun()
        else:
            st.warning("Silakan pilih jawaban terlebih dahulu sebelum mengirim!")

# Jika kuis selesai
else:
    st.header("🎉 Kuis Telah Selesai!")
    
    total_soal = len(df)
    nilai_percent = (st.session_state.skor / total_soal) * 100
    
    col1, col2 = st.columns(2)
    col1.metric("Jawaban Benar", f"{st.session_state.skor} / {total_soal}")
    col2.metric("Nilai Akhir", f"{nilai_percent:.2f}%")
    
    if nilai_percent >= 80:
        st.success("Luar Biasa! Anda sangat memahami materi ini.")
    elif nilai_percent >= 60:
        st.info("Cukup baik, tapi masih perlu banyak mengulang materi.")
    else:
        st.error("Anda belum lulus. Silakan pelajari lagi materinya.")

    if st.button("🔄 Ulangi Kuis"):
        reset_kuis()
        st.rerun()