import schedule
import time
import requests
import logging
from datetime import datetime
import os

# Configuración de Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LegalCrawler:
    def __init__(self):
        self.sources = [
            {"name": "Diario Oficial de la Federación", "url": "https://www.dof.gob.mx/", "type": "Federal"},
            {"name": "Periódico Oficial Jalisco", "url": "https://periodicooficial.jalisco.gob.mx/", "type": "Estatal"}
        ]

    def check_source_availability(self):
        """Verifica que las fuentes oficiales estén en línea."""
        logging.info("Iniciando Verificación de Fuentes Legales...")
        report = []
        
        for source in self.sources:
            try:
                response = requests.get(source["url"], timeout=10)
                status = "Online" if response.status_code == 200 else f"Error {response.status_code}"
                logging.info(f"Fuente: {source['name']} - Estado: {status}")
                report.append({"source": source["name"], "status": status, "timestamp": datetime.now().isoformat()})
            except requests.RequestException as e:
                logging.error(f"Error conectando a {source['name']}: {e}")
                report.append({"source": source["name"], "status": "Unreachable", "error": str(e)})
        
        return report

    def run_daily_scan(self):
        """
        Tarea programada:
        1. Verifica disponibilidad.
        2. (Futuro) Descarga PDFs nuevos.
        3. (Futuro) Pasa a OpenAI para resumen.
        """
        logging.info("--- EJECUTANDO ESCANEO DIARIO DE NORMATIVA ---")
        availability = self.check_source_availability()
        # Aquí se integraría la lógica de descarga y análisis con OpenAI
        # if keys_configured:
        #     analyze_updates()
        logging.info("--- ESCANEO COMPLETADO ---")

def job():
    crawler = LegalCrawler()
    crawler.run_daily_scan()

if __name__ == "__main__":
    logging.info("Servicio de Vigilancia Normativa Iniciado (Background Worker)")
    
    # Ejecutar una vez al inicio para validar
    job()
    
    # Programar a las 02:00 AM diario
    schedule.every().day.at("02:00").do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(60)
