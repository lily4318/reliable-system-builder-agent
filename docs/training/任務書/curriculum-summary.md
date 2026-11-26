# 教材進度摘要

第二版已於 2026-11-26 完成唯讀交接與驗收。本頁保存本次結果，接下來的工作由[現行訓練主檔](../../AGENT_CAPABILITY_TRAINING.md#目前工作)指派。

## 紙本交付

| 範圍 | 單元總數 | 文字可讀 | 未讀 | 來源受阻 | 逐章實作證據達 L3 以上 |
| --- | ---: | ---: | ---: | ---: | ---: |
| SQL 第三章 | 19 | 13 | 6 | 0 | 0 |

文字可讀表示讀取得到教材內容。達 L3 另需該單元可重現的自行實作與正反測試。這一列使用[驗收時的原表](https://github.com/lily4318/reliable-system-builder-agent/blob/d982f161d9fc8a634981402208a45df4407747af/docs/training/curriculum-coverage.json)，後續須按新版本重算。

## 兩次接手

初談的公開合成需求只有「看教材進度」。第一位無前文的接手者問使用者、目的、期限和能投入的人力，查出舊摘要沿用了先前資料，停在可以界定首版範圍的地方。[第一版任務](https://github.com/lily4318/reliable-system-builder-agent/blob/af3593c1efc0448df2ea09254dbb954acbf2495b/docs/training/任務書/curriculum-summary.md)

演練需求改為當天備課用的紙本，只需 SQL 第三章，一位助教有十分鐘可核對。另一個無前文工作階段只獲得同一個訓練入口，以第二版交付上表，直接停在任務書的驗收點。[第二版任務](https://github.com/lily4318/reliable-system-builder-agent/blob/d982f161d9fc8a634981402208a45df4407747af/docs/training/任務書/curriculum-summary.md)

## 核對結果

依原表識別碼分組，第 3.1、3.2、3.3、3.4 節分別有 2、4、6、7 個單元。接手者核對識別碼完整且不重複，三種來源狀態合計為 19，各單元均登錄為 L0。另用逐列計數和記憶體 SQLite 聚合交叉核對，兩者同為 19／13／6／0／0。原表內容版本為 `bd410900b0d02dd597a31165b346cb834819cb6a`。
