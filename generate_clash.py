import os

SURGE_DIR = "Surge/Ruleset"
CLASH_DIR = "Clash"

for root, dirs, files in os.walk(SURGE_DIR):
    for file in files:
        if not file.endswith(".list"):
            continue

        surge_path = os.path.join(root, file)
        relative_path = os.path.relpath(surge_path, SURGE_DIR)
        clash_base = os.path.join(CLASH_DIR, "Ruleset", os.path.dirname(relative_path))
        os.makedirs(clash_base, exist_ok=True)

        name = os.path.splitext(os.path.basename(file))[0]

        domain_rules = []
        ipcidr_rules = []

        last_comment = None  # 暂存注释

        with open(surge_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip()
                if not line:
                    continue

                if line.startswith("#"):
                    last_comment = line
                    continue

                if line.startswith(("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD")):
                    if last_comment:
                        domain_rules.append(last_comment)
                        last_comment = None
                    domain_rules.append(line)
                elif line.startswith(("IP-CIDR", "IP-CIDR6")):
                    if last_comment:
                        ipcidr_rules.append(last_comment)
                        last_comment = None
                    ipcidr_rules.append(line)
                else:
                    # 其他类型规则可以忽略或者自定义处理
                    last_comment = None

        # 写入 domain 文件
        if domain_rules:
            with open(os.path.join(clash_base, f"{name}_domain.list"), "w", encoding="utf-8") as f:
                f.write("\n".join(domain_rules))

        # 写入 ipcidr 文件
        if ipcidr_rules:
            with open(os.path.join(clash_base, f"{name}_ipcidr.list"), "w", encoding="utf-8") as f:
                f.write("\n".join(ipcidr_rules))
