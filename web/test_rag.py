from rag.pipeline import generate_ai_reply

if __name__ == "__main__":
    reply, sources = generate_ai_reply("What is the capital of France?")
    print("REPLY:\n", reply)
    print("\nSOURCES USED:")
    for s in sources:
        print(s["meta"], "score=", s["score"])