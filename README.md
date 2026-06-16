# Last-Mile Delivery Route Optimization

Simulasi komputasi perbandingan algoritma Greedy dan DFS Branch & Bound untuk optimasi rute pengantaran kurir (Last-Mile Delivery). Program ini menghitung Total Cost of Ownership (TCO) pada dua skenario ekonomi — harga BBM subsidi dan krisis — untuk menentukan algoritma mana yang lebih menguntungkan secara finansial bagi perusahaan ekspedisi.

## Anggota Kelompok
```
|          Nama           |      NPM     |
|-------------------------|--------------|
| Aulia Ramdani Nur       | 140810240002 |
| Muhammad Fathin Raihan  | 140810240026 |
| Rosa Andini Ismayanti   | 140810240048 |
| Nadya Happy Siahaan     | 140810240068 |
```
---

## Struktur Repositori

```
.
├── src/
│   ├── graph.py       # Struktur data graf (adjacency matrix)
│   ├── greedy.py      # Algoritma A: Greedy Nearest Neighbor
│   ├── bnb.py         # Algoritma B: DFS Branch and Bound
│   ├── cost.py        # Cost function: BBM, TCO
│   └── main.py        # Entry point CLI
├── data/
│   ├── locations.json         # Daftar node (hub + pelanggan)
│   ├── distance_matrix.json   # Matriks jarak antar node (km)
│   ├── packages.json          # Berat paket per pelanggan (kg)
│   └── scenarios.json         # Konfigurasi skenario ekonomi
├── docs/
│   └── output_terminal.png    # Screenshot hasil eksekusi CLI
├── .gitignore
└── README.md
```

---

## Cara Menjalankan Program

### Prasyarat

Python 3.7 atau lebih baru. Tidak ada dependensi eksternal — program hanya menggunakan library standar Python.

### Instalasi

```bash
git clone https://github.com/<username>/<nama-repo>.git
cd <nama-repo>
```

### Eksekusi

Jalankan dari direktori root repositori.

```bash
# Menjalankan kedua skenario sekaligus (default)
python src/main.py

# Menjalankan skenario subsidi saja (BBM Rp 5.000/liter)
python src/main.py --scenario subsidi

# Menjalankan skenario krisis saja (BBM Rp 20.000/liter)
python src/main.py --scenario krisis

# Menentukan path folder data secara manual
python src/main.py --scenario all --data-dir data
```

### Parameter CLI

| Parameter | Pilihan | Default | Keterangan |
|---|---|---|---|
| `--scenario` | `subsidi`, `krisis`, `all` | `all` | Skenario ekonomi yang dijalankan |
| `--data-dir` | path direktori | `data` | Lokasi folder file JSON |

---

## Dataset

Graf terdiri dari 11 node: 1 hub pusat (node 0) dan 10 lokasi pelanggan (node 1–10). Representasi menggunakan adjacency matrix berukuran 11x11 dengan bobot berupa jarak fisik dalam kilometer. Nilai 0 pada matriks berarti tidak ada jalur langsung antara dua node tersebut.

Berat paket per pelanggan:

| Node | Berat (kg) | Node | Berat (kg) |
|---|---|---|---|
| P1 | 3.0 | P6 | 1.5 |
| P2 | 1.0 | P7 | 4.0 |
| P3 | 2.0 | P8 | 3.0 |
| P4 | 6.0 | P9 | 0.5 |
| P5 | 1.0 | P10 | 8.0 |

Total beban awal: 30.0 kg. Kapasitas motor: 30.0 kg.

---

## Pemilihan Algoritma

### Algoritma A — Greedy Nearest Neighbor

Dimulai dari hub, algoritma selalu memilih node yang belum dikunjungi dengan jarak langsung terpendek dari posisi saat ini, kemudian bergerak ke node tersebut, menandainya sebagai sudah dikunjungi, dan mengulang proses hingga semua node terkunjungi sebelum kembali ke hub.

Keputusan pemilihan ini didasarkan pada karakteristiknya yang sesuai dengan deskripsi sistem lama perusahaan: eksekusi sangat cepat dan hampir tidak membebani biaya server. Kelemahannya adalah rute yang dihasilkan tidak dijamin optimal — algoritma tidak melihat ke depan, sehingga pilihan terbaik secara lokal bisa menghasilkan rute yang buruk secara global.

Trade-off: kecepatan tinggi dengan pengorbanan kualitas rute.

### Algoritma B — DFS Branch and Bound

Menggunakan penelusuran DFS secara rekursif untuk mengeksplorasi semua kemungkinan permutasi rute. Yang membedakannya dari backtracking biasa adalah mekanisme pruning berbasis lower bound: sebelum meneruskan suatu cabang, dihitung estimasi biaya minimum jika jalur ini dilanjutkan. Jika estimasi tersebut sudah melebihi atau sama dengan solusi terbaik yang sudah ditemukan (`best_cost`), cabang langsung dipangkas tanpa perlu dieksplorasi lebih jauh.

Lower bound dihitung sebagai penjumlahan dari biaya saat ini, jarak minimum yang bisa dicapai menuju setiap node yang belum dikunjungi, dan estimasi biaya kembali ke hub.

Keputusan pemilihan ini karena algoritma ini menjamin rute dengan jarak absolut terpendek, sesuai tuntutan soal untuk algoritma eksak. Dibandingkan Dynamic Programming Held-Karp, implementasi from scratch lebih mudah dipahami sambil tetap memiliki mekanisme pruning yang signifikan.

Trade-off: rute paling optimal dengan biaya komputasi yang jauh lebih besar.

---

## Analisis Kompleksitas Big-O

### Algoritma A — Greedy Nearest Neighbor

**Kompleksitas Waktu: O(n²)**

Terdapat satu loop luar yang berjalan sebanyak `n-1` iterasi (jumlah pelanggan). Di dalam setiap iterasi, terdapat loop dalam yang memeriksa semua `n` node untuk mencari tetangga terdekat. Dengan demikian total operasi perbandingan adalah `(n-1) × n`, yang disederhanakan menjadi O(n²).

```
untuk setiap node yang belum dikunjungi (n-1 kali):
    periksa semua n node → O(n)
Total: O(n × n) = O(n²)
```

**Kompleksitas Ruang: O(n)**

Memori yang digunakan terdiri dari array `visited` berukuran n dan array `route` berukuran n+1. Tidak ada struktur data tambahan yang tumbuh seiring n, sehingga kompleksitas ruang adalah O(n).

### Algoritma B — DFS Branch and Bound

**Kompleksitas Waktu: O(n!) pada worst case**

Tanpa pruning, DFS akan mengeksplorasi seluruh permutasi dari n node, yang menghasilkan n! kemungkinan rute. Setiap level rekursi memiliki satu call ke fungsi `_lower_bound` yang berjalan dalam O(n²), sehingga kompleksitas teoritis worst case adalah O(n! × n²).

```
level 0 (root): n pilihan
level 1:        n-1 pilihan per cabang
level 2:        n-2 pilihan per cabang
...
Total tanpa pruning: n × (n-1) × (n-2) × ... × 1 = n!
```

Dalam praktiknya, pruning memangkas sebagian besar cabang sejak dini sehingga waktu rata-rata jauh di bawah O(n!). Efektivitas pruning bergantung pada kualitas lower bound dan urutan eksplorasi node.

**Kompleksitas Ruang: O(n)**

Stack rekursi memiliki kedalaman maksimum n (satu level per node yang dikunjungi). Array `visited` berukuran n dan array `route` tumbuh maksimal hingga n+1 elemen. Total penggunaan memori adalah O(n).

### Perbandingan

| Algoritma | Waktu (worst case) | Ruang | Waktu Aktual (n=10) |
|---|---|---|---|
| Greedy Nearest Neighbor | O(n²) | O(n) | ~0.03–0.05 ms |
| DFS Branch and Bound | O(n!) | O(n) | ~75–80 ms |

---

## Hasil Simulasi

### Skenario Subsidi — BBM Rp 5.000/liter

| Metrik | Greedy | Branch & Bound |
|---|---|---|
| Rute | Hub→P6→P7→P3→P2→P1→P4→P5→P8→P9→P10→Hub | Hub→P2→P1→P4→P5→P8→P9→P10→P7→P3→P6→Hub |
| Jarak Rute | 79.0 km | 77.0 km |
| Waktu Eksekusi | 0.0480 ms | 79.5990 ms |
| Biaya BBM | Rp 16.315 | Rp 18.242 |
| Biaya Komputasi | Rp 2 | Rp 3.980 |
| **TCO** | **Rp 16.317** | **Rp 22.222** |

Rekomendasi: **Greedy** — lebih hemat 26.6% pada skenario ini.

### Skenario Krisis — BBM Rp 20.000/liter

| Metrik | Greedy | Branch & Bound |
|---|---|---|
| Rute | Hub→P6→P7→P3→P2→P1→P4→P5→P8→P9→P10→Hub | Hub→P2→P1→P4→P5→P8→P9→P10→P7→P3→P6→Hub |
| Jarak Rute | 79.0 km | 77.0 km |
| Waktu Eksekusi | 0.0273 ms | 74.7939 ms |
| Biaya BBM | Rp 65.260 | Rp 72.970 |
| Biaya Komputasi | Rp 1 | Rp 3.740 |
| **TCO** | **Rp 65.261** | **Rp 76.710** |

Rekomendasi: **Greedy** — lebih hemat 14.9% pada skenario ini.

---

## Analisis Keputusan Bisnis dan Titik Break-Even

### Mengapa B&B tidak unggul meski menghasilkan rute lebih pendek

Pada dataset ini, selisih jarak antara Greedy dan B&B hanya 2 km (79 km vs 77 km). Di sisi lain, B&B membutuhkan waktu eksekusi sekitar 75–80 ms, sementara Greedy hanya memerlukan ~0.03–0.05 ms. Dengan tarif server Rp 50/ms, biaya komputasi B&B mencapai Rp 3.740–3.980 per pengiriman, sedangkan Greedy hampir nol.

Penghematan BBM dari selisih 2 km pada harga Rp 5.000/liter terlalu kecil untuk menutupi biaya komputasi yang jauh lebih besar. Bahkan pada harga Rp 20.000/liter pun, TCO Greedy masih lebih rendah.

### Perhitungan Titik Break-Even

Break-even terjadi ketika penghematan BBM dari rute B&B yang lebih pendek sama dengan selisih biaya komputasinya:

```
Penghematan BBM = Selisih Biaya Komputasi

(jarak_greedy - jarak_bnb) x rasio_rata_rata x harga_bbm* = (waktu_bnb - waktu_greedy) x 50

(79 - 77) x 0.035 x harga_bbm* = (79.5 - 0.048) x 50

2 x 0.035 x harga_bbm* = 3,976

harga_bbm* = 3,976 / 0.07

harga_bbm* = Rp 56,800 per liter
```

Dengan rasio konsumsi rata-rata 0.035 liter/km dan selisih komputasi aktual dari hasil eksekusi, algoritma B&B baru menjadi pilihan yang lebih hemat secara TCO apabila harga BBM melampaui sekitar **Rp 56.800 per liter**.

### Kesimpulan

Pada kondisi harga BBM yang realistis di Indonesia, baik skenario subsidi (Rp 5.000/liter) maupun krisis (Rp 20.000/liter), algoritma **Greedy Nearest Neighbor adalah pilihan yang lebih efisien secara finansial**. Biaya komputasi server yang ditimbulkan oleh algoritma B&B jauh melebihi penghematan BBM yang diperoleh dari selisih jarak 2 km pada dataset berukuran 10 pelanggan.

Algoritma B&B akan mulai menguntungkan apabila salah satu dari kondisi berikut terpenuhi: harga BBM melampaui Rp 56.800/liter, selisih jarak antar algoritma jauh lebih besar (misalnya pada dataset dengan banyak pelanggan yang tersebar), atau biaya server turun secara signifikan sehingga biaya komputasi menjadi lebih murah.

---

## Catatan Implementasi

Seluruh logika pencarian rute dan operasi graf diimplementasikan dari awal (from scratch) tanpa menggunakan library pihak ketiga seperti `networkx` atau algoritma pencarian bawaan bahasa. Library yang digunakan hanya `json`, `os`, `time`, `sys`, dan `argparse` dari Python Standard Library untuk keperluan I/O, pengukuran waktu, dan antarmuka CLI.
