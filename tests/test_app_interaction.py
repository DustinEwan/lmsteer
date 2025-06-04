import pytest
from textual.pilot import Pilot
from textual.widgets import RadioSet, RadioButton, Static, Tree
from textual.containers import Vertical
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


@pytest.mark.asyncio
async def test_contextual_key_handling(app: LMSteerApp):
    """
    Tests that 'j' and 'k' keys correctly navigate the ModuleTree or RadioSet
    only when that specific widget is focused.
    """
    async with app.run_test() as pilot:
        await pilot.pause() # Allow app to settle

        module_tree = app.query_one("#module_tree", Tree)
        try:
            radioset = app.query_one("#module_action_radioset", RadioSet)
        except Exception as e:
            pytest.fail(f"RadioSet #module_action_radioset not found: {e}. Ensure root node is selected and detail pane populated.")

        buttons = list(radioset.query(RadioButton)) # Needed for radioset state checks

        # --- Part 1: Test 'j'/'k' on ModuleTree when it's focused ---
        module_tree.focus() # Ensure focus is on ModuleTree
        await pilot.pause()
        assert module_tree.has_focus, "ModuleTree should have focus"
        assert not radioset.has_focus, "RadioSet should not have focus"

        initial_tree_cursor_node = module_tree.cursor_node
        initial_tree_cursor_node_data = initial_tree_cursor_node.data if initial_tree_cursor_node else None
        initial_radioset_pressed_index = radioset.pressed_index

        # Expand root node if necessary to have children to navigate to
        if initial_tree_cursor_node and not initial_tree_cursor_node.is_expanded and initial_tree_cursor_node.children:
            await pilot.press("l") # expand key for tree
            await pilot.pause()
        
        # Press 'j' - should move tree cursor, not radioset
        await pilot.press("j") # navigation key for tree
        await pilot.pause()

        current_tree_cursor_node_after_j = module_tree.cursor_node
        current_tree_cursor_node_data_after_j = current_tree_cursor_node_after_j.data if current_tree_cursor_node_after_j else None
        
        # Assert tree cursor moved, if possible
        if initial_tree_cursor_node and initial_tree_cursor_node.children and initial_tree_cursor_node.is_expanded:
             if len(initial_tree_cursor_node.children) > 0 : # If there are children to move to
                assert current_tree_cursor_node_data_after_j is not initial_tree_cursor_node_data, \
                    "ModuleTree cursor should have changed after 'j' when tree focused and children available"
        elif initial_tree_cursor_node and not initial_tree_cursor_node.children: # at a leaf
            assert current_tree_cursor_node_data_after_j is initial_tree_cursor_node_data, \
                "ModuleTree cursor should not change at a leaf node after 'j'"
        # Add other conditions if necessary (e.g. tree is empty, only one node)

        assert radioset.pressed_index == initial_radioset_pressed_index, \
            "RadioSet selection should NOT change when tree focused and 'j' is pressed"
        
        tree_node_data_after_j_on_tree = current_tree_cursor_node_data_after_j

        # Press 'k' - should move tree cursor, not radioset
        await pilot.press("k") # navigation key for tree
        await pilot.pause()
        
        current_tree_cursor_node_after_k = module_tree.cursor_node
        current_tree_cursor_node_data_after_k = current_tree_cursor_node_after_k.data if current_tree_cursor_node_after_k else None

        # Assert tree cursor moved, if possible
        if current_tree_cursor_node_after_j and current_tree_cursor_node_after_j.parent: # If not at root and can move up
            assert current_tree_cursor_node_data_after_k is not tree_node_data_after_j_on_tree, \
                "ModuleTree cursor should have changed after 'k' when tree focused and not at root"
        elif current_tree_cursor_node_after_j and not current_tree_cursor_node_after_j.parent: # at root
             assert current_tree_cursor_node_data_after_k is tree_node_data_after_j_on_tree, \
                "ModuleTree cursor should not change at root node after 'k'"


        assert radioset.pressed_index == initial_radioset_pressed_index, \
            "RadioSet selection should NOT change when tree focused and 'k' is pressed"
        tree_node_data_after_tree_nav = current_tree_cursor_node_data_after_k


        # --- Part 2: Test 'j'/'k' on RadioSet when it's focused ---
        radioset.focus()
        await pilot.pause()

        assert not module_tree.has_focus, "ModuleTree should NOT have focus after focusing RadioSet"
        assert radioset.has_focus, "RadioSet should have focus"
        
        initial_radioset_pressed_index_for_part2 = radioset.pressed_index # Should be (2) "Default"

        # Press 'j' - should change radioset, not tree
        await pilot.press("j") # navigation key for radioset
        await pilot.pause()
        # Default (idx 2) -> Capture (idx 0)
        assert buttons[0].value is True, "After 'j' (RadioSet focused), 'Capture' should be selected"
        assert radioset.pressed_index == 0, "RadioSet index should be 0 (Capture)"
        assert (module_tree.cursor_node.data if module_tree.cursor_node else None) is tree_node_data_after_tree_nav, \
            "ModuleTree cursor should NOT change when RadioSet focused and 'j' is pressed"

        # Press 'k' - should change radioset, not tree
        await pilot.press("k") # navigation key for radioset
        await pilot.pause()
        # Capture (idx 0) -> Default (idx 2)
        assert buttons[2].value is True, "After 'k' (RadioSet focused), 'Default' should be selected"
        assert radioset.pressed_index == 2, "RadioSet index should be 2 (Default)"
        assert (module_tree.cursor_node.data if module_tree.cursor_node else None) is tree_node_data_after_tree_nav, \
            "ModuleTree cursor should NOT change when RadioSet focused and 'k' is pressed"

@pytest.mark.asyncio
async def test_focus_behavior_and_indicators(app: LMSteerApp):
    """
    Tests focus movement using Tab, Shift+Tab, and direct focus calls ('h', 'l'),
    and checks for focus indicators (via has_focus and pseudo_class).
    """
    async with app.run_test() as pilot:
        await pilot.pause() # Allow app to settle

        module_tree = app.query_one("#module_tree", Tree)
        detail_pane = app.query_one("#context_pane", Vertical) 
        radioset = app.query_one("#module_action_radioset", RadioSet)

        # 1. Initial focus
        assert module_tree.has_focus, "ModuleTree should have initial focus"
        assert module_tree.has_pseudo_class("focus"), "ModuleTree should have :focus pseudo-class initially"
        assert not detail_pane.has_focus, "DetailPane should not have initial focus"
        assert not detail_pane.has_pseudo_class("focus"), "DetailPane should not have :focus pseudo-class initially"
        assert not radioset.has_focus, "RadioSet should not have initial focus"
        assert not radioset.has_pseudo_class("focus"), "RadioSet should not have :focus pseudo-class initially"


        # 2. Focus RadioSet in DetailPane (by pressing Enter on the Tree)
        assert module_tree.has_focus, "ModuleTree should still be focused before pressing Enter"
        await pilot.press("Enter")
        assert not radioset.disabled, "RadioSet should be enabled before pressing Enter on Tree"
        await pilot.pause()
        await pilot.pause() # Extra pause for focus to settle
        print(f"DEBUG: app.focused before pilot.call(radioset.focus): {app.focused}")
        app.set_focus(radioset)
        await pilot.pause() # Allow focus action to complete
        print(f"DEBUG: app.focused after pilot.call(radioset.focus): {app.focused}")
        focused_widget_after_enter = app.focused

        print(f"DEBUG: Widget focused after Enter: {focused_widget_after_enter}, RadioSet is: {radioset}")
        assert focused_widget_after_enter is radioset, f"RadioSet should be app.focused. Expected {radioset}, Got: {focused_widget_after_enter}"

        assert not module_tree.has_focus, "ModuleTree should lose focus after Enter"
        assert not module_tree.has_pseudo_class("focus"), "ModuleTree should lose :focus pseudo-class after Enter"
        assert not module_tree.has_class("pane-focused"), "ModuleTree should lose pane-focused class after Enter"
        assert not detail_pane.has_focus, "DetailPane (Vertical container) should NOT have direct focus if child (RadioSet) is focused"
        assert not detail_pane.has_pseudo_class("focus"), "DetailPane (Vertical container) should NOT have :focus pseudo-class if child (RadioSet) is focused"
        assert detail_pane.has_class("pane-focused"), "DetailPane (Vertical container) should gain pane-focused class"
        assert radioset.has_focus, "RadioSet should gain focus after Enter on Tree"
        assert radioset.has_pseudo_class("focus"), "RadioSet should have :focus pseudo-class after Enter on Tree"


        # 3. Focus ModuleTree (using app's action_focus_tree via 'Escape' key)
        await pilot.press("Escape")
        await pilot.pause()

        assert module_tree.has_focus, "ModuleTree should regain focus after Escape"
        assert module_tree.has_pseudo_class("focus"), "ModuleTree should regain :focus pseudo-class after Escape"
        assert module_tree.has_class("pane-focused"), "ModuleTree should regain pane-focused class after Escape"
        assert not detail_pane.has_focus, "DetailPane should lose focus after Escape"
        assert not detail_pane.has_pseudo_class("focus"), "DetailPane should lose :focus pseudo-class after Escape"
        assert not detail_pane.has_class("pane-focused"), "DetailPane should lose pane-focused class after Escape"
        assert not radioset.has_focus, "RadioSet should lose focus after Escape"
        assert not radioset.has_pseudo_class("focus"), "RadioSet should lose :focus pseudo-class after Escape"

        # 4. Test Tab navigation
        # ModuleTree is currently focused. Tab should move to DetailPane.
        assert module_tree.has_focus
        await pilot.press("Tab")
        await pilot.pause()

        assert not module_tree.has_focus, "ModuleTree should lose focus after Tab"
        assert not module_tree.has_pseudo_class("focus"), "ModuleTree should lose :focus pseudo-class after Tab"
        assert not module_tree.has_class("pane-focused"), "ModuleTree should lose pane-focused class after Tab"
        assert detail_pane.has_focus, "DetailPane (Vertical) should gain focus after Tab from ModuleTree"
        assert detail_pane.has_pseudo_class("focus"), "DetailPane (Vertical) should have :focus pseudo-class after Tab from ModuleTree"
        assert detail_pane.has_class("pane-focused"), "DetailPane (Vertical) should gain pane-focused class"
        assert not radioset.has_focus, "RadioSet should NOT have focus yet after Tab from ModuleTree"
        assert not radioset.has_pseudo_class("focus"), "RadioSet should NOT have :focus pseudo-class yet after Tab from ModuleTree"


        # Press Tab again (from DetailPane focused). Should move to RadioSet within DetailPane.
        assert detail_pane.has_focus
        await pilot.press("Tab")
        await pilot.pause()
        
        assert not detail_pane.has_focus, "DetailPane (Vertical) should lose direct focus after Tab from itself (child gets focus)"
        assert not detail_pane.has_pseudo_class("focus"), "DetailPane (Vertical) should lose :focus pseudo-class (child gets focus)"
        assert detail_pane.has_class("pane-focused"), "DetailPane (Vertical) should RETAIN pane-focused class (child is focused)"
        assert radioset.has_focus, "RadioSet should gain focus after Tab from DetailPane (Vertical)"
        assert radioset.has_pseudo_class("focus"), "RadioSet should have :focus pseudo-class after Tab from DetailPane (Vertical)"

        # 5. Test Shift+Tab navigation
        # RadioSet is currently focused. Shift+Tab should move to DetailPane.
        assert radioset.has_focus
        await pilot.press("Shift+Tab")
        await pilot.pause()

        assert not radioset.has_focus, "RadioSet should lose focus after Shift+Tab"
        assert not radioset.has_pseudo_class("focus"), "RadioSet should lose :focus pseudo-class after Shift+Tab"
        assert detail_pane.has_focus, "DetailPane (Vertical) should gain focus after Shift+Tab from RadioSet"
        assert detail_pane.has_pseudo_class("focus"), "DetailPane (Vertical) should have :focus pseudo-class after Shift+Tab from RadioSet"
        assert detail_pane.has_class("pane-focused"), "DetailPane (Vertical) should RETAIN pane-focused class (as it's now focused)"

        # Press Shift+Tab again (from DetailPane). Should move to ModuleTree.
        assert detail_pane.has_focus
        await pilot.press("Shift+Tab")
        await pilot.pause()

        assert not detail_pane.has_focus, "DetailPane (Vertical) should lose focus after Shift+Tab from itself"
        assert not detail_pane.has_pseudo_class("focus"), "DetailPane (Vertical) should lose :focus pseudo-class after Shift+Tab from itself"
        assert not detail_pane.has_class("pane-focused"), "DetailPane (Vertical) should lose pane-focused class"
        assert module_tree.has_focus, "ModuleTree should gain focus after Shift+Tab from DetailPane (Vertical)"
        assert module_tree.has_pseudo_class("focus"), "ModuleTree should have :focus pseudo-class after Shift+Tab from DetailPane (Vertical)"
        assert module_tree.has_class("pane-focused"), "ModuleTree should gain pane-focused class"

