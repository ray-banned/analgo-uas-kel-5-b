import json # import library json untuk membace file json
import os # import library os untuk mengelola path file

# class graph digunakan untuk merepresentasikan graph berbobot
# menggunakan adjacency matrix
class Graph:
    """
    Representasi graf berbobot menggunakan adjacency matrix.
    Nilai 0 pada matrix berarti tidak ada edge langsung antara dua node.
    """

    # konstruktor class graph
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir # menyimpan lokais folder data
        self.nodes     = [] # menyimpan daftar node/lokasi
        self.matrix    = [] # menyimpan adjacency matrix
        self.n         = 0 # menyimpan jumlah node
        self._load_locations() # membuat data lokasi dari locations.json
        self._load_matrix() # membuat adjacency matrix dari distance_matrix.json

    # method untuk membaca data lokasi 
    def _load_locations(self):
        path = os.path.join(self.data_dir, "locations.json") # membuat path menuju file locations.json
        with open(path, "r") as f: # membuka file dalam node read
            data = json.load(f) # membaca isi json menjadi dictionary python
        self.nodes = data["nodes"] # mengambil daftar node dari key "nodes"
        self.n     = len(self.nodes) # menghitung jumlah node

    # method untuk membaca adjacency matrix
    def _load_matrix(self):
        path = os.path.join(self.data_dir, "distance_matrix.json") # membuat path menuju file distance_matrix.json
        with open(path, "r") as f: # membuka file json
            data = json.load(f)  # membaca isi file menjadi dictionary
        self.matrix = data["matrix"] # mengamnil matrix dari key "matrix"

    # mengembalikan jarak dari node i ke node j
    def get_distance(self, i, j):
        """
        Mengembalikan jarak (km) dari node i ke node j.
        Nilai 0 berarti tidak ada jalur langsung.
        """
        return self.matrix[i][j] # mengakses nilai pada adjacency matrix

    # mengambil seluruh tetangga (neighbor) satu node
    def get_neighbors(self, node):
        """
        Mengembalikan list (neighbor_id, jarak) dari suatu node.
        Hanya node yang memiliki edge langsung (jarak > 0) yang dikembalikan.
        """
        neighbors = [] # menyimpan daftar tetangga 
        for j in range(self.n): # iterasi seluruh node dalam graph
            if j != node and self.matrix[node][j] > 0: # jika bukan node yang sama dan memiliki jalur langsung
                neighbors.append((j, self.matrix[node][j])) # tambahkan tuple (id_tetangga, jarak)
        return neighbors # mengembalikan daftar tetangga

    # mengambil nama lokasi berdasarkan id node
    def get_node_name(self, node_id):
        return self.nodes[node_id]["name"] # mengambil nilai field "name"

    # menampilkan adjacency matrix ke terminal
    def print_matrix(self):
        """Cetak adjacency matrix ke terminal untuk debugging."""
        header = "     " + "".join(f"{j:>5}" for j in range(self.n)) # membuat header kolom 
        print(header) # menampilkan header 
        print("     " + "-" * (5 * self.n)) # menampilkan garis pemisah
        for i in range(self.n): # iterasi setiap baris matrix
            row = f"{i:>3} |" + "".join(f"{self.matrix[i][j]:>5}" for j in range(self.n)) # membuat string dengan format
            print(row) # menampilkan baris matrix
