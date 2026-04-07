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
        
        # 用于临时存储连续的注释行
        current_comments = []

        with open(surge_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # 1. 如果是注释行，先存入临时列表
                if line.startswith("#") or line.startswith(";"):
                    current_comments.append(line)
                    continue

                # 2. 如果是域名规则
                if line.startswith(("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD")):
                    if current_comments:
                        domain_rules.extend(current_comments)
                        current_comments = [] # 用完清空
                    domain_rules.append(line)
                
                # 3. 如果是 IP 规则
                elif line.startswith(("IP-CIDR", "IP-CIDR6")):
                    if current_comments:
                        ipcidr_rules.extend(current_comments)
                        current_comments = [] # 用完清空
                    ipcidr_rules.append(line)
                
                else:
                    # 如果遇到了既不是注释也不是匹配规则的行（如 USER-AGENT 等）
                    # 清空当前暂存的注释，防止注释被错误地带到下一条不相关的规则
                    current_comments = []

        # 写入 domain 文件
        if domain_rules:
            with open(os.path.join(clash_base, f"{name}_domain.list"), "w", encoding="utf-8") as f:
                f.write("\n".join(domain_rules) + "\n")

        # 写入 ipcidr 文件
        if ipcidr_rules:
            with open(os.path.join(clash_base, f"{name}_ipcidr.list"), "w", encoding="utf-8") as f:
                f.write("\n".join(ipcidr_rules) + "\n")
