import streamlit as st
import pandas as pd

# Konfigurasi Halaman Web
st.set_page_config(page_title="Kuis Pemrograman Jaringan V2", page_icon="🖥️", layout="centered")

# Link Export CSV dari Google Sheets Bank Soal V2 (47 Soal)
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1ms5wHVYz8vLuOoBZQdSMr449pMw-wIYIqB7slcT4P3A/export?format=csv"

# Fungsi untuk mengambil data (di-cache agar web tidak lambat)
@st.cache_data(ttl=60)
def ambil_data_soal():
    return pd.read_csv(SHEET_CSV_URL)

# Setup state untuk mengingat posisi kuis pengguna dan riwayat jawaban
if 'soal_aktif' not in st.session_state:
    st.session_state.soal_aktif = 0
    st.session_state.skor = 0
    st.session_state.selesai = False
    st.session_state.riwayat_jawaban = []

def reset_kuis():
    st.session_state.soal_aktif = 0
    st.session_state.skor = 0
    st.session_state.selesai = False
    st.session_state.riwayat_jawaban = []

# --- TAMPILAN WEB ---
st.title("🖥️ Kuis Pemrograman Jaringan (Version 2)")
st.write("Uji pengetahuan Anda dengan 47 soal komprehensif mengenai arsitektur jaringan, protokol transport, dan socket programming.")
st.markdown("---")

try:
    df = ambil_data_soal()
except Exception as e:
    st.error("Gagal terhubung ke Database Soal. Pastikan Google Sheets bisa diakses publik.")
    st.stop()

# Jika kuis belum selesai
if not st.session_state.selesai:
    # Ambil baris soal saat ini
    idx = st.session_state.soal_aktif
    row = df.iloc[idx]

    st.subheader(f"Soal No. {row['No']} dari {len(df)}")
    st.write(row['Soal'])

    # Pemetaan opsi untuk mempermudah pengambilan teks lengkap nanti
    pilihan = [str(row['Pilihan_A']), str(row['Pilihan_B']), str(row['Pilihan_C']), str(row['Pilihan_D'])]
    opsi_dict = {
        "A": str(row['Pilihan_A']),
        "B": str(row['Pilihan_B']),
        "C": str(row['Pilihan_C']),
        "D": str(row['Pilihan_D'])
    }
    
    jawaban_user = st.radio("Pilih jawaban Anda:", pilihan, index=None, key=f"radio_{idx}")

    # Ubah teks tombol di soal terakhir
    teks_tombol = "Kirim Semua Jawaban" if st.session_state.soal_aktif == len(df) - 1 else "Soal Selanjutnya ➡️"

    if st.button(teks_tombol):
        if jawaban_user:
            # Ambil huruf depan dari jawaban (A, B, C, atau D)
            huruf_jawaban = jawaban_user.split(".")[0].strip().upper()
            kunci_jawaban = str(row['Jawaban']).strip().upper()
            
            # Cek status benar/salah
            is_correct = (huruf_jawaban == kunci_jawaban)
            if is_correct:
                st.session_state.skor += 1
                
            # Simpan riwayat jawaban untuk ditampilkan di akhir
            st.session_state.riwayat_jawaban.append({
                "no": row['No'],
                "soal": row['Soal'],
                "jawaban_user": jawaban_user,
                "jawaban_benar": opsi_dict.get(kunci_jawaban, "Kunci tidak valid"),
                "status": is_correct
            })

            # Pindah soal atau selesaikan kuis
            if st.session_state.soal_aktif < len(df) - 1:
                st.session_state.soal_aktif += 1
            else:
                st.session_state.selesai = True
            
            # Refresh halaman
            st.rerun()
        else:
            st.warning("Silakan pilih jawaban terlebih dahulu sebelum melanjutkan!")

# Jika kuis selesai (Halaman Evaluasi)
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
        
    st.markdown("---")
    st.subheader("📋 Evaluasi Jawaban Anda")
    
    # Menampilkan daftar semua soal dengan format mirip e-learning/LMS
    for item in st.session_state.riwayat_jawaban:
        # Menggunakan container dengan border agar tampilannya rapi seperti kotak soal
        with st.container(border=True):
            st.markdown(f"**Question {item['no']}**")
            
            if item['status']:
                st.caption("✔️ :green[Correct]")
                st.write(f"**Soal:** {item['soal']}")
                st.write(f"**Jawaban:** {item['jawaban_user']}")
            else:
                st.caption("❌ :red[Incorrect]")
                st.write(f"**Soal:** {item['soal']}")
                st.write(f"**Jawaban Anda (Salah):** {item['jawaban_user']}")
                st.write(f"**Jawaban Benar:** {item['jawaban_benar']}")
                
    st.markdown("---")
    if st.button("🔄 Ulangi Kuis"):
        reset_kuis()
        st.rerun()