import os

def generate_index_page(directory='.'):
    # Create the header of the HTML page
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Most useful ETF historical returns https://peter6888.github.io/stock/</title>
    <script>
        function addFavorite() {
            var url = window.location.href;
            var title = document.title;

            if (window.sidebar && window.sidebar.addPanel) { // Firefox < 23
                window.sidebar.addPanel(title, url, "");
            } else if (window.external && ('AddFavorite' in window.external)) { // IE Favorites
                window.external.AddFavorite(url, title);
            } else if (window.opera && window.print) { // Opera
                this.title = title;
                return true;
            } else { // For other browsers (e.g., Chrome, Firefox > 23)
                alert('Press ' + (navigator.userAgent.toLowerCase().indexOf('mac') !== -1 ? 'Cmd' : 'Ctrl') + ' + D to bookmark this page.');
            }
        }
    </script>
</head>
<body>
    <h1>ETF(s)</h1>
    https://peter6888.github.io/stock/ <br> <br>
    <button onclick="addFavorite()">Add to Favorites</button>
    <ul>
    """

    # Iterate over all files in the given directory
    for file_name in os.listdir(directory):
        if file_name.endswith('.html') and file_name != 'index.html':  # Only list HTML files and exclude the index itself
            html_content += f'<li><a href="{file_name}">{file_name}</a></li>\n'

    # Close the HTML tags
    html_content += """
    </ul>
</body>
</html>
"""

    # Write the generated content to index.html
    with open(os.path.join(directory, 'index.html'), 'w', encoding='utf-8') as index_file:
        index_file.write(html_content)

    print(f"Index page generated successfully at {os.path.join(directory, 'index.html')}")

# Run the function to generate the index page in the current directory
generate_index_page()
