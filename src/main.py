import argparse
import json
import os
import sys

# Tambahkan parent folder ke path agar bisa import src/*
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph   import Graph
from src.greedy  import nearest_neighbor
from src.bnb     import branch_and_bound
from src.cost    import load_packages, calculate_fuel_cost, calculate_tco


LINE_DOUBLE = "═" * 65
LINE_SINGLE = "─" * 65
LINE_MID    = "─" * 30


def load_scenarios(data_dir="data"):
    path = os.path.join(data_dir, "scenarios.json")
    with open(path, "r") as f:
        return json.load(f)


def format_route(route, graph):
    """Mengubah list node id menjadi string rute yang mudah dibaca."""
    names = []
    for node_id in route:
        if node_id == 0:
            names.append("Hub")
        else:
            names.append(f"P{node_id}")
    return " → ".join(names)


def format_rp(value):
    """Format angka ke Rupiah dengan pemisah ribuan."""
    return f"Rp {value:>12,.0f}"


def print_segment_table(segments, graph):
    """Mencetak tabel detail biaya per segmen rute."""
    print(f"\n  {'Segmen':<18} {'Jarak':>7} {'Beban':>7} {'Rasio':>8} {'Biaya BBM':>14}")
    print(f"  {'-'*18} {'-'*7} {'-'*7} {'-'*8} {'-'*14}")
    for s in segments:
        frm  = "Hub" if s['from'] == 0 else f"P{s['from']}"
        to   = "Hub" if s['to']   == 0 else f"P{s['to']}"
        seg  = f"{frm} → {to}"
        print(
            f"  {seg:<18} "
            f"{s['distance_km']:>6.1f}km "
            f"{s['load_kg']:>6.1f}kg "
            f"{s['ratio_liter_km']:>7.4f} "
            f"Rp {s['cost_rp']:>10,.0f}"
        )


def run_simulation(scenario_key, data_dir="data"):
    """
    Menjalankan simulasi lengkap untuk satu skenario ekonomi:
    1. Load data
    2. Jalankan Greedy + B&B
    3. Hitung biaya BBM dan TCO
    4. Cetak hasil perbandingan
    """
    # load data
    graph            = Graph(data_dir)
    package_weights, capacity = load_packages(data_dir)
    scenarios        = load_scenarios(data_dir)

    if scenario_key not in scenarios:
        print(f"[ERROR] Skenario '{scenario_key}' tidak ditemukan.")
        print(f"        Pilihan yang tersedia: {list(scenarios.keys())}")
        sys.exit(1)

    scenario     = scenarios[scenario_key]
    fuel_price   = scenario["fuel_price_per_liter"]
    server_rate  = scenario["server_cost_per_ms"]
    scenario_lbl = scenario["label"]

    # output header
    print(f"\n{LINE_DOUBLE}")
    print(f"  SIMULASI ROUTING KURIR — {scenario_lbl.upper()}")
    print(f"  Harga BBM : Rp {fuel_price:,}/liter")
    print(f"  Tarif Server : Rp {server_rate}/ms")
    print(f"{LINE_DOUBLE}")

    # info graf
    total_paket = sum(package_weights.values())
    print(f"\n  Jumlah node  : {graph.n} (1 Hub + {graph.n-1} Pelanggan)")
    print(f"  Total beban  : {total_paket:.1f} kg")
    print(f"  Kapasitas motor : {capacity:.1f} kg")

    # mulai greedy
    print(f"\n{LINE_SINGLE}")
    print("  [A] ALGORITMA GREEDY — Nearest Neighbor")
    print(LINE_SINGLE)

    route_g, dist_g, time_g = nearest_neighbor(graph, start=0)
    fuel_g, segs_g          = calculate_fuel_cost(route_g, graph, package_weights, fuel_price)
    tco_g,  compute_g       = calculate_tco(fuel_g, time_g, server_rate)

    print(f"\n  Rute   : {format_route(route_g, graph)}")
    print(f"  Jarak  : {dist_g:.1f} km")
    print(f"  Waktu eksekusi : {time_g:.4f} ms")
    print_segment_table(segs_g, graph)
    print(f"\n  {'Biaya BBM':<30} {format_rp(fuel_g)}")
    print(f"  {'Biaya Komputasi':<30} {format_rp(compute_g)}")
    print(f"  {'─'*44}")
    print(f"  {'TCO (Total Cost of Ownership)':<30} {format_rp(tco_g)}")

    # jalankan branch and bound
    print(f"\n{LINE_SINGLE}")
    print("  [B] ALGORITMA EKSAK — DFS Branch and Bound")
    print(LINE_SINGLE)

    route_b, dist_b, time_b = branch_and_bound(graph, start=0)
    fuel_b, segs_b          = calculate_fuel_cost(route_b, graph, package_weights, fuel_price)
    tco_b,  compute_b       = calculate_tco(fuel_b, time_b, server_rate)

    print(f"\n  Rute   : {format_route(route_b, graph)}")
    print(f"  Jarak  : {dist_b:.1f} km")
    print(f"  Waktu eksekusi : {time_b:.4f} ms")
    print_segment_table(segs_b, graph)
    print(f"\n  {'Biaya BBM':<30} {format_rp(fuel_b)}")
    print(f"  {'Biaya Komputasi':<30} {format_rp(compute_b)}")
    print(f"  {'─'*44}")
    print(f"  {'TCO (Total Cost of Ownership)':<30} {format_rp(tco_b)}")

    # tabel perbandingan
    print(f"\n{LINE_DOUBLE}")
    print("  PERBANDINGAN TCO — RINGKASAN")
    print(LINE_DOUBLE)

    print(f"\n  {'Metrik':<32} {'Greedy':>14} {'Branch & Bound':>14}")
    print(f"  {'─'*32} {'─'*14} {'─'*14}")
    print(f"  {'Jarak Rute (km)':<32} {dist_g:>13.1f} {dist_b:>13.1f}")
    print(f"  {'Waktu Eksekusi (ms)':<32} {time_g:>13.4f} {time_b:>13.4f}")
    print(f"  {'Biaya BBM (Rp)':<32} {fuel_g:>14,.0f} {fuel_b:>14,.0f}")
    print(f"  {'Biaya Komputasi (Rp)':<32} {compute_g:>14,.0f} {compute_b:>14,.0f}")
    print(f"  {'TCO (Rp)':<32} {tco_g:>14,.0f} {tco_b:>14,.0f}")

    # analisis keputusan
    print(f"\n{LINE_SINGLE}")
    print("  ANALISIS KEPUTUSAN BISNIS")
    print(LINE_SINGLE)

    selisih_jarak   = dist_g  - dist_b
    selisih_bbm     = fuel_g  - fuel_b
    selisih_compute = compute_b - compute_g
    selisih_tco     = tco_g   - tco_b

    print(f"\n  Penghematan jarak  (B&B vs Greedy) : {selisih_jarak:+.1f} km")
    print(f"  Penghematan BBM    (B&B vs Greedy) : {format_rp(selisih_bbm)}")
    print(f"  Biaya komputasi tambahan (B&B)     : {format_rp(selisih_compute)}")
    print(f"  Selisih TCO        (B&B lebih hemat): {format_rp(selisih_tco)}")

    print()
    if tco_b < tco_g:
        persen = ((tco_g - tco_b) / tco_g) * 100
        print(f"  REKOMENDASI: Gunakan Branch & Bound")
        print(f"  Penghematan TCO sebesar {persen:.1f}% pada {scenario_lbl}.")
        print(f"  Biaya komputasi lebih mahal diimbangi rute lebih efisien.")
    elif tco_g < tco_b:
        persen = ((tco_b - tco_g) / tco_b) * 100
        print(f"  REKOMENDASI: Gunakan Greedy")
        print(f"  TCO Greedy lebih hemat {persen:.1f}% pada {scenario_lbl}.")
        print(f"  Biaya komputasi B&B tidak sebanding dengan penghematan BBM.")
    else:
        print(f"  REKOMENDASI: Kedua algoritma menghasilkan TCO yang sama.")

    print(f"\n{LINE_DOUBLE}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simulasi routing kurir — perbandingan algoritma Greedy vs Branch & Bound"
    )
    parser.add_argument(
        "--scenario",
        choices=["subsidi", "krisis", "all"],
        default="all",
        help="Pilih skenario ekonomi: subsidi | krisis | all (default: all)"
    )
    parser.add_argument(
        "--data-dir",
        default=None,
        help="Path ke folder data JSON (default: data folder di direktori script)"
    )
    args = parser.parse_args()

    # Jika data_dir tidak diberikan, gunakan path relatif terhadap script
    if args.data_dir is None:
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        args.data_dir = os.path.join(script_dir, "data")

    if args.scenario == "all":
        run_simulation("subsidi", args.data_dir)
        run_simulation("krisis",  args.data_dir)
    else:
        run_simulation(args.scenario, args.data_dir)
