import os
import sys
import time
import pandas as pd
from InquirerPy import inquirer
from tabulate import tabulate
import re
from colorama import init, Fore, Style

init(autoreset=True)

dataDIR = 'data'
dfPasien = f'{dataDIR}/pasien.csv'
dfPermohonan = f'{dataDIR}/permohonan_kunjungan.csv'

def clear():
    os.system('cls || clear')

def loading(teks="Memuat"):
    sys.stdout.write(f"\n{teks}")
    for _ in range(3):
        time.sleep(0.3)
        sys.stdout.write(".")
        sys.stdout.flush()
    print()

def baca_pasien():
    if not os.path.exists(dfPasien):
        return pd.DataFrame()
    df = pd.read_csv(dfPasien, dtype=str)

    for col in df.columns:
        df[col] = df[col].str.strip()

    return df

def baca_permohonan():
    if not os.path.exists(dfPermohonan):
        return pd.DataFrame()
    df = pd.read_csv(dfPermohonan, dtype=str)

    for col in df.columns:
        df[col] = df[col].str.strip()

    return df

#LIHAT DATA PASIEN
def lihat_data_pasien():
    clear()
    print("=" * 62)
    print("DATA PASIEN PIP HOSPITAL".center(62))
    print("=" * 62)

    df = baca_pasien()

    if df.empty:
        print(f"{Fore.RED}Tidak ada data pasien.{Style.RESET_ALL}")
        return input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...{Style.RESET_ALL}")

    df_display = df[['id', 'nama', 'ruangan', 'status_kunjungan']].copy()

    original_headers = list(df_display.columns)
    blue_headers = [f"{Fore.BLUE}{h}{Style.RESET_ALL}" for h in original_headers]

    print(tabulate(df_display, headers=blue_headers, tablefmt="rounded_grid", showindex=False))
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...{Style.RESET_ALL}")

def ajukan_permohonan():
    clear()
    print("=" * 60)
    print("FORM PERMOHONAN KUNJUNGAN PIP HOSPITAL".center(60))
    print("=" * 60)

    while True:
        nama = inquirer.text(message="Nama Penjenguk:").execute().strip()
        if nama:
            break
        print(f"{Fore.RED}Nama penjenguk tidak boleh kosong!{Style.RESET_ALL}")

    while True:
        pasien = inquirer.text(message="Nama Pasien:").execute().strip()
        if pasien:
            break
        print(f"{Fore.RED}Nama pasien tidak boleh kosong!{Style.RESET_ALL}")

    # Regex format HH.MM
    pattern_jam = r"^(?:[01]\d|2[0-3])\.[0-5]\d$"

    while True:
        jam = inquirer.text(message="Rencana Jam Besuk (cth: 09.00):").execute().strip()

        if re.match(pattern_jam, jam):
            break
        print(f"{Fore.RED}Format jam harus HH.MM (contoh 09.00)!{Style.RESET_ALL}")

    loading("Mengirim permohonan")

    df = baca_permohonan()

    newData = {
        "nama_penjenguk": nama,
        "nama_pasien": pasien,
        "jam_besuk": jam,
        "status": "Menunggu"
    }

    df = pd.concat([df, pd.DataFrame([newData])], ignore_index=True)
    df.to_csv(dfPermohonan, index=False)

    print(f"{Fore.GREEN}Permohonan Anda telah dikirim dengan status 'Menunggu'{Style.RESET_ALL}")
    print("   Silakan cek status secara berkala.")
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...{Style.RESET_ALL}")

#CEK STATUS PERMOHONAN
# ... (kode impor dan fungsi lain tetap sama)

# CEK STATUS PERMOHONAN
def cek_status_permohonan():
    clear()
    print("=" * 65)
    print("CEK STATUS KUNJUNGAN PIP HOSPITAL".center(65))
    print("=" * 65)

    nama = inquirer.text(message="Masukkan nama penjenguk:").execute()
    df = baca_permohonan()

    if df.empty:
        print(f"{Fore.YELLOW}Belum ada data permohonan.{Style.RESET_ALL}")
        return input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...{Style.RESET_ALL}")

    loading("Mencari data")

    hasil = df[df["nama_penjenguk"].str.lower().str.contains(nama.lower())]

    if hasil.empty:
        print(f"{Fore.RED}Tidak ditemukan data untuk '{nama}'.{Style.RESET_ALL}")
        return input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...{Style.RESET_ALL}")

    # Format warna status
    def format_status(s):
        if s.lower() == "pending":
            return f"{Fore.YELLOW}{s}{Style.RESET_ALL}"
        elif s.lower() == "disetujui":
            return f"{Fore.GREEN}{s}{Style.RESET_ALL}"
        else:
            return f"{Fore.RED}{s}{Style.RESET_ALL}"

    hasil = hasil.copy()
    hasil["status"] = hasil["status"].apply(format_status)

    original_headers = list(hasil.columns)
    blue_headers = [f"{Fore.BLUE}{h}{Style.RESET_ALL}" for h in original_headers]

    # PERBAIKAN DI SINI: disable_numparse=True
    # Ini mencegah tabulate mengubah "09.00" menjadi angka 9
    print(tabulate(hasil, headers=blue_headers, tablefmt="rounded_grid", showindex=False, disable_numparse=True))
    
    input(f"\n{Fore.YELLOW}Tekan Enter untuk kembali...{Style.RESET_ALL}")

# ... (main menu dan sisa kode tetap sama)

# MENU USER
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
                "4. Keluar"
            ],
        ).execute()

        pilih = pilihan.split(".")[0]

        if pilih == "1":
            lihat_data_pasien()
        elif pilih == "2":
            ajukan_permohonan()
        elif pilih == "3":
            cek_status_permohonan()
        elif pilih == "4":
            print(f"{Fore.BLUE}Terima kasih telah menggunakan sistem.{Style.RESET_ALL}")
            break