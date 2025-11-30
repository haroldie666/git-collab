import os # Untuk membersihkan terminal
import sys # Untuk mengubah runtime
import time # Untuk jeda waktu
import pandas as pd # Untuk manipulasi data
from InquirerPy import inquirer
from tabulate import tabulate # Untuk tabel
import re 
from colorama import init, Fore, Style # Untuk mewarnai teks
from datetime import datetime # Untuk menambahkan tanggal, bulan, dan haari

init(autoreset=True)

dataDIR = 'data'
dfPasien = f'{dataDIR}/pasien.csv'
dfPermohonan = f'{dataDIR}/permohonan_kunjungan.csv'
dfLog = f'{dataDIR}/log_aktivitas.csv'

def clear(): # Membersihkan terminal
    os.system('cls || clear')

def loading(teks="Memuat"):
    sys.stdout.write(f"\n{teks}")
    for _ in range(5):
        time.sleep(0.5)
        sys.stdout.write(".")
        sys.stdout.flush()
    print()

def baca_pasien():
    df = pd.read_csv(dfPasien, dtype=str)

    for col in df.columns:
        df[col] = df[col].str.strip()

    return df

def baca_permohonan():
    df = pd.read_csv(dfPermohonan, dtype=str)

    for col in df.columns:
        df[col] = df[col].str.strip()

    return df

def tambah_log(aksi, role="user"):
    log_df = pd.read_csv(dfLog)
    waktu = datetime.now().strftime("%d/%m/%Y %H:%M")
    log_baru = pd.DataFrame([{"waktu": waktu, "aksi": aksi, "role": role}])
    log_df = pd.concat([log_df, log_baru], ignore_index=True)
    log_df.to_csv(dfLog, index=False)

def lihat_data_pasien():
    clear()
    print("=" * 62)
    print("DATA PASIEN PIP HOSPITAL".center(62))
    print("=" * 62)

    df = baca_pasien()
    df_display = df[['id', 'nama', 'ruangan', 'status_kunjungan']].copy()

    headers = list(df_display.columns)
    headers_biru = [f"{Fore.BLUE}{h}{Style.RESET_ALL}" for h in headers]

    print(tabulate(df_display, headers=headers_biru, tablefmt="rounded_grid", showindex=False))
    tambah_log("Melihat daftar pasien")

    input(f"\n{Fore.YELLOW}Tekan enter untuk melanjutkan...{Style.RESET_ALL}")

def ajukan_permohonan():
    clear()
    print("=" * 60)
    print("FORM PERMOHONAN KUNJUNGAN PIP HOSPITAL".center(60))
    print("=" * 60)

    pattern_nama = r"^[a-zA-Z ]+$"

    while True:
        nama = inquirer.text(message="Nama Penjenguk:").execute().strip()

        if not nama:
            print(f"{Fore.RED}Nama penjenguk tidak boleh kosong!{Style.RESET_ALL}")
        elif not re.match(pattern_nama, nama):
            print(f"{Fore.RED}Nama harus berupa huruf dan tidak boleh mengandung simbol/angka!{Style.RESET_ALL}")
        else:
            break

    while True:
        pasien = inquirer.text(message="Nama Pasien:").execute().strip()
        
        if not pasien:
            print(f"{Fore.RED}Nama pasien tidak boleh kosong!{Style.RESET_ALL}")
        elif not re.match(pattern_nama, pasien):
            print(f"{Fore.RED}Nama harus berupa huruf dan tidak boleh mengandung simbol/angka!{Style.RESET_ALL}")
        else:
            break

    # Regex format HH.MM
    pattern_jam = r"^(?:[01]\d|2[0-3])\.[0-5]\d$"

    while True:
        jam = inquirer.text(message="Rencana Jam Besuk (cth: 09.00):").execute().strip()

        if re.match(pattern_jam, jam):
            break
        print(f"{Fore.RED}Format jam harus HH.MM (contoh 09.00)!{Style.RESET_ALL}")

    loading("Mengirim permohonan")

    df = baca_permohonan()

    if "id" not in df.columns:
        df["id"] = []

    if df.empty or df["id"].isnull().all():
        new_id = 1
    else:
        max_id = pd.to_numeric(df["id"], errors="coerce").max()
        new_id = int(max_id) + 1 if pd.notna(max_id) else 1

    data_baru = {
        "id": new_id,
        "nama_penjenguk": nama,
        "nama_pasien": pasien,
        "jam_besuk": jam,
        "status": "Menunggu"
    }

    df = pd.concat([df, pd.DataFrame([data_baru])], ignore_index=True)
    df.to_csv(dfPermohonan, index=False)
    tambah_log(f"Mengajukan kunjungan untuk {pasien}")

    print(f"{Fore.GREEN}Permohonan Anda telah dikirim dengan status 'Menunggu'{Style.RESET_ALL}")
    input(f"\n{Fore.YELLOW}Tekan enter untuk melanjutkan...{Style.RESET_ALL}")

def cek_status_permohonan():
    clear()
    print("=" * 65)
    print("CEK STATUS KUNJUNGAN PIP HOSPITAL".center(65))
    print("=" * 65)

    nama = inquirer.text(message="Masukkan nama penjenguk:").execute()
    df = baca_permohonan()

    loading("Mencari data")

    hasil = df[df["nama_penjenguk"].str.lower().str.contains(nama.lower())]

    if hasil.empty:
        print(f"{Fore.RED}Tidak ditemukan data untuk '{nama}'.{Style.RESET_ALL}")
        return input(f"\n{Fore.YELLOW}Tekan enter untuk melanjutkan...{Style.RESET_ALL}")

    def format_status(s):
        if s.lower() == "pending":
            return f"{Fore.YELLOW}{s}{Style.RESET_ALL}"
        elif s.lower() == "disetujui":
            return f"{Fore.GREEN}{s}{Style.RESET_ALL}"
        else:
            return f"{Fore.RED}{s}{Style.RESET_ALL}"

    hasil = hasil.copy()
    hasil["status"] = hasil["status"].apply(format_status)

    headers = list(hasil.columns)
    headers_biru = [f"{Fore.BLUE}{h}{Style.RESET_ALL}" for h in headers]

    print(tabulate(hasil, headers=headers_biru, tablefmt="rounded_grid", showindex=False, disable_numparse=True))
    input(f"\n{Fore.YELLOW}Tekan enter untuk melanjutkan...{Style.RESET_ALL}")

def main_menu():
    while True:
        clear()
        print("=" * 50)
        print("MENU USER".center(50))
        print("=" * 50)

        pilihan = inquirer.select(
            message="Pilih menu:",
            choices=[
                "1. Lihat Data Pasien",
                "2. Ajukan Permohonan Kunjungan",
                "3. Cek Status Kunjungan",
                "4. Kembali ke menu utama"
            ],
            pointer="➡️ ",
            qmark=""
        ).execute()

        pilih = pilihan.split(".")[0]

        if pilih == "1":
            lihat_data_pasien()
        elif pilih == "2":
            ajukan_permohonan()
        elif pilih == "3":
            cek_status_permohonan()
        elif pilih == "4":
            break