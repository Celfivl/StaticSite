import unittest
from htmlnode import LeafNode, ParentNode

class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )
    
    def test_to_html_multiple_children(self):
        child1 = LeafNode("p", "First paragraph.")
        child2 = LeafNode("p", "Second paragraph.")
        parent_node = ParentNode("div", [child1, child2])
        self.assertEqual(parent_node.to_html(), "<div><p>First paragraph.</p><p>Second paragraph.</p></div>")

    def test_to_html_nested_parent_nodes(self):
        inner_child = LeafNode("i", "italic text")
        inner_parent = ParentNode("p", [inner_child])
        outer_parent = ParentNode("div", [inner_parent])
        self.assertEqual(outer_parent.to_html(), "<div><p><i>italic text</i></p></div>")

    def test_to_html_no_tag_on_construction(self):
        with self.assertRaises(ValueError):
            ParentNode(None, [LeafNode("p", "text")])

    def test_to_html_no_children_on_construction(self):
        with self.assertRaises(ValueError):
            ParentNode("div", [])

    def test_to_html_with_props(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node], {"class": "container"})
        self.assertEqual(parent_node.to_html(), '<div class="container"><span>child</span></div>')

if __name__ == "__main__":
    unittest.main()