import json
import os


def load_packages(data_dir="data"):
    """Membaca berat paket per node dari packages.json."""
    path = os.path.join(data_dir, "packages.json")
    with open(path, "r") as f:
        data = json.load(f)

    weights = {p["node_id"]: p["weight_kg"] for p in data["packages"]}
    capacity = data["motor_capacity_kg"]
    return weights, capacity


def fuel_ratio(remaining_load_kg, total_load_kg):
    """
    Menghitung rasio konsumsi BBM (liter per km) berdasarkan beban saat ini.
    
    Konsumsi diasumsikan berubah secara linear:
    0.02 liter/km saat kosong, 0.05 liter/km saat membawa beban penuh.
    """
    if total_load_kg == 0:
        return 0.02
    ratio = 0.02 + 0.03 * (remaining_load_kg / total_load_kg)
    return ratio


def calculate_fuel_cost(route, graph, package_weights, fuel_price_per_liter):
    """
    Menghitung total biaya BBM berdasarkan rute, jarak, dan sisa beban paket.

    Parameter:
        route               : list urutan node (dihasilkan algoritma)
        graph               : objek Graph
        package_weights     : dict node_id → berat (kg)
        fuel_price_per_liter: harga BBM per liter (Rp)

    Return:
        total_fuel_cost : total biaya BBM (Rp)
        segment_details : list detail biaya per segmen (untuk display)
    """
    total_load     = sum(package_weights.values())
    remaining_load = total_load
    total_fuel_cost = 0.0
    segment_details = []

    for i in range(len(route) - 1):
        node_from = route[i]
        node_to   = route[i + 1]

        dist = graph.get_distance(node_from, node_to)
        if dist == 0:
            # Fallback: estimasi via perantara (graf sparse)
            for k in range(graph.n):
                if graph.get_distance(node_from, k) > 0 and graph.get_distance(k, node_to) > 0:
                    dist = graph.get_distance(node_from, k) + graph.get_distance(k, node_to)
                    break

        # Hitung rasio konsumsi dengan beban saat ini
        ratio = fuel_ratio(remaining_load, total_load)

        segment_cost = dist * ratio * fuel_price_per_liter
        total_fuel_cost += segment_cost

        segment_details.append({
            "from"           : node_from,
            "to"             : node_to,
            "distance_km"    : dist,
            "load_kg"        : remaining_load,
            "ratio_liter_km" : ratio,
            "cost_rp"        : segment_cost
        })

        # Beban berkurang setelah paket diturunkan di node tujuan.
        if node_to != 0 and node_to in package_weights:
            remaining_load -= package_weights[node_to]
            remaining_load  = max(remaining_load, 0.0)

    return total_fuel_cost, segment_details


def calculate_tco(fuel_cost, exec_time_ms, server_cost_per_ms=50):
    """
    Menghitung Total Cost of Ownership (TCO).

    Parameter:
        fuel_cost        : total biaya BBM (Rp)
        exec_time_ms     : waktu eksekusi algoritma (milidetik)
        server_cost_per_ms: tarif server per ms (default Rp 50)

    Return:
        tco              : total cost of ownership (Rp)
        compute_cost     : biaya komputasi saja (Rp)
    """
    compute_cost = exec_time_ms * server_cost_per_ms
    tco          = fuel_cost + compute_cost
    return tco, compute_cost
