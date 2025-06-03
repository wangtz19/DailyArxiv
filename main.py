import arxiv
import argparse
import os
import sys
from dotenv import load_dotenv
load_dotenv(override=True)
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from construct_email import render_email, send_email
from loguru import logger
from tqdm import tqdm


def get_arxiv_paper(keywords: str, categories: str, max_results: int=10, ):
    client = arxiv.Client(num_retries=10, delay_seconds=10)
    keywords = [x.strip() for x in keywords.split(',')]
    print(f"Got {len(keywords)} keywords: {keywords}")
    categories = [x.strip() for x in categories.split(',')]
    cat_query = " OR ".join(["cat:" + cat for cat in categories])
    paper_dict = {}
    for keyword in tqdm(keywords, desc="Searching arxiv papers"):
        query = f'(ti:"{keyword}" OR abs:"{keyword}") AND ({cat_query})'
        logger.info(f"Searching query: {query}")
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.LastUpdatedDate
        )
        papers = []
        for result in client.results(search):
            papers.append(result)
        logger.info(f"Found {len(papers)} papers for keyword '{keyword}' from {len(categories)} categories: {categories}.")
        paper_dict[keyword] = papers
    return paper_dict


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
    add_argument('--max_results', type=int, help='Maximum number of papers to recommend for each keyword', default=10)
    add_argument('--arxiv_keywords', type=str,
                 help='Keywords to search for in the arxiv papers, separated by commas. ')
    add_argument('--arxiv_categories', type=str, default='cs.AI,cs.LG,cs.DC,cs.NI,cs.PF',
                 help='Categories to search for in the arxiv papers, separated by commas. Default is cs.AI,cs.LG,cs.DC,cs.NI,cs.PF.')
    add_argument('--smtp_server', type=str, help='SMTP server')
    add_argument('--smtp_port', type=int, help='SMTP port')
    add_argument('--sender', type=str, help='Sender email address')
    add_argument('--receiver', type=str, help='Receiver email address')
    add_argument('--sender_password', type=str, help='Sender email password')
    args = parser.parse_args()
    
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    logger.info("Retrieving Arxiv papers...")
    paper_dict = get_arxiv_paper(args.arxiv_keywords, args.arxiv_categories, args.max_results)
    
    html = render_email(paper_dict)
    logger.info("Sending email...")
    send_email(args.sender, args.receiver, args.sender_password, args.smtp_server, args.smtp_port, html)
    logger.success("Email sent successfully! If you don't receive the email, please check the configuration and the junk box.")
