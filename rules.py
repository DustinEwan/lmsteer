from typing import TypedDict, Literal, List
import fnmatch
from transformers import AutoModel # For type hinting
from rich.console import Console # For status messages during compilation

# Define the structure of a rule
class Rule(TypedDict):
    id: str
    rule_type: Literal['instance', 'module_type', 'path_pattern']
    specifier: str  # For 'instance' and 'path_pattern', this is a path. For 'module_type', it's the type name.
    action: Literal['capture', 'skip']

def compile_rules_to_steering_config(defined_rules: List[Rule], model: AutoModel, console: Console) -> dict:
    """Compiles the defined rules into a final steering configuration for leaf modules."""
    final_steering_config = {}
    console.print("\nCompiling rules to final steering configuration...")

    # Get all leaf modules with their full paths
    leaf_modules = []
    for name, module_obj in model.named_modules():
        if not list(module_obj.children()): # Check if it's a leaf module
            leaf_modules.append((name, module_obj))

    for module_full_name, leaf_module in leaf_modules:
        leaf_module_type = type(leaf_module).__name__
        final_action = None  # Undetermined initially
        source_rule_id = None
        applied_rule_specifier = None
        applied_rule_type = None

        # Rule Precedence: Instance > Path Pattern > Module Type
        # Within each category, the last defined rule wins (hence iterating `reversed(defined_rules)`)

        # 1. Check instance rules (highest precedence)
        for rule in reversed(defined_rules):
            if rule['rule_type'] == 'instance' and rule['specifier'] == module_full_name:
                final_action = rule['action']
                source_rule_id = rule['id']
                applied_rule_specifier = rule['specifier']
                applied_rule_type = rule['rule_type']
                break
        
        if final_action is not None: # Action decided by instance rule
            if final_action == 'capture':
                final_steering_config[module_full_name] = {
                    "action": "capture_leaf_activations", 
                    "module_type": leaf_module_type,
                    "source_rule_id": source_rule_id, 
                    "source_rule_type": applied_rule_type,
                    "source_rule_specifier": applied_rule_specifier
                }
            continue # Decision made for this leaf module, move to the next leaf

        # 2. Check path pattern rules (middle precedence)
        for rule in reversed(defined_rules):
            if rule['rule_type'] == 'path_pattern' and fnmatch.fnmatch(module_full_name, rule['specifier']):
                final_action = rule['action']
                source_rule_id = rule['id']
                applied_rule_specifier = rule['specifier']
                applied_rule_type = rule['rule_type']
                break
        
        if final_action is not None: # Action decided by path pattern rule
            if final_action == 'capture':
                final_steering_config[module_full_name] = {
                    "action": "capture_leaf_activations", 
                    "module_type": leaf_module_type,
                    "source_rule_id": source_rule_id, 
                    "source_rule_type": applied_rule_type,
                    "source_rule_specifier": applied_rule_specifier
                }
            continue # Decision made, move to next leaf

        # 3. Check module type rules (lowest precedence)
        for rule in reversed(defined_rules):
            if rule['rule_type'] == 'module_type' and rule['specifier'] == leaf_module_type:
                final_action = rule['action']
                source_rule_id = rule['id']
                applied_rule_specifier = rule['specifier']
                applied_rule_type = rule['rule_type']
                break
        
        # If after all checks, final_action is 'capture', add to config
        if final_action == 'capture':
            final_steering_config[module_full_name] = {
                "action": "capture_leaf_activations", 
                "module_type": leaf_module_type,
                "source_rule_id": source_rule_id, 
                "source_rule_type": applied_rule_type,
                "source_rule_specifier": applied_rule_specifier
            }
            
    console.print(f"Compilation complete. {len(final_steering_config)} leaf modules marked for capture based on {len(defined_rules)} rules.")
    return final_steering_config
