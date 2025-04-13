# Python SQLite Project

This project is a simple application that uses SQLite for data storage. It provides a basic framework for performing CRUD (Create, Read, Update, Delete) operations on a SQLite database.

## Project Structure

```
python-sqlite-project
├── src
│   ├── app.py          # Main entry point of the application
│   └── db.py           # Database interaction functions
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
```

## Setup Instructions

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd python-sqlite-project
   ```

2. **Install dependencies**:
   It is recommended to use a virtual environment. You can create one using:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
   Then install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. **Run the application**:
   Execute the main application file:
   ```
   python src/app.py
   ```

2. **Perform CRUD operations**:
   Follow the prompts in the application to create, read, update, or delete records in the SQLite database.

## License

This project is licensed under the MIT License - see the LICENSE file for details.