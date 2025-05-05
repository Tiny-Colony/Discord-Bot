import os

class PaperManager:
    def __init__(self, file_path="posted_papers.txt"):
        self.file_path = file_path
        self.posted_papers = set()
        self.counter = 0
        self.load_papers()

    def load_papers(self):
        if not os.path.exists(self.file_path):
            return
        with open(self.file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if line.strip():
                    parts = line.strip().split(",")
                    if len(parts) >= 2:
                        self.posted_papers.add(parts[0])
                        self.counter = max(self.counter, int(parts[1]))

    def save_paper(self, paper_url):
        self.counter += 1
        with open(self.file_path, "a", encoding="utf-8") as f:
            f.write(f"{paper_url},{self.counter}\n")
        self.posted_papers.add(paper_url)
        return self.counter