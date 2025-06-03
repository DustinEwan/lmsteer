# LMSteer: Guided Language Model Steering

## Project Goal
LMSteer is a command-line tool designed to provide a guided framework for "steering" language models. This approach offers an alternative to traditional fine-tuning by allowing users to precisely control and modify model behavior through targeted interventions at the activation level.

## Core Idea
The core idea is to identify specific modules within a Hugging Face transformer model and decide how their activations should be handled. This involves:
1.  **Observation Stage (Future):** Capturing activations from selected modules as the model processes input.
2.  **Steering Configuration:** Defining rules for which activations to capture and, eventually, how to modify them.
3.  **Inference Stage (Future):** Injecting "steering vectors" (modified activations) back into the model during inference to guide its output.

This tool currently focuses on the **Steering Configuration** aspect, allowing users to specify which module activations they are interested in.

## Current Features
*   **Model Loading:** Specify any Hugging Face model via command-line argument (`--model_name`).
*   **Interactive Tree TUI:** A `rich`-based navigable tree interface displays the model's module structure. The TUI header shows a running count of defined rules.
*   **Contextual Rule Definition for All Nodes:** When any node (leaf or non-leaf) is selected in the tree:
    *   The user is prompted with contextual options to define a rule:
        *   **Instance-specific rules:** Capture or skip the exact selected module (if leaf) or all descendant leaves of the selected module (if non-leaf, by creating a `path.to.module.*` pattern).
        *   **Type-specific rules:** Always capture or never capture modules of the selected node's type.
        *   **Path pattern rules:** Capture or skip modules matching a custom, user-defined glob-like path pattern (e.g., `encoder.layer.*.attention`).
    *   Each choice creates a rule (instance, type, or path pattern) with a unique ID, added to a list of defined rules.
*   **Rule-Based Configuration & Compilation:** After interaction (quitting the TUI), all defined rules are compiled:
    *   The tool determines the final action (`capture` or `skip`) for every leaf module in the model.
    *   **Precedence:** Instance rules > Path Pattern rules > Module Type rules. The most recently defined rule within a matching category takes precedence.
*   **Configuration Output:** The resulting steering configuration, mapping full leaf module names to a detailed action object (if the final action is to capture), is saved as a JSON file. This object includes `{"action": "capture_leaf_activations", "module_type": "...", "source_rule_id": "...", "source_rule_specifier": "..."}`.

## How to Use

### 1. Setup
Ensure you have the `lmsteer` directory with `main.py` and `requirements.txt`.
Install the necessary dependencies:
```bash
pip install -r requirements.txt
```

### 2. Running the Tool
Execute the main script from your terminal, providing the Hugging Face model name you wish to configure:
```bash
python /workspace/lmsteer/main.py --model_name <your_model_name>
```
Replace `<your_model_name>` with a model identifier from Hugging Face Hub (e.g., `distilbert-base-uncased`, `gpt2`, `facebook/opt-125m`).

### 3. Configuration Process
The tool will load the model and display its structure as an interactive tree. The tree header shows the currently selected module and the total number of rules defined so far.
*   **Navigation:**
    *   `j`: Move selection down.
    *   `k`: Move selection up.
    *   `l`: Select/Expand. If a node is collapsed, `l` expands it. If a node is already expanded or is a leaf, `l` initiates the rule definition prompt for that node.
    *   `h`: Collapse/Parent. If a node is expanded, `h` collapses it. Otherwise, it moves selection to the parent node.
    *   `q`: Finish configuration, compile rules, save, and quit.
*   **Defining Rules (Any Node):** When you select any node (leaf or non-leaf) with `l` and choose to define a rule:
    *   The tree display will pause, and you'll be prompted with contextual choices:
        *   **If Leaf Node:** Options to capture/skip the specific instance, or capture/skip by its type, or define custom path patterns.
        *   **If Non-Leaf Node:** Options to capture/skip all its descendant leaves (using a `node.path.*` pattern), or capture/skip by its type, or define custom path patterns.
    *   Your choice adds a new rule (instance, type, or path pattern) to an internal list. The TUI updates the count of defined rules.
*   **Compilation and Output:** Once you quit with `q`, all the rules you've defined are compiled:
    *   The tool determines the final action for every leaf module in the model based on your rules, respecting precedence (Instance > Path Pattern > Module Type; later rules override earlier rules of the same category and matching specificity).
    *   The complete steering configuration, showing only leaf modules that are ultimately set to be captured (along with their type, the ID of the rule, and the rule specifier that caused the capture), is printed to the console and saved in a JSON file within the `/workspace/lmsteer/` directory.

## To-Do / Future Enhancements

### Core Functionality
*   [X] Basic CLI argument parsing for model name.
*   [X] Hugging Face model and tokenizer loading.
*   [X] Interactive TUI for steering configuration choices (using `rich`).
*   [X] Saving configuration to a JSON file.
*   [X] **Phase 1 TUI: Tree Navigation & Initial Leaf Prompting**
    *   [X] Iteration through model modules (via tree traversal).
    *   [X] Navigable tree display of model structure.
*   [X] **Phase 2.A TUI: Rule-Based Leaf Configuration & Compilation**
    *   [X] Replaced 5-option leaf prompt with 4-option rule definition (instance/type capture/skip).
    *   [X] Implemented a list to store user-defined rules with unique IDs.
    *   [X] Implemented a compilation step to apply defined rules with precedence to all leaf modules.
    *   [X] Final JSON config reflects compiled rules and source rule ID for captured modules.
*   [X] **Phase 2.B TUI: Contextual Options for All Nodes & Path Pattern Rules**
    *   [X] Implemented "path_pattern" rule type using `fnmatch`.
    *   [X] When any tree node (leaf or non-leaf) is selected, dynamically generate relevant action choices (instance, type, path pattern for descendants, custom path pattern).
    *   [X] Updated rule compilation to include path patterns with precedence: Instance > Path Pattern > Type.
    *   [X] Configuration for non-leaf nodes translates to path patterns affecting their descendant leaves.
*   [ ] **Bogus Input Pass (Re-evaluate if needed later):** Implement a step to pass dummy/bogus input through the model. This could be useful for:
    *   Verifying module reachability under specific inputs.
    *   Capturing activation shapes/sizes to inform the user during configuration or for later stages.
*   [ ] **Forward Hooks for Observation:**
    *   Based on the generated config, register forward hooks to actually capture activations during an "observation stage."
    *   Store these captured activations.
*   [ ] **Steering Vector Injection:**
    *   Implement mechanisms to modify/inject steering vectors (derived from observed or user-defined activations) during a separate inference run.
*   [ ] **Refine Configuration Structure:** The structure of `_steer_config.json` might evolve as hook registration and activation manipulation are implemented.

### Polish & Usability
*   [ ] **Rule Management:** Allow viewing, deleting, or modifying existing rules within the TUI before compilation.
*   [ ] **Configuration Editing:** Allow loading and editing an existing `_steer_config.json` (which would involve parsing it back into a `defined_rules` list).
*   [ ] **Advanced Module Filtering:** Offer more sophisticated ways to select/filter modules for configuration (e.g., by depth, by regex on name) perhaps integrated into the tree view or as a pre-filtering step.
*   [ ] **Documentation:** Expand in-code comments and user documentation.

## Dependencies
*   `transformers`
*   `torch`
*   `rich`
*   `uuid` (standard library)
*   `fnmatch` (standard library, for path pattern matching)

---
*This README will be updated as the project progresses.*
