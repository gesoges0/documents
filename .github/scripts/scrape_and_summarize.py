import os
import sys
import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
import html_sanitizer
import time
from datetime import datetime
import re


def sanitize_filename(filename):
    """Convert URL to a safe filename"""
    return re.sub(r"[^\w\-]", "_", filename)


def main():
    if len(sys.argv) < 3:
        print("Usage: python scrape_and_summarize.py <url> <directory>")
        sys.exit(1)

    url = sys.argv[1]
    directory = sys.argv[2]

    # Create directory if it doesn't exist
    os.makedirs(directory, exist_ok=True)

    # Scrape the URL
    print(f"Scraping URL: {url}")
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Error scraping URL: {e}")
        sys.exit(1)

    # Parse the content
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract title
    title = soup.title.string if soup.title else "No Title"

    # Remove script and style tags to clean up content
    for script in soup(["script", "style", "header", "footer", "nav"]):
        script.extract()

    # Get the text content
    content = soup.get_text(separator="\n", strip=True)

    # Truncate if needed (Claude has token limits)
    if len(content) > 50000:
        content = content[:50000] + "...[content truncated]"

    # Create the prompt
    prompt = """
# グラフィックレコーディング風インフォグラフィック変換プロンプト
## 目的
  以下の内容を、超一流デザイナーが作成したような、日本語で完璧なグラフィックレコーディング風のHTMLインフォグラフィックに変換してください。情報設計とビジュアルデザインの両面で最高水準を目指します
  手書き風の図形やアイコンを活用して内容を視覚的に表現します。
## デザイン仕様
### 1. カラースキーム
```
  <palette>
  <color name='ファッション-1' rgb='593C47' r='89' g='59' b='70' />
  <color name='ファッション-2' rgb='F2E63D' r='242' g='230' b='60' />
  <color name='ファッション-3' rgb='F2C53D' r='242' g='196' b='60' />
  <color name='ファッション-4' rgb='F25C05' r='242' g='91' b='4' />
  <color name='ファッション-5' rgb='F24405' r='242' g='68' b='4' />
  </palette>
```
### 2. グラフィックレコーディング要素
- 左上から右へ、上から下へと情報を順次配置
- 日本語の手書き風フォントの使用（Yomogi, Zen Kurenaido, Kaisei Decol）
- 手描き風の囲み線、矢印、バナー、吹き出し
- テキストと視覚要素（アイコン、シンプルな図形）の組み合わせ
- キーワードの強調（色付き下線、マーカー効果）
- 関連する概念を線や矢印で接続
- 絵文字やアイコンを効果的に配置（✏️📌📝🔍📊など）
### 3. タイポグラフィ
  - タイトル：32px、グラデーション効果、太字
  - サブタイトル：16px、#475569
  - セクション見出し：18px、#1e40af、アイコン付き
  - 本文：14px、#334155、行間1.4
  - フォント指定：
    ```html
    <style>
    
@import
 url('https://fonts.googleapis.com/css2?family=Kaisei+Decol&family=Yomogi&family=Zen+Kurenaido&display=swap');
    </style>
    ```
### 4. レイアウト
  - ヘッダー：左揃えタイトル＋右揃え日付/出典
  - 3カラム構成：左側33%、中央33%、右側33%
  - カード型コンポーネント：白背景、角丸12px、微細シャドウ
  - セクション間の適切な余白と階層構造
  - 適切にグラスモーフィズムを活用
  - 横幅は100%にして
## グラフィックレコーディング表現技法
- テキストと視覚要素のバランスを重視
- キーワードを囲み線や色で強調
- 簡易的なアイコンや図形で概念を視覚化
- 数値データは簡潔なグラフや図表で表現
- 接続線や矢印で情報間の関係性を明示
- 余白を効果的に活用して視認性を確保
## 全体的な指針
- 読み手が自然に視線を移動できる配置
- 情報の階層と関連性を視覚的に明確化
- 手書き風の要素で親しみやすさを演出
- 視覚的な記憶に残るデザイン
- フッターに出典情報を明記
## 変換する文章/記事

タイトル: {title}
URL: {url}

ーーー

{content}
    """

    # Format the prompt
    formatted_prompt = prompt.format(title=title, url=url, content=content)

    # Use Claude API to generate the summary
    print("Generating summary with Claude 3.7 Sonnet...")
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    try:
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4096,
            temperature=0.3,
            system="You are a skilled graphic recorder who creates beautiful HTML infographics.",
            messages=[{"role": "user", "content": formatted_prompt}],
        )

        # Extract the HTML content from the response
        html_content = message.content[0].text

        # Try to extract just the HTML part if Claude wrapped it in markdown code blocks
        if "```html" in html_content:
            html_content = html_content.split("```html")[1].split("```")[0].strip()
        elif "```" in html_content:
            html_content = html_content.split("```")[1].split("```")[0].strip()

        # Create a filename based on the current time and sanitized URL
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{sanitize_filename(url)[:50]}.html"
        filepath = os.path.join(directory, filename)

        # Write the HTML content to a file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"Summary written to {filepath}")

        # Output the filename for use in the next step
        print(f"OUTPUT_FILENAME={filename}")
        with open(os.environ.get("GITHUB_ENV", "/tmp/github_env"), "a") as env_file:
            env_file.write(f"OUTPUT_FILENAME={filename}\n")
            env_file.write(f"OUTPUT_TITLE={title}\n")

    except Exception as e:
        print(f"Error generating summary: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
