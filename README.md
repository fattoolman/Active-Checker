# 活躍檢查機器人
用來檢查，每周社群伺服器的成員是否有活躍

並每周產生活躍度報告
___
## 如何使用
1. 先到 DISCORD 開發平台，建立BOT，並取得TOKEN
2. 配置 config.py 檔案 (請參考下方配置說明)
3. 安裝需求 `pip install -r requirements.txt`
4. 執行 main.py
5. 並將機器人新增至伺服器
___
## 指令
### /report
- 產生即時的活躍度報告 
### /time
- 查詢下一次的重設時間 
### /reset
- 重置檢查時間與當前的用戶活躍資料
___
## 事件監聽 
### on_voice_state_update
- 成員進入伺服器，並記錄於資料表中
### on_message
- 成員的文字發言，並記錄於資料表中
### on_member_join
- 新成員的加入，並新增進資料表中
___
## 配置
### config.py
```
TOKEN = 'TO_DISCORD_DEVELOPER_GET'      # DISCORD BOT 的 TOKEN, 需要包在 '' 裡面
GUILD_ID = 0000000000000000000          # 對伺服器右鍵 - 複製 (伺服器ID)
CHANNEL_ID = 0000000000000000000        # 對文字頻道右鍵 - 複製 (頻道ID)
RESET_TIME = 7                          # 重設時間(以天為單位)，預設為 (7) 天
CHECK_RESET_TIME = 1                    # 檢測時間(以分鐘為單位)，預設為 (1) 分鐘
```