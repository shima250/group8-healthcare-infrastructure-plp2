 SafeCycle

SafeCycle is a Python command-line application designed to help users track their menstrual cycles. It allows users to log period dates, predict future cycles, manage their records, and receive basic health tips. The application uses object-oriented programming and stores data in a database.

## Features

- Register a user
- Log period start dates
- Predict the next period
- Estimate the fertile window
- View cycle history
- Update existing records
- Delete records
- Display menstrual health tips
- Validate user input

## Technology Stack

- Python 3
- Object-Oriented Programming 
- SQLite
- MySQL (Aiven) with SQLite fallback


## Project Structure

SafeCycle/
├── main.py
├── models.py
├── db.py
├── validation.py
└── README.md




## Running the Application

Start the application by running:

python main.py


After registering, you will see the following menu:


1. Log a new period start date
2. View predicted next period
3. View cycle history
4. Update a logged entry
5. Delete a logged entry
6. View a health tip
7. Exit


