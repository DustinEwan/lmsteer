import json
import os
from rich.console import Console  # For status messages


def save_steering_config(
    steering_config: dict,
    model_name: str,
    console: Console,
    base_path: str = "/workspace/lmsteer",
) -> None:
    """Saves the steering configuration to a JSON file."""
    if not steering_config:
        console.print("[yellow]No steering configuration data to save.[/yellow]")
        return

    # Sanitize model_name for use in filename (e.g., replace '/' with '_')
    safe_model_name = model_name.replace("/", "_")
    config_file_name = f"{safe_model_name}_steer_config.json"
    config_file_path = os.path.join(base_path, config_file_name)

    try:
        os.makedirs(base_path, exist_ok=True)  # Ensure the directory exists
        with open(config_file_path, "w") as f:
            json.dump(steering_config, f, indent=2)
        # Create a file URI for easier clicking in some terminals
        # Note: This might not be universally clickable, but it's a common convention.
        try:
            # Attempt to create an absolute file URI
            abs_config_file_path = os.path.abspath(config_file_path)
            file_link = f"file://{abs_config_file_path}"
            console.print(
                f"\nSteering configuration saved to [link={file_link}]{config_file_path}[/link]"
            )
        except Exception:
            # Fallback if abspath fails for some reason (e.g. non-standard environment)
            console.print(f"\nSteering configuration saved to {config_file_path}")

    except IOError as e:
        console.print(
            f"[bold red]Error saving configuration file to {config_file_path}: {e}[/bold red]"
        )
    except Exception as e:
        console.print(
            f"[bold red]An unexpected error occurred while saving configuration: {e}[/bold red]"
        )
