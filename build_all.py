import json
import subprocess
import multiprocessing

CONFIG_FILE = "champsim_config.json"
CORES = multiprocessing.cpu_count() 

policies = [
    ("lru", "no"),
    ("ship", "no"),
    ("ship", "spp_dev")
]

sizes = [
    (256, 8),
    (512, 8),
    (512, 16),
    (1024, 8),
    (1024, 16)
]

def run_command(cmd):
    subprocess.run(cmd, shell=True, check=True)

def main():
    with open(CONFIG_FILE, 'r') as f:
        config_data = json.load(f)

    for repl, pref in policies:
        for sets, ways in sizes:
            print(f"\n==================================================")
            print(f"Сборка: {repl}, prefetch: {pref}, {sets} sets, {ways} ways")
            print(f"==================================================")

            config_data["L2C"]["replacement"] = repl
            config_data["L2C"]["prefetcher"] = pref
            config_data["L2C"]["sets"] = sets
            config_data["L2C"]["ways"] = ways

            with open(CONFIG_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)

            pref_name = "no_prefetch" if pref == "no" else pref
            bin_name = f"bin/champsim_{repl}_{pref_name}_{sets}_set_{ways}_way"

            run_command(f"./config.sh {CONFIG_FILE}")
            
            run_command(f"make -j {CORES}")
            
            run_command(f"cp bin/champsim {bin_name}")

    print("\nВсе 15 бинарных файлов успешно собраны и лежат в папке bin/")

if __name__ == "__main__":
    main()