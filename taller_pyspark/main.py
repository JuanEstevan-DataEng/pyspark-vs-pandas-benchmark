import time
import pandas as pd
import os
import matplotlib.pyplot as plt
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, max, min

# --- COLORES ANSI PARA LA TERMINAL ---
class Color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def generate_temp_csv(input_file, output_file, multiplier):
    """
    Genera un archivo CSV temporal repitiendo el contenido del original 'multiplier' veces.
    """
    with open(input_file, 'r') as f_in:
        lines = f_in.readlines()
    
    header = lines[0]
    data = lines[1:]
    
    with open(output_file, 'w') as f_out:
        f_out.write(header)
        for _ in range(multiplier):
            f_out.writelines(data)
            
    return len(data) * multiplier

def main():
    # ---------------------------------------------------------
    # PARTE 1: El Taller Original (Funcionalidad Requerida)
    # ---------------------------------------------------------
    print(f"\n{Color.BOLD}{Color.PURPLE}" + "="*60)
    print(f"   PARTE 1: TALLER ORIGINAL (Dataset Pequeño)")
    print("="*60 + f"{Color.END}")
    
    print(f"{Color.DARKCYAN}[INFO] Inicializando SparkSession...{Color.END}")
    spark = SparkSession.builder \
        .appName("SalaryAnalysisLab") \
        .master("local[*]") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    # 1.1 Pandas
    start = time.time()
    df_pd = pd.read_csv("data.csv")
    time_pd = time.time() - start
    print(f"{Color.GREEN}[PANDAS]  Tiempo: {time_pd:.4f}s | Filas: {len(df_pd)}{Color.END}")

    # 1.2 PySpark
    start = time.time()
    df_spark = spark.read.csv("data.csv", header=True, inferSchema=True)
    count = df_spark.count() # Acción forzada
    time_spark = time.time() - start
    print(f"{Color.YELLOW}[PYSPARK] Tiempo: {time_spark:.4f}s | Filas: {count}{Color.END}")

    # 1.3 Operaciones
    print(f"\n{Color.CYAN}--- Resultados Análisis (PySpark) ---")
    
    print(f"{Color.BOLD}1. Muestra de datos filtrados (Salary > 50000):{Color.END}")
    df_clean = df_spark.select("YearsExperience", "Salary")
    df_clean.filter(col("Salary") > 50000).show(5)
    
    print(f"{Color.BOLD}2. Estadísticas Generales:{Color.END}")
    stats = df_clean.select(avg("Salary"), max("Salary"), min("Salary"))
    stats.show()

    # ---------------------------------------------------------
    # PARTE 2: Benchmark Escalabilidad (Gráficas)
    # ---------------------------------------------------------
    print(f"\n{Color.BOLD}{Color.PURPLE}" + "="*60)
    print(f"   PARTE 2: BENCHMARK DE ESCALABILIDAD")
    print(f"   Generando datos simulados y comparando tiempos...")
    print("="*60 + f"{Color.END}")

    # Definimos multiplicadores
    # Reducimos el máximo para evitar OOM (Out of Memory) en contenedores Docker con RAM limitada
    multipliers = [1, 5000, 10000, 100000] 
    
    times_pd = []
    times_spark = []
    row_counts = []

    temp_file = "temp_big_data.csv"

    try:
        for m in multipliers:
            # A. Generar Datos
            n_rows = generate_temp_csv("data.csv", temp_file, m)
            row_counts.append(n_rows)
            print(f"\n{Color.BLUE}--> Probando con multiplicador x{m} ({n_rows} filas)...{Color.END}")

            # B. Medir Pandas
            t0 = time.time()
            _ = pd.read_csv(temp_file)
            t_pd = time.time() - t0
            times_pd.append(t_pd)
            print(f"    {Color.GREEN}Pandas:  {t_pd:.4f}s{Color.END}")

            # C. Medir PySpark
            t0 = time.time()
            df_temp = spark.read.csv(temp_file, header=True, inferSchema=True)
            df_temp.count() # Forzar lectura
            t_sp = time.time() - t0
            times_spark.append(t_sp)
            print(f"    {Color.YELLOW}PySpark: {t_sp:.4f}s{Color.END}")

    finally:
        # Limpieza
        if os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"\n{Color.RED}[CLEANUP] Archivo temporal eliminado.{Color.END}")

    # ---------------------------------------------------------
    # PARTE 3: Generar Gráfica
    # ---------------------------------------------------------
    print(f"\n{Color.CYAN}Generando gráfica comparativa 'benchmark.png'...{Color.END}")
    
    plt.figure(figsize=(10, 6))
    plt.plot(row_counts, times_pd, marker='o', label='Pandas (Local Memory)', color='blue')
    plt.plot(row_counts, times_spark, marker='x', label='PySpark (Distributed Engine)', color='orange')
    
    plt.title('Comparación de Rendimiento: Pandas vs PySpark')
    plt.xlabel('Número de Filas')
    plt.ylabel('Tiempo de Procesamiento (segundos)')
    plt.grid(True)
    plt.legend()
    plt.savefig('benchmark.png')
    print(f"{Color.BOLD}{Color.GREEN}¡Gráfica guardada exitosamente!{Color.END}")

    spark.stop()

if __name__ == "__main__":
    main()