from arxiv import Result
from tqdm import tqdm
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib
import datetime
from loguru import logger
from typing import Dict


framework = """
<!DOCTYPE HTML>
<html>
<body>

<div>
    __CONTENT__
</div>

<br><br>
<div>
To unsubscribe, remove your email in your Github Action setting.
</div>

</body>
</html>
"""


def get_empty_html():
  block_template = """
  <table border="0" cellpadding="0" cellspacing="0" width="100%" style="font-family: Arial, sans-serif; border: 1px solid #ddd; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">
  <tr>
    <td style="font-size: 20px; font-weight: bold; color: #333;">
        No Papers Today. Take a Rest!
    </td>
  </tr>
  </table>
  """
  return block_template


def get_block_html(idx: int, title: str, authors: str, keyword: str, updated: str, arxiv_id: str, abstract: str, pdf_url: str):
    block_template = """
    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="font-family: Arial, sans-serif; border: 1px solid #ddd; border-radius: 8px; padding: 16px; background-color: #f9f9f9;">
    <tr>
        <td style="font-size: 20px; font-weight: bold; color: #333;">
            ({idx}) {title}
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #666; padding: 8px 0;">
            {authors}
            <br>
            <span><strong>Keyword: </strong><i>{keyword}</i> &nbsp;|&nbsp; <strong>Updated time: </strong><i>{updated}</i></span>
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #333; padding: 8px 0;">
            <strong>arXiv ID:</strong> {arxiv_id}
        </td>
    </tr>
    <tr>
        <td style="font-size: 14px; color: #333; padding: 8px 0;">
            <strong>abstract:</strong> {abstract}
        </td>
    </tr>

    <tr>
        <td style="padding: 8px 0;">
            <a href="{pdf_url}" style="display: inline-block; text-decoration: none; font-size: 14px; font-weight: bold; color: #fff; background-color: #d9534f; padding: 8px 16px; border-radius: 4px;">PDF</a>
        </td>
    </tr>
</table>
"""
    return block_template.format(idx=idx, title=title, authors=authors, 
                                 keyword=keyword, updated=updated,
                                 arxiv_id=arxiv_id, abstract=abstract, pdf_url=pdf_url)


def render_email(papers: Dict[str, list[Result]]):
    parts = []
    if len(papers) == 0 :
        return framework.replace('__CONTENT__', get_empty_html())
    total_papers = sum(len(p) for p in papers.values())
    pbar = tqdm(total=total_papers, desc='Rendering Email')
    idx = 0
    for keyword, paper_list in papers.items():
        for p in paper_list:
            authors = [a.name for a in p.authors[:5]]
            authors = ', '.join(authors)
            if len(p.authors) > 5:
                authors += ', ...'
            idx += 1
            parts.append(get_block_html(idx, p.title, authors, keyword,
                                        p.updated.strftime('%Y-%m-%d %H:%M:%S'),
                                        p.entry_id.split('/')[-1], p.summary, p.pdf_url))
            pbar.update(1)
    pbar.close()

    content = '<br>' + '</br><br>'.join(parts) + '</br>'
    return framework.replace('__CONTENT__', content)


def send_email(sender:str, receiver:str, password:str, 
               smtp_server:str, smtp_port:int, html:str,):
    def _format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    msg = MIMEText(html, 'html', 'utf-8')
    msg['From'] = _format_addr('Github Action <%s>' % sender)
    msg['To'] = _format_addr('You <%s>' % receiver)
    today = datetime.datetime.now().strftime('%Y/%m/%d')
    msg['Subject'] = Header(f'Daily arXiv {today}', 'utf-8').encode()

    logger.info(f"Connecting to SMTP server {smtp_server}:{smtp_port}...")
    try:
        server = smtplib.SMTP(smtp_server, smtp_port, timeout=5)
        server.starttls()
    except Exception as e:
        logger.warning(f"Failed to use TLS. {e}")
        logger.warning(f"Try to use SSL.")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    
    logger.info("Connected to SMTP server.")
    resp = server.login(sender, password)
    logger.info(f"Login resp: {resp}.")
    resp = server.sendmail(sender, [receiver], msg.as_string())
    logger.info(f"Sending resp: {resp}.")
    server.quit()
