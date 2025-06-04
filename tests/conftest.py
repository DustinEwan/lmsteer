import pytest
from typing import AsyncGenerator
from textual.pilot import Pilot
from lmsteer.tui.app import LMSteerApp
from lmsteer.app.model_utils import ModuleNode, load_model_and_tokenizer, build_module_tree
from rich.console import Console

@pytest.fixture
async def app() -> AsyncGenerator[LMSteerApp, None]:
    """
    Pytest fixture to provide an instance of LMSteerApp for testing.
    Uses a known, relatively small model.
    The app instance is yielded before run_test() is called.
    """
    model_name_str = "openai-community/gpt2"
    
    # Load the model and build the module tree
    try:
        console = Console()
        model, _ = load_model_and_tokenizer(model_name_str, console=console)
        if model is None: # Handle case where model loading failed
            pytest.fail(f"Model loading failed for {model_name_str}")
        actual_model_root = build_module_tree(model)
    except Exception as e:
        pytest.fail(f"Failed to load model or build module tree for tests: {e}")

    app_instance = LMSteerApp(model_root=actual_model_root, model_name=model_name_str)
    yield app_instance
    # app_instance will be cleaned up by Textual when the test using it finishes,
    # especially if run_test() is used as a context manager in the test.
