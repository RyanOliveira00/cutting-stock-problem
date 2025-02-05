import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import math

class TelaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Otimizador de Corte de Telas")
        self.root.geometry("1200x800")
        
        self.pecas = []
        
        self.frame_resultado = ttk.LabelFrame(root, text="Resultados", padding="10")
        self.frame_resultado.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        
        self.frame_entrada = ttk.LabelFrame(root, text="Entrada de Dados", padding="10")
        self.frame_entrada.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        
        self.frame_lista = ttk.LabelFrame(root, text="Lista de Peças", padding="10")
        self.frame_lista.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        
        self.frame_visualizacao = ttk.LabelFrame(root, text="Visualização", padding="10")
        self.frame_visualizacao.grid(row=0, column=1, rowspan=3, padx=10, pady=5, sticky="nsew")
        
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(1, weight=1)
        
        self.criar_resultado()
        self.criar_entrada()
        self.criar_lista()
        self.criar_visualizacao()
        
    def criar_resultado(self):
        self.label_telas = ttk.Label(self.frame_resultado, text="Telas necessárias: 0")
        self.label_telas.grid(row=0, column=0, padx=5, pady=5)
        
        self.label_area = ttk.Label(self.frame_resultado, text="Área total: 0 m²")
        self.label_area.grid(row=0, column=1, padx=5, pady=5)
        
        self.label_aproveitamento = ttk.Label(self.frame_resultado, text="Aproveitamento: 0%")
        self.label_aproveitamento.grid(row=0, column=2, padx=5, pady=5)

    def criar_entrada(self):
        ttk.Label(self.frame_entrada, text="Largura (m):").grid(row=0, column=0, padx=5, pady=5)
        self.largura_var = tk.StringVar()
        ttk.Entry(self.frame_entrada, textvariable=self.largura_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(self.frame_entrada, text="Comprimento (m):").grid(row=1, column=0, padx=5, pady=5)
        self.comprimento_var = tk.StringVar()
        ttk.Entry(self.frame_entrada, textvariable=self.comprimento_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(self.frame_entrada, text="Quantidade:").grid(row=2, column=0, padx=5, pady=5)
        self.quantidade_var = tk.StringVar()
        ttk.Entry(self.frame_entrada, textvariable=self.quantidade_var, width=10).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(self.frame_entrada, text="Adicionar Peça", command=self.adicionar_peca).grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(self.frame_entrada, text="Calcular Cortes", command=self.calcular_cortes).grid(row=4, column=0, columnspan=2, pady=10)
        
    def criar_lista(self):
        self.tree = ttk.Treeview(self.frame_lista, columns=("Largura", "Comprimento", "Quantidade"), show="headings")
        self.tree.heading("Largura", text="Largura (m)")
        self.tree.heading("Comprimento", text="Comprimento (m)")
        self.tree.heading("Quantidade", text="Quantidade")
        
        self.tree.column("Largura", width=100, anchor="center")
        self.tree.column("Comprimento", width=100, anchor="center")
        self.tree.column("Quantidade", width=100, anchor="center")
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(self.frame_lista, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        ttk.Button(self.frame_lista, text="Remover Peça", command=self.remover_peca).grid(row=1, column=0, pady=5)
        
    def criar_visualizacao(self):
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_visualizacao)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def adicionar_peca(self):
        try:
            largura = float(self.largura_var.get())
            comprimento = float(self.comprimento_var.get())
            quantidade = int(self.quantidade_var.get())
            
            if largura <= 0 or comprimento <= 0 or quantidade <= 0:
                raise ValueError("Valores devem ser maiores que zero")
            
            if largura > 2.45 or comprimento > 6.0:
                raise ValueError("Dimensões maiores que a tela principal (2.45 x 6.0)")
            
            self.tree.insert("", "end", values=(largura, comprimento, quantidade))
            
            self.largura_var.set("")
            self.comprimento_var.set("")
            self.quantidade_var.set("")
            
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
    
    def remover_peca(self):
        selecionado = self.tree.selection()
        if selecionado:
            self.tree.delete(selecionado)
        
    def calcular_cortes(self):
        pecas = []
        for item in self.tree.get_children():
            valores = self.tree.item(item)["values"]
            pecas.append({
                "largura": float(valores[0]),
                "comprimento": float(valores[1]),
                "quantidade": int(valores[2])
            })
        
        if not pecas:
            messagebox.showwarning("Aviso", "Adicione pelo menos uma peça!")
            return
        
        self.ax.clear()
        
        rect = plt.Rectangle((0, 0), 2.45, 6.0, fill=False, color='black')
        self.ax.add_patch(rect)
        
        pos_x, pos_y = 0, 0
        altura_maxima_linha = 0
        cores = plt.cm.Set3(np.linspace(0, 1, len(pecas)))
        
        for idx, peca in enumerate(pecas):
            for _ in range(peca["quantidade"]):
                # Verificar se precisa ir para próxima linha
                if pos_x + peca["largura"] > 2.45:
                    pos_x = 0
                    pos_y += altura_maxima_linha
                    altura_maxima_linha = 0
                
                # Calcular número de telas necessárias
        area_total = sum(p["largura"] * p["comprimento"] * p["quantidade"] for p in pecas)
        area_tela = 2.45 * 6.0
        num_telas = math.ceil(area_total / area_tela)
        aproveitamento = (area_total / (num_telas * area_tela)) * 100

        self.label_telas.config(text=f"Telas necessárias: {num_telas}")
        self.label_area.config(text=f"Área total: {area_total:.2f} m²")
        self.label_aproveitamento.config(text=f"Aproveitamento: {aproveitamento:.1f}%")

        # Posicionar cada peça
        nova_tela_necessaria = False
        for idx, peca in enumerate(pecas):
            for _ in range(peca["quantidade"]):
                if pos_x + peca["largura"] > 2.45:
                    pos_x = 0
                    pos_y += altura_maxima_linha
                    altura_maxima_linha = 0
                
                if pos_y + peca["comprimento"] > 6.0:
                    nova_tela_necessaria = True
                    break
                
                rect = plt.Rectangle(
                    (pos_x, pos_y),
                    peca["largura"],
                    peca["comprimento"],
                    fill=True,
                    alpha=0.5,
                    color=cores[idx]
                )
                self.ax.add_patch(rect)
                
                self.ax.text(
                    pos_x + peca["largura"]/2,
                    pos_y + peca["comprimento"]/2,
                    f'{peca["largura"]}x{peca["comprimento"]}',
                    ha='center',
                    va='center'
                )
                
                pos_x += peca["largura"]
                altura_maxima_linha = max(altura_maxima_linha, peca["comprimento"])
            
            if nova_tela_necessaria:
                break
        
        if nova_tela_necessaria:
            messagebox.showinfo("Aviso", f"São necessárias {num_telas} telas!")
        
        self.ax.set_xlim(-0.1, 2.55)
        self.ax.set_ylim(-0.1, 6.1)
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        self.ax.set_title('Visualização do Corte (2.45m x 6.0m)')
        
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = TelaApp(root)
    root.mainloop()