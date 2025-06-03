from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Tree # Correct: Tree from textual.widgets
from textual.widgets.tree import TreeNode # Correct: TreeNode from textual.widgets.tree
from textual.binding import Binding # Correct: Binding from textual.binding (Forcing update)

from model_utils import ModuleNode
# from rules import Rule

class LMSteerApp(App):
    """A Textual app to steer language models."""

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
    ]

    CSS_PATH = "tui.css"

    def __init__(self, model_root: ModuleNode, model_name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_root = model_root
        self.model_name = model_name
        self.defined_rules = []
        self.title = f"LMSteer - {self.model_name}"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        
        with Horizontal(id="main_content_area"):
            tree_root_label = f"{self.model_root.name} ({self.model_root.module_type})"
            yield Tree(tree_root_label, data=self.model_root, id="module_tree")
            
            with Vertical(id="context_pane"):
                yield Static("Context / Rule Definition", classes="pane_title", id="context_pane_title") 
                yield Static("Select a module in the tree to see details or define rules.", id="module_info_static")
        
        yield Footer()

    def _add_nodes_to_tree(self, textual_tree_node: TreeNode, model_node: ModuleNode) -> None:
        textual_tree_node.expand() 
        for child_model_node in model_node.children:
            label = f"{child_model_node.name}  [dim]({child_model_node.module_type})[/dim]"
            new_textual_node = textual_tree_node.add(
                label,
                data=child_model_node,
                allow_expand=not child_model_node.is_leaf
            )
            if not child_model_node.is_leaf:
                self._add_nodes_to_tree(new_textual_node, child_model_node)

    def on_mount(self) -> None:
        module_tree_widget = self.query_one("#module_tree", Tree)
        self._add_nodes_to_tree(module_tree_widget.root, self.model_root)
        module_tree_widget.focus()

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Called when a node in the Tree is selected."""
        selected_node_data = event.node.data
        context_title_widget = self.query_one("#context_pane_title", Static)
        module_info_widget = self.query_one("#module_info_static", Static)

        if selected_node_data and isinstance(selected_node_data, ModuleNode):
            module_node: ModuleNode = selected_node_data
            context_title_widget.update(f"Details for: [bold]{module_node.name}[/bold] ([italic]{module_node.module_type}[/italic])")
            
            details = (
                f"[bold]Full Path:[/bold] {module_node.get_full_path() or '(root)'}\n"
                f"[bold]Module Type:[/bold] {module_node.module_type}\n"
                f"[bold]Is Leaf:[/bold] {module_node.is_leaf}\n"
                f"[bold]Children Count:[/bold] {len(module_node.children)}\n"
            )
            module_info_widget.update(details)
        else:
            context_title_widget.update("Context / Rule Definition")
            module_info_widget.update("Select a module to see details.")

    def action_quit(self) -> None:
        self.exit()

if __name__ == '__main__':
    class DummyModuleNode(ModuleNode):
        def __init__(self, name, module_type, children=None, module=None, is_leaf=False, full_path=""):
            super().__init__(name, module_type, children if children is not None else [], module, is_leaf, full_path)

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
