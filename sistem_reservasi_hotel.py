from abc import ABC, abstractmethod


# ==========================================
# Bagian 1: ABSTRACTION & ENCAPSULATION
# ==========================================

class Kamar(ABC):
    def __init__(self, nama_tamu, nomor_kamar, hari_check_in, hari_check_out):
        if hari_check_out < hari_check_in:
            raise ValueError("Hari check out tidak boleh lebih kecil dari hari check in.")
        self.nama_tamu = nama_tamu
        self.__nomor_kamar = nomor_kamar
        self.__hari_check_in = hari_check_in
        self.__hari_check_out = hari_check_out

    def get_nomor_kamar(self):
        return self.__nomor_kamar

    def get_hari_check_in(self):
        return self.__hari_check_in

    def get_hari_check_out(self):
        return self.__hari_check_out

    def hitung_lama_menginap(self):
        return self.__hari_check_out - self.__hari_check_in

    @abstractmethod
    def hitung_biaya(self):
        pass


# ==========================================
# Bagian 2: INHERITANCE & METHOD OVERRIDING
# ==========================================

class KamarStandar(Kamar):
    def __init__(self, nama_tamu, nomor_kamar, hari_check_in, hari_check_out):
        super().__init__(nama_tamu, nomor_kamar, hari_check_in, hari_check_out)

    def hitung_biaya(self):
        lama = self.hitung_lama_menginap()
        return lama * 300000


class KamarDeluxe(Kamar):
    def __init__(self, nama_tamu, nomor_kamar, hari_check_in, hari_check_out):
        super().__init__(nama_tamu, nomor_kamar, hari_check_in, hari_check_out)

    def hitung_biaya(self):
        lama = self.hitung_lama_menginap()
        return lama * 500000


class KamarSuite(Kamar):
    def __init__(self, nama_tamu, nomor_kamar, hari_check_in, hari_check_out):
        super().__init__(nama_tamu, nomor_kamar, hari_check_in, hari_check_out)

    def hitung_biaya(self):
        lama = self.hitung_lama_menginap()
        return lama * 1000000


# ==========================================
# Bagian 3: CLASS PENGELOLA (COMPOSITION & POLYMORPHISM)
# ==========================================

class HotelApp:
    def __init__(self):
        self.__daftar_reservasi = []

    def tambah_reservasi(self, kamar):
        if isinstance(kamar, Kamar) == False:
            raise ValueError("Reservasi harus berupa objek turunan Kamar.")
        self.__daftar_reservasi.append(kamar)
        print(f"Reservasi kamar {kamar.get_nomor_kamar()} untuk {kamar.nama_tamu} berhasil ditambahkan.")

    def tampilkan_rekap_tagihan(self):
        print("")
        print("===== REKAP TAGIHAN HOTEL =====")
        print("No | Tamu | Nomor | Tipe | Lama | Total Biaya")
        print("--------------------------------------------------")
        total_semua = 0
        nomor = 1
        for kamar in self.__daftar_reservasi:
            biaya = kamar.hitung_biaya()
            lama = kamar.hitung_lama_menginap()
            tipe = type(kamar).__name__
            print(f"{nomor} | {kamar.nama_tamu} | {kamar.get_nomor_kamar()} | {tipe} | {lama} hari | Rp{biaya}")
            total_semua = total_semua + biaya
            nomor = nomor + 1
        print("--------------------------------------------------")
        print(f"Total semua tagihan: Rp{total_semua}")


# ==========================================
# Bagian 4: PROGRAM UTAMA
# ==========================================

if __name__ == "__main__":
    app = HotelApp()

    try:
        kamar1 = KamarStandar("Busiri", "101", 1, 3)
        kamar2 = KamarDeluxe("Siti", "201", 2, 5)
        kamar3 = KamarSuite("Andi", "301", 1, 2)
        app.tambah_reservasi(kamar1)
        app.tambah_reservasi(kamar2)
        app.tambah_reservasi(kamar3)
    except ValueError as e:
        print(f"Terjadi kesalahan: {e}")

    try:
        kamar_error = KamarStandar("Dewi", "102", 5, 2)
        app.tambah_reservasi(kamar_error)
    except ValueError as e:
        print(f"Validasi berhasil menolak data salah: {e}")

    app.tampilkan_rekap_tagihan()
