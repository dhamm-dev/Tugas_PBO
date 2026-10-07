"""PengelolaKaryawan: class pengelola aplikasi (setara ParkirApp pada slide).

Composition  : pengelola membuat dan memiliki list divisi, karyawan, dan absensi.
Polymorphism : list karyawan bertipe Karyawan (superclass) berisi Tetap/Kontrak/Magang;
               k.hitung_gaji(rekap) memilih rumus yang tepat saat runtime tanpa if-else tipe.
"""
from collections import Counter
from datetime import date

from absensi import Absensi, RekapAbsensi, StatusAbsensi
from divisi import Divisi
from gaji import format_rupiah
from karyawan import Karyawan
from validasi import teks_wajib


def _kunci(teks):
    return str(teks).strip().upper()


class PengelolaKaryawan:
    def __init__(self, nama_perusahaan="PT Nusantara Maju"):
        self.__nama_perusahaan = teks_wajib(nama_perusahaan, "Nama perusahaan")
        self.__daftar_divisi = []          # list[Divisi]
        self.__daftar_karyawan = []        # list[Karyawan] -> berisi berbagai subclass
        self.__daftar_absensi = []         # list[Absensi]

    @property
    def nama_perusahaan(self):
        return self.__nama_perusahaan

    # ================= CRUD DIVISI =================
    def tambah_divisi(self, divisi):
        if not isinstance(divisi, Divisi):
            raise ValueError("Objek harus bertipe Divisi.")
        if self.__temukan_divisi(divisi.kode):
            raise ValueError(f"Kode divisi {divisi.kode} sudah digunakan.")
        self.__daftar_divisi.append(divisi)
        return divisi

    def cari_divisi(self, kode):
        divisi = self.__temukan_divisi(kode)
        if divisi is None:
            raise ValueError(f"Divisi dengan kode '{_kunci(kode)}' tidak ditemukan.")
        return divisi

    def daftar_divisi(self):
        return tuple(self.__daftar_divisi)

    def ubah_divisi(self, kode, nama=None, deskripsi=None):
        divisi = self.cari_divisi(kode)
        if nama is not None:
            divisi.nama = nama
        if deskripsi is not None:
            divisi.deskripsi = deskripsi
        return divisi

    def hapus_divisi(self, kode):
        divisi = self.cari_divisi(kode)
        if divisi.jumlah_karyawan > 0:
            raise ValueError(f"Divisi {divisi.nama} masih memiliki {divisi.jumlah_karyawan} karyawan. "
                             "Pindahkan atau hapus karyawannya terlebih dahulu.")
        self.__daftar_divisi.remove(divisi)

    # ================= CRUD KARYAWAN =================
    def tambah_karyawan(self, karyawan):
        if not isinstance(karyawan, Karyawan):
            raise ValueError("Objek harus bertipe Karyawan.")
        if self.__temukan_karyawan(karyawan.id_karyawan):
            raise ValueError(f"ID karyawan {karyawan.id_karyawan} sudah digunakan.")
        if karyawan.divisi is not None and karyawan.divisi not in self.__daftar_divisi:
            raise ValueError("Divisi karyawan belum terdaftar di sistem.")
        self.__daftar_karyawan.append(karyawan)
        return karyawan

    def cari_karyawan(self, id_karyawan):
        karyawan = self.__temukan_karyawan(id_karyawan)
        if karyawan is None:
            raise ValueError(f"Karyawan dengan ID '{_kunci(id_karyawan)}' tidak ditemukan.")
        return karyawan

    def daftar_karyawan(self):
        return tuple(self.__daftar_karyawan)

    def ubah_karyawan(self, id_karyawan, **perubahan):
        """Ubah atribut yang diizinkan, contoh: ubah_karyawan('K001', nama='Budi', gaji_pokok=9_000_000)."""
        karyawan = self.cari_karyawan(id_karyawan)
        diizinkan = {"nama", "gaji_pokok", "tanggal_masuk"}
        diizinkan |= {nama for nama, _ in type(karyawan).field_tambahan()}
        tidak_dikenal = set(perubahan) - diizinkan
        if tidak_dikenal:
            raise ValueError(f"Atribut tidak dapat diubah: {', '.join(sorted(tidak_dikenal))}.")
        baru = perubahan.get("tanggal_masuk")
        if isinstance(baru, date):
            tanggal_absen = [a.tanggal for a in self.__daftar_absensi if a.id_karyawan == karyawan.id_karyawan]
            if tanggal_absen and baru > min(tanggal_absen):
                raise ValueError("Tanggal masuk tidak boleh lebih baru dari absensi yang sudah tercatat.")
        for nama_atribut, nilai in perubahan.items():
            setattr(karyawan, nama_atribut, nilai)
        return karyawan

    def pindah_divisi(self, id_karyawan, kode_divisi):
        """Pindahkan karyawan ke divisi lain; kode_divisi kosong/None = tanpa divisi."""
        karyawan = self.cari_karyawan(id_karyawan)
        karyawan.divisi = self.cari_divisi(kode_divisi) if kode_divisi else None
        return karyawan

    def hapus_karyawan(self, id_karyawan):
        karyawan = self.cari_karyawan(id_karyawan)
        karyawan.divisi = None                              # lepas dari divisi
        self.__daftar_karyawan.remove(karyawan)
        self.__daftar_absensi = [a for a in self.__daftar_absensi
                                 if a.id_karyawan != karyawan.id_karyawan]

    # ================= ABSENSI =================
    def catat_absensi(self, id_karyawan, tanggal, status, keterangan=""):
        karyawan = self.cari_karyawan(id_karyawan)
        catatan = Absensi(karyawan.id_karyawan, tanggal, status, keterangan)   # validasi tipe
        if tanggal > date.today():
            raise ValueError("Absensi tidak boleh dicatat untuk tanggal di masa depan.")
        if tanggal < karyawan.tanggal_masuk:
            raise ValueError(f"{karyawan.nama} baru masuk pada {karyawan.tanggal_masuk.isoformat()}.")
        if self.__temukan_absensi(karyawan.id_karyawan, tanggal):
            raise ValueError(f"Absensi {karyawan.nama} pada {tanggal.isoformat()} sudah tercatat.")
        self.__daftar_absensi.append(catatan)
        return catatan

    def hapus_absensi(self, id_karyawan, tanggal):
        karyawan = self.cari_karyawan(id_karyawan)
        catatan = self.__temukan_absensi(karyawan.id_karyawan, tanggal)
        if catatan is None:
            raise ValueError("Catatan absensi tidak ditemukan.")
        self.__daftar_absensi.remove(catatan)

    def daftar_absensi(self, id_karyawan, bulan=None, tahun=None):
        karyawan = self.cari_karyawan(id_karyawan)
        hasil = [a for a in self.__daftar_absensi
                 if a.id_karyawan == karyawan.id_karyawan
                 and (bulan is None or a.tanggal.month == bulan)
                 and (tahun is None or a.tanggal.year == tahun)]
        return sorted(hasil, key=lambda a: a.tanggal)

    def buat_rekap(self, id_karyawan, bulan, tahun):
        karyawan = self.cari_karyawan(id_karyawan)
        hitung = Counter(a.status for a in self.__daftar_absensi
                         if a.id_karyawan == karyawan.id_karyawan
                         and a.tanggal.month == bulan and a.tanggal.year == tahun)
        return RekapAbsensi(bulan, tahun,
                            hadir=hitung[StatusAbsensi.HADIR], izin=hitung[StatusAbsensi.IZIN],
                            sakit=hitung[StatusAbsensi.SAKIT], alpha=hitung[StatusAbsensi.ALPHA])

    # ================= GAJI (POLYMORPHISM) =================
    def hitung_gaji(self, id_karyawan, bulan, tahun):
        karyawan = self.cari_karyawan(id_karyawan)
        rekap = self.buat_rekap(id_karyawan, bulan, tahun)
        if karyawan.tanggal_masuk > rekap.akhir_periode:
            raise ValueError(f"{karyawan.nama} belum bekerja pada {rekap.nama_periode}.")
        return karyawan.hitung_gaji(rekap)       # dynamic dispatch: rumus mengikuti jenis objek

    def laporan_gaji(self, bulan, tahun):
        """List (karyawan, RincianGaji) untuk semua karyawan yang sudah bekerja pada periode itu."""
        hasil = []
        for karyawan in self.__daftar_karyawan:   # satu loop, banyak jenis, tanpa if-else
            rekap = self.buat_rekap(karyawan.id_karyawan, bulan, tahun)
            if karyawan.tanggal_masuk <= rekap.akhir_periode:
                hasil.append((karyawan, karyawan.hitung_gaji(rekap)))
        return hasil

    def total_penggajian(self, bulan, tahun):
        return sum(rincian.gaji_bersih for _, rincian in self.laporan_gaji(bulan, tahun))

    def slip_gaji(self, id_karyawan, bulan, tahun):
        karyawan = self.cari_karyawan(id_karyawan)
        rincian = self.hitung_gaji(id_karyawan, bulan, tahun)
        rekap = self.buat_rekap(id_karyawan, bulan, tahun)

        def baris(label, nilai):
            return f"  {label:<32}{format_rupiah(nilai):>16}"

        garis = "=" * 50
        teks = [garis, f"SLIP GAJI - {self.__nama_perusahaan}".center(50), garis,
                f"Periode    : {rekap.nama_periode}",
                f"Nama       : {karyawan.nama} ({karyawan.id_karyawan})",
                f"Jenis      : {karyawan.JENIS}",
                f"Divisi     : {karyawan.divisi.nama if karyawan.divisi else '-'}",
                f"Masa kerja : {karyawan.masa_kerja_teks(rekap.akhir_periode)} (per akhir periode)",
                f"Absensi    : Hadir {rekap.hadir} | Izin {rekap.izin} | Sakit {rekap.sakit} | Alpha {rekap.alpha}",
                "-" * 50, "PENDAPATAN"]
        teks += [baris(k, v) for k, v in rincian.pendapatan.items()]
        teks.append(baris("Total pendapatan", rincian.total_pendapatan))
        teks.append("POTONGAN")
        teks += [baris(k, v) for k, v in rincian.potongan.items()] or ["  (tidak ada potongan)"]
        teks.append(baris("Total potongan", rincian.total_potongan))
        teks += ["-" * 50, baris("GAJI BERSIH", rincian.gaji_bersih), garis]
        return "\n".join(teks)

    # ================= MASA KERJA =================
    def laporan_masa_kerja(self, per_tanggal=None):
        """List (karyawan, (tahun, bulan, hari)) untuk semua karyawan."""
        return [(k, k.hitung_masa_kerja(per_tanggal)) for k in self.__daftar_karyawan]

    # ================= helper private =================
    def __temukan_divisi(self, kode):
        for divisi in self.__daftar_divisi:
            if divisi.kode == _kunci(kode):
                return divisi
        return None

    def __temukan_karyawan(self, id_karyawan):
        for karyawan in self.__daftar_karyawan:
            if karyawan.id_karyawan == _kunci(id_karyawan):
                return karyawan
        return None

    def __temukan_absensi(self, id_karyawan, tanggal):
        for catatan in self.__daftar_absensi:
            if catatan.id_karyawan == id_karyawan and catatan.tanggal == tanggal:
                return catatan
        return None
