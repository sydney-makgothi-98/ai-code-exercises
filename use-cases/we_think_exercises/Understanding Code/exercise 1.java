class UserManager {
    private List<User> users;
    private DBConn database;

    public UserManager(DBConn databaseConnection) {
        database = databaseConnection;
        users = new ArrayList<>();
    }

    public boolean registerUser(String username, String password, String email) {
        if (username.length() < 3 || password.length() < 8 || !email.contains("@")) {
            return false;
        }

        for (User user : users) {
            if (user.getUsername().equals(username)) {
                return false;
            }
        }

        User newUser = new User(username, password, email);
        users.add(newUser);
        boolean inserted = database.execute("INSERT INTO users VALUES ('" + username + "', '" + password + "', '" + email + "')");
        return inserted;
    }

    public User findUserByUsername(String username) {
        for (User user : users) {
            if (user.getUsername().equals(username)) {
                return user;
            }
        }
        return null;
    }
}

class User {
    private String username;
    private String password;
    private String email;

    public User(String username, String password, String email) {
        this.username = username;
        this.password = password;
        this.email = email;
    }

    public String getUsername() { return username; }
    public String getPassword() { return password; }
    public String getEmail() { return email; }
}