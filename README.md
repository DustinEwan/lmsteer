# LMSteer: Guided Language Model Steering

## Project Goal
LMSteer is a command-line tool designed to provide a guided framework for "steering" language models. This approach offers an alternative to traditional fine-tuning by allowing users to precisely control and modify model behavior through targeted interventions at the activation level.

## Core Idea
The core idea is to identify specific modules within a Hugging Face transformer model and decide how their activations should be handled. This involves:
1.  **Observation Stage (Future):** Capturing activations from selected modules as the model processes input.
2.  **Steering Configuration:** Defining rules for which activations to capture and, eventually, how to modify them.
3.  **Inference Stage (Future):** Injecting "steering vectors" (modified activations) back into the model during inference to guide its output.

This tool is currently focused on building the **Steering Configuration** mechanism.

## Current State (Textual TUI In Progress)
*   **Model Loading:** Specify any Hugging Face model via command-line argument (`--model_name` or `--model-name`).
*   **Modular Core Logic:** The core functionalities have been refactored into separate modules:
    *   `model_utils.py`: Handles loading Hugging Face models and tokenizers. It also builds an internal tree representation (`ModuleNode`) of the model's structure, which will be used by the future TUI.
    *   `rules.py`: Defines the `Rule` data structure and contains the logic for compiling a list of defined rules into a final steering configuration. It supports instance-specific, module type-specific, and path pattern (glob-style) rules with defined precedence (Instance > Path Pattern > Module Type).
    *   `config_io.py`: Manages saving the generated steering configuration to a JSON file.
*   **Textual TUI Development:** The main script (`main.py`) now launches an interactive Terminal User Interface (TUI) built with the `Textual` library (see `tui.py` and `tui.css`). This replaces the previous placeholder TUI.
    *   The TUI loads the specified Hugging Face model.
    *   It builds and displays an interactive tree representation of the model's module structure.
    *   Users can navigate this tree (expand/collapse nodes) and view details (path, type, etc.) of the selected module.
*   **Rule Definition & Configuration (Future TUI Work):** The functionality for defining steering rules, compiling them into a steering configuration, and saving that configuration is planned for future TUI development and is not yet implemented in the current Textual TUI.

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

### 3. Current Behavior (Textual TUI)
When you run the script:
*   The specified Hugging Face model will be loaded.
*   The Textual TUI will launch.
*   You will see an interactive tree view of the model's module structure.
*   You can navigate the tree using arrow keys (or 'j'/'k' for up/down).
*   Highlighting a module will display its details (path, type, etc.) in the right-hand pane.
*   Rule definition and configuration saving are not yet implemented in the TUI.

## Roadmap & Future Enhancements

### Immediate Next Steps
*   [ ] **Complete Textual TUI for Rule Management:** The initial Textual TUI (`tui.py`) allows for model loading and module tree navigation. The next critical step is to implement full rule management capabilities:
    *   Interactively define steering rules for selected modules (e.g., capture, skip, modify activations).
    *   Display a list of currently defined rules.
    *   Allow users to edit or delete existing rules.
    *   Integrate logic to compile the defined rules into a steering configuration (using `rules.py`).
    *   Implement functionality to save the generated steering configuration to a JSON file (using `config_io.py`).

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
*   **Refactoring:** Separated core logic into `model_utils.py`, `rules.py`, and `config_io.py`.
*   Began implementation of the Textual TUI (`tui.py`, `tui.css`), replacing the placeholder TUI in `main.py`. The TUI now handles model loading, module tree display/navigation, and shows module details.
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
