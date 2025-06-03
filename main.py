import argparse
from rich.console import Console

from lmsteer.app.model_utils import load_model_and_tokenizer, build_module_tree
# from rules import Rule, compile_rules_to_steering_config # TUI will handle rules
# from config_io import save_steering_config # TUI will handle saving

from lmsteer.tui.app import LMSteerApp


def main():
    parser = argparse.ArgumentParser(
        description="LMSteer: A guided framework for steering language models."
    )
    parser.add_argument(
        "--model_name",
        "--model-name",
        dest="model_name_arg",
        type=str,
        required=True,
        help="Name of the Hugging Face model to steer (e.g., 'openai-community/gpt2', 'bert-base-uncased').",
    )
    args = parser.parse_args()

    console = Console()  # Still used by load_model_and_tokenizer
    model, tokenizer = load_model_and_tokenizer(args.model_name_arg, console)

    if model and tokenizer:
        console.print("Building module tree for the model...")
        model_root_node = build_module_tree(model)
        console.print("Module tree built. Launching TUI...")

        app = LMSteerApp(model_root=model_root_node, model_name=args.model_name_arg)
        app.run()

        # The TUI will eventually be responsible for collecting rules and triggering compilation/saving.
        # For now, the following lines are commented out.
        # defined_rules = app.get_defined_rules() # This method would need to be implemented in LMSteerApp

        # if defined_rules:
        #     console.print(f"\nCollected {len(defined_rules)} rules via TUI:")
        #     for r_idx, r_val in enumerate(defined_rules):
        #         console.print(f"  [{r_idx+1}] {r_val}")
        # else:
        #     console.print("\nNo rules were defined via TUI.")

        # steering_config = compile_rules_to_steering_config(defined_rules, model, console)

        # if steering_config:
        #     console.print("\n[bold green]Generated Steering Configuration:[/bold green]")
        #     console.print_json(data=steering_config)
        #     save_steering_config(steering_config, args.model_name_arg, console)
        # else:
        #     console.print("[yellow]No steering configuration was generated.[/yellow]")

        console.print("TUI session ended.")

    else:
        console.print("[bold red]Exiting due to model loading failure.[/bold red]")


if __name__ == "__main__":
    main()
