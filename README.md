# Daily ArXiv
Search ArXiv papers by your interested keywords, and send to your mailbox regularly.

## 🔍 About
We search related arxiv papers via [arxiv.py](https://github.com/lukasschwab/arxiv.py) and send corresponding results to your specified mailbox at a daily basis.

Our codes are adapted from [Zetero-arXiv-Daily](https://github.com/TideDra/zotero-arxiv-daily) and can be deployed through Github Action Workflow.

## 🚀 Usage
### :octocat: Github Action Deployment
1. Fork this repo.
2. Set Github Action environment secrets and variables.

|Key|Env Type|Required|Data Type|Description|Example|
|-|-|-|-|-|-|
|ARXIV_KEYWORD|Variable|✅|str|The interested keywords for searching papers|Network Traffic Classification|
|SMTP_SERVER|Variable|✅|str|The SMTP server for sending emails|smtp.feishu.cn|
|SMTP_PORT|Variable|✅|int|The port for SMTP server| 465 |
|SENDER|Variable|✅|str|The email account of the SMTP server for sending emails| xx@example.com |
|SENDER_PASSWORD|Secret|✅|str|Password of the sender account| abcdefgh |
|RECIVER|Variable|✅|str|The email account to received emails containing searched papers| yy@example.com |
|SEND_EMPTY|Variable|❌|bool|Whether to send an email when no results are retrieved | true |
|MAX_RESULTS|Variable|❌|int| The maximum number of papers to send | 10 |
> Above variables can be set via `Settings > Secrets and variables > Actions > Secrets/Variables > New repository secret/variable`.

### 🖥️ Local Running
- Prepaire environments
    ```shell
    pip install -r requirements.txt
    ```
- Run
    ```shell
    python main.py \
        --max_results <max_results> \
        --arxiv_keyword <arxiv_keyword> \
        --smtp_server <smtp_server> \
        --smtp_port <smtp_port> \
        --sender <sender> \
        --sender_password <sender_password> \
        --receiver <receiver>
    ```

## ❤️ Acknowledgement
- [Zetero-arXiv-Daily](https://github.com/TideDra/zotero-arxiv-daily) 
- [arxiv.py](https://github.com/lukasschwab/arxiv.py)
