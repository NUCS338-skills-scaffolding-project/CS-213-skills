# logic.py — Reusable skill logic
# Make it modular so other teams can import it

# logic.py — Reusable skill logic



def _has_actionable_step(text: str) -> bool:
    """
    Heuristic check: does the response already contain an action?
    """
    action_indicators = [
        "try this",
        "your turn",
        "now you",
        "go ahead and",
        "write",
        "solve",
        "test this",
    ]
    text_lower = text.lower()
    return any(indicator in text_lower for indicator in action_indicators)


def _infer_next_step(context: dict) -> str:
    """
    Generate a simple, concrete next step based on context.
    """
    topic = context.get("topic", "the concept")
    student_state = context.get("student_state", "learning")

    if student_state == "confused":
        return f"Try explaining {topic} in your own words in 2–3 sentences."
    elif student_state == "partial":
        return f"Try one practice problem using {topic} to reinforce it."
    elif student_state == "advanced":
        return f"Apply {topic} to a slightly harder example or edge case."
    else:
        return f"Write one quick example that uses {topic}."


def _append_next_step(response: str, next_step: str) -> str:
    """
    Cleanly append the next step to the response.
    """
    return response.rstrip() + "\n\nNext step: " + next_step


def run(input: dict):
    """
    Main entry point for this skill.

    Expected input:
    {
        "response": str,          # current tutor response
        "context": {
            "topic": str,
            "student_state": str  # "confused" | "partial" | "advanced"
        }
    }
    """
    response = input.get("response", "")
    context = input.get("context", {})

    # Step 1: Check if already actionable
    if _has_actionable_step(response):
        return {
            "modified": False,
            "response": response
        }

    # Step 2: Generate next step
    next_step = _infer_next_step(context)

    # Step 3: Append it
    updated_response = _append_next_step(response, next_step)

    return {
        "modified": True,
        "response": updated_response,
        "next_step": next_step
    }

if __name__ == "__main__":
    test_input = {
        "response": "Loops repeat code blocks based on a condition.",
        "context": {
            "topic": "loops",
            "student_state": "partial"
        }
    }

    result = run(test_input)
    print(result)