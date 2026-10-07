"""Fungsi validasi sederhana yang dipakai bersama oleh semua class.

Dipakai di setter/constructor agar state objek selalu valid (enkapsulasi).
"""
import math


def teks_wajib(nilai, nama_field):
    """Pastikan nilai berupa teks tidak kosong, kembalikan versi yang sudah di-strip."""
    if not isinstance(nilai, str) or not nilai.strip():
        raise ValueError(f"{nama_field} tidak boleh kosong.")
    return nilai.strip()


def nominal_tidak_negatif(nilai, nama_field):
    """Pastikan nilai berupa angka berhingga dan tidak negatif."""
    if isinstance(nilai, bool) or not isinstance(nilai, (int, float)):
        raise ValueError(f"{nama_field} harus berupa angka.")
    if not math.isfinite(nilai):
        raise ValueError(f"{nama_field} harus berupa angka yang valid.")
    if nilai < 0:
        raise ValueError(f"{nama_field} tidak boleh negatif.")
    return nilai
