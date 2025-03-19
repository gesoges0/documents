import yaml
from pathlib import Path

def generate_html(data):
    html_content = '''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>index</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        .tree {
            margin: 0;
            padding: 0;
        }
        .tree ul {
            margin-left: 20px;
            padding-left: 0;
        }
        .tree li {
            list-style-type: none;
            margin: 10px 0;
            position: relative;
        }
        .tree li::before {
            content: "├── ";
            font-family: monospace;
        }
        .tree li:last-child::before {
            content: "└── ";
            font-family: monospace;
        }
        .folder {
            font-weight: bold;
            cursor: pointer;
            color: #0066cc;
        }
        .file {
            color: #333;
        }
        .folder::before {
            content: "📁 ";
        }
        .file::before {
            content: "📄 ";
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
    </style>
</head>
<body>
    <h1>index</h1>
    <div class="tree">
'''

    # Get the index array from the data
    index = data.get('index', [])
    
    for directory in index:
        html_content += f'<ul><li><span class="folder">{directory["dir"]}</span><ul>'
        for item in directory["items"]:
            html_content += f'<li><span class="file"><a href="https://gesoges0.github.io/documents/{directory["dir"]}/{item["name"]}.html">{item["name"]}</a> (<a href="{item["source"]}">source</a>)</span></li>'
        html_content += '</ul></li></ul>'

    html_content += '''
    </div>
    <script>
        document.querySelectorAll('.folder').forEach(folder => {
            folder.addEventListener('click', () => {
                const sublist = folder.nextElementSibling;
                if (sublist) {
                    sublist.style.display = sublist.style.display === 'none' ? 'block' : 'none';
                }
            });
        });
    </script>
</body>
</html>
'''
    return html_content

def main():
    yaml_path = Path('docs/index.yaml')
    html_path = Path('docs/index.html')

    with open(yaml_path, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)

    html_content = generate_html(data)

    with open(html_path, 'w') as html_file:
        html_file.write(html_content)

if __name__ == "__main__":
    main()
