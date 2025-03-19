import os
import re
from bs4 import BeautifulSoup
import html


def extract_title_from_html(file_path):
    """Extract the title from an HTML file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        soup = BeautifulSoup(content, "html.parser")
        title_tag = soup.find("title")

        if title_tag and title_tag.string:
            return title_tag.string.strip()

        # If no title tag, try h1
        h1_tag = soup.find("h1")
        if h1_tag and h1_tag.string:
            return h1_tag.string.strip()

        # If no clear title found, use the filename
        filename = os.path.basename(file_path)
        return os.path.splitext(filename)[0]
    except Exception as e:
        print(f"Error extracting title from {file_path}: {e}")
        # Fall back to the filename
        filename = os.path.basename(file_path)
        return os.path.splitext(filename)[0]


def main():
    # Get list of new files from environment variable
    new_files_str = os.environ.get("NEW_FILES", "")
    new_files = new_files_str.strip().split()

    # Get source URL from environment variable
    source_url = os.environ.get("SOURCE_URL", "")

    if not new_files:
        print("No new files to process.")
        return

    print(f"Processing {len(new_files)} new HTML files.")
    if source_url:
        print(f"Using source URL: {source_url}")

    # Path to the index.html file
    index_path = "docs/index.html"

    # Check if index.html exists
    if os.path.exists(index_path):
        # If it exists, update it
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                content = f.read()

            soup = BeautifulSoup(content, "html.parser")

            # Find the list element or create one if it doesn't exist
            list_element = soup.find("ul")
            if not list_element:
                # If no list exists, create one and add it to the body
                list_element = soup.new_tag("ul")
                if soup.body:
                    soup.body.append(list_element)
                else:
                    body = soup.new_tag("body")
                    body.append(list_element)
                    soup.html.append(body)

            # Add entries for each new file
            for file_path in new_files:
                if not os.path.exists(file_path):
                    print(f"Warning: File {file_path} does not exist, skipping.")
                    continue

                # Extract title from HTML file
                title = extract_title_from_html(file_path)

                # Check if the link already exists to avoid duplicates
                relative_path = file_path
                if relative_path.startswith("docs/"):
                    relative_path = relative_path[5:]  # Remove "docs/" prefix

                # Check if link already exists
                existing_link = soup.find("a", href=relative_path)
                if existing_link:
                    print(f"Link to {relative_path} already exists, skipping.")
                    continue

                # Create a new list item with a link to the new file
                li = soup.new_tag("li")
                a = soup.new_tag("a", href=relative_path)
                a.string = title
                li.append(a)

                # Add source link if available
                if source_url:
                    li.append(" [")
                    source_link = soup.new_tag("a", href=source_url)
                    source_link.string = "source"
                    li.append(source_link)
                    li.append("]")

                # Add the new item to the list
                list_element.append(li)

            # Preserve indentation by using the pretty printer with the original indent
            # First, detect the indentation used in the original file
            indent = 4  # Default indentation
            indent_match = re.search(r"^\n*(\s+)<li>", content, re.MULTILINE)
            if indent_match:
                indent_str = indent_match.group(1)
                # Convert tabs to spaces if needed
                indent_str = indent_str.replace("\t", "    ")
                indent = len(indent_str)

            # Format the HTML with the detected indentation
            html_output = soup.prettify(formatter="html", indent_width=indent)

            # Write the updated content back to the file
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html_output)

            print(f"Updated {index_path} with links to new files.")

        except Exception as e:
            print(f"Error updating index.html: {e}")
            raise
    else:
        # If it doesn't exist, create a new index.html file
        try:
            html_content = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Documents Index</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        ul {
            padding-left: 20px;
        }
        li {
            margin: 10px 0;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Documents Index</h1>
    <ul>
"""

            # Add entries for each new file
            for file_path in new_files:
                if not os.path.exists(file_path):
                    print(f"Warning: File {file_path} does not exist, skipping.")
                    continue

                # Extract title from HTML file
                title = extract_title_from_html(file_path)

                # Create a relative path (remove "docs/" prefix)
                relative_path = file_path
                if relative_path.startswith("docs/"):
                    relative_path = relative_path[5:]

                entry = f'        <li><a href="{html.escape(relative_path)}">{html.escape(title)}</a>'

                # Add source link if available
                if source_url:
                    entry += f' [<a href="{html.escape(source_url)}">source</a>]'

                entry += "</li>\n"
                html_content += entry

            # Close the HTML
            html_content += """    </ul>
</body>
</html>
"""

            # Create the directory if it doesn't exist
            os.makedirs(os.path.dirname(index_path), exist_ok=True)

            # Write the content to the file
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"Created new {index_path} with links to new files.")

        except Exception as e:
            print(f"Error creating index.html: {e}")
            raise


if __name__ == "__main__":
    main()
