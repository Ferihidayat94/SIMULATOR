# APLIKASI UJIAN PESERTA & INSTRUKTUR
import streamlit as st
import pandas as pd
import os
import hashlib
from datetime import datetime, timedelta, date
from supabase import create_client, Client

# ================== Konfigurasi Halaman Streamlit ==================
st.set_page_config(page_title="Platform Ujian Instruktur & Peserta", layout="wide")

# ================== CSS Kustom (Diambil dari kode Anda) ==================
st.markdown(
    """
    <style>
        /* BARIS INI TETAP DIKOMENTARI KARENA MENYEBABKAN MASALAH IKON */
        /* @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'); */
        
        /* BARIS INI TETAP DIKOMENTARI KARENA MENYEBABKAN MASALAH IKON */
        /* html, body, [class*="st-"] { font-family: 'Inter', sans-serif; } */
        
        /* Background aplikasi */
        .stApp {
            background-color: #021021;
            background-image: radial-gradient(ellipse at bottom, rgba(52, 152, 219, 0.25) 0%, rgba(255,255,255,0) 50%),
                              linear-gradient(to top, #062b54, #021021);
            background-attachment: fixed;
            color: #ECF0F1;
        }
        .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 { color: #FFFFFF; }
        .stApp [data-testid="stHeading"] { color: #FFFFFF !important; }
        .stApp p { color: #ECF0F1 !important; }
        h1 { border-bottom: 2px solid #3498DB; padding-bottom: 10px; margin-bottom: 0.8rem; }
        [data-testid="stSidebar"] {
            background-color: rgba(2, 16, 33, 0.8);
            backdrop-filter: blur(5px);
            border-right: 1px solid rgba(52, 152, 219, 0.3);
        }
        .login-container [data-testid="stForm"], [data-testid="stForm"], [data-testid="stExpander"],
        [data-testid="stVerticalBlock"] [data-testid="stVerticalBlock"] [data-testid="stContainer"] {
            background-color: rgba(44, 62, 80, 0.6);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(52, 152, 219, 0.4);
            padding: 1.5rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        .login-title { color: #FFFFFF; text-align: center; border-bottom: none; font-size: 1.9rem; white-space: nowrap; }
        div[data-testid="stButton"] > button, div[data-testid="stDownloadButton"] > button, div[data-testid="stForm"] button {
            font-weight: 600; border-radius: 8px; border: 1px solid #3498DB !important;
            background-color: transparent !important; color: #FFFFFF !important;
            transition: all 0.3s ease-in-out; padding: 10px 24px; width: 100%;
        }
        div[data-testid="stButton"] > button:hover, div[data-testid="stDownloadButton"] > button:hover, div[data-testid="stForm"] button:hover {
            background-color: #3498DB !important; border-color: #3498DB !important;
        }
        .delete-button button { border-color: #E74C3C !important; }
        .delete-button button:hover { background-color: #C0392B !important; border-color: #C0392B !important; }
        
        /* Gaya input/select/textarea */
        div[data-baseweb="input"] > div, 
        div[data-baseweb="textarea"] > div, 
        div[data-baseweb="select"] > div {
            background-color: rgba(236, 240, 241, 0.4) !important; /* Warna dasar transparan */
            border-color: rgba(52, 152, 219, 0.4) !important;
            color: #FFFFFF !important;
            transition: all 0.2s ease-in-out; /* Transisi halus untuk semua properti yang berubah */
        }

        /* Efek HOVER */
        div[data-baseweb="input"] > div:hover,
        div[data-baseweb="textarea"] > div:hover,
        div[data-baseweb="select"] > div:hover {
            background-color: rgba(236, 240, 241, 0.55) !important; /* Sedikit lebih padat */
            border-color: rgba(52, 152, 219, 0.7) !important; /* Border lebih jelas */
        }

        /* Efek FOCUS (saat diklik/aktif) */
        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="textarea"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within {
            background-color: rgba(236, 240, 241, 0.7) !important; /* Lebih terang */
            border-color: #3498DB !important; /* Biru solid */
            box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.3) !important; /* Bayangan halus */
        }

        label, div[data-testid="stWidgetLabel"] label, .st-emotion-cache-1kyxreq e1i5pmia1 {
            color: #FFFFFF !important; font-weight: 500;
        }
        [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] .stMarkdown strong,
        [data-testid="stSidebar"] .stRadio > label span, [data-testid="stSidebar"] .stCaption {
            color: #FFFFFF !important; opacity: 1;
        }
        [data-testid="stSidebar"] .st-bo:has(input:checked) + label span { color: #5DADE2 !important; font-weight: 700 !important; }
        [data-testid="stSidebar"] .stButton > button { color: #EAECEE !important; border-color: #EAECEE !important; }
        [data-testid="stSidebar"] .stButton > button:hover { color: #FFFFFF !important; border-color: #E74C3C !important; background-color: #E74C3C !important; }
        [data-testid="stSidebarNavCollapseButton"] svg { fill: #FFFFFF !important; }
        [data-testid="stMetricLabel"] { color: #A9C5E1 !important; }
        [data-testid="stMetricValue"] { color: #FFFFFF !important; }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== Koneksi & Konfigurasi Global ==================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)
supabase = init_connection()

# ================== Fungsi-Fungsi Helper ==================
def verify_user_and_get_role(email, password):
    """
    Verifikasi user menggunakan Supabase Auth dan ambil rolenya dari metadata.
    """
    try:
        session = supabase.auth.sign_in_with_password({"email": email, "password": password})
        if session.user:
            # Ambil role dari user_metadata (Anda harus menambahkannya saat signup)
            # Jika tidak ada, coba ambil dari tabel 'users' kustom
            role = session.user.user_metadata.get('role', 'peserta')
            nama = session.user.user_metadata.get('nama_lengkap', email)

            # Jika role tidak ada di metadata, coba query tabel 'users'
            if 'role' not in session.user.user_metadata:
                user_data = supabase.table('users').select('role, nama_lengkap').eq('email', email).single().execute()
                if user_data.data:
                    role = user_data.data['role']
                    nama = user_data.data['nama_lengkap']

            return {"role": role, "email": session.user.email, "nama": nama}
    except Exception as e:
        print(f"Authentication error: {e}")
        return None
    return None

def logout():
    """Hapus semua session state dan rerun."""
    keys_to_keep = [] # Daftar session state yang ingin disimpan (jika ada)
    for key in list(st.session_state.keys()):
        if key not in keys_to_keep:
            del st.session_state[key]
    st.session_state.logged_in = False
    st.rerun()

# ================== Logika Utama Aplikasi ==================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.get("logged_in"):
    col1, col2, col3 = st.columns([1,1.5,1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h1 class="login-title">Platform Ujian Online</h1>', unsafe_allow_html=True)
        try: 
            # Anda bisa meletakkan logo di sini
            # st.image("logo.png", width=150) 
            pass
        except FileNotFoundError: pass
        
        with st.form("login_form"):
            st.markdown('<h3 style="color: #FFFFFF; text-align: center; border-bottom: none;">User Login</h3>', unsafe_allow_html=True)
            email = st.text_input("Email", placeholder="email@anda.com", key="login_email").lower()
            password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")
            
            if st.form_submit_button("Login"):
                with st.spinner("Memverifikasi..."):
                    user_data = verify_user_and_get_role(email, password)
                
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user_email = user_data['email']
                    st.session_state.user_role = user_data['role']
                    st.session_state.user_nama = user_data['nama']
                    st.session_state.last_activity = datetime.now()
                    st.rerun()
                else:
                    st.error("Email atau password salah.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ================== BAGIAN UTAMA APLIKASI SETELAH LOGIN ==================

# Timeout session
if 'last_activity' not in st.session_state or datetime.now() - st.session_state.last_activity > timedelta(minutes=60):
    logout()
st.session_state.last_activity = datetime.now()

# Ambil data user dari session state
user_role = st.session_state.get("user_role", "peserta")
user_email = st.session_state.get("user_email", "")
user_nama = st.session_state.get("user_nama", "")

with st.sidebar:
    st.title("Menu Navigasi")
    st.write(f"Selamat datang,")
    st.write(f"**{user_nama}**!")
    st.write(f"Peran: **{user_role.capitalize()}**")
    st.markdown("---")

    menu_options = []
    if user_role == 'instruktur':
        menu_options = ["Dashboard Nilai", "Kelola Soal", "Input Nilai Praktek"]
    elif user_role == 'peserta':
        menu_options = ["Mulai Ujian", "Lihat Nilai Saya"]

    menu = st.radio(
        "Pilih Halaman:", 
        menu_options, 
        label_visibility="collapsed"
    )
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    if st.button("Logout"): 
        logout()
    st.markdown("---")
    st.caption("Platform Ujian v1.0")

# ================== Logika Halaman ==================

# ----------------- Halaman Peserta -----------------
if menu == "Mulai Ujian":
    st.header("📝 Halaman Ujian")
    
    tipe_ujian = st.selectbox("Pilih Jenis Ujian:", ["Pre-Test", "Post-Test"])
    
    # Cek apakah user sudah pernah submit
    try:
        existing_submission = supabase.table('submissions').select('id').eq('user_email', user_email).eq('tipe_ujian', tipe_ujian).execute()
        if existing_submission.data:
            st.warning(f"Anda sudah pernah mengerjakan {tipe_ujian}. Nilai Anda telah dicatat.")
            st.stop()
    except Exception as e:
        st.error(f"Gagal memeriksa riwayat ujian: {e}")
        st.stop()

    if st.button(f"Mulai {tipe_ujian}"):
        st.session_state.start_quiz = True
        st.session_state.quiz_type = tipe_ujian

    if st.session_state.get('start_quiz', False) and st.session_state.quiz_type == tipe_ujian:
        try:
            # Ambil soal dari database
            response = supabase.table('questions').select('*').eq('tipe_ujian', tipe_ujian).execute()
            questions = response.data
            
            if not questions:
                st.error("Belum ada soal untuk ujian ini. Hubungi instruktur Anda.")
                st.stop()

            with st.form("quiz_form"):
                st.subheader(f"Soal {tipe_ujian}")
                answers = {}
                for i, q in enumerate(questions):
                    st.markdown(f"**{i+1}. {q['soal_text']}**")
                    options = {
                        'A': q['opsi_a'], 
                        'B': q['opsi_b'], 
                        'C': q['opsi_c'], 
                        'D': q['opsi_d']
                    }
                    answers[q['id']] = st.radio(
                        "Pilih jawaban:", 
                        options.keys(), 
                        format_func=lambda k: f"{k}. {options[k]}",
                        key=f"q_{q['id']}"
                    )
                
                submitted = st.form_submit_button("Kumpulkan Jawaban")
                if submitted:
                    with st.spinner("Memeriksa jawaban..."):
                        score = 0
                        total_questions = len(questions)
                        for q in questions:
                            if answers[q['id']] == q['kunci_jawaban']:
                                score += 1
                        
                        final_score = (score / total_questions) * 100
                        
                        # Simpan nilai ke database
                        try:
                            supabase.table('submissions').insert({
                                'user_email': user_email,
                                'tipe_ujian': tipe_ujian,
                                'nilai': final_score,
                                'submitted_at': datetime.now().isoformat()
                            }).execute()
                            
                            st.success(f"Ujian Selesai! Nilai Anda: {final_score:.2f}")
                            st.balloons()
                            st.session_state.start_quiz = False # Reset status
                        except Exception as e:
                            st.error(f"Gagal menyimpan nilai: {e}")

        except Exception as e:
            st.error(f"Gagal memuat soal: {e}")

elif menu == "Lihat Nilai Saya":
    st.header("🏆 Nilai Saya")
    
    try:
        # Ambil nilai Pre-Test dan Post-Test
        response_subs = supabase.table('submissions').select('tipe_ujian, nilai').eq('user_email', user_email).execute()
        df_subs = pd.DataFrame(response_subs.data)
        
        nilai_pre = df_subs[df_subs['tipe_ujian'] == 'Pre-Test']['nilai'].max() if not df_subs.empty else 0
        nilai_post = df_subs[df_subs['tipe_ujian'] == 'Post-Test']['nilai'].max() if not df_subs.empty else 0
        
        # Ambil nilai Praktek
        response_prac = supabase.table('practical_scores').select('nilai_praktek').eq('user_email', user_email).execute()
        nilai_praktek = response_prac.data[0]['nilai_praktek'] if response_prac.data else 0

        # Hitung Nilai Akumulasi
        # Rumus: (Nilai Post-Test + Nilai Praktek) / 2
        # (Anda bisa ganti rumusnya sesuai kebutuhan)
        if nilai_post > 0 and nilai_praktek > 0:
            nilai_akumulasi = (nilai_post + nilai_praktek) / 2
        else:
            nilai_akumulasi = 0
            
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Nilai Pre-Test", f"{nilai_pre:.2f}" if nilai_pre else "N/A")
        col2.metric("Nilai Post-Test", f"{nilai_post:.2f}" if nilai_post else "N/A")
        col3.metric("Nilai Praktek", f"{nilai_praktek:.2f}" if nilai_praktek else "N/A")
        col4.metric("Nilai Akumulasi Akhir", f"{nilai_akumulasi:.2f}", "⭐")

    except Exception as e:
        st.error(f"Gagal mengambil data nilai: {e}")

# ----------------- Halaman Instruktur -----------------
elif menu == "Dashboard Nilai":
    st.header("📊 Dashboard Nilai Peserta")

    try:
        # Ambil semua data
        all_subs = pd.DataFrame(supabase.table('submissions').select('*').execute().data)
        all_prac = pd.DataFrame(supabase.table('practical_scores').select('*').execute().data)
        all_users = pd.DataFrame(supabase.table('users').select('email, nama_lengkap').eq('role', 'peserta').execute().data)
        all_users.rename(columns={'email': 'user_email'}, inplace=True)

        if all_users.empty:
            st.warning("Belum ada data peserta terdaftar.")
            st.stop()

        # Proses data
        # 1. Pivot data submissions
        df_pivot = pd.DataFrame()
        if not all_subs.empty:
            df_pivot = all_subs.pivot_table(index='user_email', columns='tipe_ujian', values='nilai', aggfunc='max').reset_index()

        # 2. Gabungkan dengan data practical
        if not all_prac.empty:
            df_prac = all_prac[['user_email', 'nilai_praktek']]
            if not df_pivot.empty:
                df_final = pd.merge(df_pivot, df_prac, on='user_email', how='outer')
            else:
                df_final = df_prac
        else:
            df_final = df_pivot
            if not df_final.empty:
                df_final['nilai_praktek'] = pd.NA

        # 3. Gabungkan dengan nama user
        df_final = pd.merge(all_users, df_final, on='user_email', how='left')

        # Isi NaN dengan 0
        cols_to_fill = ['Pre-Test', 'Post-Test', 'nilai_praktek']
        for col in cols_to_fill:
            if col not in df_final.columns:
                df_final[col] = 0
        df_final = df_final.fillna(0)

        # 4. Hitung Akumulasi
        df_final['Nilai Akumulasi'] = (df_final['Post-Test'] + df_final['nilai_praktek']) / 2
        df_final.rename(columns={'nama_lengkap': 'Nama Peserta', 'nilai_praktek': 'Nilai Praktek'}, inplace=True)

        st.dataframe(df_final[['Nama Peserta', 'Pre-Test', 'Post-Test', 'Nilai Praktek', 'Nilai Akumulasi']], use_container_width=True)
    
    except Exception as e:
        st.error(f"Gagal memuat dashboard: {e}")


elif menu == "Kelola Soal":
    st.header("📚 Kelola Soal Ujian")

    with st.expander("➕ Tambah Soal Baru"):
        with st.form("add_question_form", clear_on_submit=True):
            st.subheader("Input Detail Soal")
            
            q_tipe = st.selectbox("Jenis Ujian", ["Pre-Test", "Post-Test"])
            q_text = st.text_area("Teks Pertanyaan")
            
            col1, col2 = st.columns(2)
            with col1:
                q_opsi_a = st.text_input("Opsi A")
                q_opsi_b = st.text_input("Opsi B")
            with col2:
                q_opsi_c = st.text_input("Opsi C")
                q_opsi_d = st.text_input("Opsi D")
            
            q_kunci = st.selectbox("Kunci Jawaban", ["A", "B", "C", "D"])
            
            if st.form_submit_button("Simpan Soal"):
                if not all([q_tipe, q_text, q_opsi_a, q_opsi_b, q_opsi_c, q_opsi_d, q_kunci]):
                    st.warning("Mohon isi semua field.")
                else:
                    try:
                        supabase.table('questions').insert({
                            'tipe_ujian': q_tipe,
                            'soal_text': q_text,
                            'opsi_a': q_opsi_a,
                            'opsi_b': q_opsi_b,
                            'opsi_c': q_opsi_c,
                            'opsi_d': q_opsi_d,
                            'kunci_jawaban': q_kunci
                        }).execute()
                        st.success("Soal berhasil disimpan!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal menyimpan soal: {e}")

    st.markdown("---")
    st.subheader("Daftar Soal Saat Ini")
    
    try:
        response = supabase.table('questions').select('*').order('id', desc=True).execute()
        df_questions = pd.DataFrame(response.data)
        
        if df_questions.empty:
            st.info("Belum ada soal di database.")
        else:
            # Gunakan st.data_editor untuk mengedit dan menghapus
            df_questions['Hapus'] = False
            edited_df = st.data_editor(
                df_questions,
                column_config={
                    "id": st.column_config.NumberColumn("ID", disabled=True),
                    "tipe_ujian": st.column_config.SelectboxColumn("Tipe", options=["Pre-Test", "Post-Test"]),
                    "soal_text": st.column_config.TextColumn("Soal"),
                    "Hapus": st.column_config.CheckboxColumn("Hapus?")
                },
                use_container_width=True,
                hide_index=True,
                key="questions_editor"
            )
            
            save_col, delete_col = st.columns(2)
            
            with save_col:
                if st.button("💾 Simpan Perubahan", use_container_width=True):
                    changes = st.session_state.questions_editor.get("edited_rows", {})
                    if changes:
                        with st.spinner("Menyimpan..."):
                            for idx, change in changes.items():
                                item_id = edited_df.iloc[idx]['id']
                                supabase.table('questions').update(change).eq('id', item_id).execute()
                            st.success("Perubahan disimpan!")
                            st.rerun()

            with delete_col:
                ids_to_delete = edited_df[edited_df['Hapus'] == True]['id'].tolist()
                if ids_to_delete:
                    st.markdown('<div class="delete-button">', unsafe_allow_html=True)
                    if st.button(f"🗑️ Hapus ({len(ids_to_delete)}) Soal Terpilih", use_container_width=True):
                        with st.spinner("Menghapus..."):
                            supabase.table('questions').delete().in_('id', ids_to_delete).execute()
                            st.success("Soal terpilih dihapus!")
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Gagal memuat daftar soal: {e}")


elif menu == "Input Nilai Praktek":
    st.header("👨‍🏫 Input Nilai Uji Praktek")
    
    try:
        # Ambil daftar peserta
        response_users = supabase.table('users').select('email, nama_lengkap').eq('role', 'peserta').execute()
        peserta_list = response_users.data
        
        if not peserta_list:
            st.warning("Belum ada peserta yang terdaftar.")
            st.stop()
        
        # Buat mapping nama ke email
        peserta_options = {p['nama_lengkap']: p['email'] for p in peserta_list}
        
        with st.form("practice_score_form", clear_on_submit=True):
            selected_nama = st.selectbox("Pilih Peserta:", options=peserta_options.keys())
            nilai = st.number_input("Masukkan Nilai Praktek (0-100)", min_value=0.0, max_value=100.0, step=1.0)
            
            if st.form_submit_button("Simpan Nilai Praktek"):
                selected_email = peserta_options[selected_nama]
                
                with st.spinner("Menyimpan nilai..."):
                    try:
                        # Gunakan upsert untuk update jika sudah ada, atau insert jika baru
                        supabase.table('practical_scores').upsert({
                            'user_email': selected_email,
                            'nilai_praktek': nilai,
                            'dinilai_oleh': user_email
                        }, on_conflict='user_email').execute()
                        
                        st.success(f"Nilai praktek untuk {selected_nama} berhasil disimpan!")
                    except Exception as e:
                        st.error(f"Gagal menyimpan nilai: {e}")

    except Exception as e:
        st.error(f"Gagal memuat daftar peserta: {e}")
