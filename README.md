# LMSteer: Guided Language Model Steering

## Project Goal
LMSteer is a command-line tool designed to provide a guided framework for "steering" language models. This approach offers an alternative to traditional fine-tuning by allowing users to precisely control and modify model behavior through targeted interventions at the activation level.

## Core Idea
The core idea is to identify specific modules within a Hugging Face transformer model and decide how their activations should be handled. This involves:
1.  **Observation Stage (Future):** Capturing activations from selected modules as the model processes input.
2.  **Steering Configuration:** Defining rules for which activations to capture and, eventually, how to modify them.
3.  **Inference Stage (Future):** Injecting "steering vectors" (modified activations) back into the model during inference to guide its output.

This tool is currently focused on building the **Steering Configuration** mechanism.

## Current State (Post-Refactor, Pre-Textual TUI)
*   **Model Loading:** Specify any Hugging Face model via command-line argument (`--model_name` or `--model-name`).
*   **Modular Core Logic:** The core functionalities have been refactored into separate modules:
    *   `model_utils.py`: Handles loading Hugging Face models and tokenizers. It also builds an internal tree representation (`ModuleNode`) of the model's structure, which will be used by the future TUI.
    *   `rules.py`: Defines the `Rule` data structure and contains the logic for compiling a list of defined rules into a final steering configuration. It supports instance-specific, module type-specific, and path pattern (glob-style) rules with defined precedence (Instance > Path Pattern > Module Type).
    *   `config_io.py`: Manages saving the generated steering configuration to a JSON file.
*   **Placeholder TUI & Rule Generation:** The main script (`main.py`) currently uses a placeholder function (`collect_rules_via_placeholder_tui`) instead of a fully interactive TUI. When run, this placeholder:
    *   Loads the specified model and builds its internal module tree.
    *   Generates a small, predefined set of sample steering rules (e.g., an instance capture, a path pattern capture, a type skip) for demonstration and to allow testing of the downstream compilation and saving logic.
*   **Configuration Output:** The steering configuration, derived from the (currently sample) rules, is compiled to determine actions for all leaf modules. The resulting configuration (showing only modules to be captured, along with their type and the source rule details) is printed to the console and saved as a JSON file (e.g., `openai-community_gpt2_steer_config.json`).

## How to Use (Current Version)

### 1. Setup
Ensure you have the `lmsteer` directory with the Python modules (`main.py`, `model_utils.py`, `rules.py`, `config_io.py`) and `requirements.txt`.
Install the necessary dependencies:
```bash
pip install -r requirements.txt
```

### 2. Running the Tool
Execute the main script from your terminal, providing the Hugging Face model name:
```bash
python /workspace/lmsteer/main.py --model_name <your_model_name>
# or
python /workspace/lmsteer/main.py --model-name <your_model_name>
```
Replace `<your_model_name>` with a model identifier from Hugging Face Hub (e.g., `distilbert-base-uncased`, `gpt2`, `facebook/opt-125m`).

### 3. Current Behavior (Placeholder TUI)
When you run the script:
*   The specified model will be loaded.
*   A message will indicate that the TUI is a placeholder and the next step is to implement it using `Textual`.
*   A few sample steering rules will be automatically generated and displayed in the console.
*   These rules will be compiled, and the resulting steering configuration (showing which leaf modules would be captured) will be printed to the console.
*   The configuration will be saved to a JSON file in the `/workspace/lmsteer/` directory (e.g., `openai-community_gpt2_steer_config.json`).

## Roadmap & Future Enhancements

### Immediate Next Steps
*   [ ] **Implement Interactive TUI with `Textual`:** Develop a new Terminal User Interface using the `Textual` library. This TUI will allow users to:
    *   Navigate the model's module structure (using the tree built by `model_utils.py`).
    *   Interactively define, view, and potentially manage steering rules.
    *   This will replace the current `collect_rules_via_placeholder_tui` function in `main.py`.

### Core Steering Functionality (Post-TUI)
*   [ ] **Forward Hooks for Observation:** Based on the generated steering configuration, register forward hooks to actually capture activations from the targeted modules during an "observation stage" (e.g., when processing a sample dataset).
*   [ ] **Steering Vector Storage & Management:** Define how captured activations (steering vectors) are stored and managed.
*   [ ] **Steering Vector Injection:** Implement mechanisms to modify and/or inject these steering vectors back into the model during a separate inference run to guide its behavior.

### CLI and Workflow Enhancements
*   [ ] **Structured CLI with Subcommands:** Refactor the command-line interface to support subcommands for a more organized workflow (e.g., `lmsteer new <config_name> <model>` to create a config, `lmsteer edit <config_name>` to modify it, `lmsteer observe <config_name> <dataset>` to capture activations, `lmsteer steer <config_name> <input_prompt>`).
*   [ ] **Advanced Rule Management in TUI:** Enhance the Textual TUI to allow easy viewing, deleting, and modifying of existing rules before compilation.
*   [ ] **Configuration Editing:** Allow loading an existing `_steer_config.json` file into the TUI for modification.

### General Polish
*   [ ] **Advanced Module Filtering/Selection:** Offer more sophisticated ways to select or filter modules within the TUI (e.g., by depth, by regex on name).
*   [ ] **Comprehensive Testing:** Develop a suite of tests for the core logic and TUI components.
*   [ ] **Expand Documentation:** Continuously update in-code comments, user guides, and examples.

### Recently Completed
*   Initial CLI argument parsing for model name (supporting `--model_name` and `--model-name`).
*   Hugging Face model and tokenizer loading.
*   Core logic for rule definition (instance, type, path pattern) and compilation with precedence.
*   Saving the compiled steering configuration to a JSON file.
*   **Refactoring:** Separated core logic into `model_utils.py`, `rules.py`, and `config_io.py`.
*   Replaced the initial `rich`-based TUI with a placeholder in `main.py` in preparation for `Textual`.
*   Set up Git repository and pushed initial refactored code to GitHub.

## Dependencies
*   `transformers`
*   `torch`
*   `rich` (Currently used for console output by utility functions; `Textual` builds upon `rich`)
*   `textual` (Planned for the new TUI)
*   `uuid` (standard library, used for rule IDs)
*   `fnmatch` (standard library, for path pattern matching)

---
*This README will be updated as the project progresses.*
