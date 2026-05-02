import os
import re
import json

RESULTS_DIR = "results"
OUTPUT_JSON = "l2_hit_rates.json"

pattern_stats = re.compile(r"cpu0->cpu0_L2C TOTAL\s+ACCESS:\s+(\d+)\s+HIT:\s+(\d+)\s+MISS:\s+(\d+)")

def calculate_geomean(rates):
    """Вычисляет геометрическое среднее списка чисел"""
    valid_rates = [r for r in rates if r > 0]
    if not valid_rates:
        return 0.0
    prod = 1.0
    for val in valid_rates:
        prod *= val
    return prod ** (1.0 / len(valid_rates))

def main():
    if not os.path.exists(RESULTS_DIR):
        print(f"Ошибка: Папка {RESULTS_DIR} не найдена")
        return

    raw_data = {}

    for filename in os.listdir(RESULTS_DIR):
        if not filename.endswith(".txt"):
            continue

        filepath = os.path.join(RESULTS_DIR, filename)
        
        parts = filename.replace(".txt", "").split("_champsim_")
        if len(parts) != 2:
            continue
        
        trace_name = parts[0]
        config_name = parts[1]
        
        if config_name not in raw_data:
            raw_data[config_name] = {}

        with open(filepath, 'r') as f:
            content = f.read()
            match = pattern_stats.search(content)
            if match:
                accesses = int(match.group(1))
                hits = int(match.group(2))
                if accesses > 0:
                    raw_data[config_name][trace_name] = hits / accesses
                else:
                    raw_data[config_name][trace_name] = 0.0
            else:
                print(f"Внимание: В файле {filename} не найдена статистика L2C")

    json_output = []
    
    for config_name, traces in raw_data.items():
        match = re.search(r'(.+)_(\d+)_set_(\d+)_way', config_name)
        if not match:
            print(f"Не удалось распарсить название: {config_name}")
            continue
            
        policy = match.group(1) 
        sets = int(match.group(2))
        ways = int(match.group(3))
        size_kb = (sets * ways * 64) // 1024 
        
        rates = list(traces.values())
        gmean = calculate_geomean(rates)
        
        json_output.append({
            "policy": policy,
            "sets": sets,
            "ways": ways,
            "size_kb": size_kb,
            "traces": traces,
            "geomean": gmean
        })

    json_output.sort(key=lambda x: (x["policy"], x["size_kb"]))

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, indent=4, ensure_ascii=False)
    
    print(f"Статистика успешно собрана и сохранена в файл {OUTPUT_JSON}")

if __name__ == "__main__":
    main()