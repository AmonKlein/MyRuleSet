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

        # 定义三类容器
        domain_rules = []
        ipcidr_rules = []
        classical_rules = [] # 存放其他所有规则 (如 USER-AGENT, PROCESS-NAME 等)
        
        current_comments = []

        with open(surge_path, "r", encoding="utf-8") as f:
            for line in f:
                raw_line = line.strip()
                if not raw_line:
                    continue

                # 1. 处理注释
                if raw_line.startswith("#") or raw_line.startswith(";"):
                    current_comments.append(raw_line)
                    continue

                # 2. 分类逻辑
                # 域名类
                if raw_line.startswith(("DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD")):
                    if current_comments:
                        domain_rules.extend(current_comments)
                        current_comments = []
                    domain_rules.append(raw_line)
                
                # IP 类
                elif raw_line.startswith(("IP-CIDR", "IP-CIDR6", "IP-ASN")):
                    if current_comments:
                        ipcidr_rules.extend(current_comments)
                        current_comments = []
                    ipcidr_rules.append(raw_line)
                
                # 3. 其他所有规则 (Classical)
                else:
                    if current_comments:
                        classical_rules.extend(current_comments)
                        current_comments = []
                    classical_rules.append(raw_line)

        # 辅助写入函数：只有列表不为空（且不只有注释）时才创建文件
        def save_if_not_empty(rules, suffix):
            # 检查列表中是否包含实际的规则（非注释行）
            has_actual_rule = any(not (r.startswith("#") or r.startswith(";")) for r in rules)
            if has_actual_rule:
                file_path = os.path.join(clash_base, f"{name}_{suffix}.list")
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(rules) + "\n")

        # 写入三个文件
        save_if_not_empty(domain_rules, "domain")
        save_if_not_empty(ipcidr_rules, "ipcidr")
        save_if_not_empty(classical_rules, "classical")
