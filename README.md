# mockendpoint-python

A mock API server for managing quotations, built with FastAPI. This project is useful for testing, prototyping, and learning about RESTful APIs and content negotiation.

## Features
- List, add, update, and delete quotations
- Supports multiple response formats: JSON, CSV, XML, HTML, YAML
- Content negotiation via the `Accept` header
- Example of header-based filtering and query parameters

## Requirements
- Python 3.10+
- [FastAPI](https://fastapi.tiangolo.com/)
- [Uvicorn](https://www.uvicorn.org/)
- [PyYAML](https://pyyaml.org/)
- [uv](https://github.com/astral-sh/uv) (preferred for dependency management)

Install dependencies with:
```bash
uv sync
```
This will install all dependencies specified in `pyproject.toml`.

## Running the Server
To start the server locally:
```bash
python main.py
```
The server will run on [http://localhost:3000](http://localhost:3000).

## API Endpoints

### `GET /quotations`
- **Description:** Retrieve a list of quotations.
- **Query Parameters:**
  - `quotationOnly` (bool, optional): If true, only the text of each quotation is returned.
- **Headers:**
  - `X-Client-Type`: `mobile` or `laptop` (default: `laptop`). If `mobile`, only the first 3 quotations are returned.
- **Response:** List of quotations in the requested format.

### `POST /quotations`
- **Description:** Add a new quotation.
- **Body:**
  - `text` (string, required)
  - `author` (string, required)
- **Response:** The created quotation object.

### `GET /quotations/{quote_id}`
- **Description:** Retrieve a specific quotation by ID.
- **Query Parameters:**
  - `quotationOnly` (bool, optional): If true, only the text is returned.
- **Response:** The quotation object or text.

### `PUT /quotations/{quote_id}`
- **Description:** Update an existing quotation.
- **Body:**
  - `text` (string, required)
  - `author` (string, required)
- **Response:** The updated quotation object.

### `DELETE /quotations/{quote_id}`
- **Description:** Delete a quotation by ID.
- **Response:** The deleted quotation object.

## Content Negotiation
Set the `Accept` header to specify the response format:
- `application/json` (default)
- `text/csv`
- `application/xml`
- `text/html`
- `application/x-yaml`

Example:
```bash
curl -H "Accept: text/csv" http://localhost:3000/quotations
```

## Development Notes
- Python version is pinned to 3.10 (see `.python-version`).
- Virtual environments and Python cache files are ignored via `.gitignore`.
- All code is in `main.py`.
- To add more endpoints or formats, edit `main.py`.

## License
MIT (add your license here)
