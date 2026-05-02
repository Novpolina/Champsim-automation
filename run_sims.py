import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Имена трасс (должны совпадать с именами трасс в папке)
TRACES = [
    "603.bwaves_s-1080B.champsimtrace.xz",
    "445.gobmk-36B.champsimtrace.xz",
    "437.leslie3d-271B.champsimtrace.xz"
]

policies = [("lru", "no"), ("ship", "no"), ("ship", "spp_dev")]
sizes = [(256, 8), (512, 8), (512, 16), (1024, 8), (1024, 16)]


# Рекомендуется поставить значение, равное половине ядер процессора или чуть больше
MAX_WORKERS = 6

def run_simulation(binary, trace):
    trace_name = trace.split('.')[1].split('-')[0] 
    binary_name = os.path.basename(binary)
    log_file = os.path.join(RESULTS_DIR, f"{trace_name}_{binary_name}.txt")
    
    if os.path.exists(log_file):
        print(f" Пропуск: {log_file} уже существует.")
        return

    cmd = f"./{binary} --warmup-instructions 50000000 --simulation-instructions 100000000 {trace}"
    print(f"Запуск: {binary_name} на трассе {trace_name}")
    
    with open(log_file, "w") as out:
        subprocess.run(cmd, shell=True, stdout=out, stderr=subprocess.STDOUT)
    print(f"Готово: {binary_name} на трассе {trace_name} -> лог сохранен")

def main():
    tasks = []
    for repl, pref in policies:
        for sets, ways in sizes:
            pref_name = "no_prefetch" if pref == "no" else pref
            binary = f"bin/champsim_{repl}_{pref_name}_{sets}_set_{ways}_way"
            
            for trace in TRACES:
                if os.path.exists(binary) and os.path.exists(trace):
                    tasks.append((binary, trace))
                else:
                    print(f"Ошибка: не найден файл {binary} или {trace}")

    print(f"Всего задач для запуска: {len(tasks)}")
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for binary, trace in tasks:
            executor.submit(run_simulation, binary, trace)

if __name__ == "__main__":
    main()