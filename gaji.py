"""Aturan gaji (konstanta) dan objek hasil perhitungan gaji."""
from dataclasses import dataclass

# ---- Aturan gaji (ubah di sini bila ketentuan berubah) ----
HARI_KERJA_PER_BULAN = 22      # dasar pembagi potongan alpha
BONUS_PER_TAHUN = 2            # persen gaji pokok per tahun masa kerja (Karyawan Tetap)
BONUS_MAKSIMAL = 20            # batas atas bonus masa kerja, dalam persen
TARIF_PAJAK = 0.0              # 0.0 = pajak/BPJS tidak dihitung; isi 0.05 untuk potongan flat 5%


def bulatkan(nilai):
    """Bulatkan ke rupiah terdekat."""
    return int(round(nilai))


def format_rupiah(nilai):
    """Format angka menjadi 'Rp1.250.000'."""
    return "Rp" + f"{nilai:,.0f}".replace(",", ".")


@dataclass(frozen=True)
class RincianGaji:
    """Hasil perhitungan gaji satu karyawan untuk satu periode (immutable)."""
    pendapatan: dict   # nama komponen -> nominal penambah
    potongan: dict     # nama komponen -> nominal pengurang

    @property
    def total_pendapatan(self):
        return sum(self.pendapatan.values())

    @property
    def total_potongan(self):
        return sum(self.potongan.values())

    @property
    def gaji_bersih(self):
        return max(0, self.total_pendapatan - self.total_potongan)
