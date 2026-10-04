from app.processors.chunker import split_text

text = """
KnowledgeBot is an AI-powered chat application designed to answer
questions using information provided by users.

Users can upload documents such as PDF, DOCX, and TXT files.
The Document Service is responsible for receiving these files,
saving them to the server, and extracting their text.

After the text has been extracted, the document is processed
before it can be used by the KnowledgeBot system.

The extracted text is divided into smaller chunks. Chunking is
important because very large documents should not be treated as
one single piece of information.

Each chunk contains a smaller portion of the original document.
The chunks can later be converted into numerical representations
called embeddings.

Embeddings allow the system to compare the meaning of a user's
question with the meaning of document chunks.

When a user asks a question, the system can search for the most
relevant chunks instead of sending the entire document to the
language model.

This process is an important part of Retrieval Augmented
Generation, commonly called RAG.

RAG allows KnowledgeBot to retrieve relevant information from
uploaded documents before generating an answer.

For example, if a user uploads a company policy document and asks
about the leave policy, KnowledgeBot can retrieve the chunks
containing information about employee leave and use those chunks
to generate an answer.

This makes the system more useful for document-based question
answering.

"""

chunks = split_text(text)

print("Number of chunks:", len(chunks))

for i, chunk in enumerate(chunks, start=1):

    print(f"\n----- CHUNK {i} -----")
    print(chunk)
