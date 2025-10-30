import unittest
from inline_markdown import extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks, block_to_block_type, markdown_to_html_node, text_to_children
from textnode import TextNode, TextType, BlockType
from htmlnode import HTMLNode, ParentNode, LeafNode, text_node_to_html_node
import re

def normalize_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()

def test_codeblock(self):
    md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

    node = markdown_to_html_node(md)
    html = node.to_html()
    print(f"Actual HTML: {html!r}")
    expected_html = '<div><pre><code >This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>'
    self.assertEqual(normalize_whitespace(html), normalize_whitespace(expected_html))

class TestInlineDelimiter(unittest.TestCase):
    # Tests for extract_markdown_images
    def test_extract_markdown_images(self):
        text = "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_multiple_images(self):
        text = "This is text with ![image1](url1) and ![image2](url2)."
        matches = extract_markdown_images(text)
        self.assertListEqual([("image1", "url1"), ("image2", "url2")], matches)

    def test_no_images(self):
        text = "This text has no images."
        matches = extract_markdown_images(text)
        self.assertListEqual([], matches)
    
    def test_image_with_link(self):
        text = "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and a link [to boot dev](https://www.boot.dev)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)
    
    def test_image_with_special_chars_in_alt(self):
        text = "![image with space and !](url.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("image with space and !", "url.png")], matches)

    def test_image_with_parenthesis(self):
        text = "![image](url(with)parenthesis.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("image", "url(with)parenthesis.png")], matches)

    def test_image_empty_alt_text(self):
        text = "![](url.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("", "url.png")], matches)

    def test_image_empty_url(self):
        text = "![alt]()"
        matches = extract_markdown_images(text)
        self.assertListEqual([("alt", "")], matches)

    def test_image_empty_url_with_parenthesis(self):
        text = "![a]() and [b](u(x)y)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("a", "")], matches)

    # Tests for extract_markdown_links
    def test_extract_markdown_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)

    def test_multiple_links(self):
        text = "This is text with [link1](url1) and [link2](url2)."
        matches = extract_markdown_links(text)
        self.assertListEqual([("link1", "url1"), ("link2", "url2")], matches)
        
    def test_no_links(self):
        text = "This text has no links."
        matches = extract_markdown_links(text)
        self.assertListEqual([], matches)
        
    def test_link_in_paragraph_with_image(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and an ![image](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("to boot dev", "https://www.boot.dev")], matches)

    def test_link_with_special_chars_in_text(self):
        text = "[link with special !#$](url.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("link with special !#$", "url.com")], matches)

    def test_link_with_parenthesis(self):
        text = "[link](url(with)parenthesis.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("link", "url(with)parenthesis.com")], matches)

    def test_link_empty_text(self):
        text = "[](url.com)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("", "url.com")], matches)

    def test_link_empty_url(self):
        text = "[text]()"
        matches = extract_markdown_links(text)
        self.assertListEqual([("text", "")], matches)

    def test_link_empty_url_with_parenthesis(self):
        text = "![a]() and [b](u(x)y)"
        matches = extract_markdown_links(text)
        self.assertListEqual([("b", "u(x)y")], matches)

    # Combined tests
    def test_mixed_content(self):
        text = "![image](url1) text [link](url2) more text"
        image_matches = extract_markdown_images(text)
        link_matches = extract_markdown_links(text)
        self.assertListEqual([("image", "url1")], image_matches)
        self.assertListEqual([("link", "url2")], link_matches)

    def test_edge_cases(self):
        text = "![[][](]"
        image_matches = extract_markdown_images(text)
        link_matches = extract_markdown_links(text)
        self.assertListEqual([], link_matches)

    # Tests for split_nodes_image
    def test_split_nodes_image_no_images(self):
        nodes = [TextNode("This is text", TextType.TEXT)]
        expected_nodes = [TextNode("This is text", TextType.TEXT)]
        self.assertEqual(split_nodes_image(nodes), expected_nodes)

    def test_split_nodes_image_single_image(self):
        nodes = [TextNode("This is text with ![image](url.png)", TextType.TEXT)]
        expected_nodes = [
            TextNode("This is text with ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "url.png"),
        ]
        self.assertEqual(split_nodes_image(nodes), expected_nodes)

    def test_split_nodes_image_multiple_images(self):
        nodes = [TextNode("![image1](url1.png) text ![image2](url2.png)", TextType.TEXT)]
        expected_nodes = [
            TextNode("image1", TextType.IMAGE, "url1.png"),
            TextNode(" text ", TextType.TEXT),
            TextNode("image2", TextType.IMAGE, "url2.png"),
        ]
        self.assertEqual(split_nodes_image(nodes), expected_nodes)
    
    def test_split_nodes_image_adjacent_images(self):
        nodes = [TextNode("![a](u1)![b](u2)", TextType.TEXT)]
        expected_nodes = [
            TextNode("a", TextType.IMAGE, "u1"),
            TextNode("b", TextType.IMAGE, "u2"),
        ]
        self.assertEqual(split_nodes_image(nodes), expected_nodes)

    def test_split_nodes_image_mixed_content(self):
        nodes = [TextNode("text ![image](url.png) text [link](url2)", TextType.TEXT)]
        expected_nodes = [
            TextNode("text ", TextType.TEXT),
            TextNode("image", TextType.IMAGE, "url.png"),
            TextNode(" text [link](url2)", TextType.TEXT)
        ]
        self.assertEqual(split_nodes_image(nodes), expected_nodes)
    
    def test_split_nodes_image_multiple_nodes(self):
        nodes = [
            TextNode("text ![image1](url1.png)", TextType.TEXT),
            TextNode("![image2](url2.png) more text", TextType.TEXT)
        ]
        expected_nodes = [
            TextNode("text ", TextType.TEXT),
            TextNode("image1", TextType.IMAGE, "url1.png"),
            TextNode("image2", TextType.IMAGE, "url2.png"),
            TextNode(" more text", TextType.TEXT)
        ]
        self.assertEqual(split_nodes_image(nodes), expected_nodes)

    # Tests for split_nodes_link
    def test_split_nodes_link_no_links(self):
        nodes = [TextNode("This is text", TextType.TEXT)]
        expected_nodes = [TextNode("This is text", TextType.TEXT)]
        self.assertEqual(split_nodes_link(nodes), expected_nodes)

    def test_split_nodes_link_single_link(self):
        nodes = [TextNode("This is text with [link](url.com)", TextType.TEXT)]
        expected_nodes = [
            TextNode("This is text with ", TextType.TEXT),
            TextNode("link", TextType.LINK, "url.com"),
        ]
        self.assertEqual(split_nodes_link(nodes), expected_nodes)

    def test_split_nodes_link_multiple_links(self):
        nodes = [TextNode("[link1](url1.com) text [link2](url2.com)", TextType.TEXT)]
        expected_nodes = [
            TextNode("link1", TextType.LINK, "url1.com"),
            TextNode(" text ", TextType.TEXT),
            TextNode("link2", TextType.LINK, "url2.com"),
        ]
        self.assertEqual(split_nodes_link(nodes), expected_nodes)

    def test_split_nodes_link_adjacent_links(self):
        nodes = [TextNode("[x](u1)[y](u2)", TextType.TEXT)]
        expected_nodes = [
            TextNode("x", TextType.LINK, "u1"),
            TextNode("y", TextType.LINK, "u2"),
        ]
        self.assertEqual(split_nodes_link(nodes), expected_nodes)

    def test_split_nodes_link_mixed_content(self):
        nodes = [TextNode("text [link](url.com) text ![image](url2.png)", TextType.TEXT)]
        expected_nodes = [
            TextNode("text ", TextType.TEXT),
            TextNode("link", TextType.LINK, "url.com"),
            TextNode(" text ![image](url2.png)", TextType.TEXT)
        ]
        self.assertEqual(split_nodes_link(nodes), expected_nodes)

    def test_split_nodes_with_existing_non_text_nodes(self):
        nodes = [
            TextNode("bold text", TextType.BOLD),
            TextNode("text [link](url.com) text ![image](url2.png)", TextType.TEXT)
        ]
        expected_nodes = [
            TextNode("bold text", TextType.BOLD),
            TextNode("text ", TextType.TEXT),
            TextNode("link", TextType.LINK, "url.com"),
            TextNode(" text ![image](url2.png)", TextType.TEXT)
        ]
        self.assertEqual(split_nodes_link(nodes), expected_nodes)
    
    def test_split_nodes_link_multiple_nodes(self):
        nodes = [
            TextNode("text [link1](url1.com)", TextType.TEXT),
            TextNode("[link2](url2.com) more text", TextType.TEXT)
        ]
        expected_nodes = [
            TextNode("text ", TextType.TEXT),
            TextNode("link1", TextType.LINK, "url1.com"),
            TextNode("link2", TextType.LINK, "url2.com"),
            TextNode(" more text", TextType.TEXT)
        ]
        self.assertEqual(split_nodes_link(nodes), expected_nodes)

    # Tests for text_to_textnodes
    def test_text_to_textnodes_example(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        expected_nodes = [
            TextNode("This is ", TextType.TEXT, None),
            TextNode("text", TextType.BOLD, None),
            TextNode(" with an ", TextType.TEXT, None),
            TextNode("italic", TextType.ITALIC, None),
            TextNode(" word and a ", TextType.TEXT, None),
            TextNode("code block", TextType.CODE, None),
            TextNode(" and an ", TextType.TEXT, None),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT, None),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        actual_nodes = text_to_textnodes(text)
        self.assertEqual(actual_nodes, expected_nodes)

    def test_text_to_textnodes_no_formatting(self):
        text = "This is plain text"
        expected_nodes = [TextNode("This is plain text", TextType.TEXT, None)]
        actual_nodes = text_to_textnodes(text)
        self.assertEqual(actual_nodes, actual_nodes)

    def test_text_to_textnodes_bold_italic_code(self):
        text = "**bold** _italic_ `code`"
        expected_nodes = [
            TextNode("bold", TextType.BOLD, None),
            TextNode(" ", TextType.TEXT, None),
            TextNode("italic", TextType.ITALIC, None),
            TextNode(" ", TextType.TEXT, None),
            TextNode("code", TextType.CODE, None),
        ]
        actual_nodes = text_to_textnodes(text)
        self.assertEqual(actual_nodes, expected_nodes)

    def test_text_to_textnodes_image_link(self):
        text = "![image](url) [link](url2)"
        expected_nodes = [
            TextNode("image", TextType.IMAGE, "url"),
            TextNode(" ", TextType.TEXT, None),
            TextNode("link", TextType.LINK, "url2"),
        ]
        actual_nodes = text_to_textnodes(text)
        self.assertEqual(actual_nodes, expected_nodes)

    def test_text_to_textnodes_empty(self):
        text = ""
        expected_nodes = [TextNode("", TextType.TEXT, None)]
        actual_nodes = text_to_textnodes(text)
        self.assertEqual(actual_nodes, actual_nodes)

    # Tests for markdown_to_blocks
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_empty(self):
        md = ""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_multiple_newlines(self):
        md = """
This is a paragraph


Another paragraph



Yet another paragraph
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is a paragraph",
                "Another paragraph",
                "Yet another paragraph",
            ],
        )

    def test_markdown_to_blocks_leading_trailing_newlines(self):
        md = """

This is a paragraph

"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["This is a paragraph"])

    def test_markdown_to_blocks_windows_newlines(self):
        md = "Para1\r\n\r\nPara2\r\nLine2"
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            ["Para1", "Para2\r\nLine2"])

    def test_markdown_to_blocks_whitespace_blank_lines(self):
        md = "A\n \n\t\nB"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["A", "B"])

    def test_markdown_to_blocks_only_whitespace(self):
        md = " \n\t\n  "
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, [])

    def test_markdown_to_blocks_trailing_single_newline(self):
        md = "A\n"
        blocks = markdown_to_blocks(md)
        self.assertEqual(blocks, ["A"])

    # Tests for block_to_block_type
    def test_block_to_block_type_heading(self):
        self.assertEqual(block_to_block_type("# This is a heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("## This is a heading"), BlockType.HEADING)
        self.assertEqual(block_to_block_type("###### This is a heading"), BlockType.HEADING)

    def test_block_to_block_type_code(self):
        self.assertEqual(block_to_block_type("```\nThis is code\n```"), BlockType.CODE)
        self.assertEqual(block_to_block_type("``````"), BlockType.CODE)

    def test_block_to_block_type_quote(self):
        self.assertEqual(block_to_block_type("> This is a quote\n> This is another line"), BlockType.QUOTE)

    def test_block_to_block_type_unordered_list(self):
        self.assertEqual(block_to_block_type("- Item 1\n- Item 2"), BlockType.UNORDERED_LIST)

    def test_block_to_block_type_ordered_list(self):
        self.assertEqual(block_to_block_type("1. Item 1\n2. Item 2"), BlockType.ORDERED_LIST)

    def test_block_to_block_type_paragraph(self):
        self.assertEqual(block_to_block_type("This is a paragraph"), BlockType.PARAGRAPH)

    def test_block_to_block_type_mixed(self):
         self.assertEqual(block_to_block_type("1. item 1\n2. item 2\n\nThis is a new para"), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_out_of_order(self):
        self.assertEqual(block_to_block_type("1. item 1\n3. item 2"), BlockType.PARAGRAPH)

    def test_block_to_block_type_ordered_list_not_starting_at_one(self):
        self.assertEqual(block_to_block_type("2. item 1\n3. item 2"), BlockType.PARAGRAPH)

    def test_block_to_block_type_empty(self):
        self.assertEqual(block_to_block_type(""), BlockType.PARAGRAPH)

    def test_block_to_block_type_heading_no_space(self):
        self.assertEqual(block_to_block_type("#Heading"), BlockType.PARAGRAPH)

     # Tests for markdown_to_html_node
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><p>Thisis<b>bolded</b>paragraphtextinaptaghere</p><p>Thisisanotherparagraphwith<i>italic</i>textand<code>code</code>here</p></div>',
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        print(f"Actual HTML: {html!r}")
        expected_html = '<div><pre><code>This is text that _should_ remain the **same** even with inline stuff </code></pre></div>'
        self.assertEqual(normalize_whitespace(html), normalize_whitespace(expected_html))
    
    def test_list(self):
        md = """- Item 1
- Item 2"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            '<div><ul><li>Item 1</li><li>Item 2</li></ul></div>',
        )
    
    def test_heading(self):
        md = """# Title"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(html, "<div><h1>Title</h1></div>")

    def test_text_to_children_bold(self):
        text = "**bolded**"
        html_nodes = text_to_children(text)
        self.assertEqual(len(html_nodes), 1)
        self.assertEqual(html_nodes[0].to_html(), "<b>bolded</b>")

    def test_text_to_children_italic(self):
        text = "_italic_"
        html_nodes = text_to_children(text)
        self.assertEqual(len(html_nodes), 1)
        self.assertEqual(html_nodes[0].to_html(), "<i>italic</i>")

    def test_text_to_children_code(self):
        text = "`code`"
        html_nodes = text_to_children(text)
        self.assertEqual(len(html_nodes), 1)
        self.assertEqual(html_nodes[0].to_html(), "<code>code</code>")

    def test_text_to_children_link(self):
        text = "[link](url)"
        html_nodes = text_to_children(text)
        self.assertEqual(len(html_nodes), 1)
        self.assertEqual(html_nodes[0].to_html(), '<a href="url">link</a>')

    def test_text_to_children_image(self):
        text = "![image](url)"
        html_nodes = text_to_children(text)
        self.assertEqual(len(html_nodes), 1)
        self.assertEqual(html_nodes[0].to_html(), '<img src="url" alt="image" />')

    def test_text_to_children_mixed(self):
        text = "This is **bolded** text with _italic_ and `code` and [link](url) and ![image](url)."
        html_nodes = text_to_children(text)
        self.assertEqual(len(html_nodes), 11)
        self.assertEqual(html_nodes[1].to_html(), "<b>bolded</b>")
        self.assertEqual(html_nodes[5].to_html(), "<code>code</code>")
        self.assertEqual(html_nodes[7].to_html(), '<a href="url">link</a>')
        self.assertEqual(html_nodes[9].to_html(), '<img src="url" alt="image" />')