import sys
import os

# Add project root to sys.path if running directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from neonodes.problems import daily_temperatures, eval_rpn
from neonodes.renderers.stack import StackRenderer

def test_daily_temperatures_flow():
    print("Testing Daily Temperatures stack renderer flow...")
    input_data = [73, 74, 75, 71, 69, 72, 76, 73]
    
    # Run problem recorder
    frames = daily_temperatures.run(list(input_data))
    
    renderer = StackRenderer()
    filtered = renderer.filter_frames(frames)
    
    # Verify we got some steps
    assert len(filtered) > 0, "Should have filtered frames"
    
    # Compute states for a step in the middle (e.g. step where we pop and compare)
    # Let's find a step with 'pop' operation
    pop_step_idx = None
    for idx, f in enumerate(filtered):
        state = renderer.compute_states(filtered, idx)
        if state.get("op_type") == "pop":
            pop_step_idx = idx
            break
            
    assert pop_step_idx is not None, "Should find at least one pop operation in Daily Temperatures flow"
    
    state = renderer.compute_states(filtered, pop_step_idx)
    # Verify pointers are tracked
    pointers = state.get("pointers", {})
    assert "i" in pointers, "'i' pointer should be tracked"
    assert "idx" in pointers or "idx" in state.get("accumulated_locals", {}), "idx should be tracked"
    
    # Verify variable entries style pointers
    entries = renderer.variable_entries(filtered[pop_step_idx])
    keys = [name for name, val, col in entries]
    assert "stack" in keys, "stack should be in variable entries"
    assert "i" in keys, "i pointer should be in variable entries"

def test_eval_rpn_flow():
    print("Testing Eval RPN stack renderer flow...")
    input_data = ["2", "1", "+", "3", "*"]
    
    frames = eval_rpn.run(list(input_data))
    renderer = StackRenderer()
    filtered = renderer.filter_frames(frames)
    
    assert len(filtered) > 0, "Should have filtered frames"
    
    # Find a push step
    push_step_idx = None
    for idx, f in enumerate(filtered):
        state = renderer.compute_states(filtered, idx)
        if state.get("op_type") == "push":
            push_step_idx = idx
            break
            
    assert push_step_idx is not None, "Should find at least one push operation"
    
    state = renderer.compute_states(filtered, push_step_idx)
    assert len(state.get("stack", [])) > 0, "Stack should not be empty after a push"
