import tkinter as tk
from tkinter import filedialog

import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import random


class GraphApp:
    def __init__(self, master):
        self.error_label = None
        self.entry_edges = None
        self.entry_vertices = None
        self.export_count = 0  # Biến đếm để tạo số thứ tự cho các tệp xuất
        self.include_weights = tk.BooleanVar()  # Biến để kiểm tra người dùng có chọn thêm trọng số hay không
        self.master = master
        self.master.title("Graph Management")

        # Full-screen view
        self.master.state('zoomed')

        # Change the background color
        self.master.configure(bg="#f2f2f2")  # Light grey background

        # Create a frame for the menu on the left
        menu_frame = tk.Frame(self.master, bg="#333", width=200, height=master.winfo_height())
        menu_frame.pack(side="left", fill="y")

        # Add menu buttons to the menu frame
        menu_label = tk.Label(menu_frame, text="Menu", font=("Helvetica", 16, "bold"), fg="white", bg="#333")
        menu_label.pack(pady=10)

        # Find Shortest Path button
        btn_shortest_path = tk.Button(menu_frame, text="Find Shortest Path", font=("Arial", 12), width=20,
                                      bg="#00509e", fg="white", command=self.find_shortest_path)
        btn_shortest_path.pack(pady=10)

        # Find Minimum Spanning Tree button
        btn_mst = tk.Button(menu_frame, text="Find MST", font=("Arial", 12), width=20,
                            bg="#00509e", fg="white", command=self.find_mst)
        btn_mst.pack(pady=10)

        # Export to File button
        btn_export = tk.Button(menu_frame, text="Export to File", font=("Arial", 12), width=20,
                               bg="#00509e", fg="white", command=self.export_to_file)
        btn_export.pack(pady=10)

        # Import from File button
        btn_import = tk.Button(menu_frame, text="Import from File", font=("Arial", 12), width=20,
                               bg="#00509e", fg="white", command=self.import_from_file)
        btn_import.pack(pady=10)

        # Main title
        self.title_label = tk.Label(self.master, text="Graph Management Application",
                                    font=("Helvetica", 24, "bold"), fg="#333", bg="#f2f2f2")
        self.title_label.pack(pady=20)

        # Input section for data
        input_frame = tk.Frame(self.master, bg="#f2f2f2")
        input_frame.pack(pady=10)

        input_label = tk.Label(input_frame, text="Enter Data Graph:", font=("Arial", 14),
                               fg="#00509e", bg="#f2f2f2")
        input_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Use tk.Text for multi-line input
        self.entry_data = tk.Text(input_frame, width=50, height=5, font=("Arial", 12), fg="#333", bg="#e6f7ff")
        self.entry_data.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Input fields for source and target vertices
        input_label_source = tk.Label(input_frame, text="Source Vertex:", font=("Arial", 14), fg="#00509e",
                                      bg="#f2f2f2")
        input_label_source.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_source = tk.Entry(input_frame, width=30, font=("Arial", 12), fg="#333", bg="#e6f7ff")
        self.entry_source.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        input_label_target = tk.Label(input_frame, text="Target Vertex:", font=("Arial", 14), fg="#00509e",
                                      bg="#f2f2f2")
        input_label_target.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_target = tk.Entry(input_frame, width=30, font=("Arial", 12), fg="#333", bg="#e6f7ff")
        self.entry_target.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Drop-down menu for algorithm selection
        self.selected_algorithm = tk.StringVar(self.master)
        self.selected_algorithm.set("Dijkstra")  # Default value

        algorithms = ["Dijkstra", "Floyd-Warshall"]
        algorithm_menu = tk.OptionMenu(self.master, self.selected_algorithm, *algorithms)
        algorithm_menu.config(font=("Arial", 12), width=20)
        algorithm_menu.pack(pady=10)

        # Example label
        example_label = tk.Label(self.master, text="Example: node1,node2,weight (e.g., 1,2,10)",
                                 font=("Arial", 10, "italic"), fg="#888", bg="#f2f2f2")
        example_label.pack()

        # Buttons for Manual Graph and Random Graph
        self.button_manual_draw = tk.Button(self.master, text="Draw Manual Graph", font=("Arial", 12),
                                            bg="#2196F3", fg="white", width=20, command=self.draw_manual_graph)
        self.button_manual_draw.pack(pady=10)

        self.button_random_graph = tk.Button(self.master, text="Generate Random Graph", font=("Arial", 12),
                                             bg="#4CAF50", fg="white", width=20, command=self.create_popup)
        self.button_random_graph.pack(pady=10)

        self.output_label = tk.Label(self.master, text="", font=("Arial", 12), fg="#333",
                                     bg="#f2f2f2")
        self.output_label.pack(pady=10)

        self.G = nx.Graph()  # undirected graph
        self.canvas_widget = None  # Initialize the canvas widget
        self.pos = None  # Store the layout for consistent node positioning

    # Manual input graph creation
    def draw_manual_graph(self):
        try:
            data = self.entry_data.get("1.0", tk.END).strip()  # Lấy toàn bộ nội dung từ widget Text
            edges = data.splitlines()

            self.G.clear()

            for edge in edges:
                edge_data = edge.split(',')
                if len(edge_data) != 3:
                    self.output_label.config(text="Invalid input format! Each line should be: node1,node2,weight",
                                             fg="red")
                    return

                node1 = int(edge_data[0])
                node2 = int(edge_data[1])
                weight = int(edge_data[2])

                self.G.add_edge(node1, node2, weight=weight)

            self.pos = nx.spring_layout(self.G)
            self.draw_graph()

            self.output_label.config(text="Graph created successfully.", fg="green")

        except ValueError:
            self.output_label.config(text="Please enter valid integers for nodes and weight!", fg="red")

    # Create random graph
    def create_popup(self):
        self.popup = tk.Toplevel(self.master)
        self.popup.title("Enter number of vertices and edges")
        popup_width, popup_height = 300, 350
        self.popup.resizable(False, False)

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        center_x = int(screen_width / 2 - popup_width / 2)
        center_y = int(screen_height / 2 - popup_height / 2)
        self.popup.geometry(
            f"{popup_width}x{popup_height}+{center_x}+{center_y}")

        tk.Label(self.popup, text="Number of vertices:").pack(pady=10)
        self.entry_vertices = tk.Entry(self.popup, width=30)
        self.entry_vertices.pack(pady=5)

        tk.Label(self.popup, text="Number of edges:").pack(pady=10)
        self.entry_edges = tk.Entry(self.popup, width=30)
        self.entry_edges.pack(pady=5)

        # Checkbox for including weights
        tk.Checkbutton(self.popup, text="Include weights", variable=self.include_weights).pack(pady=10)

        self.error_label = tk.Label(self.popup, text="", fg="red")
        self.error_label.pack(pady=10)

        tk.Button(self.popup, text="Confirm", command=self.validate_input).pack(pady=10)

    def validate_input(self):
        try:
            num_vertices = int(self.entry_vertices.get())
            num_edges = int(self.entry_edges.get())

            if num_vertices < 1:
                self.error_label.config(text="Number of vertices must be at least 1.")
                return

            min_edges = 0
            max_edges = (num_vertices * (num_vertices - 1)) // 2

            if num_edges < min_edges or num_edges > max_edges:
                self.error_label.config(
                    text=f"Number of edges must be between {min_edges} and {max_edges}.")
                return

            self.random_graph(num_vertices, num_edges)
            self.popup.destroy()
        except ValueError:
            self.error_label.config(text="Please enter valid numbers!")

    def random_graph(self, num_vertices, num_edges):
        self.G.clear()
        self.G.add_nodes_from(range(1, num_vertices + 1))

        possible_edges = [(u, v) for u in range(1, num_vertices + 1) for v in range(1, num_vertices + 1) if u < v]
        random.shuffle(possible_edges)

        edges_to_add = possible_edges[:num_edges]

        for u, v in edges_to_add:
            if self.include_weights.get():
                weight = random.randint(1, 10)  # Random weight for each edge
                self.G.add_edge(u, v, weight=weight)
            else:
                self.G.add_edge(u, v)

        self.pos = nx.spring_layout(self.G)
        self.draw_graph()

        if self.include_weights.get():
            self.output_label.config(
                text=f"Generated random graph with {num_vertices} vertices and {len(edges_to_add)} edges with weights.")
        else:
            self.output_label.config(
                text=f"Generated random graph with {num_vertices} vertices and {len(edges_to_add)} edges without weights.")

    def export_to_file(self):
        if self.G.number_of_edges() == 0:
            self.output_label.config(text="No graph data to export!", fg="red")
            return

        # Đường dẫn thư mục để lưu tệp (thay đổi đường dẫn này theo nhu cầu)
        export_folder = "C:/path/to/your/folder"

        # Kiểm tra nếu thư mục không tồn tại thì tạo mới
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)

        # Tăng số thứ tự mỗi lần export
        self.export_count += 1

        try:
            # Ghi dữ liệu vào tệp .txt trong thư mục cụ thể
            txt_file_path = os.path.join(export_folder, f"graph_data_{self.export_count}.txt")
            with open(txt_file_path, "w") as file:
                file.write("Source,Target,Weight\n")
                for u, v, data in self.G.edges(data=True):
                    weight = data.get('weight', 'N/A')  # Hiển thị 'N/A' nếu không có trọng số
                    file.write(f"{u},{v},{weight}\n")

            # Lưu hình ảnh đồ thị dưới dạng .png trong thư mục cụ thể
            png_file_path = os.path.join(export_folder, f"graph_image_{self.export_count}.png")
            fig, ax = plt.subplots(figsize=(10, 8))
            nx.draw(self.G, self.pos, with_labels=True, node_color="blue", edge_color="black", font_color="white",
                    ax=ax)
            edge_labels = nx.get_edge_attributes(self.G, 'weight')
            nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=edge_labels, ax=ax)

            plt.title("Graph")
            plt.savefig(png_file_path)  # Lưu hình ảnh dưới dạng .png
            plt.close(fig)

            self.output_label.config(text=f"Graph data exported to {txt_file_path} and {png_file_path}", fg="green")

        except IOError as e:
            self.output_label.config(text=f"Error exporting file: {e}", fg="red")

    def import_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not file_path:
            return

        try:
            with open(file_path, 'r') as file:
                lines = file.readlines()

            self.G.clear()
            for line in lines[1:]:  # Bỏ qua dòng tiêu đề nếu có
                node1, node2, weight = line.strip().split(',')
                self.G.add_edge(int(node1), int(node2), weight=float(weight))

            self.pos = nx.spring_layout(self.G)
            self.draw_graph()

            self.output_label.config(text=f"Graph imported successfully from {file_path}", fg="green")

        except Exception as e:
            self.output_label.config(text=f"Error importing file: {e}", fg="red")

    def import_from_file(self):
        try:
            file_path = filedialog.askopenfilename(
                title="Select Graph Data File",
                filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
            )
            if not file_path:
                return  # User cancelled the file dialog

            with open(file_path, 'r') as file:
                data = file.read().strip()

            edges = data.splitlines()
            self.G.clear()

            for edge in edges:
                edge_data = edge.split(',')
                if len(edge_data) != 3:
                    self.output_label.config(
                        text="Invalid file format! Each line should be: node1,node2,weight",
                        fg="red"
                    )
                    return

                node1 = int(edge_data[0].strip())
                node2 = int(edge_data[1].strip())
                weight = int(edge_data[2].strip())

                self.G.add_edge(node1, node2, weight=weight)

            self.pos = nx.spring_layout(self.G)
            self.draw_graph()
            self.output_label.config(text="Graph imported successfully.", fg="green")

        except FileNotFoundError:
            self.output_label.config(text="File not found.", fg="red")
        except ValueError:
            self.output_label.config(text="Please ensure the file contains valid integers.", fg="red")
        except Exception as e:
            self.output_label.config(text=f"An error occurred: {e}", fg="red")
    # Placeholder for find_mst (Minimum Spanning Tree)
    def find_mst(self):
        self.output_label.config(text="Find MST feature is not implemented yet.", fg="red")

    # Shortest path finding logic using Dijkstra
    def find_shortest_path_dijkstra(self):
        try:
            source = int(self.entry_source.get())
            target = int(self.entry_target.get())

            if source not in self.G.nodes or target not in self.G.nodes:
                self.output_label.config(text="Invalid input! Please enter valid vertices.", fg="red")
                return

            shortest_path = nx.dijkstra_path(self.G, source=source, target=target)
            path_length = nx.dijkstra_path_length(self.G, source=source, target=target)

            self.output_label.config(text=f"Shortest path: {shortest_path} (Length: {path_length})", fg="green")
            self.highlight_path(shortest_path)

        except nx.NetworkXNoPath:
            self.output_label.config(text="No path exists between the specified vertices!", fg="red")
        except ValueError:
            self.output_label.config(text="Invalid input! Please enter valid vertices.", fg="red")

    # Shortest path finding logic using Floyd-Warshall
    def find_shortest_path_floyd_warshall(self):
        try:
            source = int(self.entry_source.get())
            target = int(self.entry_target.get())

            if source not in self.G.nodes or target not in self.G.nodes:
                self.output_label.config(text="Invalid input! Please enter valid vertices.", fg="red")
                return

            # Create the predecessor and distance matrices for Floyd-Warshall
            predecessors, dist_matrix = nx.floyd_warshall_predecessor_and_distance(self.G)

            if target not in dist_matrix[source]:
                self.output_label.config(text="No path exists between the specified vertices!", fg="red")
                return

            # Reconstruct the shortest path using the predecessors
            path = []
            current = target
            while current != source:
                path.append(current)
                current = predecessors[source][current]
            path.append(source)
            path.reverse()

            path_length = dist_matrix[source][target]

            self.output_label.config(text=f"Shortest path: {path} (Length: {int(path_length)})", fg="green")
            self.highlight_path(path)

        except ValueError:
            self.output_label.config(text="Invalid input! Please enter valid vertices.", fg="red")

    def find_shortest_path(self):
        algorithm = self.selected_algorithm.get()

        if algorithm == "Dijkstra":
            self.find_shortest_path_dijkstra()
        elif algorithm == "Floyd-Warshall":
            self.find_shortest_path_floyd_warshall()

    def highlight_path(self, path):
        if self.canvas_widget:
            self.canvas_widget.destroy()

        fig, ax = plt.subplots(figsize=(10, 8))

        if self.pos is None:
            self.pos = nx.spring_layout(self.G)

        nx.draw(self.G, self.pos, with_labels=True, node_color="blue", edge_color="black", font_color="white", ax=ax)

        # Hiển thị nhãn trọng số của các cạnh
        edge_labels = nx.get_edge_attributes(self.G, 'weight')
        nx.draw_networkx_edge_labels(self.G, self.pos, edge_labels=edge_labels, ax=ax)

        # Vẽ các cạnh của đường đi ngắn nhất
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(self.G, self.pos, edgelist=path_edges, edge_color="red", width=2.5, ax=ax)
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=path, node_color="red", ax=ax)
        nx.draw_networkx_labels(self.G, self.pos, font_color='white')

        self.canvas = FigureCanvasTkAgg(fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()

    def draw_graph(self):
        if self.canvas_widget:
            self.canvas_widget.destroy()

        plt.clf()
        fig, ax = plt.subplots(figsize=(10, 8))

        pos = self.pos if self.pos else nx.spring_layout(self.G)

        if self.G.number_of_edges() > 0:
            edge_labels = nx.get_edge_attributes(self.G, 'weight')
            nx.draw(self.G, pos, with_labels=True, node_color="blue", edge_color="black", font_color="white", ax=ax)
            nx.draw_networkx_edge_labels(self.G, pos, edge_labels=edge_labels, ax=ax)

        nx.draw_networkx_nodes(self.G, pos, node_color="blue", ax=ax)
        nx.draw_networkx_labels(self.G, pos, font_color='white')

        plt.title("Graph")
        self.canvas = FigureCanvasTkAgg(fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()


if __name__ == '__main__':
    root = tk.Tk()
    app = GraphApp(root)
    root.mainloop()
