import arxiv
import asyncio
import logging
from typing import List, Dict

# 非同期論文取得関数
async def fetch_arxiv_papers(query="cat:cs.CL", max_results=50) -> List[Dict]:
    try:
        client = arxiv.Client()
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate
        )
        papers = []

        def get_papers():
            for result in client.results(search):
                papers.append({
                    "title": result.title,
                    "summary": result.summary,
                    "url": result.entry_id,
                    "published": result.published
                })

        await asyncio.get_event_loop().run_in_executor(None, get_papers)
        return papers
    except Exception as e:
        logging.error(f"Error fetching papers: {e}")
        return []

# 論文フィルタリング関数
async def filter_papers(papers: List[Dict]) -> List[Dict]:
    try:
        keywords = ["LLM", "RAG", "large language model", "retrieval-augmented generation",
                   "language model", "prompt", "instruction tuning"]
        filtered = []
        for paper in papers:
            text = (paper["title"] + paper["summary"]).lower()
            if any(kw.lower() in text for kw in keywords):
                filtered.append(paper)
        return filtered
    except Exception as e:
        logging.error(f"Error filtering papers: {e}")
        return []