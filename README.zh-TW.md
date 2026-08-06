# 3xa-harness

給長期跑真實工作的 AI 代理用的紀律 skill——專治那些「慢慢壞掉」的環節

四顆 skill 圍成一個迴圈：**凍結**任務是什麼、**卡閘**只有人能判的東西、**當下記錄**每個決策、**用證據結案**
另有一顆選配加裝
MIT 授權、零依賴、一分鐘內裝好

## 這是用來解決什麼的

短任務怎麼做都不太會出事
跑上好幾週的工作會壞在 prompt 技巧碰不到的地方

- **範圍在施工中自己長大**
  交出來的東西已經不是當初講定的那個，而且沒人指得出是哪一刻變的

- **感官判斷被代理自己模擬掉**
  代理看一眼算圖結果，判定沒問題，接著在上面疊三步
  「語言模型看起來沒問題」跟「要扛這支片上架的人看起來沒問題」是兩件事

- **決策說過就蒸發**
  一次駁回、一次糾正只在對話裡講過一次，下一次 context 重置就沒了
  於是同一個錯誤、或同一場爭論，再來一遍

- **回報跑在證據前面**
  長 session 末尾憑記憶寫的摘要會失真，而失真的方向總是往「事情做得很順」那一版偏

每顆 skill 都是一個具體、可核對的機制：一份凍結的文件、一個把不要的檔案拖進去的資料夾、一行 grep 得到的索引行、一份結案訊息直接複製出來的報告
代理做得到，人也能從同一份磁碟現況核對它有沒有真的做到

## 安裝

一個 marketplace、兩顆 plugin——先裝核心，其他按需要加

```bash
claude plugin marketplace add https://github.com/3xachris/3xa-harness
claude plugin install harness-core@3xa-harness
```

Codex 使用者可把同一組四顆核心 skill 複製到使用者 skill 目錄

```powershell
$dest = Join-Path $HOME '.agents\skills'
New-Item -ItemType Directory -Force $dest | Out-Null
Copy-Item skills\core\workorder,skills\core\sensory-gate,skills\core\decision-log,skills\core\honest-closeout -Destination $dest -Recurse -Force
Get-ChildItem $dest\workorder,$dest\sensory-gate,$dest\decision-log,$dest\honest-closeout -Filter SKILL.md
```

最後一行應列出四個 `SKILL.md`；開一個新的 Codex session，描述一個符合情境的任務，確認 skill 已被發現並觸發

| plugin | 裝了會多什麼 |
|---|---|
| `harness-core` | 四顆一組的紀律迴圈：`workorder`、`sensory-gate`、`decision-log`、`honest-closeout` |
| `harness-debug` | `staged-diagnosis`——核心診斷迴圈的完整加強版，給那種看一眼看不出來的錯 |

```bash
claude plugin install harness-debug@3xa-harness
```

裝好之後正常描述任務就好——「開工前先把這件事凍下來」「幫我審這批算圖」「記一下我們為什麼放棄這個做法」——對得上的 skill 會自己觸發
每顆都是 model-invoked

**其他代理工具**：[skills.sh](https://skills.sh) 讀同一份 repo——核心四顆放在 `skills/core/<名稱>/SKILL.md`，全部 skill 也都宣告在 `.claude-plugin/` 裡，兩種格式它都懂

```bash
npx skills@latest add 3xachris/3xa-harness
```

**三條路擇一：Claude plugin、Codex 使用者 skill，或 skills.sh**；每條路徑都會安裝同一組 skill，選超過一條會讓每顆 skill 出現兩次

## 包裡有什麼

| skill | 一句話用法 |
|---|---|
| [`workorder`](skills/core/workorder/SKILL.md) | 先把任務凍結——一句話、已知事實、素材與其授權、釘死的參數、預算熔斷、驗收條件、非目標——然後一口氣跑到 `DONE`、`CLOSED-FAILED` 或 `STOPPED`；遇到難查的失敗就用核心診斷迴圈，選配的 `staged-diagnosis` 是它的加強版 |
| [`sensory-gate`](skills/core/sensory-gate/SKILL.md) | 圖／音／影整批丟進一個 gate 資料夾（內含 `rejects/` 子夾），代理停在那裡等你；你不滿意哪個，拖進 `rejects/` 就是表態，一個字都不用打 |
| [`decision-log`](skills/core/decision-log/SKILL.md) | 一份條目 append-only、頂端摘要可維護的日誌，每條開頭一行固定格式索引行，內容只指路不複製；另在專案「每次都會載入的那份檔案」裝一行指標 |
| [`honest-closeout`](skills/core/honest-closeout/SKILL.md) | 每條驗收都用證據回答、人給的診斷歸給人、背景任務關掉要有憑據、聊天訊息從報告裡原文複製出來 |
| [`staged-diagnosis`](addons/debug/skills/staged-diagnosis/SKILL.md) | 重現 → 最小化 → 假設 → 打點 → 修復 → 回歸，每一階段產出的東西就是下一階段要用的材料 |

每顆 skill 都帶著自己的規則、步驟、一條可核對的完成判準
核心四顆另附一份 `CASES.md`——記錄「哪一次翻車換來這條規則」，已通用化

## 有在運作的話，你會看到

不用打開任何 `SKILL.md`，在自己的工作裡就能核對的訊號

- 代理把問題**一次問在開頭**，而不是每二十分鐘停下來問一個本來就該先問的決定
- 要你審的東西是**一個資料夾＋一句白話問題**，回答只要拖檔案，不用打一段字
- 新開的 session **先開決策日誌再開程式碼**，不再把你上週定案的事重吵一遍
- 結案報告會告訴你每個宣稱的證據在哪；失敗就直說失敗，而不是磨得漂漂亮亮把失敗磨掉
- 你想去磁碟上查核某個宣稱時，磁碟跟它講的一樣

## 誠實邊界

這裡給的是紀律、不是強制力
沒有任何東西擋著代理跳過某一步——這些協議之所以有效，是因為寫得夠具體、跟得動，而且跳過了看得出來
真的要在物理上卡死一道閘，那是你自己專案裡的 hook 該做的事，而且值得寫

## 出處

書寫標準採用 Matt Pocock 的 [`writing-for-agents`](https://github.com/mattpocock/skills)：正向目標優先於禁令、一個意思只在一處定義、完成判準要可檢查且窮盡
`staged-diagnosis` 的階段順序是同一份 repo 裡 `/diagnosing-bugs` 的通用化版本
兩者皆 MIT

English: [README.md](README.md)

## 授權

MIT——見 [LICENSE](LICENSE)
拿去用、拿去改、包進你自己的產品都可以
