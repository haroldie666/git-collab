import csv
import os
import inquirer

# ambil file data di users.csv
FOLDER_DASAR = os.path.dirname(os.path.abspath(__file__))
FILE_USERS = os.path.join(FOLDER_DASAR, "data", "users.csv")

# fungsi baca csv
def baca_users():
    if not os.path.exists(FILE_USERS):
        return []
    with open(FILE_USERS, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

# fungsi nulis ke csv
def simpan_user_baru(username, password, role):
    data = baca_users()
    fieldnames = ["username", "password", "role"]
    with open(FILE_USERS, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        data.append({"username": username, "password": password, "role": role})
        writer.writerows(data)

# cek data (sudah ada apa blom)
def username_sudah_dipakai(username, daftar_user):
    return any(u["username"] == username for u in daftar_user)
def password_sudah_dipakai(password, daftar_user):
    return any(u["password"] == password for u in daftar_user)

# program utama
def mulai_registrasi():
    daftar_user = baca_users()
    print("\n--- Buat Username Baru ---")
    while True:
        username_baru = input("Masukkan username baru: ").strip()
        if username_sudah_dipakai(username_baru, daftar_user):
            print("Username sudah dipakai, ganti yang lain")
        else:
            print(f"Username tersedia → {username_baru}")
            break
    print("\n--- Buat Password Baru ---")
    while True:
        password_baru = input("Masukkan password baru: ").strip()
        if password_sudah_dipakai(password_baru, daftar_user):
            print("Password sudah terdaftar, buat yang lebih unik!")
        else:
            print(f"Password tersedia → {password_baru}")
            break
    print("\n=== MENU REGISTRASI ===")
    pilihan = [
        inquirer.List(
            "role",
            message="Pilih role akun baru:",
            choices=["Admin", "User Biasa", "Batal"],
        )
    ]
    jawaban_role = inquirer.prompt(pilihan)["role"]
    if jawaban_role == "Batal":
        print("Registrasi dibatalkan.")
        return

# varifikasi data yang baru diinput
    print("\n--- Verifikasi Data Baru ---")
    verif_user = input("Masukkan ulang username baru: ").strip()
    verif_pass = input("Masukkan ulang password baru: ").strip()
    if verif_user != username_baru or verif_pass != password_baru:
        print("Data tidak cocok! Registrasi dibatalkan.")
        return

# autentikasi
    if jawaban_role == "Admin":
        print("\n--- Autentikasi Admin ---")
        auth_user = input("Masukkan username autentikasi: ").strip()
        auth_pass = input("Masukkan password autentikasi: ").strip()
        if auth_user == username_baru and auth_pass == password_baru:
            print("Autentikasi berhasil! (akun baru memverifikasi dirinya sendiri)")
        else:
            print("Autentikasi gagal! Registrasi dibatalkan")
            return
        role_final = "admin"
        print("\nRegistrasi admin selesai!")
    else:
        role_final = "user"
        print("\nRegistrasi user berhasil!")

# simpan data ke csv
    simpan_user_baru(username_baru, password_baru, role_final)
    print(f"\nAkun tersimpan ke CSV → {FILE_USERS}")

# mennjalankan program
if __name__ == "__main__":
    mulai_registrasi()
