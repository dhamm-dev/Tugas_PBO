
import sys
from datetime import date

from absensi import NAMA_BULAN, StatusAbsensi
from data_contoh import muat_data_contoh, periode_bulan_lalu
from divisi import Divisi
from gaji import format_rupiah
from karyawan import KaryawanKontrak, KaryawanMagang, KaryawanTetap
from pengelola import PengelolaKaryawan

# Registri jenis karyawan: menambah jenis baru cukup menambah satu baris di sini
JENIS_KARYAWAN = {"1": KaryawanTetap, "2": KaryawanKontrak, "3": KaryawanMagang}


# ===================== helper input / output =====================
def garis(judul=""):
    print("\n" + "=" * 64)
    if judul:
        print(judul.center(64))
        print("=" * 64)


def input_teks(prompt, boleh_kosong=False):
    nilai = input(prompt).strip()
    if not nilai and not boleh_kosong:
        raise ValueError("Input tidak boleh kosong.")
    return nilai


def input_angka(prompt):
    teks = input(prompt).strip()
    try:
        return float(teks)
    except ValueError:
        raise ValueError(f"'{teks}' bukan angka yang valid.")


def input_bulat(prompt, default=None):
    teks = input(prompt).strip()
    if not teks and default is not None:
        return default
    try:
        return int(teks)
    except ValueError:
        raise ValueError(f"'{teks}' bukan bilangan bulat yang valid.")


def input_tanggal(prompt, default_hari_ini=False):
    teks = input(prompt).strip()
    if not teks and default_hari_ini:
        return date.today()
    try:
        return date.fromisoformat(teks)
    except ValueError:
        raise ValueError("Format tanggal harus YYYY-MM-DD, contoh 2024-03-15.")


def input_periode():
    bulan_default, tahun_default = periode_bulan_lalu()
    bulan = input_bulat(f"Bulan 1-12 [{bulan_default}]: ", bulan_default)
    tahun = input_bulat(f"Tahun [{tahun_default}]: ", tahun_default)
    return bulan, tahun


def cetak_karyawan(daftar):
    if not daftar:
        print("(belum ada data karyawan)")
        return
    print(f"{'ID':<6}{'Nama':<20}{'Jenis':<18}{'Divisi':<22}{'Tgl masuk':<12}{'Gaji pokok':>14}")
    print("-" * 92)
    for k in daftar:
        divisi = k.divisi.nama if k.divisi else "-"
        print(f"{k.id_karyawan:<6}{k.nama[:19]:<20}{k.JENIS:<18}{divisi[:21]:<22}"
              f"{k.tanggal_masuk.isoformat():<12}{format_rupiah(k.gaji_pokok):>14}")


def cetak_divisi(daftar):
    if not daftar:
        print("(belum ada data divisi)")
        return
    for d in daftar:
        print(f"{d}  | Total gaji pokok: {format_rupiah(d.total_gaji_pokok())}")


# ===================== menu divisi =====================
def divisi_tambah(p):
    kode = input_teks("Kode divisi        : ")
    nama = input_teks("Nama divisi        : ")
    deskripsi = input_teks("Deskripsi (opsional): ", boleh_kosong=True)
    p.tambah_divisi(Divisi(kode, nama, deskripsi))
    print("Divisi berhasil ditambahkan.")


def divisi_lihat(p):
    cetak_divisi(p.daftar_divisi())


def divisi_detail(p):
    divisi = p.cari_divisi(input_teks("Kode divisi: "))
    print(f"{divisi}\nDeskripsi: {divisi.deskripsi or '-'}")
    cetak_karyawan(divisi.anggota)


def divisi_ubah(p):
    kode = input_teks("Kode divisi yang diubah: ")
    nama = input_teks("Nama baru (kosong = tetap)      : ", boleh_kosong=True)
    deskripsi = input_teks("Deskripsi baru (kosong = tetap): ", boleh_kosong=True)
    p.ubah_divisi(kode, nama or None, deskripsi or None)
    print("Divisi berhasil diubah.")


def divisi_hapus(p):
    p.hapus_divisi(input_teks("Kode divisi yang dihapus: "))
    print("Divisi berhasil dihapus.")


MENU_DIVISI = {"1": ("Tambah divisi", divisi_tambah), "2": ("Lihat semua divisi", divisi_lihat),
               "3": ("Detail divisi + anggota", divisi_detail), "4": ("Ubah divisi", divisi_ubah),
               "5": ("Hapus divisi", divisi_hapus)}


# ===================== menu karyawan =====================
def karyawan_tambah(p):
    print("Jenis karyawan:")
    for kode, kelas in JENIS_KARYAWAN.items():
        print(f"  {kode}. {kelas.JENIS}")
    pilihan = input_teks("Pilih jenis: ")
    if pilihan not in JENIS_KARYAWAN:
        raise ValueError("Jenis karyawan tidak tersedia.")
    kelas = JENIS_KARYAWAN[pilihan]

    id_karyawan = input_teks("ID karyawan                : ")
    nama = input_teks("Nama                       : ")
    tanggal_masuk = input_tanggal("Tanggal masuk (YYYY-MM-DD): ")
    label_gaji = "Uang saku (Rp)" if kelas is KaryawanMagang else "Gaji pokok (Rp)"
    gaji_pokok = input_angka(f"{label_gaji:<27}: ")
    tambahan = {atribut: input_angka(f"{label:<27}: ") for atribut, label in kelas.field_tambahan()}
    kode_divisi = input_teks("Kode divisi (kosong = tanpa): ", boleh_kosong=True)
    divisi = p.cari_divisi(kode_divisi) if kode_divisi else None   # validasi dulu sebelum objek dibuat

    karyawan = kelas(id_karyawan, nama, tanggal_masuk, gaji_pokok, **tambahan)  # polymorphic construction
    p.tambah_karyawan(karyawan)
    if divisi:
        p.pindah_divisi(karyawan.id_karyawan, divisi.kode)
    print("Karyawan berhasil ditambahkan.")


def karyawan_lihat(p):
    cetak_karyawan(p.daftar_karyawan())


def karyawan_detail(p):
    karyawan = p.cari_karyawan(input_teks("ID karyawan: "))
    print(karyawan.ringkasan())                       # method yang di-override tiap subclass
    print("Masa kerja:", karyawan.masa_kerja_teks())


def karyawan_ubah(p):
    karyawan = p.cari_karyawan(input_teks("ID karyawan yang diubah: "))
    print(f"Mengubah: {karyawan.nama}. Kosongkan isian bila tidak ingin mengubah.")
    perubahan = {}
    nama = input_teks("Nama baru                     : ", boleh_kosong=True)
    if nama:
        perubahan["nama"] = nama
    gaji = input_teks("Gaji pokok / uang saku baru   : ", boleh_kosong=True)
    if gaji:
        perubahan["gaji_pokok"] = input_angka_dari(gaji)
    tanggal = input_teks("Tanggal masuk baru (YYYY-MM-DD): ", boleh_kosong=True)
    if tanggal:
        perubahan["tanggal_masuk"] = tanggal_dari(tanggal)
    for atribut, label in type(karyawan).field_tambahan():
        nilai = input_teks(f"{label} baru: ", boleh_kosong=True)
        if nilai:
            perubahan[atribut] = input_angka_dari(nilai)
    p.ubah_karyawan(karyawan.id_karyawan, **perubahan)
    print("Data karyawan berhasil diubah.")


def input_angka_dari(teks):
    try:
        return float(teks)
    except ValueError:
        raise ValueError(f"'{teks}' bukan angka yang valid.")


def tanggal_dari(teks):
    try:
        return date.fromisoformat(teks)
    except ValueError:
        raise ValueError("Format tanggal harus YYYY-MM-DD.")


def karyawan_pindah(p):
    id_karyawan = input_teks("ID karyawan: ")
    kode = input_teks("Kode divisi tujuan (kosong = tanpa divisi): ", boleh_kosong=True)
    p.pindah_divisi(id_karyawan, kode)
    print("Karyawan berhasil dipindahkan.")


def karyawan_hapus(p):
    karyawan = p.cari_karyawan(input_teks("ID karyawan yang dihapus: "))
    if input_teks(f"Yakin hapus {karyawan.nama} beserta absensinya? (y/n): ").lower() == "y":
        p.hapus_karyawan(karyawan.id_karyawan)
        print("Karyawan berhasil dihapus.")
    else:
        print("Dibatalkan.")


MENU_KARYAWAN = {"1": ("Tambah karyawan", karyawan_tambah), "2": ("Lihat semua karyawan", karyawan_lihat),
                 "3": ("Detail karyawan", karyawan_detail), "4": ("Ubah data karyawan", karyawan_ubah),
                 "5": ("Pindah divisi", karyawan_pindah), "6": ("Hapus karyawan", karyawan_hapus)}


# ===================== menu absensi =====================
def absensi_catat(p):
    id_karyawan = input_teks("ID karyawan                          : ")
    tanggal = input_tanggal("Tanggal YYYY-MM-DD [hari ini]         : ", default_hari_ini=True)
    status = StatusAbsensi.dari_teks(input_teks("Status (Hadir/Izin/Sakit/Alpha)        : "))
    keterangan = input_teks("Keterangan (opsional)                : ", boleh_kosong=True)
    p.catat_absensi(id_karyawan, tanggal, status, keterangan)
    print("Absensi berhasil dicatat.")


def absensi_lihat(p):
    id_karyawan = input_teks("ID karyawan: ")
    bulan, tahun = input_periode()
    catatan = p.daftar_absensi(id_karyawan, bulan, tahun)
    if not catatan:
        print("(tidak ada catatan absensi pada periode ini)")
    for a in catatan:
        print(" ", a)


def absensi_rekap(p):
    id_karyawan = input_teks("ID karyawan: ")
    bulan, tahun = input_periode()
    r = p.buat_rekap(id_karyawan, bulan, tahun)
    print(f"Rekap {r.nama_periode}: Hadir {r.hadir} | Izin {r.izin} | Sakit {r.sakit} | Alpha {r.alpha}")


def absensi_hapus(p):
    p.hapus_absensi(input_teks("ID karyawan: "), input_tanggal("Tanggal YYYY-MM-DD: "))
    print("Catatan absensi dihapus.")


MENU_ABSENSI = {"1": ("Catat absensi", absensi_catat), "2": ("Lihat absensi per bulan", absensi_lihat),
                "3": ("Rekap absensi bulanan", absensi_rekap), "4": ("Hapus catatan absensi", absensi_hapus)}


# ===================== menu gaji & masa kerja =====================
def gaji_slip(p):
    id_karyawan = input_teks("ID karyawan: ")
    bulan, tahun = input_periode()
    print(p.slip_gaji(id_karyawan, bulan, tahun))


def cetak_laporan_gaji(p, bulan, tahun):
    print(f"\nLAPORAN GAJI {NAMA_BULAN[bulan - 1].upper()} {tahun}")
    print(f"{'ID':<6}{'Nama':<20}{'Jenis':<18}{'Pendapatan':>14}{'Potongan':>13}{'Gaji bersih':>15}")
    print("-" * 86)
    for k, r in p.laporan_gaji(bulan, tahun):
        print(f"{k.id_karyawan:<6}{k.nama[:19]:<20}{k.JENIS:<18}{format_rupiah(r.total_pendapatan):>14}"
              f"{format_rupiah(r.total_potongan):>13}{format_rupiah(r.gaji_bersih):>15}")
    print("-" * 86)
    print(f"{'TOTAL PENGGAJIAN':<64}{format_rupiah(p.total_penggajian(bulan, tahun)):>22}")


def gaji_laporan(p):
    bulan, tahun = input_periode()
    cetak_laporan_gaji(p, bulan, tahun)


MENU_GAJI = {"1": ("Slip gaji satu karyawan", gaji_slip), "2": ("Laporan gaji semua karyawan", gaji_laporan)}


def cetak_laporan_masa_kerja(p):
    print(f"\nMASA KERJA PER {date.today().isoformat()}")
    print(f"{'ID':<6}{'Nama':<20}{'Tgl masuk':<12}{'Masa kerja'}")
    print("-" * 64)
    for k, (tahun, bulan, hari) in p.laporan_masa_kerja():
        print(f"{k.id_karyawan:<6}{k.nama[:19]:<20}{k.tanggal_masuk.isoformat():<12}"
              f"{tahun} tahun {bulan} bulan {hari} hari")


def masa_kerja_laporan(p):
    cetak_laporan_masa_kerja(p)


def masa_kerja_satu(p):
    karyawan = p.cari_karyawan(input_teks("ID karyawan: "))
    print(f"{karyawan.nama}: {karyawan.masa_kerja_teks()}")


MENU_MASA_KERJA = {"1": ("Masa kerja semua karyawan", masa_kerja_laporan),
                   "2": ("Masa kerja satu karyawan", masa_kerja_satu)}


def muat_contoh(p):
    if p.daftar_karyawan() or p.daftar_divisi():
        raise ValueError("Data contoh hanya dapat dimuat saat sistem masih kosong.")
    bulan, tahun = muat_data_contoh(p)
    print(f"Data contoh dimuat (5 karyawan, 3 divisi, absensi {NAMA_BULAN[bulan - 1]} {tahun}).")


# ===================== menu runner =====================
def jalankan_menu(judul, pilihan, pengelola, label_kembali="Kembali"):
    """Menu generik: dictionary dispatch menggantikan rantai if-elif."""
    while True:
        garis(judul)
        for kode, (label, _) in pilihan.items():
            print(f"  {kode}. {label}")
        print(f"  0. {label_kembali}")
        pilih = input("Pilih menu: ").strip()
        if pilih == "0":
            return
        if pilih not in pilihan:
            print("[!] Menu tidak tersedia.")
            continue
        try:
            pilihan[pilih][1](pengelola)
        except ValueError as error:
            print(f"[!] {error}")


def buat_menu_utama():
    return {
        "1": ("Kelola Divisi", lambda p: jalankan_menu("KELOLA DIVISI", MENU_DIVISI, p)),
        "2": ("Kelola Karyawan", lambda p: jalankan_menu("KELOLA KARYAWAN", MENU_KARYAWAN, p)),
        "3": ("Absensi", lambda p: jalankan_menu("ABSENSI", MENU_ABSENSI, p)),
        "4": ("Gaji", lambda p: jalankan_menu("PENGELOLAAN GAJI", MENU_GAJI, p)),
        "5": ("Masa Kerja", lambda p: jalankan_menu("MASA KERJA", MENU_MASA_KERJA, p)),
        "6": ("Muat data contoh", muat_contoh),
    }


# ===================== demo otomatis =====================
def jalankan_demo():
    p = PengelolaKaryawan("PT Nusantara Maju")
    bulan, tahun = muat_data_contoh(p)

    garis("1. DATA DIVISI"); cetak_divisi(p.daftar_divisi())
    garis("2. DATA KARYAWAN (satu list, tiga jenis objek)"); cetak_karyawan(p.daftar_karyawan())
    garis("3. RINGKASAN (method ringkasan() di-override tiap subclass)")
    for k in p.daftar_karyawan():
        print(" ", k.ringkasan())
    garis("4. MASA KERJA"); cetak_laporan_masa_kerja(p)
    garis("5. LAPORAN GAJI (polymorphism: satu loop, tiga rumus)"); cetak_laporan_gaji(p, bulan, tahun)
    garis("6. SLIP GAJI")
    for id_karyawan in ("K001", "K003", "K005"):
        print(p.slip_gaji(id_karyawan, bulan, tahun))
        print()
    garis("7. CRUD & VALIDASI")
    p.ubah_karyawan("K003", gaji_pokok=5_500_000, uang_makan_per_hari=35_000)
    print("Ubah K003     :", p.cari_karyawan("K003").ringkasan())
    p.pindah_divisi("K003", "HRD")
    print("Pindah K003   :", p.cari_divisi("HRD"))
    percobaan = {
        "Hapus divisi berisi karyawan": lambda: p.hapus_divisi("IT"),
        "Gaji pokok negatif": lambda: KaryawanTetap("K099", "Uji", date(2020, 1, 1), -1),
        "Tanggal masuk masa depan": lambda: KaryawanTetap("K099", "Uji", date(2999, 1, 1), 1),
        "ID duplikat": lambda: p.tambah_karyawan(KaryawanMagang("K001", "Uji", date(2020, 1, 1), 1)),
        "Instansiasi class abstrak": lambda: __import__("karyawan").Karyawan("K100", "Uji", date(2020, 1, 1), 1),
    }
    for nama, aksi in percobaan.items():
        try:
            aksi()
            print(f"{nama}: [TIDAK ADA ERROR - periksa kode!]")
        except (ValueError, TypeError) as error:
            print(f"{nama}: ditolak -> {error}")
    p.hapus_karyawan("K005")
    print("Hapus K005    : sisa karyawan =", len(p.daftar_karyawan()),
          "| anggota IT =", p.cari_divisi("IT").jumlah_karyawan)


# ===================== entry point =====================
def main():
    if "--demo" in sys.argv:
        jalankan_demo()
        return
    pengelola = PengelolaKaryawan("PT Nusantara Maju")
    print("SISTEM PENGELOLAAN KARYAWAN - PT Nusantara Maju")
    try:
        jalankan_menu("MENU UTAMA", buat_menu_utama(), pengelola, label_kembali="Keluar")
    except (KeyboardInterrupt, EOFError):
        pass
    print("\nTerima kasih. Program selesai.")


if __name__ == "__main__":
    main()
