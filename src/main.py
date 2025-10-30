from textnode import TextNode, TextType
import os
import shutil
def main():
    node = TextNode("This is some anchor text", TextType.LINK, "https://www.boot.dev")

    print(node)

def recursive_copy(source_dir, dest_dir):
    """
    Recursively copies the contents of the source directory to the destination directory.
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

        if os.path.isfile(source_item):
            print(f"Copying file: {source_item} to {dest_item}")
            shutil.copy2(source_item, dest_item)  # copy2 preserves metadata
        elif os.path.isdir(source_item):
            print(f"Copying directory: {source_item} to {dest_item}")
            recursive_copy(source_item, dest_item)

main()