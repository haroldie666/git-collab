import os
import csv
import inquirer
from tabulate import tabulate

# agar program bisa menemukan file csv info_umum dan info_dokter csv
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
dataDIR = os.path.join(BASE_DIR, "data")
dfInfoUmum = os.path.join(dataDIR, "info_umum.csv")
dfInfoDokter = os.path.join(dataDIR, "info_dokter.csv")

# membaca file csv
def baca_csv(path_file):
    if not os.path.exists(path_file):
        print(f"[ERROR] File '{path_file}' tidak ditemukan.")
        return []
    with open(path_file, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

# biar outputnya gak nimpa
def clear():
    os.system("cls || clear")

# membuat tabel menjadi rounded outline pake tabulate
def tampilkan_tabel(data):
    if not data:
        print("Tidak ada data untuk ditampilkan.")
        return
    headers = list(data[0].keys())
    rows = [list(row.values()) for row in data]
    # Warna biru untuk header
    biru = "\033[94m"
    reset = "\033[0m"
    headers_warna = [f"{biru}{h}{reset}" for h in headers]
    # menampilkan rounded outline
    print(tabulate(rows, headers=headers_warna, tablefmt="rounded_outline"))
    print()  # spasi di bawah tabel

# Menu tabulate 
def tampilkan_menu_tabulate():
    menu = [
        ["1", "Lihat Jadwal Besuk"],
        ["2", "Lihat Jadwal Dokter"],
        ["3", "Keluar"]
    ]
    print("\n=== MENU INFORMASI ===")
    for nomor, nama in menu:
        print(f"{nomor}. {nama}")

# menu utama
def menu_utama():
    while True:
        clear()
        tampilkan_menu_tabulate()
        pilihan = inquirer.list_input(
            "Pilih menu:",
            choices=[
                "1. Lihat Jadwal Besuk",
                "2. Lihat Jadwal Dokter",
                "Keluar"
            ]
        )
        if pilihan.startswith("1"):
            clear()
            print("\n=== JADWAL BESUK ===")
            data = baca_csv(dfInfoUmum)
            tampilkan_tabel(data)
            kuning = "\033[93m"
            reset = "\033[0m"
            input(f"{kuning}Tekan ENTER untuk melanjutkan...{reset}")
        elif pilihan.startswith("2"):
            clear()
            print("\n=== JADWAL DOKTER ===")
            data = baca_csv(dfInfoDokter)
            tampilkan_tabel(data)
            kuning = "\033[93m"
            reset = "\033[0m"
            input(f"{kuning}Tekan ENTER untuk melanjutkan...{reset}")
        else:
            print("Terima kasih!")
            break
        
# menjalankan program
if __name__ == "__main__":
    menu_utama()