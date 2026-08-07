# 3xa-harness

給長時間執行真實工作的 agent 使用的紀律 skills: 凍結範圍、把只能由人判斷的內容送進 gate、留下決策、用證據誠實收尾

四個核心 skill 圍成一個工作迴圈: `workorder` 凍結任務, `sensory-gate` 保留人的判斷, `decision-log` 讓決策跨過 context reset, `honest-closeout` 逐項連回證據. 另有一個可選的除錯 add-on. MIT, 零依賴, 不到一分鐘即可安裝

## 安裝

```bash
claude plugin marketplace add https://github.com/3xachris/3xa-harness
claude plugin install harness-core@3xa-harness
```

需要較完整的診斷流程時, 也可以安裝選配的 debug plugin:

```bash
claude plugin install harness-debug@3xa-harness
```

Codex 使用者也可以把四個核心 skill 複製到使用者 skill 目錄:

```powershell
$dest = Join-Path $HOME '.agents\skills'
New-Item -ItemType Directory -Force $dest | Out-Null
Copy-Item skills\core\workorder,skills\core\sensory-gate,skills\core\decision-log,skills\core\honest-closeout -Destination $dest -Recurse -Force
Get-ChildItem $dest\workorder,$dest\sensory-gate,$dest\decision-log,$dest\honest-closeout -Filter SKILL.md
```

其他 agent 可用 [skills.sh](https://skills.sh):

```bash
npx skills@latest add 3xachris/3xa-harness
```

選 Claude plugin, Codex user skills 或 skills.sh 其中一條路即可. 選多條會讓每個 skill 被安裝兩次

## 可執行的收尾驗證

這包包含 [`verify_closeout.py`](verify_closeout.py), 是獨立的 Python 3 腳本. 它不是附屬範例, 而是把工單、收尾與決策日誌串起來的形式檢查: 逐一配對 `AC-n`, 檢查 evidence path, 確認 `DONE` 有獨立功能驗證, 檢查每個 gate 有 disposition, 也檢查決策日誌是否指向收尾報告. 可由人或 CI 執行:

```bash
python verify_closeout.py artifacts/order.md artifacts/closeout.md docs/decisions.md --root .
```

它只檢查格式和可追溯連結, 不替人判斷內容是否正確. 舊格式報告會輸出 `Unable to verify, skipped` 並以不同 exit code 結束. 最後一行會再次說明這個邊界

## 接入既有專案

可以把記錄放在既有專案的文件區和 artifacts 區, 例如:

```text
your-project/
├── AGENTS.md                    # 或 CLAUDE.md: 每次都會載入的指標檔
├── docs/decisions.md            # 一份 append-only 決策日誌
└── artifacts/
    └── checkout-20260807/
        ├── order.md
        ├── closeout.md
        └── gate/review-01/
```

第一次建立日誌時, 在 agent 每次都會載入的 `AGENTS.md`, `CLAUDE.md` 或等效檔案加入:

```markdown
## Decision log

`docs/decisions.md` — 本專案的決策、拒絕與修正, newest last. 開始工作前先讀它
```

這就是新 session 自動找到日誌的機制. 工單、gate 資料夾、證據和收尾放在同一個 artifacts 資料夾. 既有 issue 和 PR 可作為工單或收尾中的 evidence path 或連結; 測試報告放在相應 `AC-n` 的證據欄, 若是獨立執行也可作為 `Functional verification` 證據. 決策日誌記錄 gate 開啟、人工作出的 disposition、修正, 最後以 `closeout` 指向報告

```bash
python verify_closeout.py artifacts/checkout-20260807/order.md artifacts/checkout-20260807/closeout.md docs/decisions.md --root .
```

## 最小完整範例

[`.verification-demo/`](.verification-demo/) 是一個可直接照抄的小任務, 真實檔案串起工單、gate 與收尾:

```text
.verification-demo/
├── order.md
├── closeout.md
├── decisions.md
├── evidence/verification.txt
└── gate/review-01/approved.txt
```

工單用 `- [ ] AC-1: ... | evidence: ...` 凍結兩條驗收線, 收尾用同一個 `AC-n` 標記逐條回答. 日誌開啟並結束 `review-01`, 再指向收尾. 收尾則記錄獨立測試、gate 核准和證據路徑. 在 repo 根目錄執行:

```bash
python verify_closeout.py .verification-demo/order.md .verification-demo/closeout.md .verification-demo/decisions.md --root .
```

應以 exit code `0` 成功解析; 最後的誠實邊界仍表示內容是否正確由人判斷

## 四個核心 skill

| Skill | 用途 |
|---|---|
| [`workorder`](skills/core/workorder/SKILL.md) | 先凍結一句話、已知事實、材料、固定參數、預算、`AC-n` 驗收線和非目標 |
| [`sensory-gate`](skills/core/sensory-gate/SKILL.md) | 把圖片、音訊或影片集中到 gate 資料夾, 由人記錄 reviewer、批次和核准範圍 |
| [`decision-log`](skills/core/decision-log/SKILL.md) | 讓決策、拒絕、修正和收尾跨過 context reset, 並由每次載入的專案檔指向它 |
| [`honest-closeout`](skills/core/honest-closeout/SKILL.md) | 逐條回答驗收, 把功能驗證與 hash、環境 identity 分開, 並保留人員修正和背景程序狀態 |
| [`staged-diagnosis`](addons/debug/skills/staged-diagnosis/SKILL.md) | 將難解錯誤拆成 reproduce、minimise、hypothesise、instrument、fix、regression-test 六段 |

`DONE` 的獨立功能驗證不等於 hash 或環境 identity. hash 說明檢查的是哪些 bytes, environment 說明在哪裡執行; 它們不證明功能真的正確

## 誠實邊界

這些是 protocols, 不是 enforcement. 它們不會物理阻止任何步驟被略過; 價值在於規則具體且可檢查, 略過時會留下可見缺口. 真正需要物理 enforcement 的 gate, 應由你的專案自行接 hook

## Credits

寫作標準參考 Matt Pocock 的 [`writing-for-agents`](https://github.com/mattpocock/skills): 用正向目標取代禁止語句, 每個意思只有一個權威定義, 每個步驟都有可檢查的完成條件. `staged-diagnosis` 的順序也是同一 repo 的 `/diagnosing-bugs` 泛化. Both MIT

English: [README.md](README.md)

## 授權

MIT, 詳見 [LICENSE](LICENSE). 可在自己的產品中使用、fork 和 ship
