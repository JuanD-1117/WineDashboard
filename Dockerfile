# Imagen de WineDashboard. Fija Python 3.12 para no depender del Python del anfitrión
# (macOS trae 3.9 y las versiones actuales de Streamlit y pandas exigen >= 3.11).
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --root-user-action=ignore -r requirements.txt

COPY app.py .

EXPOSE 8501

HEALTHCHECK --interval=10s --timeout=5s --retries=12 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/_stcore/health')"

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.headless=true", "--browser.gatherUsageStats=false"]
