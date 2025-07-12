import csv

def read_csv(filename):
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def append_csv(filename, row):
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(row)

def get_clients_for_therapist(therapist_email):
    """
    Return a list of all users with role 'client' whose therapist_email matches.
    """
    users = read_csv('users.csv')
    return [
        u for u in users
        if u.get('role') == 'client' and u.get('therapist_email') == therapist_email
    ]

def assign_client_to_therapist(client_email, therapist_email):
    """
    Set the therapist_email of the given client to this therapist.
    Returns True if assignment was made, False otherwise.
    """
    users = read_csv('users.csv')
    updated = False

    for u in users:
        if u.get('email') == client_email and u.get('role') == 'client':
            if u.get('therapist_email') != therapist_email:
                u['therapist_email'] = therapist_email
                updated = True
            break

    if updated:
        # overwrite users.csv with the updated list
        with open('users.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "role","email","password","first_name","last_name","therapist_email","mantra"
            ])
            writer.writeheader()
            writer.writerows(users)
        return True

    return False

# New helper functions for client management and mantra updates
def get_user_by_email(email):
    """
    Return a single user dict matching the provided email, or None if not found.
    """
    users = read_csv('users.csv')
    return next((u for u in users if u.get('email') == email), None)

def update_user_mantra(client_email, mantra):
    """
    Update the 'mantra' field for the given client.
    Returns True if update was successful, False otherwise.
    """
    users = read_csv('users.csv')
    updated = False
    for u in users:
        if u.get('email') == client_email and u.get('role') == 'client':
            u['mantra'] = mantra
            updated = True
            break

    if updated:
        with open('users.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "role","email","password","first_name","last_name","therapist_email","mantra"
            ])
            writer.writeheader()
            writer.writerows(users)
    return updated