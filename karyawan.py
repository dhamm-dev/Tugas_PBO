"""Hierarki class karyawan.

Abstraction    : Karyawan adalah abstract class, hitung_gaji() adalah kontrak tanpa implementasi.
Encapsulation  : atribut private (__) + property dengan validasi.
Inheritance    : KaryawanTetap, KaryawanKontrak, KaryawanMagang memakai super().__init__().
Overriding     : hitung_gaji(), ringkasan(), field_tambahan() ditimpa di tiap subclass.
"""
import calendar
from abc import ABC, abstractmethod
from datetime import date

from divisi import Divisi
from gaji import (BONUS_MAKSIMAL, BONUS_PER_TAHUN, HARI_KERJA_PER_BULAN, TARIF_PAJAK,
                  RincianGaji, bulatkan, format_rupiah)
from validasi import nominal_tidak_negatif, teks_wajib


class Karyawan(ABC):
    JENIS = "Karyawan"

    def __init__(self, id_karyawan, nama, tanggal_masuk, gaji_pokok, divisi=None):
        self.__id_karyawan = teks_wajib(id_karyawan, "ID karyawan").upper()
        self.__nama = ""
        self.__tanggal_masuk = None
        self.__gaji_pokok = 0
        self.__divisi = None
        self.nama = nama                      # lewat setter -> tervalidasi
        self.tanggal_masuk = tanggal_masuk
        self.gaji_pokok = gaji_pokok
        self.divisi = divisi

    # ---------- encapsulation ----------
    @property
    def id_karyawan(self):
        return self.__id_karyawan             # read-only: ID tidak boleh berubah

    @property
    def nama(self):
        return self.__nama

    @nama.setter
    def nama(self, nilai):
        self.__nama = teks_wajib(nilai, "Nama karyawan")

    @property
    def tanggal_masuk(self):
        return self.__tanggal_masuk

    @tanggal_masuk.setter
    def tanggal_masuk(self, nilai):
        if not isinstance(nilai, date):
            raise ValueError("Tanggal masuk harus bertipe date.")
        if nilai > date.today():
            raise ValueError("Tanggal masuk tidak boleh di masa depan.")
        self.__tanggal_masuk = nilai

    @property
    def gaji_pokok(self):
        return self.__gaji_pokok

    @gaji_pokok.setter
    def gaji_pokok(self, nilai):
        self.__gaji_pokok = nominal_tidak_negatif(nilai, "Gaji pokok")

    @property
    def divisi(self):
        return self.__divisi

    @divisi.setter
    def divisi(self, nilai):
        """Pindah divisi; kedua sisi relasi (Karyawan <-> Divisi) diperbarui sekaligus."""
        if nilai is not None and not isinstance(nilai, Divisi):
            raise ValueError("Divisi harus bertipe Divisi atau None.")
        if nilai is self.__divisi:
            return
        if self.__divisi is not None:
            self.__divisi._lepas(self)
        self.__divisi = nilai
        if nilai is not None:
            nilai._daftarkan(self)

    # ---------- masa kerja ----------
    def hitung_masa_kerja(self, per_tanggal=None):
        """Masa kerja dari tanggal masuk sampai per_tanggal (default: hari ini).

        Mengembalikan tuple (tahun, bulan, hari).
        """
        acuan = per_tanggal or date.today()
        masuk = self.__tanggal_masuk
        if acuan < masuk:
            raise ValueError(f"{self.__nama} belum masuk kerja pada {acuan.isoformat()}.")
        total_bulan = (acuan.year - masuk.year) * 12 + (acuan.month - masuk.month)
        if acuan.day < masuk.day:
            total_bulan -= 1
        tahun_a, bulan_a = divmod(masuk.month - 1 + total_bulan, 12)
        tahun_a += masuk.year
        bulan_a += 1
        hari_a = min(masuk.day, calendar.monthrange(tahun_a, bulan_a)[1])
        hari = (acuan - date(tahun_a, bulan_a, hari_a)).days
        return total_bulan // 12, total_bulan % 12, hari

    def masa_kerja_tahun(self, per_tanggal=None):
        return self.hitung_masa_kerja(per_tanggal)[0]

    def masa_kerja_teks(self, per_tanggal=None):
        tahun, bulan, hari = self.hitung_masa_kerja(per_tanggal)
        return f"{tahun} tahun {bulan} bulan {hari} hari"

    # ---------- abstraction ----------
    @abstractmethod
    def hitung_gaji(self, rekap):
        """Kontrak: setiap jenis karyawan wajib menghitung gaji dengan aturannya sendiri.

        rekap : RekapAbsensi bulan yang dihitung. Mengembalikan RincianGaji.
        """

    @classmethod
    def field_tambahan(cls):
        """Daftar (nama_atribut, label) komponen khusus tiap jenis; ditimpa di subclass."""
        return ()

    # ---------- helper untuk subclass ----------
    def _potongan_alpha(self, rekap):
        if rekap.alpha == 0:
            return {}
        per_hari = self.__gaji_pokok / HARI_KERJA_PER_BULAN
        return {f"Potongan alpha ({rekap.alpha} hari)": bulatkan(per_hari * rekap.alpha)}

    @staticmethod
    def _potongan_pajak(bruto):
        if TARIF_PAJAK <= 0:
            return {}
        return {f"Pajak/BPJS ({TARIF_PAJAK:.0%})": bulatkan(bruto * TARIF_PAJAK)}

    # ---------- tampilan ----------
    def ringkasan(self):
        divisi = self.__divisi.nama if self.__divisi else "-"
        return (f"[{self.__id_karyawan}] {self.__nama} | {self.JENIS} | Divisi: {divisi} | "
                f"Masuk: {self.__tanggal_masuk.isoformat()} | Gaji pokok: {format_rupiah(self.__gaji_pokok)}")

    def __str__(self):
        return self.ringkasan()


class KaryawanTetap(Karyawan):
    """Gaji pokok + tunjangan jabatan + bonus masa kerja - potongan alpha."""
    JENIS = "Karyawan Tetap"

    def __init__(self, id_karyawan, nama, tanggal_masuk, gaji_pokok, tunjangan_jabatan=0, divisi=None):
        super().__init__(id_karyawan, nama, tanggal_masuk, gaji_pokok, divisi)
        self.__tunjangan_jabatan = 0
        self.tunjangan_jabatan = tunjangan_jabatan

    @property
    def tunjangan_jabatan(self):
        return self.__tunjangan_jabatan

    @tunjangan_jabatan.setter
    def tunjangan_jabatan(self, nilai):
        self.__tunjangan_jabatan = nominal_tidak_negatif(nilai, "Tunjangan jabatan")

    @classmethod
    def field_tambahan(cls):
        return (("tunjangan_jabatan", "Tunjangan jabatan (Rp)"),)

    def hitung_gaji(self, rekap):
        tahun = self.masa_kerja_tahun(rekap.akhir_periode)
        persen = min(tahun * BONUS_PER_TAHUN, BONUS_MAKSIMAL)
        pendapatan = {
            "Gaji pokok": bulatkan(self.gaji_pokok),
            "Tunjangan jabatan": bulatkan(self.tunjangan_jabatan),
            f"Bonus masa kerja ({persen}%)": bulatkan(self.gaji_pokok * persen / 100),
        }
        potongan = self._potongan_alpha(rekap)
        potongan.update(self._potongan_pajak(sum(pendapatan.values())))
        return RincianGaji(pendapatan, potongan)

    def ringkasan(self):
        return super().ringkasan() + f" | Tunjangan: {format_rupiah(self.__tunjangan_jabatan)}"


class KaryawanKontrak(Karyawan):
    """Gaji pokok + uang makan per hari hadir - potongan alpha."""
    JENIS = "Karyawan Kontrak"

    def __init__(self, id_karyawan, nama, tanggal_masuk, gaji_pokok, uang_makan_per_hari=0, divisi=None):
        super().__init__(id_karyawan, nama, tanggal_masuk, gaji_pokok, divisi)
        self.__uang_makan_per_hari = 0
        self.uang_makan_per_hari = uang_makan_per_hari

    @property
    def uang_makan_per_hari(self):
        return self.__uang_makan_per_hari

    @uang_makan_per_hari.setter
    def uang_makan_per_hari(self, nilai):
        self.__uang_makan_per_hari = nominal_tidak_negatif(nilai, "Uang makan per hari")

    @classmethod
    def field_tambahan(cls):
        return (("uang_makan_per_hari", "Uang makan per hari (Rp)"),)

    def hitung_gaji(self, rekap):
        self.masa_kerja_tahun(rekap.akhir_periode)    # memastikan sudah bekerja pada periode ini
        pendapatan = {
            "Gaji pokok": bulatkan(self.gaji_pokok),
            f"Uang makan ({rekap.hadir} hari)": bulatkan(self.uang_makan_per_hari * rekap.hadir),
        }
        potongan = self._potongan_alpha(rekap)
        potongan.update(self._potongan_pajak(sum(pendapatan.values())))
        return RincianGaji(pendapatan, potongan)

    def ringkasan(self):
        return super().ringkasan() + f" | Uang makan/hari: {format_rupiah(self.__uang_makan_per_hari)}"


class KaryawanMagang(Karyawan):
    """Uang saku tetap (disimpan di gaji_pokok) + uang transport per hari hadir. Tanpa potongan alpha."""
    JENIS = "Karyawan Magang"

    def __init__(self, id_karyawan, nama, tanggal_masuk, gaji_pokok, uang_transport_per_hari=0, divisi=None):
        super().__init__(id_karyawan, nama, tanggal_masuk, gaji_pokok, divisi)
        self.__uang_transport_per_hari = 0
        self.uang_transport_per_hari = uang_transport_per_hari

    @property
    def uang_transport_per_hari(self):
        return self.__uang_transport_per_hari

    @uang_transport_per_hari.setter
    def uang_transport_per_hari(self, nilai):
        self.__uang_transport_per_hari = nominal_tidak_negatif(nilai, "Uang transport per hari")

    @classmethod
    def field_tambahan(cls):
        return (("uang_transport_per_hari", "Uang transport per hari (Rp)"),)

    def hitung_gaji(self, rekap):
        self.masa_kerja_tahun(rekap.akhir_periode)
        pendapatan = {
            "Uang saku": bulatkan(self.gaji_pokok),
            f"Uang transport ({rekap.hadir} hari)": bulatkan(self.uang_transport_per_hari * rekap.hadir),
        }
        return RincianGaji(pendapatan, self._potongan_pajak(sum(pendapatan.values())))

    def ringkasan(self):
        return super().ringkasan() + f" | Transport/hari: {format_rupiah(self.__uang_transport_per_hari)}"
