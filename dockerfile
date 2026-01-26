# USAMOS PYTHON 3.9 SLIM (Ligero y estable basado en Debian)
FROM python:3.9-slim

# VARIABLES DE ENTORNO PARA PYTHON
# Evita que Python genere archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
# Evita que Python guarde logs en buffer (imprime directo a consola para AWS Logs)
ENV PYTHONUNBUFFERED=1

# DIRECTORIO DE TRABAJO
WORKDIR /app

# INSTALACIÓN DE DEPENDENCIAS
# Copiamos primero solo el requirements.txt para aprovechar la caché de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# COPIAR EL CÓDIGO FUENTE
# Copiamos app.py, engine.py y cualquier otro archivo necesario
COPY . .

# SEGURIDAD: CREAR USUARIO NO-ROOT
# Es mala práctica correr apps en producción como 'root'
RUN useradd -m agro_user && chown -R agro_user /app
USER agro_user

# EXPONER EL PUERTO 5000
EXPOSE 5000

# COMANDO DE ARRANQUE (GUNICORN)
# -w 4: 4 Workers para concurrencia
# --access-logfile -: Redirige logs a stdout (para que AWS CloudWatch los vea)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--access-logfile", "-", "--error-logfile", "-", "app:app"]