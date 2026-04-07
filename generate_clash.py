import os

SURGE_DIR = "Surge/Ruleset"
CLASH_DIR = "Clash/Ruleset"

for root, dirs, files in os.walk(SURGE_DIR):
    for file in files:
        if not file.endswith(".list"):
            continue

        surge_path = os.path.join(root, file)

        # 计算对应 clash 路径
        relative_path = os.path.relpath(surge_path, SURGE_DIR)
        clash_base = os.path.join(CLASH_DIR, os.path.dirname(relative_path))
        os.makedirs(clash_base, exist_ok=True)

        name = os.path.splitext(os.path.basename(file))[0]

        domain_rules = []
        ipcidr_rules = []

        with open(surge_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if line.startswith(("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD")):
                    domain_rules.append(line)
                elif line.startswith(("IP-CIDR", "IP-CIDR6")):
                    ipcidr_rules.append(line)

        # 写入 domain
        if domain_rules:
            with open(os.path.join(clash_base, f"{name}_domain.list"), "w", encoding="utf-8") as f:
                f.write("\n".join(domain_rules))

        # 写入 ipcidr
        if ipcidr_rules:
            with open(os.path.join(clash_base, f"{name}_ipcidr.list"), "w", encoding="utf-8") as f:
                f.write("\n".join(ipcidr_rules))