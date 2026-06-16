import time

_best_cost  = float('inf')
_best_route = []


def _lower_bound(graph, current, visited, current_cost):
    """
    Menghitung estimasi batas bawah (lower bound) total biaya
    jika melanjutkan dari node `current`.
    """
    lb = current_cost

    for j in range(graph.n):
        if not visited[j]:
            # Jarak minimum menuju node j dari node manapun yang sudah dikunjungi
            min_in = float('inf')
            for k in range(graph.n):
                if graph.get_distance(k, j) > 0:
                    if min_in > graph.get_distance(k, j):
                        min_in = graph.get_distance(k, j)
            if min_in < float('inf'):
                lb += min_in

    # Tambahkan estimasi jarak kembali ke Hub (node 0)
    min_back = float('inf')
    for k in range(graph.n):
        if visited[k] and graph.get_distance(k, 0) > 0:
            if graph.get_distance(k, 0) < min_back:
                min_back = graph.get_distance(k, 0)
    if min_back < float('inf'):
        lb += min_back

    return lb


def _dfs(graph, current, visited, route, current_cost):
    """
    Fungsi rekursif DFS dengan Branch and Bound Pruning.
    """
    global _best_cost, _best_route

    all_visited = all(visited[j] for j in range(graph.n))
    if all_visited:
        return_dist = graph.get_distance(current, 0)
        if return_dist > 0:
            total = current_cost + return_dist
            if total < _best_cost:
                _best_cost  = total
                _best_route = route + [0]
        return

    # Pruning: hitung lower bound
    lb = _lower_bound(graph, current, visited, current_cost)
    if lb >= _best_cost:
        return

    # Rekursi ke semua node yang belum dikunjungi
    for next_node in range(1, graph.n):
        if not visited[next_node]:
            dist = graph.get_distance(current, next_node)
            if dist == 0:
                dist = _find_indirect(graph, current, next_node)
            if dist == 0:
                continue

            visited[next_node] = True
            _dfs(
                graph,
                next_node,
                visited,
                route + [next_node],
                current_cost + dist
            )

            visited[next_node] = False


def _find_indirect(graph, src, dst):
    """
    Cari jarak terpendek dari src ke dst via satu node perantara.
    Mengembalikan 0 jika tidak ditemukan jalur.
    """
    best = float('inf')
    for k in range(graph.n):
        if graph.get_distance(src, k) > 0 and graph.get_distance(k, dst) > 0:
            via = graph.get_distance(src, k) + graph.get_distance(k, dst)
            if via < best:
                best = via
    return best if best < float('inf') else 0


def branch_and_bound(graph, start=0):
    """
    Algoritma DFS Branch and Bound Pruning.

    Menjamin rute dengan total jarak paling optimal secara absolut
    dengan cara menelusuri semua kemungkinan rute (DFS) sambil
    memangkas cabang yang sudah pasti lebih mahal dari solusi terbaik
    yang sudah ditemukan.

    Parameter:
        graph : objek Graph
        start : node awal (default 0 = Hub)

    Return:
        route      : list urutan node optimal (termasuk kembali ke hub)
        total_dist : total jarak rute optimal (km)
        exec_ms    : waktu eksekusi (milidetik)
    """
    global _best_cost, _best_route

    # Reset state global sebelum mulai
    _best_cost  = float('inf')
    _best_route = []

    start_time = time.perf_counter()

    visited        = [False] * graph.n
    visited[start] = True

    _dfs(graph, start, visited, [start], 0.0)

    end_time = time.perf_counter()
    exec_ms  = (end_time - start_time) * 1000

    return _best_route, _best_cost, exec_ms
