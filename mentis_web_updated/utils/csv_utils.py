# CSV utility functions
import csv
import os

def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def append_csv(path, row):
    file_exists = os.path.isfile(path)
    with open(path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists or os.stat(path).st_size == 0:
            if path.endswith("users.csv"):
                writer.writerow(["role", "email", "password"])
            elif path.endswith("journal.csv"):
                writer.writerow(["entry_id", "user_email", "text", "datetime"])
            elif path.endswith("analysis.csv"):
                writer.writerow(["id", "user_email", "related_entry_ids", "sentiment", "summary", "date_span"])
        writer.writerow(row)

def get_clients_for_therapist(therapist_email):
    users = read_csv('users.csv')
    return [u for u in users if u['role'] == 'client' and u.get('therapist_email') == therapist_email]

def assign_client_to_therapist(client_email, therapist_email):
    users = read_csv('users.csv')
    updated = False
    for u in users:
        if u['role'] == 'client' and u['email'] == client_email:
            u['therapist_email'] = therapist_email
            updated = True
            break
    if updated:
        with open('users.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['role', 'email', 'password', 'therapist_email'])
            writer.writeheader()
            writer.writerows(users)
    return updated
