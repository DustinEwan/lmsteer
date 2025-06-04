from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Header,
    Footer,
    Static,
    Tree,
    RadioSet,
    RadioButton,
    Button,
)  # Correct: Tree from textual.widgets
from textual.widgets.tree import TreeNode  # Correct: TreeNode from textual.widgets.tree
from textual.binding import (
    Binding,
)  # Correct: Binding from textual.binding (Forcing update)
from textual.events import Key, Focus

from lmsteer.app.model_utils import ModuleNode
# from rules import Rule


class CustomTree(Tree):
    def on_key(self, event: Key) -> None:
        prevent_default = False
        if event.key == "k":
            self.action_cursor_up()
            prevent_default = True
        elif event.key == "j":
            self.action_cursor_down()
            prevent_default = True
        elif event.key == "h":
            if self.cursor_node and self.cursor_node.is_expanded:
                self.action_toggle_node()
            prevent_default = True
        elif event.key == "l":
            if (
                self.cursor_node
                and not self.cursor_node.is_expanded
                and self.cursor_node.allow_expand
            ):
                self.action_toggle_node()
            prevent_default = True
        elif event.key == "enter":
            if self.cursor_node is not None:
                self.post_message(NodeExplicitlySelected(self.cursor_node))
            prevent_default = True

        if prevent_default:
            event.stop()

    def action_select_cursor(self) -> None:
        """Called when the cursor is selected (e.g. by pressing Enter).
        We override this to prevent toggling the node, but still allow
        the selection event to propagate for updating details.
        """
        if self.cursor_node is not None:
            self.post_message(NodeExplicitlySelected(self.cursor_node))


class NodeExplicitlySelected(Tree.NodeSelected):
    """Posted when a node is explicitly selected (e.g., by Enter key)."""

    pass

class NavigableRadioSet(RadioSet):
    def on_key(self, event: Key) -> None:
        buttons = list(self.query(RadioButton))  # Get RadioButton children
        if not buttons:  # No buttons to navigate
            return

        current_index = -1
        for i, button in enumerate(buttons):
            if button.value:  # RadioButton.value is True if it's selected
                current_index = i
                break

        if event.key == "k":  # Up
            event.stop()
            if current_index == -1 or current_index == 0:
                buttons[-1].value = True  # Select last
            else:
                buttons[current_index - 1].value = True  # Select previous
        elif event.key == "j":  # Down
            event.stop()
            if current_index == -1 or current_index == len(buttons) - 1:
                buttons[0].value = True  # Select first
            else:
                buttons[current_index + 1].value = True  # Select next
        else:
            super().on_key(event)

class LMSteerApp(App):
    """A Textual app to steer language models."""

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", show=True),
        Binding("k,up", "cursor_up", "Cursor Up", show=False),
        Binding("j,down", "cursor_down", "Cursor Down", show=False),
        Binding("h,left", "collapse_node", "Collapse Node", show=False),
        Binding("l,right", "expand_node", "Expand Node", show=False),
        Binding("escape", "focus_tree", "Focus Tree", show=False, priority=True),
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
            yield CustomTree(tree_root_label, data=self.model_root, id="module_tree")

            with Vertical(id="context_pane"):
                yield Static(
                    "Context / Rule Definition",
                    classes="pane_title",
                    id="context_pane_title",
                )
                yield Static(
                    "Select a module in the tree to see details or define rules.",
                    id="module_info_static",
                )
                yield NavigableRadioSet(
                    RadioButton(
                        "Capture Activations for this module", id="radio_capture_module"
                    ),
                    RadioButton(
                        "Skip Activations for this module", id="radio_skip_module"
                    ),
                    RadioButton(
                        "Default / Inherit", id="radio_default_module", value=True
                    ),  # Default selection
                    id="module_action_radioset",
                )
                yield Static(
                    "Effective Status: (details pending)", id="effective_status_static"
                )
                yield Button(
                    "Define Steering Rule...",
                    variant="primary",
                    id="define_rule_button",
                )

        yield Footer()

    def _add_nodes_to_tree(
        self, textual_tree_node: TreeNode, model_node: ModuleNode
    ) -> None:
        textual_tree_node.expand()
        for child_model_node in model_node.children:
            label = (
                f"{child_model_node.name}  [dim]({child_model_node.module_type})[/dim]"
            )
            new_textual_node = textual_tree_node.add(
                label, data=child_model_node, allow_expand=not child_model_node.is_leaf
            )
            if not child_model_node.is_leaf:
                self._add_nodes_to_tree(new_textual_node, child_model_node)

    def on_mount(self) -> None:
        # Store references to the widgets
        self.module_tree_widget = self.query_one("#module_tree", CustomTree)
        self.context_pane_widget = self.query_one("#context_pane", Vertical)

        # Populate the tree
        self._add_nodes_to_tree(self.module_tree_widget.root, self.model_root)

        # Set initial focus to the tree
        self.module_tree_widget.focus()

        # Set initial focus highlighting
        self.module_tree_widget.add_class("pane-focused")
        self.context_pane_widget.remove_class("pane-focused")

    def on_focus(self, event: Focus) -> None:
        """Handle focus events to highlight the active pane."""
        # Check if the focused widget is the tree itself or a descendant
        if event.widget == self.module_tree_widget or self.module_tree_widget.is_ancestor_of(event.widget):
            if not self.module_tree_widget.has_class("pane-focused"):
                self.module_tree_widget.add_class("pane-focused")
            if self.context_pane_widget.has_class("pane-focused"):
                self.context_pane_widget.remove_class("pane-focused")
        # Check if the focused widget is the context pane or a descendant
        elif event.widget == self.context_pane_widget or self.context_pane_widget.is_ancestor_of(event.widget):
            if not self.context_pane_widget.has_class("pane-focused"):
                self.context_pane_widget.add_class("pane-focused")
            if self.module_tree_widget.has_class("pane-focused"):
                self.module_tree_widget.remove_class("pane-focused")
    def _update_module_details(self, module_node: ModuleNode | None) -> None:
        """Updates the context pane with details of the given module_node."""
        context_title_widget = self.query_one("#context_pane_title", Static)
        module_info_widget = self.query_one("#module_info_static", Static)

        # Get references to new UI elements
        radio_set = self.query_one("#module_action_radioset", RadioSet)
        radio_capture = self.query_one("#radio_capture_module", RadioButton)
        radio_skip = self.query_one("#radio_skip_module", RadioButton)
        radio_default = self.query_one("#radio_default_module", RadioButton)
        effective_status_widget = self.query_one("#effective_status_static", Static)
        define_rule_button = self.query_one(
            "#define_rule_button", Button
        )  # Though its state isn't changed here

        if module_node and isinstance(module_node, ModuleNode):
            context_title_widget.update(
                f"Details for: [bold]{module_node.name}[/bold] ([italic]{module_node.module_type}[/italic])"
            )

            details = (
                f"[bold]Full Path:[/bold] {module_node.get_full_path() or '(root)'}\n"
                f"[bold]Module Type:[/bold] {module_node.module_type}\n"
                f"[bold]Is Leaf:[/bold] {module_node.is_leaf}\n"
                f"[bold]Children Count:[/bold] {len(module_node.children)}\n"
            )
            module_info_widget.update(details)

            # Update and enable UI elements for module-specific actions
            radio_capture.label = (
                f"Capture Activations for this module ({module_node.name})"
            )
            radio_skip.label = f"Skip Activations for this module ({module_node.name})"

            radio_set.disabled = False

            # TODO: Set radio_set.pressed_button based on actual module config.
            # For now, if a module is selected, we might want to ensure "Default/Inherit" is
            # initially selected until we load its specific state.
            # Or, we let it retain the last state. For now, let's explicitly set to default.
            # This will be replaced by loading actual config.
            radio_default.value = True

            effective_status_widget.update(
                f"Effective Status: (Config for {module_node.name} pending)"
            )

        else:  # No module selected
            context_title_widget.update("Context / Rule Definition")
            module_info_widget.update(
                "Highlight a module in the tree to see details and set its capture status. "
                "Use 'Define Steering Rule...' to create or manage broader rules."
            )

            # Reset radio button labels to generic, disable RadioSet for module-specific actions
            radio_capture.label = "Capture Activations for this module"
            radio_skip.label = "Skip Activations for this module"

            radio_default.value = True
            radio_set.disabled = True

            # define_rule_button remains enabled.
            define_rule_button.disabled = False

            effective_status_widget.update(
                "Effective Status: No module selected. Select a module or define a global rule."
            )

    def on_tree_node_highlighted(self, event: Tree.NodeHighlighted) -> None:
        """Called when a node in the Tree is highlighted."""
        # event.node can be None if the tree is empty or loses focus
        highlighted_node_data = event.node.data if event.node else None
        self._update_module_details(highlighted_node_data)

    def on_node_explicitly_selected(self, event: NodeExplicitlySelected) -> None:
        """Called when a node in the Tree is explicitly selected (e.g., by Enter)."""
        # _update_module_details is typically called by on_tree_node_highlighted.
        # NodeSelected (and thus NodeExplicitlySelected) usually follows a highlight.


        radio_set = self.query_one("#module_action_radioset", RadioSet)
        # Only focus if a module is actually selected (event.node.data exists)
        # and the radio_set is enabled (which _update_module_details should have set).
        if event.node and event.node.data and not radio_set.disabled:

            self.set_focus(radio_set)
        event.stop()  # Prevent any default Tree.NodeSelected behavior if not desired

    def action_collapse_node(self) -> None:
        """Collapses the current tree node if it is expanded."""
        tree = self.query_one(Tree)
        if tree.cursor_node and tree.cursor_node.is_expanded:
            tree.action_toggle_node()

    def action_expand_node(self) -> None:
        """Expands the current tree node if it is collapsed and has children."""
        tree = self.query_one(Tree)
        if (
            tree.cursor_node
            and not tree.cursor_node.is_expanded
            and tree.cursor_node.allow_expand
        ):
            tree.action_toggle_node()

    def action_focus_tree(self) -> None:
        """Shifts focus to the module tree."""
        tree = self.query_one("#module_tree", CustomTree)
        tree.focus()

    def action_quit(self) -> None:
        self.exit()


if __name__ == "__main__":

    class DummyModuleNode(ModuleNode):
        def __init__(
            self,
            name,
            module_type,
            children=None,
            module=None,
            is_leaf=False,
            full_path="",
        ):
            super().__init__(
                name,
                module_type,
                children if children is not None else [],
                module,
                is_leaf,
                full_path,
            )

    dummy_transformer = DummyModuleNode(
        name="transformer",
        module_type="Block",
        full_path="transformer",
        children=[
            DummyModuleNode(
                name="h",
                module_type="ModuleList",
                full_path="transformer.h",
                children=[
                    DummyModuleNode(
                        name="0",
                        module_type="Layer",
                        full_path="transformer.h.0",
                        children=[
                            DummyModuleNode(
                                name="attn",
                                module_type="Attention",
                                full_path="transformer.h.0.attn",
                                is_leaf=True,
                            ),
                            DummyModuleNode(
                                name="mlp",
                                module_type="MLP",
                                full_path="transformer.h.0.mlp",
                                is_leaf=True,
                            ),
                        ],
                    ),
                    DummyModuleNode(
                        name="1",
                        module_type="Layer",
                        full_path="transformer.h.1",
                        is_leaf=True,
                    ),
                ],
            ),
            DummyModuleNode(
                name="ln_f",
                module_type="LayerNorm",
                full_path="transformer.ln_f",
                is_leaf=True,
            ),
        ],
    )
    dummy_root = DummyModuleNode(
        name="GPT2Model",
        module_type="Model",
        full_path="",
        children=[
            DummyModuleNode(
                name="wte", module_type="Embedding", full_path="wte", is_leaf=True
            ),
            dummy_transformer,
            DummyModuleNode(
                name="wpe", module_type="Embedding", full_path="wpe", is_leaf=True
            ),
        ],
    )

    app = LMSteerApp(model_root=dummy_root, model_name="dummy_gpt2")
    app.run()
