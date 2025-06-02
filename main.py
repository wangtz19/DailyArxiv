import arxiv
import argparse
import os
import sys
from dotenv import load_dotenv
load_dotenv(override=True)
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from construct_email import render_email, send_email
from loguru import logger


def get_arxiv_paper(keyword: str, max_results: int=10, ):
    client = arxiv.Client(num_retries=10, delay_seconds=10)
    query = f'(ti:"{keyword}" OR abs:"{keyword}") AND (cat:cs.AI OR cat:cs.LG OR cat:cs.DC OR cat:cs.NI OR cat:cs.PF)'
    logger.info(f"Searching query: {query}")
    logger.info(f"Max results: {max_results}")
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.LastUpdatedDate
    )
    papers = []
    for result in client.results(search):
        papers.append(result)
    return papers


parser = argparse.ArgumentParser(description="Daily Arxiv Paper for Networking")

def add_argument(*args, **kwargs):
    def get_env(key: str, default=None):
        # handle environment variables generated at Workflow runtime
        # Unset environment variables are passed as '', we should treat them as None
        v = os.environ.get(key)
        if v == '' or v is None:
            return default
        return v
    parser.add_argument(*args, **kwargs)
    arg_full_name = kwargs.get('dest',args[-1][2:])
    env_name = arg_full_name.upper()
    env_value = get_env(env_name)
    if env_value is not None:
        #convert env_value to the specified type
        if kwargs.get('type') == bool:
            env_value = env_value.lower() in ['true','1']
        else:
            env_value = kwargs.get('type')(env_value)
        parser.set_defaults(**{arg_full_name:env_value})


if __name__ == '__main__':
    add_argument('--send_empty', type=bool, help='If get no arxiv paper, send empty email', default=False)
    add_argument('--max_results', type=int, help='Maximum number of papers to recommend', default=10)
    add_argument('--arxiv_keyword', type=str, help='Arxiv search query')
    add_argument('--smtp_server', type=str, help='SMTP server')
    add_argument('--smtp_port', type=int, help='SMTP port')
    add_argument('--sender', type=str, help='Sender email address')
    add_argument('--receiver', type=str, help='Receiver email address')
    add_argument('--sender_password', type=str, help='Sender email password')
    args = parser.parse_args()
    
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    logger.info("Retrieving Arxiv papers...")
    papers = get_arxiv_paper(args.arxiv_keyword, args.max_results)
    if len(papers) == 0:
        logger.info("No new papers found. Yesterday maybe a holiday and no one submit their work :). If this is not the case, please check the ARXIV_QUERY.")
        if not args.send_empty:
          exit(0)
    html = render_email(papers)
    logger.info("Sending email...")
    send_email(args.sender, args.receiver, args.sender_password, args.smtp_server, args.smtp_port, html)
    logger.success("Email sent successfully! If you don't receive the email, please check the configuration and the junk box.")
