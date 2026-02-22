from rag.detection_pipeline import generate_ppd_score

if __name__ == "__main__":
    user_input = (
        "I feel exhausted all the time since giving birth. "
        "I cry for no reason, feel disconnected from my baby, "
        "and I barely sleep even when the baby is asleep."
    )

    result, sources = generate_ppd_score(user_input)

    print("PPD DETECTION RESULT:\n", result)
    print("\nSOURCES USED:")
    for s in sources:
        print(s["meta"], "score=", s["score"])