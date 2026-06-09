import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.pyplot as plt
from func import GraficadorExcel, ConfiguracionModo

class AplicacionGraficos:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Gráficos - Sector Salud")
        self.root.geometry("1300x750")
        
        # Cargar modo nocturno guardado
        self.modo_oscuro = ConfiguracionModo.cargar_modo()
        
        # Variables
        self.graficador = None
        self.current_canvas = None
        self.current_figure = None
        self.toolbar = None
        
        # Variable para columnas adicionales en apilamiento
        self.columnas_apilamiento = []
        
        # Configurar estilos
        self.configurar_estilos()
        
        # Crear interfaz
        self.crear_widgets()
        
        # Aplicar modo inicial
        self.aplicar_modo()
        
    def configurar_estilos(self):
        """Configura estilos de ttk"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
    def crear_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame izquierdo (controles)
        left_frame = ttk.Frame(main_frame, width=380)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # Frame derecho (gráfico)
        self.right_frame = ttk.Frame(main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Botón cargar archivo
        ttk.Button(left_frame, text="📂 Cargar Archivo Excel", command=self.cargar_excel).pack(pady=10)
        
        # Frame de configuración de gráficos
        config_frame = ttk.LabelFrame(left_frame, text="Configuración del Gráfico", padding=10)
        config_frame.pack(fill=tk.X, pady=10)
        
        # Tipo de gráfico
        ttk.Label(config_frame, text="Tipo de Gráfico:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.tipo_grafico = ttk.Combobox(config_frame, values=[
            "lineal", "barras", "dispersion", "apilamiento", "circular", "multiple"
        ], state="readonly", width=20)
        self.tipo_grafico.grid(row=0, column=1, pady=5, sticky=tk.W)
        self.tipo_grafico.bind("<<ComboboxSelected>>", self.cambiar_tipo_grafico)
        
        # Columnas
        ttk.Label(config_frame, text="Columna X / Categoría:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.col_x = ttk.Combobox(config_frame, state="readonly", width=20)
        self.col_x.grid(row=1, column=1, pady=5, sticky=tk.W)
        
        ttk.Label(config_frame, text="Columna Y / Valor:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.col_y = ttk.Combobox(config_frame, state="readonly", width=20)
        self.col_y.grid(row=2, column=1, pady=5, sticky=tk.W)
        
        # Frame para columnas de apilamiento (dinámico)
        self.apilamiento_frame = ttk.LabelFrame(config_frame, text="Columnas para Apilar", padding=5)
        self.apilamiento_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=tk.W+tk.E)
        self.apilamiento_frame.grid_remove()  # Ocultar inicialmente
        
        # Lista de columnas seleccionadas para apilamiento
        self.lista_apilamiento = tk.Listbox(self.apilamiento_frame, height=4, selectmode=tk.MULTIPLE)
        self.lista_apilamiento.pack(fill=tk.X, pady=5)
        
        # Botones para agregar/quitar columnas de apilamiento
        btn_frame = ttk.Frame(self.apilamiento_frame)
        btn_frame.pack(fill=tk.X)
        ttk.Button(btn_frame, text="➕ Agregar columna", command=self.agregar_columna_apilamiento).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="➖ Quitar selección", command=self.quitar_columna_apilamiento).pack(side=tk.LEFT, padx=2)
        
        # Título personalizado
        ttk.Label(config_frame, text="Título personalizado:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.titulo_entry = ttk.Entry(config_frame, width=25)
        self.titulo_entry.grid(row=4, column=1, pady=5, sticky=tk.W)
        
        # Botón generar
        ttk.Button(config_frame, text="🎨 Generar Gráfico", command=self.generar_grafico).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Botón modo nocturno
        self.btn_modo = ttk.Button(left_frame, text="🌙 Modo Nocturno", command=self.toggle_modo)
        self.btn_modo.pack(pady=10)
        
        # Frame para controles de zoom
        zoom_frame = ttk.LabelFrame(left_frame, text="Controles de Zoom", padding=10)
        zoom_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(zoom_frame, text="💡 Usa la rueda del mouse\npara hacer zoom en el gráfico", 
                 justify=tk.CENTER).pack(pady=5)
        ttk.Button(zoom_frame, text="🔍 Restablecer Zoom", command=self.reset_zoom).pack(pady=5)
        
    def agregar_columna_apilamiento(self):
        """Agrega una columna seleccionada a la lista de apilamiento"""
        seleccion = self.col_y_apilamiento.get()
        if seleccion and seleccion not in self.columnas_apilamiento:
            self.columnas_apilamiento.append(seleccion)
            self.actualizar_lista_apilamiento()
            
    def quitar_columna_apilamiento(self):
        """Quita las columnas seleccionadas de la lista de apilamiento"""
        seleccionados = self.lista_apilamiento.curselection()
        for idx in reversed(seleccionados):
            if idx < len(self.columnas_apilamiento):
                del self.columnas_apilamiento[idx]
        self.actualizar_lista_apilamiento()
        
    def actualizar_lista_apilamiento(self):
        """Actualiza la lista visual de columnas para apilar"""
        self.lista_apilamiento.delete(0, tk.END)
        for col in self.columnas_apilamiento:
            self.lista_apilamiento.insert(tk.END, col)
            
    def cargar_excel(self):
        """Carga archivo Excel"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if archivo:
            try:
                self.graficador = GraficadorExcel(archivo)
                categoricas, numericas = self.graficador.obtener_columnas()
                
                # Actualizar comboboxes
                self.col_x['values'] = categoricas + numericas
                self.col_y['values'] = numericas
                self.col_y_apilamiento = ttk.Combobox(self.apilamiento_frame, values=numericas, state="readonly", width=18)
                self.col_y_apilamiento.pack(pady=5)
                
                if categoricas:
                    self.col_x.set(categoricas[0])
                if numericas:
                    self.col_y.set(numericas[0])
                    self.col_y_apilamiento.set(numericas[0] if len(numericas) > 0 else "")
                
                # Limpiar lista de apilamiento
                self.columnas_apilamiento = []
                self.actualizar_lista_apilamiento()
                
                messagebox.showinfo("Éxito", f"Archivo cargado correctamente\n{len(self.graficador.df)} filas, {len(self.graficador.df.columns)} columnas")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{str(e)}")
                
    def cambiar_tipo_grafico(self, event=None):
        """Cambia según tipo de gráfico"""
        tipo = self.tipo_grafico.get()
        if tipo == "apilamiento":
            self.apilamiento_frame.grid()
        else:
            self.apilamiento_frame.grid_remove()
            
    def generar_grafico(self):
        """Genera el gráfico seleccionado"""
        if not self.graficador:
            messagebox.showwarning("Advertencia", "Primero carga un archivo Excel")
            return
            
        tipo = self.tipo_grafico.get()
        if not tipo:
            messagebox.showwarning("Advertencia", "Selecciona un tipo de gráfico")
            return
            
        x_col = self.col_x.get()
        y_col = self.col_y.get()
        titulo = self.titulo_entry.get() if self.titulo_entry.get().strip() else None
        
        try:
            if tipo == "apilamiento":
                if len(self.columnas_apilamiento) < 2:
                    messagebox.showwarning("Advertencia", "Selecciona al menos 2 columnas para el gráfico de apilamiento")
                    return
                self.current_figure = self.graficador.crear_figura(tipo, x_col, self.columnas_apilamiento, titulo)
            elif tipo == "multiple":
                # Para gráfico múltiple, usar varias combinaciones
                if self.col_y_apilamiento.get():
                    extra = self.col_y_apilamiento.get()
                else:
                    extra = y_col
                combinaciones = [
                    ("barras", x_col, [y_col]),
                    ("lineal", x_col, [y_col]),
                    ("dispersion", x_col, [extra])
                ]
                self.current_figure = self.graficador.grafico_multiple(
                    ["barras", "lineal", "dispersion"],
                    combinaciones,
                    titulo or "Múltiples Gráficos"
                )
            else:
                self.current_figure = self.graficador.crear_figura(tipo, x_col, [y_col], titulo)
                
            # Mostrar gráfico con zoom
            self.mostrar_grafico_con_zoom()
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el gráfico:\n{str(e)}")
            
    def mostrar_grafico_con_zoom(self):
        """Muestra el gráfico en la interfaz con funcionalidad de zoom"""
        # Limpiar frame derecho
        for widget in self.right_frame.winfo_children():
            widget.destroy()
            
        # Crear frame para el gráfico y la toolbar
        graph_frame = ttk.Frame(self.right_frame)
        graph_frame.pack(fill=tk.BOTH, expand=True)
        
        # Crear canvas de matplotlib
        self.current_canvas = FigureCanvasTkAgg(self.current_figure, graph_frame)
        self.current_canvas.draw()
        
        # Conectar evento de la rueda del mouse para zoom
        self.current_canvas.get_tk_widget().bind('<Control-MouseWheel>', self.zoom_con_rueda)
        self.current_canvas.get_tk_widget().bind('<Control-Button-4>', self.zoom_con_rueda)
        self.current_canvas.get_tk_widget().bind('<Control-Button-5>', self.zoom_con_rueda)
        self.current_canvas.get_tk_widget().bind('<Button-2>', self.pan_inicio)  # Botón medio para pan
        self.current_canvas.get_tk_widget().bind('<B2-Motion>', self.pan_mover)
        
        self.current_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Agregar toolbar de matplotlib (ya incluye zoom y pan)
        self.toolbar = NavigationToolbar2Tk(self.current_canvas, graph_frame)
        self.toolbar.update()
        self.toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Barra de herramientas adicional
        toolbar_frame = ttk.Frame(self.right_frame)
        toolbar_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(toolbar_frame, text="💾 Guardar gráfico", 
                  command=self.guardar_grafico).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text="🔄 Limpiar", 
                  command=self.limpiar_grafico).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text="🔍 Zoom In", 
                  command=self.zoom_in).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar_frame, text="🔍 Zoom Out", 
                  command=self.zoom_out).pack(side=tk.LEFT, padx=5)
                  
    def zoom_con_rueda(self, event):
        """Función para hacer zoom con la rueda del mouse"""
        if self.current_figure is None:
            return
            
        ax = self.current_figure.gca()
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        # Factor de zoom
        zoom_factor = 1.1 if event.delta > 0 or event.num == 4 else 0.9
        
        # Calcular centro del zoom
        if hasattr(event, 'x') and hasattr(event, 'y'):
            xdata = ax.transData.inverted().transform([event.x, event.y])[0]
            ydata = ax.transData.inverted().transform([event.x, event.y])[1]
            
            # Zoom centrado en el cursor
            x_range = (xlim[1] - xlim[0]) * zoom_factor
            y_range = (ylim[1] - ylim[0]) * zoom_factor
            
            new_xlim = (xdata - x_range/2, xdata + x_range/2)
            new_ylim = (ydata - y_range/2, ydata + y_range/2)
        else:
            # Zoom centrado en el centro del gráfico
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0]) * zoom_factor
            y_range = (ylim[1] - ylim[0]) * zoom_factor
            
            new_xlim = (x_center - x_range/2, x_center + x_range/2)
            new_ylim = (y_center - y_range/2, y_center + y_range/2)
        
        ax.set_xlim(new_xlim)
        ax.set_ylim(new_ylim)
        self.current_canvas.draw()
        
    def pan_inicio(self, event):
        """Iniciar pan (movimiento)"""
        if self.current_figure is None:
            return
        self.pan_start_x = event.x
        self.pan_start_y = event.y
        self.pan_start_xlim = self.current_figure.gca().get_xlim()
        self.pan_start_ylim = self.current_figure.gca().get_ylim()
        
    def pan_mover(self, event):
        """Mover el gráfico (pan)"""
        if self.current_figure is None or not hasattr(self, 'pan_start_x'):
            return
            
        ax = self.current_figure.gca()
        dx = event.x - self.pan_start_x
        dy = event.y - self.pan_start_y
        
        # Convertir movimiento de píxeles a unidades de datos
        x_range = self.pan_start_xlim[1] - self.pan_start_xlim[0]
        y_range = self.pan_start_ylim[1] - self.pan_start_ylim[0]
        
        fig_width = self.current_canvas.get_width_height()[0]
        fig_height = self.current_canvas.get_width_height()[1]
        
        x_shift = -dx * x_range / fig_width
        y_shift = dy * y_range / fig_height
        
        ax.set_xlim(self.pan_start_xlim[0] + x_shift, self.pan_start_xlim[1] + x_shift)
        ax.set_ylim(self.pan_start_ylim[0] + y_shift, self.pan_start_ylim[1] + y_shift)
        self.current_canvas.draw()
        
    def zoom_in(self):
        """Aumentar zoom"""
        if self.current_figure:
            ax = self.current_figure.gca()
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0]) * 0.8
            y_range = (ylim[1] - ylim[0]) * 0.8
            ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
            self.current_canvas.draw()
            
    def zoom_out(self):
        """Disminuir zoom"""
        if self.current_figure:
            ax = self.current_figure.gca()
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
            x_center = (xlim[0] + xlim[1]) / 2
            y_center = (ylim[0] + ylim[1]) / 2
            x_range = (xlim[1] - xlim[0]) * 1.2
            y_range = (ylim[1] - ylim[0]) * 1.2
            ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
            self.current_canvas.draw()
            
    def reset_zoom(self):
        """Restablecer zoom original"""
        if self.current_figure and self.graficador:
            # Regenerar el gráfico original
            self.generar_grafico()
            
    def guardar_grafico(self):
        """Guarda el gráfico actual"""
        if self.current_figure:
            archivo = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG Image", "*.png"), ("PDF", "*.pdf"), ("SVG", "*.svg")]
            )
            if archivo:
                self.current_figure.savefig(archivo, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Éxito", f"Gráfico guardado en:\n{archivo}")
                
    def limpiar_grafico(self):
        """Limpia el gráfico actual"""
        for widget in self.right_frame.winfo_children():
            widget.destroy()
        self.current_figure = None
        self.current_canvas = None
        self.toolbar = None
        
    def toggle_modo(self):
        """Alterna modo nocturno/claro"""
        self.modo_oscuro = not self.modo_oscuro
        ConfiguracionModo.guardar_modo(self.modo_oscuro)
        self.aplicar_modo()
        
    def aplicar_modo(self):
        """Aplica el modo actual a toda la interfaz"""
        if self.modo_oscuro:
            # Modo oscuro
            bg_color = "#2b2b2b"
            fg_color = "#ffffff"
            self.root.configure(bg=bg_color)
            self.btn_modo.config(text="☀️ Modo Claro")
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
            self.style.configure("TLabelFrame", background=bg_color, foreground=fg_color)
            self.style.configure("TButton", background="#3c3c3c", foreground=fg_color)
            self.style.map("TButton", background=[('active', '#4a4a4a')])
            self.style.configure("TCombobox", fieldbackground="#3c3c3c", foreground=fg_color)
            self.style.configure("TEntry", fieldbackground="#3c3c3c", foreground=fg_color)
            self.style.configure("TListbox", background="#3c3c3c", foreground=fg_color)
            
            # Configurar matplotlib para modo oscuro
            plt.style.use('dark_background')
        else:
            # Modo claro
            bg_color = "#f0f0f0"
            fg_color = "#000000"
            self.root.configure(bg=bg_color)
            self.btn_modo.config(text="🌙 Modo Nocturno")
            self.style.configure("TFrame", background=bg_color)
            self.style.configure("TLabel", background=bg_color, foreground=fg_color)
            self.style.configure("TLabelFrame", background=bg_color, foreground=fg_color)
            self.style.configure("TButton", background="#e0e0e0", foreground=fg_color)
            self.style.map("TButton", background=[('active', '#d0d0d0')])
            self.style.configure("TCombobox", fieldbackground="white", foreground=fg_color)
            self.style.configure("TEntry", fieldbackground="white", foreground=fg_color)
            self.style.configure("TListbox", background="white", foreground=fg_color)
            
            # Configurar matplotlib para modo claro
            plt.style.use('default')
            
        # Refrescar el gráfico si existe
        if self.current_figure:
            self.mostrar_grafico_con_zoom()

if __name__ == "__main__":
    root = tk.Tk()
    app = AplicacionGraficos(root)
    root.mainloop()