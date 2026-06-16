import time # import library time untuk mengukur waktu ekseskusi algoritma

# fungsi algoritma greedy nearest neighbor
def nearest_neighbor(graph, start=0):
    """
    Algoritma A - Greedy Nearest Neighbor.

    Strategi: dari posisi saat ini, selalu pilih node yang belum
    dikunjungi dengan jarak terdekat. Jika tidak ada tetangga langsung,
    gunakan jarak terpendek dari seluruh matriks (lewat node perantara
    tidak dimodelkan, jadi fallback ke node terdekat yang reachable).

    Parameter:
        graph : objek Graph
        start : node awal (default 0 = Hub)

    Return:
        route      : list urutan node yang dikunjungi (termasuk kembali ke hub)
        total_dist : total jarak rute (km)
        exec_ms    : waktu eksekusi (milidetik)
    """
    start_time = time.perf_counter() # mencatat waktu mulai eksekusi 

    n       = graph.n # jumlah node dalam graph
    visited = [False] * n # menandai apakah node sudah dikunjungi
    route   = [start] # rute diawali dari node start
    visited[start] = True # tandai node awal sebagai sudah dikunjungi
    current = start # posisi saat ini 
    total_dist = 0.0 # total jarak tempuh

    for _ in range(n - 1): # mengunjungi seluruh node selain node awal
        nearest  = -1 # menyimpan kandidat node terdekat 
        min_dist = float('inf')

        # Cari node unvisited/tetangga terdekat dari posisi saat ini
        for j in range(n):
            if not visited[j] and graph.get_distance(current, j) > 0: # jika node belum dikunjungi dan memiliki jalur langsung
                if graph.get_distance(current, j) < min_dist: # jika jaraknya <
                    min_dist = graph.get_distance(current, j) # simpan jarak minimum baru
                    nearest  = j # simpan node terdekat

        # Jika tidak ada tetangga langsung, cari node unvisited
        # mana pun yang paling dekat dari matriks (toleransi graf sparse)
        if nearest == -1:
            for j in range(n): # periksa semua node yang belum dikunjungi
                if not visited[j]:
                    # Cari jarak via node lain sebagai estimasi fallback
                    for k in range(n):
                        if graph.get_distance(current, k) > 0 and graph.get_distance(k, j) > 0: # current --> k --> j
                            dist_via_k = graph.get_distance(current, k) + graph.get_distance(k, j) # hitung total jarak melalui k
                            if dist_via_k < min_dist: # jika lebih pendek
                                min_dist = dist_via_k
                                nearest  = j

        # fallback terakhir (graph terputus)
        if nearest == -1:
            # Tidak ada jalur ditemukan — ambil node unvisited pertama
            for j in range(n): # ambil node belum dikunjungi pertama
                if not visited[j]:
                    nearest  = j
                    min_dist = 999 # nilai penalti jarak
                    break

        # update perjalanan
        route.append(nearest) # tambahkan node ke rute
        visited[nearest] = True # tandai sebagai sudah dikunjungi
        total_dist      += min_dist  # tambahkan jarak ke total
        current          = nearest # pindah ke node tersbut

    # Kembali ke Hub/ node awal
    return_dist = graph.get_distance(current, start)
    if return_dist == 0: # jika tidak ada jalur langsung
        # Cari jalur balik via perantara
        for k in range(n):
            if graph.get_distance(current, k) > 0 and graph.get_distance(k, start) > 0:
                return_dist = graph.get_distance(current, k) + graph.get_distance(k, start)
                break
    total_dist += return_dist # tambahkan jarak kembali ke total 
    route.append(start) # tambahkan hub ke akhir rute

    end_time = time.perf_counter() # mencatat waktu selesai eksekusi
    exec_ms  = (end_time - start_time) * 1000 # menghitung waktu ekseskusi dalam milidetik

    return route, total_dist, exec_ms # mengembalikan hasil
