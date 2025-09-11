erDiagram
    User {
        int id PK
        string email
        string avatar
        string phone
        string country
    }

    Client {
        int id PK
        string email
        string full_name
        text comment
        int owner_id FK
    }

    Message {
        int id PK
        string subject
        text body
        int owner_id FK
    }

    Mailing {
        int id PK
        datetime start_time
        datetime end_time
        string status
        int message_id FK
        int owner_id FK
    }

    Attempt {
        int id PK
        datetime attempt_time
        string status
        text server_response
        int mailing_id FK
    }

    User ||--o{ Client : owns
    User ||--o{ Message : owns
    User ||--o{ Mailing : owns
    Message ||--o{ Mailing : used_in
    Mailing }o--o{ Client : recipients
    Mailing ||--o{ Attempt : has