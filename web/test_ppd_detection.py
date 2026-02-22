from rag.detection_pipeline import generate_ppd_score

if __name__ == "__main__":
    user_input = (
        "Based on the rag-index presented answer the PPD depression chance."
    )

    result, sources = generate_ppd_score(user_input)

    print("PPD DETECTION RESULT:\n", result)
    print("\nSOURCES USED:")
    for s in sources:
        print(s["meta"], "score=", s["score"])