## **Approach**

The solution uses a **heuristic-based analysis engine** to identify document structure without relying on large ML models, ensuring it is fast, lightweight, and works entirely offline.

The core logic follows these steps:
1.  **Metadata Extraction**: The `PyMuPDF` library parses the PDF to extract text blocks along with their rich metadata, including font size, font name, page number, and precise coordinates.
2.  **Style Clustering**: Text blocks are grouped by common stylistic properties (font size and name). This allows the algorithm to identify recurring styles used for headings.
3.  **Heuristic Filtering**: Styles that are very frequent are assumed to be body text and are filtered out, leaving a smaller set of candidate heading styles.
4.  **Hierarchical Ranking**: The remaining candidate styles are ranked to determine their heading level (H1, H2, H3). The primary ranking criterion is **font size (descending)**. The secondary criterion is **indentation (ascending)** to resolve ties.
5.  **Title and Outline Generation**: A special rule identifies the document title. The final outline is then constructed by iterating through the document and tagging text blocks that match the identified heading styles.

This approach is inherently **language-agnostic**, as it relies on visual structure rather than natural language content, making it suitable for multilingual documents (e.g., Japanese).

## **Libraries Used**

* **`PyMuPDF`**: A high-performance Python library for data extraction from PDF documents.
* **No ML models** are used to comply with the size and performance constraints.

## **How to Build and Run**

The entire solution is containerized with Docker.

### **Prerequisites**
* [Docker](https://www.docker.com/get-started) installed.

### **1. Build the Docker Image**
Navigate to the root directory of the project (where the `Dockerfile` is located) and run:
```bash
docker build --platform linux/amd64 -t pdf-outliner:latest .
```

### **2. Prepare Input/Output Directories**
Create two directories on your host machine:
* `input`: Place your PDF files here.
* `output`: The resulting JSON files will be saved here.

### **3. Run the Container**
Execute the following command, replacing `$(pwd)` with the absolute path to your current directory if needed:
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-outliner:latest
```
The container will automatically process all PDFs in `/app/input` and place the corresponding JSON files in `/app/output` before exiting.
