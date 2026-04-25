#!/bin/bash
set -e  # detiene el script si cualquier comando falla

# Esperar a que la base de datos esté lista
echo "Waiting for database..."
sleep 3

# Aplicar las migraciones
echo "Applying Alembic migrations..."
alembic upgrade head

# Iniciar el servidor — usa los argumentos del CMD/command si se pasan
echo "Initializing server..."
exec "$@"
    
    