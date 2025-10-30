import re
from textnode import TextNode, TextType, BlockType
from htmlnode import HTMLNode, ParentNode, LeafNode, text_node_to_html_node

IMAGE_PATTERN = r"!\[([^\[\]]*)\]\(((?:[^()]|\([^\)]*\))*)\)"
LINK_PATTERN  = r"(?<!!)\[([^\[\]]*)\]\(((?:[^()]|\([^\)]*\))*)\)"
BOLD_PATTERN = r"\*\*([^*]+)\*\*"
ITALIC_PATTERN = r"_([^_]+)_"
CODE_PATTERN = r"`([^`]+)`"

def extract_markdown_images(text):
    return re.findall(IMAGE_PATTERN, text)

def extract_markdown_links(text):
    return re.findall(LINK_PATTERN, text)

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        text_to_split = old_node.text
        while True:
            image_match = re.search(IMAGE_PATTERN, text_to_split)
            if not image_match:
                break

            alt_text, url = image_match.groups()
            start, end = image_match.span()

            if start > 0:
                new_nodes.append(TextNode(text_to_split[:start], TextType.TEXT))

            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            text_to_split = text_to_split[end:]

        if text_to_split:
            new_nodes.append(TextNode(text_to_split, TextType.TEXT))

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        text_to_split = old_node.text
        while True:
            link_match = re.search(LINK_PATTERN, text_to_split)
            if not link_match:
                break

            link_text, url = link_match.groups()
            start, end = link_match.span()

            if start > 0:
                new_nodes.append(TextNode(text_to_split[:start], TextType.TEXT))

            new_nodes.append(TextNode(link_text, TextType.LINK, url))
            text_to_split = text_to_split[end:]

        if text_to_split:
            new_nodes.append(TextNode(text_to_split, TextType.TEXT))

    return new_nodes

def split_nodes_bold(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
        
        text_to_split = old_node.text
        while True:
            bold_match = re.search(BOLD_PATTERN, text_to_split)
            if not bold_match:
                break
            
            bold_text = bold_match.group(1)
            start, end = bold_match.span()
            
            if start > 0:
                new_nodes.append(TextNode(text_to_split[:start], TextType.TEXT))
                
            new_nodes.append(TextNode(bold_text, TextType.BOLD))
            text_to_split = text_to_split[end:]
            
        if text_to_split:
            new_nodes.append(TextNode(text_to_split, TextType.TEXT))
    return new_nodes

def split_nodes_italic(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
            
        text_to_split = old_node.text
        while True:
            italic_match = re.search(ITALIC_PATTERN, text_to_split)
            if not italic_match:
                break
            
            italic_text = italic_match.group(1)
            start, end = italic_match.span()
            
            if start > 0:
                new_nodes.append(TextNode(text_to_split[:start], TextType.TEXT))
                
            new_nodes.append(TextNode(italic_text, TextType.ITALIC))
            text_to_split = text_to_split[end:]
            
        if text_to_split:
            new_nodes.append(TextNode(text_to_split, TextType.TEXT))
    return new_nodes

def split_nodes_code(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue
            
        text_to_split = old_node.text
        while True:
            code_match = re.search(CODE_PATTERN, text_to_split)
            if not code_match:
                break
            
            code_text = code_match.group(1)
            start, end = code_match.span()
            
            if start > 0:
                new_nodes.append(TextNode(text_to_split[:start], TextType.TEXT))
            
            new_nodes.append(TextNode(code_text, TextType.CODE))
            text_to_split = text_to_split[end:]
            
        if text_to_split:
            new_nodes.append(TextNode(text_to_split, TextType.TEXT))
    return new_nodes

def text_to_textnodes(text):
    if not text:
        return [TextNode("", TextType.TEXT)]
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_code(nodes)
    nodes = split_nodes_bold(nodes)
    nodes = split_nodes_italic(nodes)
    return nodes

def markdown_to_blocks(markdown):
    # Split on a newline, then any number of whitespace-only lines, then a newline
    blocks = re.split(r"(?:\r?\n[ \t]*){2,}", markdown)
    # Strip each block to remove leading/trailing whitespace
    blocks = [block.strip() for block in blocks]
    # Filter out empty blocks
    blocks = [block for block in blocks if block]
    return blocks

def block_to_block_type(block):
    lines = block.splitlines()

    # Empty block should be a paragraph
    if not block:
        return BlockType.PARAGRAPH

    # Code block
    if block.strip() == "``````":
        return BlockType.CODE
    if len(lines) >= 2 and lines[0].strip() == "```" and lines[-1].strip() == "```":
        return BlockType.CODE

    # Heading
    if re.match(r"^#{1,6} .+", block):
        return BlockType.HEADING

    # Quote block
    if len(lines) > 0 and all(re.match(r"^> .+", line) for line in lines):
        return BlockType.QUOTE

    # Unordered list
    if len(lines) > 0 and all(re.match(r"^- .+", line) for line in lines):
        return BlockType.UNORDERED_LIST

    # Ordered list
    if len(lines) > 0:
        numbers = []
        valid_ordered_list = True
        for line in lines:
            match = re.match(r"^(\d+)\. .+", line)
            if match:
                numbers.append(int(match.group(1)))
            else:
                valid_ordered_list = False
                break

        if valid_ordered_list:
            if numbers[0] != 1:
                return BlockType.PARAGRAPH
            for i in range(len(numbers) - 1):
                if numbers[i+1] != numbers[i] + 1:
                    return BlockType.PARAGRAPH
            return BlockType.ORDERED_LIST

    # Paragraph
    return BlockType.PARAGRAPH

def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    html_nodes = []
    for text_node in text_nodes:
        html_nodes.append(text_node_to_html_node(text_node))
    return html_nodes

def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        if block_type == BlockType.HEADING:
            level = block.split(" ")[0].count("#")
            text = block[level + 1:].strip()
            children.append(ParentNode(f"h{level}", text_to_children(text)))
        elif block_type == BlockType.CODE:
            lines = block.splitlines()
            code_text = "\n".join(lines[1:-1]) + "\n"
            children.append(ParentNode("pre", [LeafNode("code", code_text)]))
        elif block_type == BlockType.QUOTE:
            lines = block.splitlines()
            text = " ".join([line[2:] for line in lines])
            children.append(ParentNode("blockquote", text_to_children(text)))
        elif block_type == BlockType.UNORDERED_LIST:
            list_items = []
            for line in block.splitlines():
                text = line[2:]
                list_items.append(ParentNode("li", text_to_children(text)))
            children.append(ParentNode("ul", list_items))
        elif block_type == BlockType.ORDERED_LIST:
            list_items = []
            for i, line in enumerate(block.splitlines(), 1):
                text = line[len(str(i)) + 2:]
                list_items.append(ParentNode("li", text_to_children(text)))
            children.append(ParentNode("ol", list_items))
        else:  # Paragraph
            text = block.replace('\n', ' ')
            text = "".join(text.split())
            children.append(ParentNode("p", text_to_children(text)))

    return ParentNode("div", children)