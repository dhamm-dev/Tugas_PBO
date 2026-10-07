"""Class Divisi: satu divisi memiliki banyak karyawan (relasi 1 ke banyak)."""
from validasi import teks_wajib


class Divisi:
    def __init__(self, kode, nama, deskripsi=""):
        self.__kode = teks_wajib(kode, "Kode divisi").upper()
        self.__nama = ""
        self.__deskripsi = ""
        self.__daftar_karyawan = []      # referensi ke objek Karyawan (agregasi)
        self.nama = nama
        self.deskripsi = deskripsi

    # ---- encapsulation ----
    @property
    def kode(self):
        return self.__kode

    @property
    def nama(self):
        return self.__nama

    @nama.setter
    def nama(self, nilai):
        self.__nama = teks_wajib(nilai, "Nama divisi")

    @property
    def deskripsi(self):
        return self.__deskripsi

    @deskripsi.setter
    def deskripsi(self, nilai):
        self.__deskripsi = str(nilai).strip()

    @property
    def anggota(self):
        """Salinan read-only daftar karyawan, supaya list asli tidak dimanipulasi dari luar."""
        return tuple(self.__daftar_karyawan)

    @property
    def jumlah_karyawan(self):
        return len(self.__daftar_karyawan)

    # ---- relasi dengan Karyawan ----
    def tambah_karyawan(self, karyawan):
        karyawan.divisi = self           # setter Karyawan yang menjaga kedua sisi relasi tetap sinkron

    def keluarkan_karyawan(self, karyawan):
        if karyawan.divisi is not self:
            raise ValueError(f"{karyawan.nama} bukan anggota divisi {self.__nama}.")
        karyawan.divisi = None

    def _daftarkan(self, karyawan):
        """Dipanggil internal oleh Karyawan.divisi; jangan dipanggil langsung."""
        if karyawan not in self.__daftar_karyawan:
            self.__daftar_karyawan.append(karyawan)

    def _lepas(self, karyawan):
        """Dipanggil internal oleh Karyawan.divisi; jangan dipanggil langsung."""
        if karyawan in self.__daftar_karyawan:
            self.__daftar_karyawan.remove(karyawan)

    def total_gaji_pokok(self):
        return sum(k.gaji_pokok for k in self.__daftar_karyawan)

    def __str__(self):
        return f"[{self.__kode}] {self.__nama} - {self.jumlah_karyawan} karyawan"
