import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
import csv
import matplotlib.pyplot as plt
from collections import defaultdict
import os

class RegistroFinanciero:
    def __init__(self, monto, categoria, descripcion, fecha=None):
        self.monto = monto
        self.categoria = categoria
        self.descripcion = descripcion
        self.fecha = fecha if fecha else datetime.now().strftime("%Y-%m-%d")

    def resumen(self):
        return f"{self.fecha} | {self.categoria} | ${self.monto:.2f} | {self.descripcion}"

class Transaccion(RegistroFinanciero):
    def __init__(self, tipo, monto, categoria, descripcion, fecha=None):
        super().__init__(monto, categoria, descripcion, fecha)
        self.tipo = tipo  

    def __str__(self):
        return f"{self.fecha} | {self.tipo} | {self.categoria} | ${self.monto:.2f} | {self.descripcion}"

class Usuario:
    def __init__(self, nombre):
        self.nombre = nombre
        self.transacciones = []

    def agregar_transaccion(self, transaccion):
        self.transacciones.append(transaccion)

    def obtener_balance(self):
        ingresos = sum(t.monto for t in self.transacciones if t.tipo == "Ingreso")
        gastos = sum(t.monto for t in self.transacciones if t.tipo == "Gasto")
        return ingresos - gastos

    def guardar_en_csv(self, archivo):
        with open(archivo, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Fecha", "Tipo", "Categoría", "Monto", "Descripción"])
            for t in self.transacciones:
                writer.writerow([t.fecha, t.tipo, t.categoria, t.monto, t.descripcion])

class GastosAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Control de Gastos Personales")
        self.usuario = Usuario("Steven")

        self.crear_widgets()

    def crear_widgets(self):
        frame_inputs = ttk.Frame(self.root)
        frame_inputs.grid(row=0, column=0, padx=10, pady=5)

        ttk.Label(frame_inputs, text="Tipo:").grid(column=0, row=0)
        self.tipo = ttk.Combobox(frame_inputs, values=["Ingreso", "Gasto"])
        self.tipo.grid(column=1, row=0)
        self.tipo.current(0)

        ttk.Label(frame_inputs, text="Monto:").grid(column=0, row=1)
        self.monto = ttk.Entry(frame_inputs)
        self.monto.grid(column=1, row=1)

        ttk.Label(frame_inputs, text="Categoría:").grid(column=0, row=2)
        self.categoria = ttk.Entry(frame_inputs)
        self.categoria.grid(column=1, row=2)

        ttk.Label(frame_inputs, text="Descripción:").grid(column=0, row=3)
        self.descripcion = ttk.Entry(frame_inputs)
        self.descripcion.grid(column=1, row=3)

        ttk.Button(frame_inputs, text="Agregar", command=self.agregar_transaccion).grid(column=0, row=4, columnspan=2, pady=10)

        self.lista = tk.Listbox(self.root, width=80)
        self.lista.grid(row=1, column=0, padx=10, pady=10)

        self.balance_label = ttk.Label(self.root, text="Balance: $0.00")
        self.balance_label.grid(row=2, column=0)

        frame_buttons = ttk.Frame(self.root)
        frame_buttons.grid(row=3, column=0, pady=10)

        ttk.Button(frame_buttons, text="Gráfico de Gastos", command=self.mostrar_grafico_gastos).grid(column=0, row=0, padx=5)
        ttk.Button(frame_buttons, text="Guardar CSV", command=self.guardar_csv).grid(column=1, row=0, padx=5)
        ttk.Button(frame_buttons, text="Filtrar por categoría", command=self.filtrar_categoria).grid(column=2, row=0, padx=5)
        ttk.Button(frame_buttons, text="Mostrar todo", command=self.mostrar_todo).grid(column=3, row=0, padx=5)

    def agregar_transaccion(self):
        try:
            tipo = self.tipo.get()
            monto = float(self.monto.get())
            categoria = self.categoria.get()
            descripcion = self.descripcion.get()

            if monto <= 0:
                raise ValueError

            transaccion = Transaccion(tipo, monto, categoria, descripcion)
            self.usuario.agregar_transaccion(transaccion)

            self.lista.insert(tk.END, str(transaccion))
            self.actualizar_balance()

            self.monto.delete(0, tk.END)
            self.categoria.delete(0, tk.END)
            self.descripcion.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Por favor ingresa un monto válido.")

    def actualizar_balance(self):
        balance = self.usuario.obtener_balance()
        self.balance_label.config(text=f"Balance: ${balance:.2f}")

    def mostrar_grafico_gastos(self):
        categorias = defaultdict(float)
        for t in self.usuario.transacciones:
            if t.tipo == "Gasto":
                categorias[t.categoria] += t.monto

        if not categorias:
            messagebox.showinfo("Sin datos", "No hay gastos para mostrar.")
            return

        etiquetas = list(categorias.keys())
        valores = list(categorias.values())

        plt.figure(figsize=(6,6))
        plt.pie(valores, labels=etiquetas, autopct='%1.1f%%', startangle=140)
        plt.title('Distribución de Gastos por Categoría')
        plt.axis('equal')
        plt.show()

    def guardar_csv(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if archivo:
            self.usuario.guardar_en_csv(archivo)
            messagebox.showinfo("Guardado", "Archivo guardado correctamente.")

    def filtrar_categoria(self):
        cat = simpledialog.askstring("Filtrar", "Ingrese la categoría a filtrar:")
        if cat:
            self.lista.delete(0, tk.END)
            for t in self.usuario.transacciones:
                if t.categoria.lower() == cat.lower():
                    self.lista.insert(tk.END, str(t))

    def mostrar_todo(self):
        self.lista.delete(0, tk.END)
        for t in self.usuario.transacciones:
            self.lista.insert(tk.END, str(t))

if __name__ == "__main__":
    root = tk.Tk()
    app = GastosAppGUI(root)
    root.mainloop()
