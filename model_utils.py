from transformers import AutoModel, AutoTokenizer
from rich.console import Console  # Keep for load_model_and_tokenizer status messages


# Simplified node for internal tree representation, independent of Rich
class ModuleNode:
    def __init__(self, name, module, parent_node=None):
        self.name = name
        self.module = module
        self.module_type = type(module).__name__
        self.parent_node = parent_node
        self.children = []
        self.is_leaf = not list(module.children())

    def add_child(self, child_node):
        self.children.append(child_node)

    def get_full_path(self):
        if self.parent_node is None:  # Root node (representing the model itself)
            return ""

        parent_full_path = self.parent_node.get_full_path()
        if parent_full_path:
            return f"{parent_full_path}.{self.name}"
        else:  # Parent is the root ModuleNode
            return self.name


def _build_module_tree_recursive(module_to_inspect, parent_module_node: ModuleNode):
    for name_suffix, child_module in module_to_inspect.named_children():
        child_node = ModuleNode(
            name=name_suffix, module=child_module, parent_node=parent_module_node
        )
        parent_module_node.add_child(child_node)
        if list(child_module.children()):  # If it's not a leaf, recurse
            _build_module_tree_recursive(child_module, child_node)


def build_module_tree(model: AutoModel) -> ModuleNode:
    """Builds an internal tree representation of the model's modules."""
    model_class_name = type(model).__name__
    # The root ModuleNode represents the model itself.
    # Its name is the model class name for potential display, its path is effectively empty.
    root_internal_node = ModuleNode(
        name=model_class_name, module=model, parent_node=None
    )
    _build_module_tree_recursive(model, root_internal_node)
    return root_internal_node


def load_model_and_tokenizer(model_name: str, console: Console):
    """Loads the specified Hugging Face model and tokenizer."""
    try:
        console.print(f"Loading model: [bold cyan]{model_name}[/bold cyan]...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        if tokenizer.pad_token is None:
            if tokenizer.eos_token is not None:
                tokenizer.pad_token = tokenizer.eos_token
                console.print(
                    f"Tokenizer for [bold cyan]{model_name}[/bold cyan] did not have a pad_token. Set to [bold green]eos_token[/bold green]."
                )
            elif tokenizer.unk_token is not None:
                tokenizer.pad_token = tokenizer.unk_token
                console.print(
                    f"Tokenizer for [bold cyan]{model_name}[/bold cyan] did not have a pad_token. Set to [bold green]unk_token[/bold green]."
                )
            else:
                # This part might need adjustment if the model doesn't have eos or unk
                # For now, we'll keep the previous logic of adding a PAD token.
                # However, some models might not need/expect it.
                tokenizer.add_special_tokens({"pad_token": "[PAD]"})
                console.print(
                    f"Tokenizer for [bold cyan]{model_name}[/bold cyan] did not have a pad_token. Added a new pad_token [bold green]'[PAD]'[/bold green]."
                )

        model = AutoModel.from_pretrained(model_name, trust_remote_code=True)
        console.print("[green]Model and tokenizer loaded successfully.[/green]")
        return model, tokenizer
    except Exception as e:
        console.print(f"[bold red]Error loading model {model_name}: {e}[/bold red]")
        return None, None
