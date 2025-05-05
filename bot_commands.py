import logging
import asyncio
from config import openai_client, SYSTEM_PROMPTS
from arxiv_client import fetch_arxiv_papers, filter_papers

# 論文要約関数
async def summarize_paper(paper: dict) -> str:
    try:
        system_prompt = (
            "あなたは論文の要約をする教育者です。"
            "論文の内容を分かりやすく説明してください。"
        )

        prompt = f"""以下の論文について、概要・手法・結果を簡潔に要約してください。
        タイトル: {paper['title']}
        要約: {paper['summary']}
        """

        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Error summarizing paper: {e}")
        return "要約中にエラーが発生しました。"

# GPTコマンド処理関数
async def handle_gpt_command(message, content):
    try:
        parts = content.split(maxsplit=1)
        if len(parts) > 1 and parts[0].startswith("--"):
            prompt_type = parts[0][2:]
            user_content = parts[1]
            system_prompt = SYSTEM_PROMPTS.get(prompt_type, SYSTEM_PROMPTS["default"])
        else:
            user_content = content
            system_prompt = SYSTEM_PROMPTS["default"]

        response = openai_client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
        )
        return await message.channel.send(response.choices[0].message.content)
    except Exception as e:
        logging.error(f"Error in GPT response: {e}")
        return await message.channel.send("エラーが発生しました...")

# 論文コマンド処理関数
async def handle_papers_command(message, paper_manager):
    await message.channel.send("新着論文を確認中なのです...✨")
    try:
        papers = await fetch_arxiv_papers()
        if not papers:
            return await message.channel.send("論文の取得に失敗しました...")

        filtered_papers = await filter_papers(papers)
        new_papers = [p for p in filtered_papers if p["url"] not in paper_manager.posted_papers]

        if not new_papers:
            return await message.channel.send("条件に合う新しい論文が見つかりませんでした...")

        for paper in new_papers[:3]:
            summary = await summarize_paper(paper)
            paper_number = paper_manager.save_paper(paper["url"])
            paper_message = (
                f"📚 **新着論文 No.{paper_number} のお知らせなのです！**\n\n"
                f"{summary}\n\n"
                f"🔗 論文リンク: {paper['url']}"
            )
            await message.channel.send(paper_message)
            await asyncio.sleep(1)

    except Exception as e:
        logging.error(f"Error in papers command: {e}")
        await message.channel.send("処理中にエラーが発生しました...")