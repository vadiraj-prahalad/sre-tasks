from app.services.chunking_service import split_into_chunks


def main() -> None:
    text = " ".join([f"word{i}" for i in range(1, 301)])

    chunks = split_into_chunks(
        text,
        chunk_size=120,
        overlap=20,
    )

    print(f"Total chunks: {len(chunks)}")

    for index, chunk in enumerate(chunks):
        words = chunk.split()
        print("-" * 60)
        print(f"Chunk {index}")
        print(f"Word count: {len(words)}")
        print(f"Start word: {words[0]}")
        print(f"End word: {words[-1]}")


if __name__ == "__main__":
    main()
