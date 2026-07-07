FROM eclipse-temurin:11

# Actualizar e instalar Python3, PIP y setuptools
RUN apt-get update && apt-get install -y python3 python3-pip python3-setuptools && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos primero los requerimientos para aprovechar la caché de Docker
COPY requirements.txt .

# Instalar dependencias con versiones fijas
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copiamos el resto del código
COPY . .

# Comando por defecto
CMD ["python3", "main.py"]
