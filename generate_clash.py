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
        classical_rules = []

        current_comments = []

        with open(surge_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # 1️⃣ 注释
                if line.startswith("#") or line.startswith(";"):
                    current_comments.append(line)
                    continue

                # 2️⃣ DOMAIN 类
                if line.startswith(("DOMAIN", "DOMAIN-SUFFIX")):
                    if current_comments:
                        domain_rules.extend(current_comments)
                        current_comments = []
                    domain_rules.append(line)

                # ⚠️ DOMAIN-KEYWORD 归入 classical
                elif line.startswith("DOMAIN-KEYWORD"):
                    if current_comments:
                        classical_rules.extend(current_comments)
                        current_comments = []
                    classical_rules.append(line)

                # 3️⃣ IP 类
                elif line.startswith(("IP-CIDR", "IP-CIDR6")):
                    if current_comments:
                        ipcidr_rules.extend(current_comments)
                        current_comments = []
                    ipcidr_rules.append(line)

                # 4️⃣ 其他规则 → classical
                else:
                    if current_comments:
                        classical_rules.extend(current_comments)
                        current_comments = []
                    classical_rules.append(line)

        # 写入 domain 文件
        if domain_rules:
            with open(os.path.join(clash_base, f"{name}_domain.list"), "w", encoding="utf-8") as f:
                f.write("\n".join(domain_rules) + "\n")

        # 写入 ipcidr 文件
        if ipcidr_rules:
            with open(os.path.join(clash_base, f"{name}_ipcidr.list"), "w", encoding="utf-8") as f:
                f.write("\n".join(ipcidr_rules) + "\n")

        # 写入 classical 文件
        if classical_rules:
            with open(os.path.join(clash_base, f"{name}_classical.list"), "w", encoding="utf-8") as f:
                f.write("\n".join(classical_rules) + "\n")
