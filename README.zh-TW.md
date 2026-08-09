<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.png">
  <img alt="3xa-harness" src="assets/hero-light.png">
</picture>

# 3xa-harness

給長時間執行真實工作的 agent 使用的紀律 skills: 凍結範圍、把只能由人判斷的內容送進 gate、留下決策、用證據誠實收尾

五個核心 skill 圍成一個工作迴圈: `workorder` 凍結任務, `sensory-gate` 保留人的判斷, `decision-log` 讓決策跨過 context reset, `handoff` 在工作換手時交接狀態, `honest-closeout` 逐項連回證據. 另有一個可選的除錯 add-on. MIT, 零依賴, 不到一分鐘即可安裝

## 先選份量, 再決定裝什麼

不必先吞下整套迴圈才能用這個 repo. 對眼前的任務回答五個問題:

```text
新任務
│
├─ 會跨過這次對話存活, 或換一個 session 接手嗎?
├─ 邊界還沒定, 範圍可能一直長大嗎?
├─ 要交給別人(subagent、外包、隊友)嗎?
├─ 做錯了很難撤銷嗎?
├─ 要有人親眼看或親耳聽結果嗎?
│
├─ 全部否
│   └─ Light: 只留一筆 decision-log —
│      改了什麼、一行理由、細節放在哪. 不開 order 不寫收尾
│
└─ 任一是
    └─ Core: workorder + decision-log + honest-closeout
       ├─ 工作要換手          → 加 handoff
       └─ 有圖/音/影要人判斷   → 加 sensory-gate
```

每個條件的完整說明在[什麼時候開完整迴圈](#什麼時候開完整迴圈). 然後只拿你答出來的那個份量:

| 份量 | 拿什麼 | 在哪 |
|---|---|---|
| **Light** | 不用裝任何東西 — 這個做法就是每次改動留一筆紀錄. 想把 skill 本體帶著, 裝核心 plugin 即可(用不到的 skill 不會出聲), 或只複製 `skills/core/decision-log/` 進你的 skill 目錄; 目前沒有「只裝 decision-log」的獨立 plugin | [輕量路徑](#輕量路徑) |
| **Core** | `harness-core` plugin — 五顆 skill 的完整迴圈, 依任務性質逐顆觸發 | [安裝](#安裝) |
| **Validation** | Core 之上, 在信任收尾報告之前跑 `verify_closeout.py`, 再用 `harness-audit` 兩支檢查掃記錄本身 | [可執行的收尾驗證](#可執行的收尾驗證) |
| **CI** | Validation 之上, 用 GitHub Actions 範本在每個動到 artifacts 的 PR 上自動跑 | [整合範本](#整合範本) |

`sensory-gate` 只在有東西必須由人看或聽時才進場 — 完整迴圈的任務若不含任何媒體, 從頭到尾不會開 gate

## 什麼時候開完整迴圈

要不要凍結 `workorder` 並跑完整迴圈, 看的是任務的**性質**不是大小 — 一個龐大但機械式的工作和一個五行的小修都可能落在任一邊. 符合下列任一項就開:

- **會跨過這次對話存活.** 這次做不完, 或換一個 session — 明天的你, 或別人 — 接手. 凍結的 order 就是那個 session 該讀的東西, 而不是要你去回想
- **邊界還沒定.** 需求還模糊, 或者「順手做掉」的念頭一直冒出來. 凍結逼邊界在第一個編輯之前就存在
- **要交給別人.** subagent、外包、隊友 — order 就是他們拿到的整份 brief, 取代那段產生它的對話
- **做錯了很難撤銷.** schema migration、刪除資料集、已發布的版本 — 任何 `git revert` 救不回來的東西
- **要有人親眼看或親耳聽結果.** 渲染圖、配音、剪好的影片 — 這正是 `sensory-gate` 存在的理由, 而 workorder 給那次審核一條可核銷的驗收線

以上都不是「這件事要花不少時間」— 一個很長、一次做完、容易復原、也沒人會碰的重構不需要任何一項, 不管它動了幾個檔案. 一行設定值的修改, 只要明天換一個 session 接手, 就需要

## 輕量路徑

不開完整迴圈不代表什麼都不留. 上面五項都不符合時, 略過 order、預算熔斷和收尾報告 — 但仍然寫下這一筆 `decision-log`: 改了什麼、一行理由、細節放在哪. 這才是冷讀真正需要的事實; workorder 其餘六個欄位是為了保護五分鐘小修不會有的東西(可能漂移的範圍、陌生人需要信任的證據)

全有或全無, 兩種人都會停手不做: 全略過, 悄悄變大的小修就再也沒被框成一件事; 全都要, 小修就會為了躲文書作業改成不留紀錄地做掉, 比完全沒文書作業更糟. 這一筆紀錄, 是不管份量多輕都值得留下的部分

如果一件「輕量」任務做著做著發現比想像中大 — 三個檔案下去了, 邊界還在冒 — 那就是該停下來補寫一份 order 的訊號, 不是繼續裸奔下去

## 安裝

Claude Code 對話裡直接打:

```
/plugin marketplace add 3xachris/3xa-harness
/plugin install harness-core@3xa-harness
```

或改用終端機, 結果一樣:

```bash
claude plugin marketplace add https://github.com/3xachris/3xa-harness
claude plugin install harness-core@3xa-harness
```

需要較完整的診斷流程時, 也可以安裝選配的 debug plugin; 要機器掃自己的記錄, 加裝 audit plugin:

```bash
claude plugin install harness-debug@3xa-harness
claude plugin install harness-audit@3xa-harness
```

Codex 使用者也可以把五個核心 skill 複製到使用者 skill 目錄:

```powershell
$dest = Join-Path $HOME '.agents\skills'
New-Item -ItemType Directory -Force $dest | Out-Null
Copy-Item skills\core\workorder,skills\core\sensory-gate,skills\core\decision-log,skills\core\handoff,skills\core\honest-closeout -Destination $dest -Recurse -Force
Get-ChildItem $dest\workorder,$dest\sensory-gate,$dest\decision-log,$dest\handoff,$dest\honest-closeout -Filter SKILL.md
```

加裝的 skill 用同樣方式複製 — 每個 addon skill 資料夾都自帶所需腳本, 複製資料夾就是完整安裝:

```powershell
Copy-Item addons\debug\skills\staged-diagnosis,addons\audit\skills\claim-audit,addons\audit\skills\repo-audit -Destination $dest -Recurse -Force
Get-ChildItem $dest\claim-audit,$dest\repo-audit -Filter *.py
```

第二行應該列出 `claim_audit.py` 與 `repo_audit.py`, 與各自的 `SKILL.md` 同層. 腳本與 skill 放同一層是刻意的: skill 的腳本若擺在 repo 別處, 任何以資料夾為單位複製的安裝路徑都會拿到一顆壞掉的 skill

OpenCode 使用者要 clone 整個 repo 進 OpenCode 的 skill 目錄, 不是只複製裡面的 `skills/` 資料夾, 要留完整 repo 結構, 路徑會長成 `~/.opencode/skills/3xa-harness/skills/core/<skill-name>/SKILL.md`:

```sh
git clone https://github.com/3xachris/3xa-harness.git ~/.opencode/skills/3xa-harness
```

OpenCode 會自動找出 `~/.opencode/skills/` 底下每個 `SKILL.md`, 不用改任何設定檔, 重啟 OpenCode 後生效

其他 agent 可用 [skills.sh](https://skills.sh):

```bash
npx skills@latest add 3xachris/3xa-harness
```

*本環境未驗證* — 寫這份 README 的沙盒環境在網路層擋掉 npm/node 對外連線, 這行指令沒能在本地實跑過, 寫法照 skills.sh 文件對「用 owner/repo 加 GitHub repo」的既有形狀寫; 若你那邊也失敗, 錯誤會長這樣: `npm error code EACCES` / `FetchError ... registry.npmjs.org`, 那是你的網路環境問題, 不是這個 repo 的問題 — 上面 Claude plugin 與 Codex 兩條路徑都不經過 npm

選 Claude plugin, Codex user skills, OpenCode 或 skills.sh 其中一條路即可, 選多條會讓每個 skill 被安裝兩次

## 可執行的收尾驗證

### 在建第一份成品前

先查這件事, 不要等做完才查: [`verify_closeout.py`](verify_closeout.py) 需要 `PATH` 上有 Python 3.9 以上. 在第一份 order 出現之前, 先確認一次:

```bash
python --version
```

指令失敗, 或版本低於 3.9, 就別圍著這支腳本建 artifacts 資料夾 — 腳本本身到時候也啟動不了, 沒辦法告訴你這件事. 改用肉眼跑同樣五題:

1. order 裡每個 `AC-n`, 收尾裡都有對應的 `- [PASS/FAIL/BLOCKED] AC-n` 那行
2. `| evidence:` 後面每個路徑都打得開
3. 收尾狀態若是 `DONE`, 要有一行 `- Functional verification: ... | evidence: ...`, 證據路徑打得開, 而且描述不只是 hash 或環境宣稱
4. 決策日誌裡每個 gate 開啟紀錄 — 帶 `gate` 欄位的 `yaml` 區塊, 或舊式 `> Gate: ...` 那行 — 都有對應的 disposition (`disposition` 欄位, 或舊式 `> Gate disposition: ...` 那行); 收尾的 `[GATE]` 那行與該 disposition 的 reviewer、archive 一致; archive 不是 `none` 時該路徑打得開
5. 決策日誌裡有一筆指向本報告的收尾條目 — 新格式是 `type: closeout` 配 `source: <指向本報告的路徑>`, 舊格式是 `> Type: closeout | Target: <指向本報告的路徑>`

跑腳本能更快抓出手動核對時的疏漏; 它不能取代判斷內容對不對 — 不管有沒有 runtime 都一樣

這包包含 `verify_closeout.py`, 是獨立的 Python 3 腳本. 它不是附屬範例, 而是把工單、收尾與決策日誌串起來的形式檢查: 逐一配對 `AC-n`, 檢查 evidence path, 確認 `DONE` 有獨立功能驗證, 檢查每個 gate 有 disposition, 也檢查決策日誌是否指向收尾報告. 可由人或 CI 執行:

```bash
python verify_closeout.py artifacts/order.md artifacts/closeout.md docs/decisions.md --root .
```

它只檢查格式和可追溯連結, 不替人判斷內容是否正確. 舊格式報告會輸出 `Unable to verify, skipped` 並以不同 exit code 結束. 最後一行會再次說明這個邊界

## 記錄健檢

`verify_closeout.py` 驗的是一件任務的紙本自洽. `harness-audit` 這個加裝驗的是整批記錄隨時間的腐化 — 那種不在單一任務內部、而在任務與任務之間長出來的東西. 兩支腳本沿用驗證器的建造約束: Python 3.9+, 純標準庫, 三態 exit code（`0` 乾淨 / `1` 候選, 交給人判 / `2` 無法驗證）, 最後一行都寫明它只驗形式

**什麼時候裝**: 你的專案有「之後的工作會依賴」的 Markdown 記錄 — 決策日誌、收尾報告、帶數字的 spec — 而且不只一個 session 或一個人會讀它們. **什麼時候跳過**: 專案沒有這類記錄（`repo_audit.py` 五項有三項會讀不到東西, `claim_audit.py` 掃的會是沒人當成事實來源的散文）, 或記錄夠短命、沒人會拿著過期的那份行動. 這兩顆 skill 跟整包其他 skill 一樣是 model-invoked: 裝了之後, 任務對上觸發語境（審一份收尾、冷啟動接手專案）agent 自己會伸手拿; 兩支腳本不經 agent、人跑或 CI 跑也完全可用

**跑一次的成本** — 2026-08-08 在本 repo 實測（21 份 Markdown 記錄、幾支腳本; 一個 77 檔 / 1.4 MB 的語料 0.41 秒跑完）: 兩支都在半秒內結束, 成本全在讀輸出 — [`claim_audit.py`](addons/audit/skills/claim-audit/claim_audit.py) 在這裡回了 2 行待判, [`repo_audit.py`](addons/audit/skills/repo-audit/repo_audit.py) 零 finding. 兩個數字都跟記錄裡實際堆了多少無出處或腐化材料成正比, 所以老專案的第一次執行最貴, baseline 就是為那一次而存在的. 有一個數字我們給不出來: `repo_audit.py` 程式碼訊號的誤報率 — 那需要一套已標好正確答案的語料, 我們沒有; 所以每一列訊號都明寫是「該看的地方」不是判決, 報告本身也這麼說

```bash
python addons/audit/skills/claim-audit/claim_audit.py --root .
python addons/audit/skills/repo-audit/repo_audit.py --root . --report artifacts/repo-audit.md
```

[`claim_audit.py`](addons/audit/skills/claim-audit/claim_audit.py) 列出那些「把數字當事實寫下來, 卻沒有任何東西能讓讀者回查」的行 — 沒有路徑、沒有日期、沒有量測動詞, 也沒有標 `[UNVERIFIED]`. 它是 `honest-closeout` 所定義的 `[UNVERIFIED]` 慣例的機械那一半. 每一筆命中都要落成三種編輯之一 — 補出處、標未驗證、撤掉宣稱 — 或寫下判為假陽性的理由. `--baseline` 用內容雜湊記下當前結果, 讓既有專案採用時不必先清完一千行舊債; 反過來, 拿它去清掉沒人看過的命中, 就是把檢查變成綠燈, 那是這支唯一的誤用方式

[`repo_audit.py`](addons/audit/skills/repo-audit/repo_audit.py) 跑五項量測、印一份報告: 超過該類別上限的檔案與相對上次執行的成長; 每一個不再解析得到的 `source:`、`[[WikiLink]]`、`| evidence:` 路徑與相對連結; 同一個病灶累積到門檻的 `correction` 條目; 程式碼裡的債務訊號（吞掉的例外、被關掉的檢查、暫時性標記、要人手動同步的註解、寫死進共用常數的日期）; 以及在期限內沒有任何東西引用過的追蹤文件. 命中以 `file:line` 加「該做哪個編輯」成表, 後面接掃描量體、天生要重跑的常駐項, 以及 — 報告空的時候第一個該讀的 — 這次執行測不到的每一件事, 包含任何讀到空輸入集因而什麼都沒報的檢查

`repo_audit.py` 五項檢查裡有三項 — size、pointers、corrections — 是去解析 `decision-log` 的條目, 所以需要真的有一本日誌可讀; 沒有的時候它會在報告裡逐項點名說自己沒讀到東西, 而不是回一個乾淨結果. signals 與 references 兩項在任何 repo 都能跑. 有用 baseline 就把 `.harness-audit-baseline.json` 進版控: baseline 不進版控等於每個隊友第一次跑都吃到整批舊債, 這檢查一週內就會死. 另外兩個產生檔 `.harness-audit-history.jsonl` 與 `.harness-audit-references.json` 每次執行重寫、不承載任何判斷, 不必進版控

兩支都會讀專案根目錄的 `.harness-audit.json`, 沒有這個檔也能照上面的預設版面直接跑. [本 repo 自己的設定檔](.harness-audit.json)就是一份實例: 它的記錄放在 `.verification-demo/` 而不是 `docs/` 與 `artifacts/`, 所以只改了路徑, 其餘沿用. 門檻值 — 日誌 200 KB 分卷、同一病灶三次更正、180 天沒被引用 — 是為了看得見而挑的整數, 不是對你專案的量測結果; 遇到第一個對你不成立的, 就改掉並記下理由

把 `claim_audit.py` 掛在寫檔動作上是選配的專案接線, 性質與收尾驗證器相同. 在 Claude Code 裡就是 `.claude/settings.json` 的一個 `PostToolUse` hook, 只掃剛被改的那一個檔, 只報基線之後新增的宣稱:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "python addons/audit/skills/claim-audit/claim_audit.py --hook", "timeout": 30 }
        ]
      }
    ]
  }
}
```

hook 模式下這支腳本 fail **open**: 任何內部錯誤都放行該次編輯, 並且把錯誤報出來而不是吞掉. 它是稽核不是門鎖, 而一個看起來在跑、實際什麼都沒做的閘, 比沒有閘更糟. 不接 hook 也完全可用, 人跑或 CI 跑都行

| Skill | 它堵住哪種失敗 |
|---|---|
| [`claim-audit`](addons/audit/skills/claim-audit/SKILL.md) | 憑記憶寫出來的數字 — 每個宣稱都帶著出處、標記, 或一條寫下來的駁回理由 |
| [`repo-audit`](addons/audit/skills/repo-audit/SKILL.md) | 記錄在任務之間腐化 — 斷掉的指標、重複的補丁、沒人引用的文件, 每一筆都附該做的編輯 |

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

## 搭配 Obsidian 更好用 — 推薦但非必要

`decision-log` 與 `handoff` 都是純 Markdown: 每個條目底下一個 YAML 區塊, 條目之間用 `[[path/from/root/file.md#標題]]` 這種 WikiLink 互指, 這裡沒有任何東西需要裝 app 才能讀 — agent 直接讀檔案, 人不裝任何渲染器也照樣冷讀得懂同一份文字, 把同一個資料夾當 Obsidian vault 打開, 多兩件事本來要手動維護: 改檔名時所有指向它的 `[[...]]` 會跟著更新, 反向連結面板能看到哪些條目引用了這一條, 這兩件事都只是讀取這包本來就會寫的檔案, 不改變磁碟上的任何內容 — 也沒有用到任何 Obsidian 專屬語法 (沒有 Dataview 查詢碼, 沒有 Templater 腳本), 不裝 Obsidian 什麼都不會壞

推薦是因為你的團隊可能已經在用, 使用者基數大, 不是因為這裡任何一個 skill 依賴它, 每個 skill 與 `verify_closeout.py` 有沒有 Obsidian 在場行為完全一樣, Obsidian 本身的商業/團隊授權條款是它自己的事, 與這個 repo 的 MIT 授權分開 — 要用在團隊上前先查 [obsidian.md/pricing](https://obsidian.md/pricing) 目前的條款, 不合適的話任何純文字或 Markdown 編輯器都能一樣讀這些檔案

## 整合範本

[`templates/`](templates/) 底下三個檔案把這包接進 PR 實際被審的地方 — 直接複製, 不用重寫:

| 範本 | 複製到 |
|---|---|
| [`PULL_REQUEST_TEMPLATE.md`](templates/PULL_REQUEST_TEMPLATE.md) | `.github/PULL_REQUEST_TEMPLATE.md` — 對照 `honest-closeout` 收尾報告的段落, 同一批驗收與驗證行同時回答 PR 和收尾 |
| [`ISSUE_TEMPLATE_workorder-request.md`](templates/ISSUE_TEMPLATE_workorder-request.md) | `.github/ISSUE_TEMPLATE/workorder-request.md` — 在任何人把任務凍結成 order 之前, 先記下任務的粗略樣子, 附一份對照「什麼時候開完整迴圈」的checklist |
| [`ci-verify-closeout.yml`](templates/ci-verify-closeout.yml) | `.github/workflows/verify-closeout.yml` — 在每個動到 artifacts 資料夾的 PR 上跑 `verify_closeout.py`. 照抄就會先跑這個 repo 自己的 `.verification-demo/`; 要接自己的專案, 改 run step 裡的三個路徑即可 |

CI 範本刻意不讓警示擋下合併 — `verify_closeout.py` 的 exit code 1 是給人看的候選警示, 對應下方「誠實邊界」一節, 不是合併關卡. 範本裡的註解寫了團隊想改成硬性關卡時要刪哪一行

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

## 每顆 skill 一句話

核心（`harness-core`）:

| Skill | 它堵住哪種失敗 |
|---|---|
| [`workorder`](skills/core/workorder/SKILL.md) | 範圍漂移 — 第一個編輯之前先凍結任務與驗收線, 一趟跑到底 |
| [`sensory-gate`](skills/core/sensory-gate/SKILL.md) | 假裝有判斷 — 把只能由人看或聽的東西集中成一個可審的資料夾 |
| [`decision-log`](skills/core/decision-log/SKILL.md) | 決策蒸發 — 一本 append-only 日誌, 冷啟動的 session 先讀它再讀 code |
| [`handoff`](skills/core/handoff/SKILL.md) | 狀態死在換手那一刻 — 換手當下寫一份完整快照 |
| [`honest-closeout`](skills/core/honest-closeout/SKILL.md) | 報告跑得比證據快 — 每個宣稱都連著一條人打得開的路徑 |

加裝（`harness-debug`, 選裝）:

| Skill | 用途 |
|---|---|
| [`staged-diagnosis`](addons/debug/skills/staged-diagnosis/SKILL.md) | 將難解錯誤拆成 reproduce、minimise、hypothesise、instrument、fix、regression-test 六段 |

`DONE` 的獨立功能驗證不等於 hash 或環境 identity. hash 說明檢查的是哪些 bytes, environment 說明在哪裡執行; 它們不證明功能真的正確

## 誠實邊界

這些是 protocols, 不是 enforcement. 它們不會物理阻止任何步驟被略過; 價值在於規則具體且可檢查, 略過時會留下可見缺口. 真正需要物理 enforcement 的 gate, 應由你的專案自行接 hook

## Credits

寫作標準參考 Matt Pocock 的 [`writing-for-agents`](https://github.com/mattpocock/skills): 用正向目標取代禁止語句, 每個意思只有一個權威定義, 每個步驟都有可檢查的完成條件. `staged-diagnosis` 的順序也是同一 repo 的 `/diagnosing-bugs` 泛化; `handoff` 則把同一 repo 的 `handoff` 與 `claude-handoff` 指令泛化成一顆 model-invoked、清單驅動的 skill. All MIT

English: [README.md](README.md)

## 授權

MIT, 詳見 [LICENSE](LICENSE). 可在自己的產品中使用、fork 和 ship
