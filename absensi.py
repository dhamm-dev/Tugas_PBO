"""Pencatatan absensi: status, catatan harian, dan rekap bulanan."""
import calendar
from dataclasses import dataclass
from datetime import date
from enum import Enum

NAMA_BULAN = ("Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli",
              "Agustus", "September", "Oktober", "November", "Desember")


class StatusAbsensi(Enum):
    HADIR = "Hadir"
    IZIN = "Izin"
    SAKIT = "Sakit"
    ALPHA = "Alpha"

    @classmethod
    def dari_teks(cls, teks):
        kunci = str(teks).strip().upper()
        for status in cls:
            if status.name == kunci:
                return status
        pilihan = ", ".join(s.value for s in cls)
        raise ValueError(f"Status absensi tidak dikenal: '{teks}'. Pilihan: {pilihan}.")


class Absensi:
    """Satu catatan kehadiran seorang karyawan pada satu tanggal (read-only)."""

    def __init__(self, id_karyawan, tanggal, status, keterangan=""):
        if not isinstance(tanggal, date):
            raise ValueError("Tanggal absensi harus bertipe date.")
        if not isinstance(status, StatusAbsensi):
            raise ValueError("Status absensi harus bertipe StatusAbsensi.")
        self.__id_karyawan = id_karyawan
        self.__tanggal = tanggal
        self.__status = status
        self.__keterangan = str(keterangan).strip()

    @property
    def id_karyawan(self):
        return self.__id_karyawan

    @property
    def tanggal(self):
        return self.__tanggal

    @property
    def status(self):
        return self.__status

    @property
    def keterangan(self):
        return self.__keterangan

    def __str__(self):
        ket = f" ({self.__keterangan})" if self.__keterangan else ""
        return f"{self.__tanggal.isoformat()} | {self.__status.value}{ket}"


@dataclass(frozen=True)
class RekapAbsensi:
    """Ringkasan jumlah hari per status dalam satu bulan."""
    bulan: int
    tahun: int
    hadir: int = 0
    izin: int = 0
    sakit: int = 0
    alpha: int = 0

    def __post_init__(self):
        if not 1 <= self.bulan <= 12:
            raise ValueError("Bulan harus antara 1 sampai 12.")
        if not 1 <= self.tahun <= 9999:
            raise ValueError("Tahun tidak valid.")
        if min(self.hadir, self.izin, self.sakit, self.alpha) < 0:
            raise ValueError("Jumlah hari tidak boleh negatif.")

    @property
    def akhir_periode(self):
        return date(self.tahun, self.bulan, calendar.monthrange(self.tahun, self.bulan)[1])

    @property
    def nama_periode(self):
        return f"{NAMA_BULAN[self.bulan - 1]} {self.tahun}"
