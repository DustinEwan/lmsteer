from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical # Will use these more later
from textual.widgets import Header, Footer, Static, Tree
from textual.widgets.tree import TreeNode
from textual.binding import Binding

from model_utils import ModuleNode # We'll need this to type hint
# from rules import Rule # Will need this when we handle rules

class LMSteerApp(App):
    """A Textual app to steer language models."""

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        # Add more bindings here as we develop (e.g., for defining rules)
    ]

    CSS_PATH = "tui.css" # We can add a CSS file later for styling

    def __init__(self, model_root: ModuleNode, model_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_root = model_root
        self.model_name = model_name
        self.defined_rules = [] # Initialize list to store Rule objects
        self.title = f"LMSteer - {self.model_name}" # Set dynamic window title

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=False) # Clock not essential, keep it clean
        
        with Horizontal(id="main_content_area"):
            # Module Tree Pane
            tree_root_label = f"{self.model_root.name} ({self.model_root.module_type})"
            yield Tree(tree_root_label, data=self.model_root, id="module_tree")
            
            # Context Pane (placeholder for now)
            with Vertical(id="context_pane"):
                yield Static("Context / Rule Definition", classes="pane_title", id="context_pane_title") 
                yield Static("Select a module in the tree to see details or define rules.", id="module_info_static")
        
        yield Footer()

    def _add_nodes_to_tree(self, textual_tree_node: TreeNode, model_node: ModuleNode) -> None:
        """Recursively adds nodes from our ModuleNode structure to the Textual Tree.

        Args:
            textual_tree_node: The parent TreeNode in the Textual Tree widget.
            model_node: The corresponding ModuleNode from our model structure whose children are to be added.
        """
        textual_tree_node.expand() # Expand parent by default
        for child_model_node in model_node.children:
            label = f"{child_model_node.name}  [dim]({child_model_node.module_type})[/dim]"
            # Store the actual ModuleNode object in the data attribute of the tree node
            # Mark as not expandable if it's a leaf in our model structure
            new_textual_node = textual_tree_node.add(
                label,
                data=child_model_node,
                allow_expand=not child_model_node.is_leaf
            )
            if not child_model_node.is_leaf:
                self._add_nodes_to_tree(new_textual_node, child_model_node)

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        module_tree_widget = self.query_one(Tree)
        # The root of the Textual tree already represents self.model_root (set in compose)
        # So we populate its children.
        self._add_nodes_to_tree(module_tree_widget.root, self.model_root)
        module_tree_widget.focus()

    def action_quit(self) -> None:
        """An action to quit the application."""
        self.exit()

if __name__ == '__main__':
    # This is for testing the TUI directly if needed
    class DummyModuleNode(ModuleNode):
        def __init__(self, name, module_type, children=None, module=None, is_leaf=False, full_path=""):
            super().__init__(name, module_type, children if children is not None else [], module, is_leaf, full_path)

    # Create a simple dummy tree for testing
    dummy_transformer = DummyModuleNode(name="transformer", module_type="Block", full_path="transformer", children=[
        DummyModuleNode(name="h", module_type="ModuleList", full_path="transformer.h", children=[
            DummyModuleNode(name="0", module_type="Layer", full_path="transformer.h.0", children=[
                DummyModuleNode(name="attn", module_type="Attention", full_path="transformer.h.0.attn", is_leaf=True),
                DummyModuleNode(name="mlp", module_type="MLP", full_path="transformer.h.0.mlp", is_leaf=True)
            ]),
            DummyModuleNode(name="1", module_type="Layer", full_path="transformer.h.1", is_leaf=True)
        ]),
        DummyModuleNode(name="ln_f", module_type="LayerNorm", full_path="transformer.ln_f", is_leaf=True)
    ])
    dummy_root = DummyModuleNode(name="GPT2Model", module_type="Model", full_path="", children=[
        DummyModuleNode(name="wte", module_type="Embedding", full_path="wte", is_leaf=True),
        dummy_transformer,
        DummyModuleNode(name="wpe", module_type="Embedding", full_path="wpe", is_leaf=True)
    ])
    
    app = LMSteerApp(model_root=dummy_root, model_name="dummy_gpt2")
    app.run()
