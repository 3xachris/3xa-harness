# 3xa-harness

給長時間實作工作的代理使用的紀律 skills

四顆核心 skill 組成一個迴圈：先凍結工單、把只能由人判斷的內容送過 gate、留下決策日誌、最後用證據收尾。另有一顆選配的診斷 skill。MIT 授權，零安裝依賴

## 安裝

```bash
claude plugin marketplace add https://github.com/3xachris/3xa-harness
claude plugin install harness-core@3xa-harness
```

也可把 `skills/core/` 下的四顆 skill 複製到 Codex 使用者 skill 目錄。除核心外，`harness-debug` 提供 `staged-diagnosis`

## 可執行的收尾驗證

專案內的 [`verify_closeout.py`](verify_closeout.py) 是獨立的 Python 3 腳本。選 Python 是因為開發機與 CI 最常已有 Python，且標準庫即可維持零依賴。用一份凍結工單、一份收尾報告與一份決策日誌執行：

```bash
python verify_closeout.py artifacts/order.md artifacts/closeout.md docs/decisions.md --root .
```

它會檢查五件事：驗收 ID 是否逐條回答、報告宣稱的證據路徑是否存在、`DONE` 是否有獨立功能驗證、每個已開 gate 是否有具名處置與必要的封存路徑、決策日誌是否有指向本報告的 `closeout` 條目

命中只會列為候選警示，交由人判斷，不會自動判定內容失敗。沒有結構化欄位的舊報告會印出「無法驗證，跳過」並使用不同於完成檢查的退出碼。最後一行固定說明：這支只驗形式，內容對不對是人的事

Claude Code hook 綁定只是專案可自行加上的選配，腳本本身可由人或 CI 直接執行

## 四顆核心 skill

| Skill | 用途 |
|---|---|
| [`workorder`](skills/core/workorder/SKILL.md) | 凍結範圍、材料、參數、預算、逐條驗收與非目標 |
| [`sensory-gate`](skills/core/sensory-gate/SKILL.md) | 讓人審查圖、音、影，保存批次雜湊、核可者與拒絕封存 |
| [`decision-log`](skills/core/decision-log/SKILL.md) | 讓決策、拒絕、修正與收尾條目在 context reset 後仍可追溯 |
| [`honest-closeout`](skills/core/honest-closeout/SKILL.md) | 用每條驗收的證據、獨立功能驗證與 gate register 完成收尾 |

## 邊界

這些是可遵循、可稽核的協議。驗證器只驗機械形式，不判斷根因、證據內容或人類判斷是否正確

English: [README.md](README.md)

## 授權

MIT，詳見 [LICENSE](LICENSE)
