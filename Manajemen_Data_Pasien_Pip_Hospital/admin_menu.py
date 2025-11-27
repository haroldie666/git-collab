import os
import pandas as pd
from colorama import Fore, Style, init
from datetime import datetime
from tabulate import tabulate
from InquirerPy import inquirer
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
init(autoreset=True)

dataDIR = 'data'     
dfPasien = (f'{dataDIR}/pasien.csv')
dfLog = (f'{dataDIR}/log_aktivitas.csv')
dfPermohonan = f'{dataDIR}/permohonan_kunjungan.csv'

def clear():
    os.system('cls || clear')

def baca_pasien():
    df = pd.read_csv(dfPasien, dtype=str)  # Baca semua sebagai string dulu
    if df.empty:
        return df

    # Konversi kolom 'id' ke integer (gunakan Int64 agar aman jika ada NaN)
    df['id'] = pd.to_numeric(df['id'], errors='coerce').astype('Int64')
    return df

def simpan_pasien(df):
    if "id" in df.columns and not df.empty:
        df = df.copy()
        df["id"] = pd.to_numeric(df["id"], errors='coerce').astype('Int64')
    df.to_csv(dfPasien, index=False)

def tambah_log(aksi, role="admin"):
    log_df = pd.read_csv(dfLog)
    waktu = datetime.now().strftime("%d/%m/%Y %H:%M")
    new_log = pd.DataFrame([{"waktu": waktu, "aksi": aksi, "role": role}])
    log_df = pd.concat([log_df, new_log], ignore_index=True)
    log_df.to_csv(dfLog, index=False)

def setujui_permohonan():
    df = pd.read_csv(dfPermohonan, dtype=str)
    print("="*70)
    print("Permohonan Kunjungan Pengunjung".center(70))
    print("="*70)   

    df_display = df.rename(columns={
        "id": "ID",
        "nama_penjenguk": "Nama Penjenguk",
        "nama_pasien": "Nama Pasien",
        "jam_besuk": "Jam Besuk",
        "status": "Status"
    })

    print(tabulate(df_display.values.tolist(), headers=df_display.columns.tolist(), tablefmt="rounded_outline", disable_numparse=True))

    idx_input = input("\nPilih nomor permohonan untuk ditindak: ").strip()
    if not idx_input.isdigit():
        print(Fore.RED + "Masukkan nomor yang valid." + Style.RESET_ALL)
        input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
        return setujui_permohonan()

    idx = int(idx_input) - 1
    if idx < 0 or idx >= len(df):
        print(Fore.RED + "Nomor tidak valid." + Style.RESET_ALL)
        input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
        return

    current_status = df.loc[idx, "status"]
    nama_penjenguk = df.loc[idx, "nama_penjenguk"]
    nama_pasien = df.loc[idx, "nama_pasien"]

    print(f"\nPermohonan: {nama_penjenguk} untuk {nama_pasien}")
    print(f"Status saat ini: {current_status}")

    action = inquirer.select(
        message="Pilih tindakan:",
        choices=["Setujui", "Tolak", "Batalkan"],
        pointer="➡️ ",
        qmark=""
    ).execute()

    if action == "Setujui":
        df.loc[idx, "status"] = "Disetujui"
        tambah_log(f"Menyetujui kunjungan: {nama_penjenguk} untuk {nama_pasien}")
        print(Fore.GREEN + f"\nPermohonan {nama_penjenguk} telah disetujui!" + Style.RESET_ALL)
    elif action == "Tolak":
        df.loc[idx, "status"] = "Ditolak"
        tambah_log(f"Menolak kunjungan: {nama_penjenguk} untuk {nama_pasien}")
        print(Fore.RED + f"\nPermohonan {nama_penjenguk} telah ditolak!" + Style.RESET_ALL)
    else:
        print(Fore.RED + "\nOperasi dibatalkan." + Style.RESET_ALL)

    df.to_csv(dfPermohonan, index=False)
    print(Fore.GREEN + "\nPerubahan telah disimpan." + Style.RESET_ALL)
    input(Fore.YELLOW + "\nTekan enter untuk melanjutkan..." + Style.RESET_ALL)
    clear()

def lihat_pasien():
    df = baca_pasien()
    if df.empty:
        print("\nBelum ada data pasien.")
    else:
        print("="*150)
        print("Daftar Pasien".center(150))
        print("="*150)
        df_display = df.copy()

        def truncate(text, max_len=20):
            s = str(text).strip() if pd.notna(text) else ""
            return s if len(s) <= max_len else s[:max_len-3] + "..."

        for col in df_display.columns:
            df_display[col] = df_display[col].apply(truncate)

        df_display = df_display.rename(columns={
            "id": "ID",
            "bpjs": "BPJS",
            "nama": "Nama",
            "umur": "Umur",
            "jenis_kelamin": "JK",
            "penyakit": "Penyakit",
            "tgl_masuk": "Tgl Masuk",
            "tgl_keluar": "Tgl Keluar",
            "dokter": "Dokter",
            "ruangan": "Ruang",
            "status_kunjungan": "Status"
        })

        headers = [f"{Fore.BLUE}{col}{Style.RESET_ALL}" for col in df_display.columns]
        rows = df_display.values.tolist()
        print(tabulate(rows, headers=headers, tablefmt="rounded_outline", maxcolwidths=20))

    input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)

def tambah_pasien():
    df = baca_pasien()
    try:
        print("="*50)
        print("Tambah Pasien Baru".center(50))
        print("="*50)

        # Input nama (wajib)
        while True:
            nama = input("Nama pasien: ").strip()
            if nama:
                break
            else:
                print(Fore.RED + "Data tidak boleh kosong." + Style.RESET_ALL)
        
        # Input BPJS (wajib, harus angka, dan unik jika diisi)
        while True:
            bpjs = input("Nomor BPJS: ").strip()
            if not bpjs:
                print(Fore.RED + "Nomor BPJS tidak boleh kosong." + Style.RESET_ALL)
                continue
            if not bpjs.isdigit():
                print(Fore.RED + "Nomor BPJS harus berupa angka." + Style.RESET_ALL)
                continue
            # Cek keunikan
            if not df.empty and bpjs in df['bpjs'].values:
                print(Fore.RED + f"Nomor BPJS '{bpjs}' sudah terdaftar! Gunakan nomor lain." + Style.RESET_ALL)
                continue
            break

        # Input umur (harus angka)
        while True:
            umur = input("Umur: ").strip()
            if umur.isdigit():
                break
            else:
                print(Fore.RED + "Umur harus berisi angka. Silakan coba lagi." + Style.RESET_ALL)

        # Input jenis kelamin (pilih L/P)
        jk = inquirer.select(
            message="Jenis kelamin:",
            choices=["L", "P"],
            pointer="➡️ ",
            qmark=""
        ).execute()

        # Input penyakit (wajib)
        while True:
            penyakit = input("Penyakit: ").strip()
            if penyakit:
                break
            else:
                print(Fore.RED + "Data tidak boleh kosong." + Style.RESET_ALL)

        # Input tanggal masuk (wajib, harus format DD MMM YYYY)
        while True:
            tgl_masuk = input("Tanggal masuk (contoh: 10 Nov 2025): ").strip()
            if not tgl_masuk:
                print(Fore.RED + "Tanggal masuk tidak boleh kosong." + Style.RESET_ALL)
                continue
            if validasi_tanggal_csv(tgl_masuk) and tgl_masuk != "-":
                break
            else:
                print(Fore.RED + "Format tanggal masuk salah! Contoh yang benar: 10 Nov 2025" + Style.RESET_ALL)

        # Input tanggal keluar (boleh tanggal atau "-", tidak boleh kosong/format salah)
        while True:
            tgl_keluar = input("Tanggal keluar (contoh: 15 Nov 2025 atau -): ").strip()
            if not tgl_keluar:
                print(Fore.RED + "Tanggal keluar tidak boleh kosong." + Style.RESET_ALL)
                continue
            if validasi_tanggal_csv(tgl_keluar):
                break
            else:
                print(Fore.RED + "Format tanggal keluar salah! Contoh: 15 Nov 2025 atau '-'" + Style.RESET_ALL)

        # Input dokter (wajib)
        while True:
            dokter = input("Dokter: ").strip()
            if dokter:
                break
            else:
                print(Fore.RED + "Data tidak boleh kosong." + Style.RESET_ALL)

        # Input ruangan (wajib)
        while True:
            ruangan = input("Ruangan: ").strip()
            if ruangan:
                break
            else:
                print(Fore.RED + "Data tidak boleh kosong." + Style.RESET_ALL)

        # Input status kunjungan
        status = inquirer.select(
            message="Status kunjungan:",
            choices=["Ada", "Tidak ada"],
            pointer="➡️ ",
            qmark=""
        ).execute()

        # Generate ID baru
        new_id = df["id"].astype(int).max() + 1 if not df.empty else 1

        # Buat data baru — termasuk bpjs
        new_row = {
            "id": new_id,
            "bpjs": bpjs,  # ✅ Simpan BPJS
            "nama": nama,
            "umur": int(umur),
            "jenis_kelamin": jk,
            "penyakit": penyakit,
            "tgl_masuk": tgl_masuk,
            "tgl_keluar": tgl_keluar,
            "dokter": dokter,
            "ruangan": ruangan,
            "status_kunjungan": status
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        simpan_pasien(df)
        tambah_log(f"Menambah pasien: {nama}")
        print(Fore.GREEN + f"\nPasien {nama} berhasil ditambahkan!" + Style.RESET_ALL)

    except Exception as e:
        print(Fore.RED + f"\nTerjadi kesalahan: {e}" + Style.RESET_ALL)

    input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
    clear()

def validasi_tanggal_csv(tgl_str):
    """Validasi apakah string tanggal sesuai format 'DD MMM YYYY' atau '-'."""
    if tgl_str == "-":
        return True
    try:
        datetime.strptime(tgl_str, "%d %b %Y")
        return True
    except ValueError:
        return False

def edit_pasien():
    df = baca_pasien()
    lihat_pasien()
    
    id_edit = input("\nID pasien: ").strip()
    if not id_edit.isdigit():
        print(Fore.RED + "\nID harus berupa angka." + Style.RESET_ALL)
        input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
        return edit_pasien()

    id_edit = int(id_edit)
    if id_edit not in df["id"].values:
        print(Fore.RED + f"\nID {id_edit} tidak ditemukan. Daftar ID yang tersedia: {sorted(df['id'].dropna().astype(int).tolist())}" + Style.RESET_ALL)
        input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
        return

    idx = df[df["id"] == id_edit].index[0]
    data_lama = df.loc[idx].to_dict()

    print("="*60)
    print("Edit Data Pasien.".center(60))
    print("="*60)
    print(f"\nMengedit data pasien ID {id_edit} ({data_lama['nama']})")
    print("-" * 50)

    nama_baru = input(f"Nama [{data_lama['nama']}]: ").strip() or data_lama['nama']

    while True:
        bpjs_baru = input(f"BPJS [{data_lama.get('bpjs', '')}]: ").strip() or data_lama.get('bpjs', '')
        if not bpjs_baru:
            print("Nomor BPJS tidak boleh kosong.")
            continue
        if not bpjs_baru.isdigit():
            print("Nomor BPJS harus berupa angka.")
            continue
        if bpjs_baru != data_lama.get('bpjs', '') and not df.empty and bpjs_baru in df['bpjs'].values:
            print(f"Nomor BPJS '{bpjs_baru}' sudah digunakan oleh pasien lain!")
            continue
        break

    while True:
        umur_input = input(f"Umur [{data_lama['umur']}]: ").strip() or str(data_lama['umur'])
        if umur_input.isdigit():
            umur_baru = int(umur_input)
            break
        else:
            print("Umur harus angka.")

    jk_baru = inquirer.select(
        message=f"Jenis kelamin [{data_lama['jenis_kelamin']}]:",
        choices=["L", "P"],
        default=data_lama['jenis_kelamin'],
        pointer="➡️ ",
        qmark=""
    ).execute()

    penyakit_baru = input(f"Penyakit [{data_lama['penyakit']}]: ").strip() or data_lama['penyakit']
    if not penyakit_baru:
        print("Penyakit tidak boleh kosong.")
        input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
        return

    # Validasi Tanggal Masuk
    while True:
        tgl_masuk_baru = input(f"Tanggal masuk (contoh: 10 Nov 2025) [{data_lama['tgl_masuk']}]: ").strip() or data_lama['tgl_masuk']
        if not tgl_masuk_baru:
            print("Tanggal masuk tidak boleh kosong.")
            continue
        if validasi_tanggal_csv(tgl_masuk_baru) and tgl_masuk_baru != "-":
            break
        else:
            print("Format tanggal masuk salah! Harus seperti: 10 Nov 2025")

    while True:
        tgl_keluar_baru = input(f"Tanggal keluar (contoh: 15 Nov 2025 atau -) [{data_lama['tgl_keluar']}]: ").strip() or data_lama['tgl_keluar']
        if not tgl_keluar_baru:
            print("Tanggal keluar tidak boleh kosong.")
            continue
        if validasi_tanggal_csv(tgl_keluar_baru):
            break
        else:
            print("Format tanggal keluar salah! Harus seperti: 15 Nov 2025 atau '-'")

    dokter_baru = input(f"Dokter [{data_lama['dokter']}]: ").strip() or data_lama['dokter']
    if not dokter_baru:
        print("Dokter tidak boleh kosong.")
        input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
        return

    ruangan_baru = input(f"Ruangan [{data_lama['ruangan']}]: ").strip() or data_lama['ruangan']
    if not ruangan_baru:
        print("Ruangan tidak boleh kosong.")
        input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
        return

    status_baru = inquirer.select(
        message=f"Status kunjungan [{data_lama['status_kunjungan']}]:",
        choices=["Ada", "Tidak ada"],
        default=data_lama['status_kunjungan'],
        pointer="➡️ ",
        qmark=""
    ).execute()

    # Simpan perubahan
    df.loc[idx, "nama"] = nama_baru
    df.loc[idx, "bpjs"] = bpjs_baru
    df.loc[idx, "umur"] = umur_baru
    df.loc[idx, "jenis_kelamin"] = jk_baru
    df.loc[idx, "penyakit"] = penyakit_baru
    df.loc[idx, "tgl_masuk"] = tgl_masuk_baru
    df.loc[idx, "tgl_keluar"] = tgl_keluar_baru
    df.loc[idx, "dokter"] = dokter_baru
    df.loc[idx, "ruangan"] = ruangan_baru
    df.loc[idx, "status_kunjungan"] = status_baru

    simpan_pasien(df)
    tambah_log(f"Edit pasien ID {id_edit}: {nama_baru}")
    print(Fore.GREEN + "\nData pasien berhasil diperbarui!" + Style.RESET_ALL)
    input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
    clear()

def hapus_pasien():
    df = baca_pasien()
    if df.empty:
        print(Fore.RED + "\nTidak ada pasien." + Style.RESET_ALL)
        input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
        return

    lihat_pasien()
    id_hapus = input("\nID pasien: ").strip()
    if not id_hapus.isdigit() or int(id_hapus) not in df["id"].values:
        print(Fore.RED + "\nID tidak valid." + Style.RESET_ALL)
        input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
        return

    id_hapus = int(id_hapus)
    nama = df[df["id"] == id_hapus]["nama"].values[0]

    if inquirer.confirm(f"Hapus {nama}", default=False).execute():
        # Hapus baris dengan ID tertentu
        df = df[df["id"] != id_hapus].reset_index(drop=True)

        # Reset ulang kolom 'id' agar berurutan dari 1
        df["id"] = range(1, len(df) + 1)

        simpan_pasien(df)
        tambah_log(f"Hapus pasien: {nama}")
        print(Fore.GREEN + "\nBerhasil dihapus dan ID diperbarui." + Style.RESET_ALL)
    else:
        print(Fore.RED + "\nDibatalkan." + Style.RESET_ALL)

    input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
    clear()

def lihat_log():
    df = pd.read_csv(dfLog)
    print("="*90)
    print("Log Aktivitas Admin".center(90))
    print("="*90)
    print(tabulate(df.values.tolist(), headers=df.columns.tolist(), tablefmt="rounded_outline"))
    input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)
    clear()

def tampilkan_grafik_pasien():
    df = baca_pasien()

    # Konversi kolom tanggal ke format datetime
    df["tgl_masuk_parsed"] = pd.to_datetime(df["tgl_masuk"], format="%d %b %Y", errors="coerce")

    # Hitung jumlah pasien per hari
    df["tanggal"] = df["tgl_masuk_parsed"].dt.date
    daily_counts = df["tanggal"].value_counts().sort_index()

    # Ambil tanggal dan jumlah pasien
    dates = pd.to_datetime(daily_counts.index)
    counts = daily_counts.values

    # Buat grafik
    plt.figure(figsize=(10, 6))
    plt.plot(dates, counts, marker='o', linestyle='-', linewidth=2)

    # Format sumbu X agar menampilkan "DD MMM YYYY"
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    plt.xticks(rotation=45)

    plt.title("Grafik Pasien per Hari")
    plt.xlabel("Tanggal Masuk")
    plt.ylabel("Jumlah Pasien")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    input("\nTekan Enter untuk kembali...")
    clear()

def lihat_permohonan_kunjungan():
    df = pd.read_csv(dfPermohonan, dtype=str)

    print("="*70)
    print("Daftar Permohonan Kunjungan".center(70))
    print("="*70)

    df_display = df.rename(columns={
        "id": "ID",
        "nama_penjenguk": "Nama Penjenguk",
        "nama_pasien": "Nama Pasien",
        "jam_besuk": "Jam Besuk",
        "status": "Status"
    })

    headers = [f"{Fore.BLUE}{col}{Style.RESET_ALL}" for col in df_display.columns]
    rows = df_display.values.tolist()

    print(tabulate(rows, headers=headers, tablefmt="rounded_outline", disable_numparse=True))

    if inquirer.confirm("Ingin mengelola salah satu permohonan?", default=False).execute():
        clear()
        setujui_permohonan()
    clear()

def menu_admin(username):
    clear()
    while True:
        pilihan = inquirer.select(
            message="\n=========================================\n               Menu Admin             \n=========================================",
            choices=[
                "Lihat data pasien",
                "Tambah pasien baru",
                "Edit data pasien",
                "Hapus pasien",
                "Lihat permohonan kunjungan",
                "Lihat log aktivitas",
                "Tampilkan grafik pasien",
                "Kembali ke menu utama"
            ],
            pointer="➡️ ",
            qmark="" 
        ).execute()

        clear()
        if pilihan == "Lihat data pasien": 
            lihat_pasien()
            clear()
        elif pilihan == "Tambah pasien baru": 
            tambah_pasien()
        elif pilihan == "Edit data pasien": 
            edit_pasien()
        elif pilihan == "Hapus pasien": 
            hapus_pasien()
        elif pilihan == "Lihat permohonan kunjungan": 
            lihat_permohonan_kunjungan() 
        elif pilihan == "Lihat log aktivitas": 
            lihat_log()
        elif pilihan == "Tampilkan grafik pasien": 
            tampilkan_grafik_pasien()
        elif pilihan == "Kembali ke menu utama":
            print(f"Goodbye {username}!")
            clear()
            break
        else:
            print("Pilihan tidak valid.")
            input(Fore.YELLOW + "Tekan enter untuk melanjutkan..." + Style.RESET_ALL)