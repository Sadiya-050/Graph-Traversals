from flask import Flask, request, render_template
import graphviz

app = Flask(__name__)

class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/selection', methods=["POST"])
def selection():
    traversals = request.form.getlist("traversal")
    traversals = [t.capitalize() for t in traversals]
    if len(traversals) != 2:
        return render_template("invalid.html", message="Select Exactly 2 Traversal Options")
    elif "Inorder" not in traversals:
        return render_template("invalid.html", message="Select Inorder as one of the Traversals")
    return render_template("traversals.html", traversals=traversals)

def getPreOrder(postorder, inorder):
    if not postorder or not inorder:
        return None, []
    root_value = postorder[-1]
    root = TreeNode(root_value)
    root_index = inorder.index(root_value)
    
    left_inorder = inorder[:root_index]
    right_inorder = inorder[root_index + 1:]
    left_postorder = postorder[:len(left_inorder)]
    right_postorder = postorder[len(left_inorder):-1]
    
    left_root, left_preorder = getPreOrder(left_postorder, left_inorder)
    right_root, right_preorder = getPreOrder(right_postorder, right_inorder)
    
    root.left = left_root
    root.right = right_root
    
    return root, [root.value] + left_preorder + right_preorder

def getPostOrder(preorder, inorder):
    if not preorder or not inorder:
        return None, []
    root_value = preorder[0]
    root = TreeNode(root_value)
    root_index = inorder.index(root_value)
    
    left_inorder = inorder[:root_index]
    right_inorder = inorder[root_index + 1:]
    left_preorder = preorder[1:len(left_inorder) + 1]
    right_preorder = preorder[len(left_inorder) + 1:]
    
    left_root, left_postorder = getPostOrder(left_preorder, left_inorder)
    right_root, right_postorder = getPostOrder(right_preorder, right_inorder)
    
    root.left = left_root
    root.right = right_root
    
    return root, left_postorder + right_postorder + [root.value]

def generate_tree_image(root, filename="static/tree"):
    dot = graphviz.Digraph()
    
    def add_nodes_edges(node):
        if not node:
            return
        dot.node(str(node.value))
        if node.left:
            dot.edge(str(node.value), str(node.left.value))
            add_nodes_edges(node.left)
        if node.right:
            dot.edge(str(node.value), str(node.right.value))
            add_nodes_edges(node.right)
    
    add_nodes_edges(root)
    dot.render(filename, format='png', cleanup=False)

@app.route('/traversals', methods=["POST"])
def traversals():
    traversals = request.form.to_dict()
    keys = list(traversals.keys())

    if "Inorder" in keys and "Postorder" in keys:
        inorder = traversals["Inorder"].split()
        postorder = traversals["Postorder"].split()
        if len(inorder) != len(postorder):
            return render_template("invalid.html", message="The length of the Inorder and Postorder traversals is different")
        resultName = "Preorder"
        try:
            root, result = getPreOrder(postorder, inorder)
        except:
            return render_template("invalid.html", message="The Inorder and Postorder traversals are Invalid")
        
    elif "Inorder" in keys and "Preorder" in keys:
        inorder = traversals["Inorder"].split()
        preorder = traversals["Preorder"].split()
        if len(inorder) != len(preorder):
            return render_template("invalid.html", message="The length of the Inorder and Preorder traversals is different")
        resultName = "Postorder"
        try:
            root, result = getPostOrder(preorder, inorder)
        except:
            return render_template("invalid.html", message="The Inorder and Preorder traversals are Invalid")
            
    generate_tree_image(root)
    return render_template("result.html", resultName=resultName, traversal=" ".join(result), image_path="static/tree.png")

if __name__ == "__main__":
    app.run(debug=True)