import time
import threading
import requests
import json
import statistics

# Configuración
API_URL = "http://localhost:8000/analyze"
NUM_REQUESTS = 50
CONCURRENT_THREADS = 10

# Payload de prueba (Un caso complejo para estresar el motor)
PAYLOAD = {
    "tipo_inmueble": "Hospital General",
    "m2_construccion": 12000,
    "niveles": 6,
    "aforo": 800,
    "aforo_autorizado": 800,
    "trabajadores": 250,
    "municipio": "Monterrey",
    "estado": "Nuevo León", # Activa lógica experto Mosler
    "has_gas": True,
    "has_substation": True,
    "has_machine_room": True
}

results = []
errors = 0

def make_request(req_id):
    global errors
    start_time = time.time()
    try:
        response = requests.post(API_URL, json=PAYLOAD, timeout=30)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            results.append(elapsed)
            # print(f"Req {req_id}: OK ({elapsed:.2f}s)")
        else:
            errors += 1
            print(f"Req {req_id}: ERROR {response.status_code}")
    except Exception as e:
        errors += 1
        print(f"Req {req_id}: EXCEPTION {e}")

def run_load_test():
    print(f"--- INICIANDO PRUEBA DE CARGA ---")
    print(f"Target: {API_URL}")
    print(f"Requests: {NUM_REQUESTS} | Concurrency: {CONCURRENT_THREADS}")
    
    threads = []
    start_total = time.time()
    
    # Batches processing
    for i in range(0, NUM_REQUESTS, CONCURRENT_THREADS):
        batch = []
        for j in range(CONCURRENT_THREADS):
            if i + j < NUM_REQUESTS:
                t = threading.Thread(target=make_request, args=(i+j,))
                batch.append(t)
                t.start()
        
        for t in batch:
            t.join()
            
    total_time = time.time() - start_total
    
    print("\n--- RESULTADOS DE LA PRUEBA ---")
    if results:
        print(f"Total Requests: {NUM_REQUESTS}")
        print(f"Successful: {len(results)}")
        print(f"Failed: {errors}")
        print(f"Total Duration: {total_time:.2f}s")
        print(f"Avg Latency: {statistics.mean(results):.4f}s")
        print(f"Max Latency: {max(results):.4f}s")
        print(f"Min Latency: {min(results):.4f}s")
        print(f"Throughput: {len(results)/total_time:.2f} req/s")
    else:
        print("No successful requests recorded.")

if __name__ == "__main__":
    run_load_test()
