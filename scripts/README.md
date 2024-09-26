# PSL Auction System

## Overview

The PSL Auction System is a C++ application designed to facilitate an auction for cricket players in the Pakistan Super League (PSL). It allows team managers to log in, view players from different categories, and place bids on players. The system also provides an administrative interface for managing teams and players.

## Features

- **User Authentication**: Login for team managers and admin.
- **Player Management**: Admin can add, delete, and manage players.
- **Bidding System**: Team managers can bid on players from various categories (Batsmen, Bowlers, All-Rounders).
- **Data Persistence**: Player and team information is stored in text files.

## Project Structure

```plaintext
temp_repo/
├── PSL Auction System/
│   ├── ATeam.cpp
│   ├── ATeam.h
│   ├── admin.cpp
│   ├── admin.h
│   ├── allrounders.cpp
│   ├── allrounders.h
│   ├── batsmen.cpp
│   ├── batsmen.h
│   ├── bowlers.cpp
│   ├── bowlers.h
│   ├── main.cpp
│   ├── players.cpp
│   ├── players.h
│   ├── teams.txt
│   ├── players.txt
│   ├── batsmen.txt
│   ├── bowlers.txt
│   ├── allrounders.txt
├── Sln file (visual studio)/
│   ├── Project3.sln
│   ├── Readme.txt
└── .git/
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/hamza-amin-4365/OOP_PSL_Auction.git
   ```

2. Navigate to the project directory:
   ```bash
   cd OOP_PSL_Auction
   ```

3. Open the solution file in Visual Studio: `Project3.sln`.

4. Build the project and run the `main.cpp` file.

## Usage

### Admin Functions
- **Add Team**: Admin can add a new team with a name and budget.
- **Delete Team**: Admin can delete an existing team.
- **Add Player**: Admin can add players to the auction system.

### Team Manager Functions
- **Login**: Managers can log in using their credentials.
- **Bidding**: Managers can bid on players during the auction.

### Player Categories
- Batsmen
- Bowlers
- All-Rounders

Each player type has its own dedicated file for managing player data.

## Contributing

Contributions are welcome! Please fork this repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For any inquiries, please contact Hamza Amin at [mh4070685@gmail.com](mailto:mh4070685@gmail.com).

## Acknowledgments

- This project was developed as part of a coursework assignment for Object-Oriented Programming.