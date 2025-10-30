import os
import shutil
from inline_markdown import markdown_to_html_node, extract_title  # Import from inline_markdown

def recursive_copy(source_dir, dest_dir):
    """
    Recursively copies the contents of the source directory to the destination directory,
    excluding Zone.Identifier files.
    Deletes the destination directory's contents beforehand.
    """
    if os.path.exists(dest_dir):
        print(f"Deleting existing destination directory: {dest_dir}")
        shutil.rmtree(dest_dir)

    print(f"Creating destination directory: {dest_dir}")
    os.makedirs(dest_dir)

    for item in os.listdir(source_dir):
        source_item = os.path.join(source_dir, item)
        dest_item = os.path.join(dest_dir, item)

        if item.endswith(":Zone.Identifier"):
            print(f"Skipping file: {source_item}")
            continue

        if os.path.isfile(source_item):
            print(f"Copying file: {source_item} to {dest_item}")
            shutil.copy2(source_item, dest_item)  # copy2 preserves metadata
        elif os.path.isdir(source_item):
            print(f"Copying directory: {source_item} to {dest_item}")
            recursive_copy(source_item, dest_item)


def generate_page(from_path, template_path, dest_path):
    """
    Generates an HTML page from a markdown file, a template, and a destination path.

    Args:
        from_path: Path to the markdown file.
        template_path: Path to the HTML template file.
        dest_path: Path to write the generated HTML file.
    """
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    # Read the markdown file
    try:
        with open(from_path, "r") as f:
            markdown_content = f.read()
    except FileNotFoundError:
        print(f"Error: Markdown file not found at {from_path}")
        return
    except Exception as e:
        print(f"Error reading markdown file: {e}")
        return

    # Read the template file
    try:
        with open(template_path, "r") as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"Error: Template file not found at {template_path}")
        return
    except Exception as e:
        print(f"Error reading template file: {e}")
        return

    # Convert markdown to HTML
    try:
        html_content = markdown_to_html_node(markdown_content).to_html()
    except Exception as e:
        print(f"Error converting markdown to HTML: {e}")
        return

    # Extract the title
    try:
        title = extract_title(markdown_content)
    except ValueError:
        title = "Default Title" #provide a default title to prevent the program from crashing

    # Replace placeholders in the template
    try:
        output_content = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    except Exception as e:
        print(f"Error replacing placeholders in template: {e}")
        return

    # Write the output to the destination file
    try:
        # Create any necessary directories
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        with open(dest_path, "w") as f:
            f.write(output_content)
    except Exception as e:
        print(f"Error writing to destination file: {e}")
        return

    print(f"Successfully generated page at {dest_path}")

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    """
    Crawls the content directory and generates a new .html file for each markdown file,
    using the specified template. The generated pages are written to the public directory
    in the same directory structure.

    Args:
        dir_path_content: Path to the content directory containing markdown files.
        template_path: Path to the HTML template file.
        dest_dir_path: Path to the destination directory (e.g., "public").
    """

    for root, _, files in os.walk(dir_path_content):
        for file in files:
            if file.endswith(".md"):
                # Construct the full paths
                md_file_path = os.path.join(root, file)

                # Calculate the relative path from the content directory
                relative_path = os.path.relpath(md_file_path, dir_path_content)

                # Construct the destination path in the public directory
                html_file_name = os.path.splitext(relative_path)[0] + ".html"
                html_dest_path = os.path.join(dest_dir_path, html_file_name)

                # Generate the page
                generate_page(md_file_path, template_path, html_dest_path)


def main():
    # Delete anything in the public directory
    if os.path.exists("public"):
        print("Deleting existing public directory")
        shutil.rmtree("public")

    # Copy all the static files from static to public
    recursive_copy("static", "public")

    # Generate pages recursively
    generate_pages_recursive("content", "template.html", "public")


if __name__ == "__main__":
    main()