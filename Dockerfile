# Usa una imagen oficial de Python 3.9 slim
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de dependencias y del proyecto
COPY requirements.txt .
COPY . .

# Instala las dependencias
RUN pip install --upgrade pip && pip install -r requirements.txt

# Expone el puerto (opcional, para bots no es necesario)
# EXPOSE 8000

# Comando para correr tu bot
CMD ["python", "telegram_bot.py"]
