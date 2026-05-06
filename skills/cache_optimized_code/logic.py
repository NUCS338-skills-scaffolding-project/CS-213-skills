# logic.py — Cache Locality Tutor (TA-style)

def analyze_access_pattern(code: str):
    """
    Very simple heuristic to detect row-major vs column-major access.
    (Can be improved later)
    """
    code = code.replace(" ", "")

    # Detect patterns like arr[i][j] vs arr[j][i]
    if "[i][j]" in code:
        return "row-major-friendly"
    elif "[j][i]" in code:
        return "column-major-unfriendly"
    else:
        return "unknown"


def guided_response(pattern):
    """
    Socratic TA-style questioning
    """
    if pattern == "column-major-unfriendly":
        return (
            "🤔 Let's think about this together:\n"
            "How is your array being accessed here—row by row or column by column?\n\n"
            "💡 Hint: In C, arrays are stored row-wise in memory.\n"
            "What do you think happens if we access elements far apart in memory?\n"
        )

    elif pattern == "row-major-friendly":
        return (
            "Nice—your access pattern looks sequential in memory 👀\n"
            "Why do you think accessing neighboring elements might be faster?\n"
            "Think about how cache loads data in chunks (cache lines)."
        )

    else:
        return (
            "Can you describe how your loop is accessing memory?\n"
            "Are elements being accessed next to each other, or jumping around?\n"
        )


def hint_response(pattern):
    """
    Gives a stronger hint but not full answer
    """
    if pattern == "column-major-unfriendly":
        return (
            "⚠️ It looks like your code may be accessing memory column-wise.\n"
            "Since C uses row-major order, this can cause cache misses.\n\n"
            "👉 Try switching the loop order—what happens if you iterate over rows first?"
        )

    elif pattern == "row-major-friendly":
        return (
            "✅ Your access pattern aligns well with memory layout.\n"
            "This likely improves spatial locality and reduces cache misses."
        )

    else:
        return (
            "Try examining your loop order and how indices are used.\n"
            "Efficient code usually accesses memory sequentially."
        )


def explain_response(pattern):
    """
    Full explanation (teaching mode)
    """
    if pattern == "column-major-unfriendly":
        return (
            "📚 Explanation:\n"
            "C stores 2D arrays in row-major order, meaning rows are contiguous in memory.\n"
            "If you access elements column-by-column (e.g., arr[j][i]), you jump across memory.\n"
            "This leads to poor spatial locality and frequent cache misses.\n\n"
            "💡 Optimization idea:\n"
            "Reorder your loops so that the inner loop accesses contiguous elements (row-wise)."
        )

    elif pattern == "row-major-friendly":
        return (
            "📚 Explanation:\n"
            "Your code accesses memory sequentially (row-wise), which aligns with how arrays are stored in C.\n"
            "This improves spatial locality because nearby elements are loaded into cache together.\n\n"
            "✅ This is cache-friendly!"
        )

    else:
        return (
            "📚 General concept:\n"
            "Cache performance depends on how memory is accessed.\n"
            "Sequential access improves spatial locality, while scattered access increases cache misses."
        )


def run(input):
    """
    Main entry point for the Cache Locality Tutor
    :param input: dict with keys:
        - code: str (required)
        - mode: str ("guided", "hint", "explain") optional
    :return: TA-style response
    """
    code = input.get("code", "")
    mode = input.get("mode", "guided")

    if not code:
        return "Please provide a code snippet to analyze."

    pattern = analyze_access_pattern(code)

    if mode == "guided":
        return guided_response(pattern)
    elif mode == "hint":
        return hint_response(pattern)
    elif mode == "explain":
        return explain_response(pattern)
    else:
        return "Invalid mode. Use 'guided', 'hint', or 'explain'."