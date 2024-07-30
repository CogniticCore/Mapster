![36 1](https://github.com/user-attachments/assets/9b87e166-19f4-4e5a-bd27-d4cddb890e87)
[<p align="center"><img alt="alt_text" width="80px" src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/YouTube_full-color_icon_%282017%29.svg/1280px-YouTube_full-color_icon_%282017%29.svg.png" /></p>](https://www.youtube.com/watch?v=lVltFC7K8sY)
# API Documentation for Learning Roadmap Generator

## Solution Description

The Learning Roadmap Generator API creates personalized learning roadmaps for users based on their desired topics. The API leverages OpenAI for topic generation, Serper for web resource recommendations, and various graph algorithms for optimizing the learning path. Key functionalities include generating a learning roadmap, expanding nodes, merging graphs, retrieving resources, applying PageRank, and converting graphs to trees.

## Setup Instructions

### Prerequisites

- Python 3.7+
- pip
- Virtual environment

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/CogniticCore/Mapster
   cd ROADMAP_PLANNER_API
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables. Create a `.env` file in the root directory and add your API keys:
   ```bash
   OPENAI_API_KEY=<your_openai_api_key>
   SERPER_API_KEY=<your_serper_api_key>
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API User Guide

### Endpoints

#### `GET /graph/full`
Generate a full learning roadmap with all cleaning and ranking steps.

[![Thumbnail](https://i.ytimg.com/an_webp/lVltFC7K8sY/mqdefault_6s.webp?du=3000&sqp=CKDKpbUG&rs=AOn4CLDeU9ErtGQxAtdlHDuPdj2e-YZBzw)](https://www.youtube.com/watch?v=lVltFC7K8sY)

##### Parameters

- `openai_api_key` (str): OpenAI API key.
- `serper_api_key` (str): Serper API key.
- `prompt` (str): The prompt for the LLM.
- `depth` (int): The depth of the roadmap. Default is 3.
- `retries` (int): The number of retries for the LLM call. Default is 2.

##### Responses

- `200 OK`: Returns the cleaned and ranked learning roadmap.
- `422 Unprocessable Entity`: Validation error.

##### Example

```bash
curl -X 'GET' \
  'http://mapster-cogniticcore.onrender.com/graph/full?openai_api_key=<OPENAI_API_KEY>&serper_api_key=<SERPER_API_KEY>&prompt=Learn+Python&depth=3&retries=2' \
  -H 'accept: application/json'
```

#### `POST /graph/expandnode`
Expand a specific node in the roadmap.

##### Parameters

- `openai_api_key` (str): OpenAI API key.
- `serper_api_key` (str): Serper API key.
- `upload_file` (UploadFile): The uploaded roadmap file.
- `depth` (int): The depth of the roadmap. Default is 3.
- `retries` (int): The number of retries for the LLM call. Default is 2.
- `target_node` (str): The ID of the target node to expand.

##### Responses

- `200 OK`: Returns the expanded learning roadmap.
- `422 Unprocessable Entity`: Validation error.

##### Example

```bash
curl -X 'POST' \
  'http://mapster-cogniticcore.onrender.com/graph/ExpandNode?openai_api_key=<OPENAI_API_KEY>&serper_api_key=<SERPER_API_KEY>&depth=3&retries=2&target_node=node1' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'upload_file=@path_to_your_file.json'
```

#### `GET /graph`
Generate a learning roadmap.

##### Parameters

- `openai_api_key` (str): OpenAI API key.
- `prompt` (str): The prompt for the LLM.
- `depth` (int): The depth of the roadmap. Default is 3.
- `retries` (int): The number of retries for the LLM call. Default is 2.

##### Responses

- `200 OK`: Returns the generated learning roadmap.
- `422 Unprocessable Entity`: Validation error.

##### Example

```bash
curl -X 'GET' \
  'http://mapster-cogniticcore.onrender.com/graph?openai_api_key=<OPENAI_API_KEY>&prompt=Learn+Python&depth=3&retries=2' \
  -H 'accept: application/json'
```

#### `POST /mergegraph`
Merge nodes in the roadmap to remove redundancy.

##### Parameters

- `openai_api_key` (str): OpenAI API key.
- `upload_file` (UploadFile): The uploaded roadmap file.
- `retries` (int): The number of retries for the LLM call. Default is 2.

##### Responses

- `200 OK`: Returns the roadmap with redundant nodes removed.
- `422 Unprocessable Entity`: Validation error.

##### Example

```bash
curl -X 'POST' \
  'http://mapster-cogniticcore.onrender.com/mergegraph?openai_api_key=<OPENAI_API_KEY>&retries=2' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'upload_file=@path_to_your_file.json'
```

#### `POST /graph/resources`
Get recommended resources for the roadmap.

##### Parameters

- `serper_api_key` (str): Serper API key.
- `upload_file` (UploadFile): The uploaded roadmap file.
- `retries` (int): The number of retries for the LLM call. Default is 2.

##### Responses

- `200 OK`: Returns the roadmap with recommended resources.
- `422 Unprocessable Entity`: Validation error.

##### Example

```bash
curl -X 'POST' \
  'http://mapster-cogniticcore.onrender.com/graph/resources?serper_api_key=<SERPER_API_KEY>&retries=2' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'upload_file=@path_to_your_file.json'
```

#### `POST /graph/pageranker`
Apply PageRank algorithm to the roadmap.

##### Parameters

- `upload_file` (UploadFile): The uploaded roadmap file.

##### Responses

- `200 OK`: Returns the roadmap with PageRank scores.
- `422 Unprocessable Entity`: Validation error.

##### Example

```bash
curl -X 'POST' \
  'http://mapster-cogniticcore.onrender.com/graph/pageranker' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'upload_file=@path_to_your_file.json'
```

#### `POST /graph/tree`
Convert a graph to a tree structure.

##### Parameters

- `upload_file` (UploadFile): The uploaded roadmap file.

##### Responses

- `200 OK`: Returns the roadmap as a tree structure.
- `422 Unprocessable Entity`: Validation error.

##### Example

```bash
curl -X 'POST' \
  'http://mapster-cogniticcore.onrender.com/graph/tree' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'upload_file=@path_to_your_file.json'
```

#### `POST /graphranking`
Sort the roadmap by PageRank scores.

##### Parameters

- `upload_file` (UploadFile): The uploaded roadmap file.

##### Responses

- `200 OK`: Returns the sorted roadmap.
- `422 Unprocessable Entity`: Validation error.

##### Example

```bash
curl -X 'POST' \
  'http://mapster-cogniticcore.onrender.com/graphranking' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'upload_file=@path_to_your_file.json'
```

## Input/Output Details

### Input Data

- **openai_api_key**: OpenAI API key for generating topics.
- **serper_api_key**: Serper API key for web search recommendations.
- **prompt**: The prompt for generating the learning roadmap.
- **depth**: The depth of the roadmap to generate.
- **retries**: The number of retries for API calls.
- **upload_file**: JSON file containing the roadmap graph.
- **target_node**: The ID of the target node to expand.

### Output Data

- **Learning Roadmap**: JSON object representing the learning roadmap with nodes and edges.
- **Recommended Resources**: JSON object with web resources related to the topics.
- **PageRank Scores**: JSON object with nodes ranked based on PageRank algorithm.
- **Converted Tree**: JSON object representing the roadmap as a tree structure.
- **Ranked Roadmap**: JSON object with nodes ranked based on various attributes.

# Contributors

- Front End Developer: [https://github.com/hisunedayo](Hisunedayo🦊)
- Back End Developer: [https://github.com/34RTHY](34RTHY🌏)
- AI Developers: [https://github.com/tonpia](tonpia🎍)
