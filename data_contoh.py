"""Data contoh agar seluruh fitur bisa langsung dicoba tanpa mengetik data satu per satu."""
from datetime import date, timedelta

from absensi import StatusAbsensi
from divisi import Divisi
from karyawan import KaryawanKontrak, KaryawanMagang, KaryawanTetap


def periode_bulan_lalu(hari_ini=None):
    """Mengembalikan (bulan, tahun) bulan sebelum hari ini."""
    hari_ini = hari_ini or date.today()
    if hari_ini.month == 1:
        return 12, hari_ini.year - 1
    return hari_ini.month - 1, hari_ini.year


def muat_data_contoh(pengelola):
    """Isi pengelola dengan 3 divisi, 5 karyawan, dan absensi bulan lalu. Mengembalikan (bulan, tahun)."""
    it = pengelola.tambah_divisi(Divisi("IT", "Teknologi Informasi", "Pengembangan dan infrastruktur sistem"))
    keu = pengelola.tambah_divisi(Divisi("KEU", "Keuangan", "Akuntansi dan penggajian"))
    hrd = pengelola.tambah_divisi(Divisi("HRD", "Sumber Daya Manusia", "Rekrutmen dan kepegawaian"))

    h = date.today()
    pengelola.tambah_karyawan(KaryawanTetap("K001", "Budi Santoso", date(h.year - 5, 3, 1), 8_000_000,
                                            tunjangan_jabatan=2_000_000, divisi=it))
    pengelola.tambah_karyawan(KaryawanTetap("K002", "Siti Aminah", date(h.year - 2, 7, 15), 7_000_000,
                                            tunjangan_jabatan=1_000_000, divisi=keu))
    pengelola.tambah_karyawan(KaryawanKontrak("K003", "Andi Wijaya", date(h.year - 1, 6, 1), 5_000_000,
                                              uang_makan_per_hari=30_000, divisi=it))
    pengelola.tambah_karyawan(KaryawanKontrak("K004", "Dewi Lestari", date(h.year - 1, 2, 10), 4_500_000,
                                              uang_makan_per_hari=25_000, divisi=hrd))
    pengelola.tambah_karyawan(KaryawanMagang("K005", "Rizky Pratama", date(h.year - 1, 9, 1), 1_500_000,
                                             uang_transport_per_hari=20_000, divisi=it))

    bulan, tahun = periode_bulan_lalu(h)
    hari_kerja = []
    tanggal = date(tahun, bulan, 1)
    while tanggal.month == bulan:
        if tanggal.weekday() < 5:                      # Senin-Jumat
            hari_kerja.append(tanggal)
        tanggal += timedelta(days=1)

    pengecualian = {                                   # urutan hari kerja ke-n -> status
        "K001": {3: StatusAbsensi.IZIN},
        "K002": {5: StatusAbsensi.SAKIT, 12: StatusAbsensi.ALPHA},
        "K003": {2: StatusAbsensi.ALPHA, 9: StatusAbsensi.ALPHA},
        "K004": {},
        "K005": {7: StatusAbsensi.IZIN},
    }
    for id_karyawan, khusus in pengecualian.items():
        for urutan, hari in enumerate(hari_kerja, start=1):
            pengelola.catat_absensi(id_karyawan, hari, khusus.get(urutan, StatusAbsensi.HADIR))
    return bulan, tahun
