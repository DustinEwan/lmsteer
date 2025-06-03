import argparse
import uuid # For generating rule IDs in the placeholder TUI
from rich.console import Console

from model_utils import load_model_and_tokenizer, build_module_tree, ModuleNode
from rules import Rule, compile_rules_to_steering_config
from config_io import save_steering_config

def collect_rules_via_placeholder_tui(model_root_node: ModuleNode, console: Console) -> list[Rule]:
    """
    Placeholder for the Textual TUI. 
    For now, it prints a message and can return a predefined set of rules for testing.
    """
    console.print("\n[bold yellow]TUI for rule collection to be implemented with Textual.[/bold yellow]")
    console.print("This placeholder will simulate some rule creation.")

    sample_rules = []
    
    first_leaf_path = None
    first_leaf_type = None
    first_non_leaf_path = None # Can be empty string for root
    first_non_leaf_type = None

    # Helper to find example nodes for placeholder rules
    def find_example_nodes_for_placeholder(node: ModuleNode, current_node_path: str):
        nonlocal first_leaf_path, first_leaf_type, first_non_leaf_path, first_non_leaf_type

        if node.is_leaf:
            if first_leaf_path is None:
                first_leaf_path = current_node_path
                first_leaf_type = node.module_type
        else: # Non-leaf
            if first_non_leaf_path is None: # Take the first non-leaf encountered
                first_non_leaf_path = current_node_path
                first_non_leaf_type = node.module_type
        
        # Recurse if we haven't found all examples yet
        if not (first_leaf_path and first_non_leaf_path is not None):
            for child in node.children:
                # Correctly construct child_path: if current_node_path is empty (root), child_path is just child.name
                child_path = f"{current_node_path}.{child.name}" if current_node_path else child.name
                find_example_nodes_for_placeholder(child, child_path)

    # The root_node itself (model_root_node) has a name (model class) but its path for rule purposes is empty.
    # Its direct children will have paths like 'wte', 'h.0', etc.
    # So, we start traversal from model_root_node, and its initial path for its children context is ""
    find_example_nodes_for_placeholder(model_root_node, model_root_node.get_full_path()) 

    if first_leaf_path and first_leaf_type:
        console.print(f"[cyan]Placeholder: Creating sample INSTANCE CAPTURE rule for: {first_leaf_path} ({first_leaf_type})[/cyan]")
        sample_rules.append({
            'id': uuid.uuid4().hex,
            'rule_type': 'instance',
            'specifier': first_leaf_path, 
            'action': 'capture'
        })
    
    if first_non_leaf_path is not None and first_non_leaf_type:
        # If path is empty (root), pattern should be "*"
        pattern_specifier = f"{first_non_leaf_path}.*" if first_non_leaf_path else "*"
        # Display 'model_root' if path is empty for clarity in the message
        display_path_for_pattern = first_non_leaf_path if first_non_leaf_path else type(model_root_node.module).__name__ + " (root)"
        console.print(f"[cyan]Placeholder: Creating sample PATH PATTERN CAPTURE rule for descendants of: {display_path_for_pattern} (pattern: {pattern_specifier})[/cyan]")
        sample_rules.append({
            'id': uuid.uuid4().hex,
            'rule_type': 'path_pattern',
            'specifier': pattern_specifier, 
            'action': 'capture'
        })
        
        type_for_skip_rule = first_leaf_type if first_leaf_type and first_leaf_type != first_non_leaf_type else first_non_leaf_type
        if type_for_skip_rule:
            console.print(f"[cyan]Placeholder: Creating sample MODULE TYPE SKIP rule for: {type_for_skip_rule}[/cyan]")
            sample_rules.append({
                'id': uuid.uuid4().hex,
                'rule_type': 'module_type',
                'specifier': type_for_skip_rule, 
                'action': 'skip'
            })

    if not sample_rules:
        console.print("[yellow]Placeholder: No sample rules created (e.g., model might be too shallow or no leaves found for examples).[/yellow]")

    return sample_rules

def main():
    parser = argparse.ArgumentParser(description="LMSteer: A guided framework for steering language models.")
    parser.add_argument("--model_name", "--model-name", dest="model_name_arg", type=str, required=True, 
                        help="Name of the Hugging Face model to steer (e.g., 'openai-community/gpt2', 'bert-base-uncased').")
    args = parser.parse_args()

    console = Console()
    model, tokenizer = load_model_and_tokenizer(args.model_name_arg, console)

    if model and tokenizer:
        console.print("Building module tree for the model...")
        model_root_node = build_module_tree(model)

        defined_rules = collect_rules_via_placeholder_tui(model_root_node, console)

        if defined_rules:
            console.print(f"\nCollected {len(defined_rules)} rules via placeholder TUI:")
            for r_idx, r_val in enumerate(defined_rules):
                console.print(f"  [{r_idx+1}] {r_val}")
        else:
            console.print("\nNo rules were defined by the placeholder TUI.")

        steering_config = compile_rules_to_steering_config(defined_rules, model, console)

        if steering_config:
            console.print("\n[bold green]Generated Steering Configuration:[/bold green]")
            console.print_json(data=steering_config)
            save_steering_config(steering_config, args.model_name_arg, console)
        else:
            console.print("[yellow]No steering configuration was generated (e.g., no capture rules resulted from compilation, or no rules defined).[/yellow]")
    else:
        console.print("[bold red]Exiting due to model loading failure.[/bold red]")

if __name__ == "__main__":
    main()
