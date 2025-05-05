import discord
import logging
import asyncio
from config import DISCORD_TOKEN, discord_intents, PAPER_CHANNEL_ID
from paper_manager import PaperManager
from bot_commands import handle_gpt_command, handle_papers_command, summarize_paper
from arxiv_client import fetch_arxiv_papers, filter_papers

# Discord クライアントの設定
discord_client = discord.Client(intents=discord_intents)
paper_manager = PaperManager()

# 自動投稿関数
async def auto_post_papers():
    await discord_client.wait_until_ready()
    channel = discord_client.get_channel(PAPER_CHANNEL_ID)

    while not discord_client.is_closed():
        try:
            papers = await fetch_arxiv_papers()
            logging.info(f"取得した論文数: {len(papers)}")
            if not papers:
                logging.info("論文の取得に失敗しました")
                await asyncio.sleep(3600)
                continue

            filtered_papers = await filter_papers(papers)
            logging.info(f"フィルタ後の論文数: {len(filtered_papers)}")
            new_papers = [p for p in filtered_papers if p["url"] not in paper_manager.posted_papers]
            logging.info(f"新規論文数: {len(new_papers)}")

            if new_papers:
                for paper in new_papers[:1]:
                    try:
                        summary = await summarize_paper(paper)
                        paper_number = paper_manager.save_paper(paper["url"])
                        paper_message = (
                            f"📚 **新着論文 No.{paper_number} のお知らせなのです！**\n\n"
                            f"{summary}\n\n"
                            f"🔗 論文リンク: {paper['url']}"
                        )
                        await channel.send(paper_message)
                        await asyncio.sleep(1)
                    except Exception as e:
                        logging.error(f"個別の論文処理でエラー: {e}")
            else:
                logging.info("新規の論文は見つかりませんでした")

        except Exception as e:
            logging.error(f"自動投稿タスクでエラー: {e}")

        await asyncio.sleep(7200)

@discord_client.event
async def on_ready():
    print(f'Logged in as {discord_client.user}')
    logging.info(f'Bot started successfully as {discord_client.user}')
    discord_client.loop.create_task(auto_post_papers())

@discord_client.event
async def on_message(message):
    if message.author.bot:
        return

    try:
        if message.content.startswith('!gpt '):
            await handle_gpt_command(message, message.content[len('!gpt '):])
        elif message.content == '!papers':
            await handle_papers_command(message, paper_manager)
    except Exception as e:
        logging.error(f"Error in message handling: {e}")

if __name__ == "__main__":
    try:
        print("Bot starting...")
        discord_client.run(DISCORD_TOKEN)
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        print(f"エラーが発生しました: {e}")
        input("Enterキーを押して終了")