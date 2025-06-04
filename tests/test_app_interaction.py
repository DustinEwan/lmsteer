import pytest
from textual.pilot import Pilot
from textual.widgets import RadioSet, RadioButton, Static
from lmsteer.tui.app import LMSteerApp
# The 'app' fixture is automatically used from tests/conftest.py
# The 'pilot' fixture is provided by Textual's testing capabilities

@pytest.mark.asyncio
async def test_radioset_jk_navigation(app: LMSteerApp): # Fixture is now app
    """
    Tests 'j' and 'k' navigation within the NavigableRadioSet in the detail pane.
    """
    async with app.run_test() as pilot: # Use app.run_test() as a context manager
        assert pilot is not None, "Pilot object is None after app.run_test()"
        # Wait for the app to settle. The root model node should be selected by default,
        # showing its RadioSet in the detail pane.
        await pilot.pause()

        # Ensure the RadioSet is present
        try:
            radioset = app.query_one("#module_action_radioset", RadioSet)
        except Exception as e:
            pytest.fail(f"RadioSet #module_action_radioset not found: {e}")
        
        buttons = list(radioset.query(RadioButton))
        button_labels = [b.label.plain for b in buttons]
        expected_labels = ["Capture Activations for this module (GPT2Model)", "Skip Activations for this module (GPT2Model)", "Default / Inherit"]
        assert button_labels == expected_labels, f"Radio button labels are not as expected: {button_labels}"

        # Initial state: "Default" (index 2) should be selected
        assert buttons[2].value is True, "Initial selection should be 'Default'"

        # Focus the detail pane (where the RadioSet is).
        # Default focus is on the tree. 'l' moves focus to the detail pane.
        # To focus the detail pane:
        # 1. 'l' on root node (GPT2Model) expands it. Focus stays on tree.
        # 2. 'j' moves to first child (e.g., wte).
        # 3. Directly focus the RadioSet in the detail pane.
        await pilot.press("l") # Expand root
        await pilot.pause()
        await pilot.press("j") # Move to first child in tree
        await pilot.pause()
        app.query_one("#module_action_radioset").focus() # Directly focus the RadioSet
        await pilot.pause() # Ensure focus shift is processed

        # --- Test navigation ---

        # Current: Default (idx 2)
        # Press 'j' (down): Default (idx 2) -> Capture (idx 0)
        await pilot.press("j")
        await pilot.pause()
        assert buttons[0].value is True, "After 'j' from Default, 'Capture' should be selected"

        # Current: Capture (idx 0)
        # Press 'k' (up): Capture (idx 0) -> Default (idx 2)
        await pilot.press("k")
        await pilot.pause()
        assert buttons[2].value is True, "After 'k' from Capture, 'Default' should be selected"

        # Current: Default (idx 2)
        # Press 'k' (up): Default (idx 2) -> Skip (idx 1)
        await pilot.press("k")
        await pilot.pause()
        assert buttons[1].value is True, "After 'k' from Default, 'Skip' should be selected"

        # Current: Skip (idx 1)
        # Press 'j' (down): Skip (idx 1) -> Default (idx 2)
        await pilot.press("j")
        await pilot.pause()
        assert buttons[2].value is True, "After 'j' from Skip, 'Default' should be selected"

        # Current: Default (idx 2)
        # One more 'j' to ensure it wraps to Capture
        await pilot.press("j")
        await pilot.pause()
        assert buttons[0].value is True, "After 'j' from Default (again), 'Capture' should be selected"

        # Current: Capture (idx 0)
        # One more 'k' to ensure it wraps to Default
        await pilot.press("k")
        await pilot.pause()
        assert buttons[2].value is True, "After 'k' from Capture (again), 'Default' should be selected"


@pytest.mark.asyncio
async def test_module_tree_navigation_and_detail_update(app: LMSteerApp):
    """
    Tests 'j' and 'k' navigation within the module tree (CustomTree)
    and verifies that the detail pane updates accordingly.
    """
    async with app.run_test() as pilot:
        assert pilot is not None, "Pilot object is None after app.run_test()"
        await pilot.pause() # Allow app to settle

        module_tree = app.query_one("#module_tree")
        module_info_display = app.query_one("#module_info_static", Static)

        # Initial state: Root node should be selected
        initial_cursor_node = module_tree.cursor_node
        assert initial_cursor_node is not None, "Initial cursor node is None"
        initial_cursor_node_data = initial_cursor_node.data
        assert initial_cursor_node_data is not None, "Initial cursor node data is None"
        initial_node_name = initial_cursor_node_data.name
        initial_node_display_path = "(root)"  # Path displayed for root in TUI
        initial_node_type_str = initial_cursor_node_data.module_type
        
        assert initial_node_name == "GPT2Model", f"Initial selected node name is not GPT2Model: {initial_node_name}"
        initial_details_text = module_info_display.renderable
        assert f"[bold]Full Path:[/bold] {initial_node_display_path}" in initial_details_text, f"Initial module path display is incorrect. Expected '[bold]Full Path:[/bold] {initial_node_display_path}' in '{initial_details_text}'"
        assert f"[bold]Module Type:[/bold] {initial_node_type_str}" in initial_details_text, f"Initial module type display is incorrect. Expected '[bold]Module Type:[/bold] {initial_node_type_str}' in '{initial_details_text}'"

        # Expand the root node to make children visible for navigation
        await pilot.press("l") 
        await pilot.pause()

        # Press 'j' to move to the first child
        await pilot.press("j")
        await pilot.pause()

        # New state: First child should be selected
        first_child_cursor_node = module_tree.cursor_node
        assert first_child_cursor_node is not None, "First child cursor node is None"
        first_child_node_data = first_child_cursor_node.data
        assert first_child_node_data is not None, "First child cursor node data is None"
        first_child_node_name = first_child_node_data.name
        first_child_node_path = first_child_node_data.get_full_path() # Use get_full_path() for actual path
        first_child_node_type_str = first_child_node_data.module_type

        assert first_child_node_name != initial_node_name, "Node selection did not change after pressing 'j'"
        # We expect the first child of GPT2Model to be 'wte' for gpt2 model
        assert first_child_node_name == "wte", f"Expected first child to be 'wte', got {first_child_node_name}"
        first_child_details_text = module_info_display.renderable
        assert f"[bold]Full Path:[/bold] {first_child_node_path}" in first_child_details_text, f"Module path display did not update for first child. Expected '[bold]Full Path:[/bold] {first_child_node_path}' in '{first_child_details_text}'"
        assert f"[bold]Module Type:[/bold] {first_child_node_type_str}" in first_child_details_text, f"Module type display did not update for first child. Expected '[bold]Module Type:[/bold] {first_child_node_type_str}' in '{first_child_details_text}'"
        
        # Press 'k' to move back to the root
        await pilot.press("k")
        await pilot.pause()

        # Back to initial state: Root node should be selected
        back_to_root_cursor_node = module_tree.cursor_node
        assert back_to_root_cursor_node is not None, "Root node (after k) is None"
        back_to_root_node_data = back_to_root_cursor_node.data
        assert back_to_root_node_data is not None, "Root node data (after k) is None"
        assert back_to_root_node_data.name == initial_node_name, "Node selection did not return to root after pressing 'k'"
        root_details_text_after_k = module_info_display.renderable
        assert f"[bold]Full Path:[/bold] {initial_node_display_path}" in root_details_text_after_k, f"Module path display did not revert to root's path. Expected '[bold]Full Path:[/bold] {initial_node_display_path}' in '{root_details_text_after_k}'"
        assert f"[bold]Module Type:[/bold] {initial_node_type_str}" in root_details_text_after_k, f"Module type display did not revert to root's type. Expected '[bold]Module Type:[/bold] {initial_node_type_str}' in '{root_details_text_after_k}'"

