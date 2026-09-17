# NLP 实验主循环详解：一个循环、五个函数，各实验如何实现它们

> 8 个实验外壳完全相同：**遍历数据 → 每条记录依次过五个函数**。
> 本文的做法：先给出主循环和五个函数的**签名（契约）**；然后每个函数一章，列出各实验为**同一个函数**写出的不同**函数体**；
> 最后给主循环的四种**变形**，每种都附上变形后的完整代码。全文函数名、变量名、循环结构前后一致。

---

## 一、主循环与五个函数的契约

```python
rows    = read_rows()                             # ① list[dict]，一条记录一个 dict
results = []
for item in rows:
    prompt = make_prompt(item)                     # ② dict → str   （模型输入）
    out    = call_model(prompt)                    # ③ str  → str   （模型输出，永远是原始文本）
    pred   = parse(out)                            # ④ str  → list/dict （干净结构）
    results.append({**item, "pred": pred, "raw": out})   # 结果+原文先落盘
write_jsonl(results)
evaluate(results)                                 # ⑤ 打分，把 pred 与 item["gold"] 对齐比较
```

五个函数的签名即"插槽"，课程里**所有**实验都是往这些插槽里填不同的函数体：

```python
def read_rows(path) -> list[dict]:     # 数据输入：文件 → 每行 dict，含 "text"/"gold" 等
def make_prompt(item: dict) -> str:    # 数据输入→模型输入：dict → 一段文本
def call_model(prompt: str) -> str:    # 核心动作：文本 → 文本（原始回复，未解析）
def parse(out: str) -> list | dict:    # 模型输出：脏文本 → 干净结构（之后才能和 gold 比）
def evaluate(results: list[dict]) -> dict:   # 评测：遍历结果，pred 归一化后 vs gold 打分
```

约定（保证全文连贯的规则）：
- **`call_model` 永远返回 `str`**——Ollama/openai/本地模型都 decode 成文本再返回；tokenize 只是它的内部动作。
- **`parse` 只做"文本→结构"**；"结构→可比较的集合"这类归一化放在 `evaluate` 里对 pred、gold 两侧同时做。
- 真实代码常把 ②③④ 捏成一个 `extract()`（见实验一），或把 ④⑤ 捏进 `compute_metrics`（见 3.1）——**捏合只是把插槽边界前移/后移，不改变五个阶段**。

一个最小可用实现（对应"Ollama 批量评测"这条最常见的线）：

```python
def read_rows(path):                                # ①
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]

def make_prompt(item):                              # ②
    return f"从下面句子抽取实体，只输出 JSON。\n句子：{item['text']}"

def call_model(prompt):                             # ③
    r = requests.post(OLLAMA_URL, json={"model": MODEL, "prompt": prompt,
        "stream": False, "format": SCHEMA, "options": {"temperature": 0}}, timeout=60)
    r.raise_for_status()
    return r.json()["response"]                     # 字符串，留给 parse

def parse(out):                                     # ④
    try: return json.loads(out)
    except Exception: return []                     # 解析失败给占位，不中断

def evaluate(results):                              # ⑤
    tot = {"c": 0, "p": 0, "g": 0}
    for r in results:
        g, p = normalize(r["gold"]), normalize(r["pred"])   # 见 ⑤，两侧同构
        tot["c"] += len(g & p); tot["p"] += len(p); tot["g"] += len(g)
    P = tot["c"] / tot["p"] if tot["p"] else 0.
    R = tot["c"] / tot["g"] if tot["g"] else 0.
    return {"P": P, "R": R, "F1": 2 * P * R / (P + R) if P + R else 0.}
```

---

## 二、五个函数：各实验塞进来的函数体

### ① `read_rows` 的三种函数体

主循环只认 dict，所以装载差异都在这里消化：

```python
# 体1（jsonl，最通用）：一行一个 JSON 对象
def read_rows(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]

# 体2（CSV 金标准，实验一/二）：gold 列是 JSON 串或 词/词 分隔，进循环前还原
def read_rows(path):
    with open(path, encoding="utf-8-sig", newline="") as f:   # BOM 必加 -sig
        reader = csv.DictReader(f)
        rows = list(reader)
    for r in rows:
        r["gold"] = json.loads(r["gold"]) if r["gold"].startswith("{") else \
                    [w.strip() for w in r["gold"].split("/") if w.strip()]
    return rows

# 体3（HF Dataset，实验三/四/五）：只装载+固定 seed 切分；②由 map 批量调 make_prompt 完成
def read_rows(paths):
    ds = load_dataset("json", data_files={"train": paths[0], "test": paths[1]})
    return ds
```
> 备注：HF 版通常把 ①+② 合并成一次 `ds = ds.map(lambda ex: {"text": make_prompt(ex)})`（map 要求回调返回 dict，包一层列名）；训练/评测脚本必须用**同一个 `seed`** 切分，否则评测泄漏到训练数据。

### ② `make_prompt` 的六种函数体（dict → str）

**体 A · 中文指令 + 结构约束（实验一/二抽取、实验三/四 baseline）**
```python
def make_prompt(item):
    return f"""请从下面句子中抽取 (实体, 关系, 实体) 三元组，只输出 JSON，不要解释。
句子：{item['text']}"""
# 结构约束由 call_model 的 payload["format"]=SCHEMA 承担（见 ③体A），这里只说清任务
```
原理：把任务"翻译"成模型能续写的自然语言；JSON 形状约束另走 schema。坑：schema 的 `properties` 键名必须和 `required` 一致（实验二真实 bug，约束静默失效）。

**体 B · few-shot 选例版（实验二意见挖掘）**
```python
POOL = read_jsonl("data/fewshot_pool.jsonl")     # 示例池，模块级只读一次

def make_prompt(item):
    q = embed(item["text"])                       # 内部用到 helper：embed/top_k
    picked = top_k_by_cos(q, POOL, k=5)           # 余弦相似度挑最像的 5 条
    examples = "\n".join(json.dumps(e) for e in picked)
    return (f"参照下面带答案的例子，抽取意见四元组(holder,target,expression,polarity)，"
            f"只输出 JSON。\n例子：\n{examples}\n待抽文本：{item['text']}")
```
原理：小模型需要"输出格式示范"，示例越像 query 越好；选例逻辑只是它的内部 helper，不改变 ② 的签名。

**体 C · 续写问答版（实验三分类微调）**
```python
def make_prompt(item):                            # 训练数据：末尾带标准答案
    return f"Instruction: 给新闻分类，类别是以下四类之一。\nInput: {item['text']}\nAnswer: {item['label']}"
# 推理时同一函数、同一常量，只是没有 item["label"] —— 循环外对模板做 .split("Answer:")[0]
```
原理：causal LM 自回归学整段，分类＝"读到 `Answer:` 后接着吐出类名"，从而**不需要标签→id 映射**。

**体 D · 任务前缀版（实验五摘要/翻译）**
```python
def make_prompt(item):
    return PREFIX + item["text"]                  # PREFIX = "summarize: " / "translate English to French: "
```
原理：T5 多任务靠前缀区分任务；`PREFIX` 放 config，训练/推理引用同一个常量，改一字效果都崩。

**体 E · 检索拼装版（实验六 RAG）**（检索动作见 3.3）
```python
def make_prompt(item):                            # item={"question": q}，上下文已由 call_model 取回
    return PROMPT_TEMPLATE.format(context=item["context"], question=item["question"])
```
原理：prompt 模板外置 yaml，占位符 `.format` 填充；块按 `[1] 标题\n正文` 编号引用、总量受预算限制。

### ③ `call_model` 的三台发动机（str → str）

**体 A · 本地 Ollama（实验一/二/三/四 baseline）**
```python
def call_model(prompt):
    r = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2.5:1.5b", "prompt": prompt, "stream": False,
        "format": SCHEMA,                          # 与 make_prompt 体 A 配对
        "options": {"temperature": 0}}, timeout=120)
    r.raise_for_status()
    return r.json()["response"]                    # 仍是字符串；parse 再 json.loads
```
分类场景把 `SCHEMA` 换成 enum 变体＝"强制单选"（实验三 baseline）。`temperature=0`＝贪心可复现。

**体 B · openai 兼容端点（实验二参考代码）**
```python
def call_model(prompt):
    client = make_client_by_model_prefix(MODEL)    # 内部按 qwen/deepseek 前缀切 base_url
    completion = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_BLOCK},     # few-shot/思考说明
                  {"role": "user",   "content": prompt}],
        top_p=0.1, seed=666)
    return completion.choices[0].message.content
```
流式思考解码（内部 helper `decode_thinking`）：逐 chunk 取 `delta.content`，思考段走 `delta.reasoning_content`，记得 `if not chunk.choices: continue`。

**体 C · 本地 transformers（实验三~七）**
```python
def call_model(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(device)     # tokenize 只是内部动作
    with torch.no_grad():
        outputs = model.generate(**inputs, max_new_tokens=128,
                                 do_sample=False, temperature=0.0,   # 采样版见 3.2
                                 pad_token_id=tokenizer.eos_token_id)
    gen = outputs[0][inputs["input_ids"].shape[1]:]                 # 掐掉 prompt
    return tokenizer.decode(gen, skip_special_tokens=True)          # 返回 str
```
`pad_token is None → pad_token = eos_token` 是 Qwen 系必做兜底。

**通用注意点**：单条异常 `try/except` 记 log、返回占位**继续跑**；`timeout` 随文本变长调大；长跑边算边写盘。

### ④ `parse` 的分级容错（str → 结构）

```python
def parse(out):
    if not isinstance(out, str): return None
    try:    return json.loads(out)                 # ① 有 schema 保底：直接成功
    except Exception: pass
    m = re.search(r"\{.*\}", out, re.DOTALL)       # ② 自由文本里抠最外层 JSON
    if m:
        try: return json.loads(m.group())
        except Exception: return None              # ③ 彻底失败 → 占位
    return None
```
各实验在此基础上叠加"取片段"：
- 实验三：模型回的是自然语言，`parse` 换成 `decode.split("Answer:")[-1].strip().split("\n")[0]`，对不上就在标签表里子串查找，兜底 `"ERROR"`；
- 实验四：先 `normalize_completion_text`（兼容 str / `[{"content":…}]` / dict），再进上面的分级解析；
- 实验二：数组在文字后面时，从右往左试每个 `[` 的后缀能否解析，失败按 `JSONDecodeError.pos` 截尾；
- 实验七：回的是代码围栏，`parse` 换成剥围栏 ` ```python ` → ` ``` ` 取内部文本；
- 实验二另外有键名兼容（模型可能把 `Source` 写成 `Expression`），属 parse 内部归一。

### ⑤ `evaluate` 的五种尺子（含"两侧归一化"）

`evaluate` 的骨架统一是：**先把 pred 和 gold 各归一化成同构集合，再打分**。归一化因任务而异的正是课程反复强调的"集合化"：

```python
def normalize(x):                                 # 取决于任务，三选一：
    # 词级（实验一 CWS）：词表 → 字符区间集合，让切分对齐变成集合求交
    return {(start, start + len(w)) for w in x}   # 由累进 start 得到
    # 实体/三元组（实验一二四）：去空白+大写归一 → 元组
    return {(e["text"].strip().upper(), e["type"]) for e in x}
    # 槽位（实验二意见）：→ 词 token 集合，空槽用 frozenset(["_"])
```
打分五种尺子（按任务形态选一个，微平均/除零保护通用）：

| 任务 | evaluate 用什么 | 对应实验 |
|---|---|---|
| 分词/抽取/NER/实体 | 集合交集 P/R/F1（见 1.最小实现） | 一、二、四 |
| 分类 | `accuracy_score` + 归一混淆矩阵 `ConfusionMatrixDisplay(..., normalize="true")` | 三 |
| 抽取式 QA | EM / token-F1：`normalize_answer` 链(lower→去标点→去冠词→空白)；`Counter(pred)&Counter(truth)`；多参考取 max | 五 |
| 摘要/翻译 | ROUGE / BLEU：先"解码三步曲"(logits→argmax/-100还原→batch_decode)+strip；BLEU 的 refs 用 `[[ref]]` | 五 |
| RAG（无金标） | term_recall / exact_match：在"答案+检索文本"里查期望术语 | 六 |
| 代码（无金标文本答案） | 见 3.4：不评分，直接跑 | 七 |

通用规矩：评测与训练**同 seed 切分**；指标写 json，画图脚本**只回读 jsonl**；预测存 `raw` 以便重评。

---

## 三、主循环的四种变形（附改写后的代码）

主循环真正跑不动五种情况：**要训练**、**要采样出组回传梯度**、**"调用"分两级（先检索）**、**评分对象是可执行文件**、**对象是对话轮**。每种只是把 ①②③④⑤ 里某一两级替换/拉长，其余保持原样——对照原循环看差异即可。

### 3.1 变形一：训练（实验三/五）——`call_model` 出现"训练/推理"两个模式

```python
# —— 训练：循环体整体交给 Trainer；③ 从"forward"变成"forward+backward" ——
tokenized = dataset.map(make_prompt).map(tokenize)   # ② 全量预处理（含 labels=input_ids.copy()）
trainer = Trainer(model=model, args=training_args,
                  train_dataset=tokenized["train"],
                  data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
                  processing_class=tokenizer,        # 老版本参数名 tokenizer=
                  compute_metrics=compute_metrics)   # = ④⑤ 的批处理合并版
trainer.train()
trainer.model.save_pretrained(OUTPUT_DIR)            # 结果"落盘"= 权重文件

# —— 推理：把原主循环原样重跑一遍，只有 ③ 换成生成模式 ——
rows = read_rows(TEST_FILE)
for item in rows:
    results.append({**item, "pred": parse(call_model(make_prompt(item)))})   # ②③④ 照旧
write_jsonl(results); evaluate(results)
```
`compute_metrics` 就是把 ④⑤ 提前搬进训练的回调：解码 → 去 -100 → ROUGE/BLEU，签名见 `datasets` 约定 `(eval_pred) -> dict`。
RL 变体（实验四）另见 3.2。

### 3.2 变形二：GRPO（实验四）——循环的"一条"从句子变成"一组采样"

```python
for group in rows:                                  # 一条 prompt = 一组
    prompts = [make_prompt(group)] * NUM_GENERATIONS
    outputs = call_model_batch(prompts)             # ③ 采样版：do_sample=True,t=0.8,top_p=0.9,
                                                    #    num_return_sequences=NUM_GENERATIONS
    texts   = [parse(o) for o in outputs]           # ④ 轻解析
    rewards = reward_fn(completions=[{"content": t} for t in texts],
                        answer=group["answer"])     # ⑤ 稠密分档打分(格式/文本/漏报/误报/clip)
    adv     = (rewards - mean(rewards)) / (std(rewards) or 1.0)   # 组内相对优势，无 critic
    loss    = -(log_prob(texts) * adv).mean()       # ⑤ 的结果回流成 ③ 的更新信号
    loss.backward()
```
`reward_fn` 就是实验四里的 `reward_function`，签名是 trl 的最小契约：入参 `completions` 列表 + `answer`，返回等长 `list[float]`。正式版用 `trl.GRPTrainer`，它替你管理 采样/优势/更新/日志（键：`rewards/<名字>/mean`、`frac_reward_zero_std`）。

### 3.3 变形三：RAG（实验六）——③ 内部多一级检索，⑤ 换无参考指标

```python
# —— ③ 从"一发即答"变成"先检索、再生成"：签名 str→str 不变 ——
def call_model(question):                 # question 即 make_prompt 的输出
    hits = index.search(embed(question), top_k)      # ③a 检索 top-k 块（FAISS IndexFlatIP）
    ctx  = format_context(hits)                      #     块→"[i] 标题\n正文"，受预算限制
    return generate(PROMPT_TEMPLATE.format(context=ctx, question=question))   # ③b 再生成

rows = [{"question": q} for q in questions]          # ① item 从"句子"变成"问题"
for item in rows:                                    # 主循环照旧
    results.append({**item, "pred": parse(call_model(make_prompt(item)))})
evaluate(results)                                    # ⑤ 换成 term_recall 等无参考指标
```
建索引在循环外做一次（离线）：`read_rows(文档) → 分块 → embedding → faiss.add → write_index`。
GRAG 只是把 ③a 的排序规则换成"向量分 + 文档图上 PPR 分各 min-max 归一化后融合"——生成器 ③b、评测 ⑤ 全程不动，归因才干净。

### 3.4 变形四：代码判题（实验七）——`parse` 落文件，`evaluate` 用 subprocess 真跑

```python
# —— ⑤ 的"尺子"不存在文本答案，改成：编译/运行 I/O 是否一致 ——
for task in tasks:                                   # ① task = {question, tests}
    code = call_model(make_prompt(task))             # ③ 代码模型生成（带回 markdown 围栏）
    clean = parse(code)                              # ④ = 剥围栏，拿纯代码
    path = OUTPUT_DIR / f"{task['id']}/solution.py"
    path.write_text(clean, encoding="utf-8")         # ④ 落成"可执行文件"而非 dict
    results.append({"id": task["id"], **judge(task, path)})   # ⑤ 逐用例真跑

def judge(task, path):                               # ⑤ 裁判
    passed_all = True
    for case in task["tests"]:
        cp = subprocess.run(["python", str(path)], input=case["input"], text=True,
                            stdout=PIPE, stderr=PIPE, timeout=10)
        ok = cp.returncode == 0 and \
             cp.stdout.strip() == case["output"].strip()   # 行尾空白先归一
        passed_all &= ok
    return {"passed": passed_all, ...}               # TLE/RE/WA 分型；翻译用 javac 编译判 PASS/FAIL
```
原理：代码是"可执行答案"，对错由行为（编译 + IO）决定，任何文本相似度评分都会误判。坑：判题子进程/文件头加 `sys.set_int_max_str_digits(0)`（Python 3.11+ 超长 int 会抛异常）。

### 3.5 变形五：Agent（实验八）——对象从"一批句子"变成一个"对话轮"

Agent 是离五函数最远的一种：它没有"预测 vs gold"，输出是**动作**。但单轮流水线仍可对位：

```python
def run_turn(query, memory):                         # 一个"item"= 一轮对话
    action   = planner(query, memory)                # ② 文本 → {thought, action, action_input}
    allowed, reason = permissions.check(action)      # ③ 前的安全闸(白名单/危险词/路径越界)
    if not allowed:
        return f"拒绝执行：{reason}"                  # ④ 输出=拒绝文本，照样记录
    obs = skills[action["action"]](**action["action_input"])   # ③ 技能=纯函数 str→str
    memory.push(query, action, obs)                  # ④ 记录(trace/memory) ≈ results.append
    return build_answer(action, obs)                 # 输出

# —— 外层评测循环把它当"⑤"用：行为对不对，而不是措辞对不对 ——
for case in test_cases:                              # 每条 = {query, expected_action, should_refuse}
    rt = AgentRuntime(); ans = rt.turn(case["query"])   # 每例新实例，记忆不串扰
    score_tool   += (rt.last_action == case["expected_action"])
    score_safety += (case["should_refuse"] and "拒绝" in ans)
report = {"工具选择率": ..., "安全拒绝率": ..., "任务完成率": ...}
```
因为 `planner` 输出的动作协议固定为 dict、技能固定为"字符串进字符串出"，未来把规则 planner 换成真 LLM 时，②③ 之外的代码零改动。

---

## 四、变形对照与逐实验速查

不变式：**每个实验 = 遍历数据 → ②③④ 产出结构化 `pred` → ⑤ 与 `gold` 对齐打分**；
训练只是让 ③ 暂时多一个更新模式；RAG/代码/Agent 只是把 ③、④ 或 ⑤ 其中一个拉长替换。

| 实验 | read_rows ① | make_prompt ② | call_model ③ | parse ④ | evaluate ⑤ |
|---|---|---|---|---|---|
| 一 CWS/NER | csv→gold 还原 | 体A 指令+约束 | 体A Ollama | loads→**词→字符区间** | 集合 P/R/F1 微平均 |
| 二 抽取/意见 | csv→gold | 体A / 体B few-shot | 体B openai 兼容 | 右起`[`容错+键别名 | 三元组严格/宽松；槽 token 集相交 |
| 三 分类 | HF→map | 体C 续写问答 | 训练 Trainer / 推理 体C | 取 `Answer:` 后首行 | accuracy+混淆矩阵 |
| 四 NER+GRPO | BIO→实体集 | 体A 指令+约束 | 3.2 采样出组+回传 | `extract_json` 抠 `{}` | reward_fn=稠密分档(见 3.2) |
| 五 QA/摘要/翻译 | HF→切分 | 体D PREFIX(+offset) | Trainer / 推理解码三步曲 | 解码三步曲 | EM-F1 / ROUGE / BLEU |
| 六 RAG | 文档→分块建索引 | 体E 模板 | 3.3 检索+生成两级 | 同上 | term_recall 等无参考 |
| 七 代码生成 | 清洗成 {题,用例} | 指令"只给代码" | 本地代码模型 generate | 剥围栏→写文件 | 3.4 subprocess 真跑 |
| 八 Agent | 对话轮+记忆 | 规则 planner→动作 | 权限+技能分发 | (动作即结果) | 工具选择率/完成率/安全拒绝率 |
