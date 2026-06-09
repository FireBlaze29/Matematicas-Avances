import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import os
import json

class GraficadorExcel:
    def __init__(self, file_path):
        """Inicializa el graficador con un archivo Excel"""
        self.file_path = file_path
        self.df = pd.read_excel(file_path, sheet_name=0)
        self.columnas_numericas = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.columnas_categoricas = self.df.select_dtypes(include=['object']).columns.tolist()
        
    def obtener_columnas(self):
        """Retorna listas de columnas numéricas y categóricas"""
        return self.columnas_categoricas, self.columnas_numericas
    
    def grafico_lineal(self, ax, x_col, y_col, titulo=None):
        """Gráfico de líneas"""
        self.df_sorted = self.df.sort_values(by=x_col)
        ax.plot(self.df_sorted[x_col], self.df_sorted[y_col], marker='o', linestyle='-', linewidth=2)
        ax.set_xlabel(x_col, fontsize=10)
        ax.set_ylabel(y_col, fontsize=10)
        ax.set_title(titulo or f"Gráfico Lineal: {y_col} vs {x_col}", fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
    def grafico_barras(self, ax, x_col, y_col, titulo=None):
        """Gráfico de barras"""
        ax.bar(self.df[x_col], self.df[y_col], color='skyblue', edgecolor='black')
        ax.set_xlabel(x_col, fontsize=10)
        ax.set_ylabel(y_col, fontsize=10)
        ax.set_title(titulo or f"Diagrama de Barras: {y_col} por {x_col}", fontsize=12, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3, axis='y')
        
    def grafico_dispersion(self, ax, x_col, y_col, titulo=None):
        """Gráfico de dispersión"""
        ax.scatter(self.df[x_col], self.df[y_col], alpha=0.6, color='green', edgecolors='black')
        ax.set_xlabel(x_col, fontsize=10)
        ax.set_ylabel(y_col, fontsize=10)
        ax.set_title(titulo or f"Diagrama de Dispersión: {y_col} vs {x_col}", fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        
    def grafico_apilamiento(self, ax, x_col, y_cols, titulo=None):
        """Gráfico de barras apiladas"""
        if len(y_cols) < 2:
            raise ValueError("Se necesitan al menos 2 columnas para apilar")
        
        datos = self.df.set_index(x_col)[y_cols]
        datos.plot(kind='bar', stacked=True, ax=ax, colormap='viridis', edgecolor='black')
        ax.set_xlabel(x_col, fontsize=10)
        ax.set_ylabel("Valores", fontsize=10)
        ax.set_title(titulo or "Diagrama de Apilamiento", fontsize=12, fontweight='bold')
        ax.tick_params(axis='x', rotation=45)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3, axis='y')
        
    def grafico_circular(self, ax, col_cat, col_num, num_categorias=10, titulo=None):
        """Gráfico circular (top N categorías)"""
        datos = self.df.groupby(col_cat)[col_num].sum().sort_values(ascending=False)
        
        if len(datos) > num_categorias:
            otros = datos[num_categorias:].sum()
            datos = datos[:num_categorias]
            datos["Otros"] = otros
            
        colores = plt.cm.Set3(np.linspace(0, 1, len(datos)))
        ax.pie(datos.values, labels=datos.index, autopct='%1.1f%%', colors=colores, startangle=90)
        ax.set_title(titulo or f"Gráfico Circular: {col_num} por {col_cat}", fontsize=12, fontweight='bold')
        ax.axis('equal')
        
    def grafico_multiple(self, tipo_graficos, combinaciones, titulo_global="Múltiples Gráficos"):
        """Crea múltiples gráficos en una figura"""
        num_plots = len(combinaciones)
        fig, axes = plt.subplots(1, num_plots, figsize=(6*num_plots, 5))
        if num_plots == 1:
            axes = [axes]
            
        fig.suptitle(titulo_global, fontsize=14, fontweight='bold')
        
        for idx, (tipo, x_col, y_cols) in enumerate(combinaciones):
            if tipo == 'lineal':
                self.grafico_lineal(axes[idx], x_col, y_cols[0])
            elif tipo == 'barras':
                self.grafico_barras(axes[idx], x_col, y_cols[0])
            elif tipo == 'dispersion':
                self.grafico_dispersion(axes[idx], x_col, y_cols[0])
            elif tipo == 'apilamiento':
                self.grafico_apilamiento(axes[idx], x_col, y_cols)
            elif tipo == 'circular':
                self.grafico_circular(axes[idx], x_col, y_cols[0])
                
        plt.tight_layout()
        return fig
    
    def crear_figura(self, tipo_grafico, x_col, y_cols, titulo=None):
        """Crea una figura según el tipo de gráfico"""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if tipo_grafico == "lineal":
            self.grafico_lineal(ax, x_col, y_cols[0], titulo)
        elif tipo_grafico == "barras":
            self.grafico_barras(ax, x_col, y_cols[0], titulo)
        elif tipo_grafico == "dispersion":
            self.grafico_dispersion(ax, x_col, y_cols[0], titulo)
        elif tipo_grafico == "apilamiento":
            self.grafico_apilamiento(ax, x_col, y_cols, titulo)
        elif tipo_grafico == "circular":
            self.grafico_circular(ax, x_col, y_cols[0], titulo=titulo)
            
        plt.tight_layout()
        return fig

class ConfiguracionModo:
    ARCHIVO_CONFIG = "modo_config.json"
    
    @classmethod
    def cargar_modo(cls):
        """Carga el modo guardado (True=oscuro, False=claro)"""
        if os.path.exists(cls.ARCHIVO_CONFIG):
            with open(cls.ARCHIVO_CONFIG, 'r') as f:
                datos = json.load(f)
                return datos.get('modo_oscuro', False)
        return False
    
    @classmethod
    def guardar_modo(cls, modo_oscuro):
        """Guarda el modo"""
        with open(cls.ARCHIVO_CONFIG, 'w') as f:
            json.dump({'modo_oscuro': modo_oscuro}, f)