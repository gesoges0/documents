import os
import sys
from bs4 import BeautifulSoup
import re


def main():
    if len(sys.argv) < 2:
        print("Usage: python update_index.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    filename = os.environ.get("OUTPUT_FILENAME")
    title = os.environ.get("OUTPUT_TITLE")

    if not filename or not title:
        print("Error: OUTPUT_FILENAME or OUTPUT_TITLE not set")
        sys.exit(1)

    # Check if index.html exists in the directory
    index_path = os.path.join(directory, "index.html")

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

            # Create a new list item with a link to the new file
            li = soup.new_tag("li")
            a = soup.new_tag("a", href=filename)
            a.string = title
            li.append(a)

            # Add the new item to the list
            list_element.append(li)

            # Write the updated content back to the file
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(str(soup))

            print(f"Updated {index_path} with link to {filename}")

        except Exception as e:
            print(f"Error updating index.html: {e}")
            sys.exit(1)
    else:
        # If it doesn't exist, create a new index.html file
        try:
            html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Summaries</title>
</head>
<body>
    <h1>Document Summaries</h1>
    <ul>
        <li><a href="{filename}">{title}</a></li>
    </ul>
</body>
</html>
"""
            # Create the directory if it doesn't exist
            os.makedirs(directory, exist_ok=True)

            # Write the content to the file
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            print(f"Created new {index_path} with link to {filename}")

        except Exception as e:
            print(f"Error creating index.html: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
