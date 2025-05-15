# Peer-to-Peer Lending Platform - Simplified Console App

import csv
import os
from datetime import datetime, timedelta
import uuid

# File paths
data_folder = 'data'
users_file = os.path.join(data_folder, 'users.csv')
loans_file = os.path.join(data_folder, 'loans.csv')
repayments_file = os.path.join(data_folder, 'repayments.csv')

# Ensure data folder exists
os.makedirs(data_folder, exist_ok=True)

# Initialize CSV files if they don't exist
def init_csv(file_path, headers):
    if not os.path.exists(file_path):
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

init_csv(users_file, ['user_id', 'name', 'role'])
init_csv(loans_file, ['loan_id', 'borrower_id', 'amount', 'interest_rate', 'duration', 'status'])
init_csv(repayments_file, ['loan_id', 'investor_id', 'monthly_payment', 'due_date', 'paid'])

# Helper functions
def generate_id():
    return str(uuid.uuid4())[:8]

def load_csv(file_path):
    with open(file_path, 'r') as f:
        return list(csv.DictReader(f))

def write_csv(file_path, data, headers):
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

def append_csv(file_path, row):
    with open(file_path, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        writer.writerow(row)

# Business logic

def register_user():
    name = input("Enter your name: ")
    role = input("Role (borrower/investor): ").lower()
    if role not in ['borrower', 'investor']:
        print("Invalid role.")
        return
    user_id = generate_id()
    append_csv(users_file, {'user_id': user_id, 'name': name, 'role': role})
    print(f"✅ User '{name}' registered with ID: {user_id}")

def list_loan():
    borrower_id = input("Enter your user ID: ")
    users = load_csv(users_file)
    if not any(u['user_id'] == borrower_id and u['role'] == 'borrower' for u in users):
        print("❌ Invalid borrower ID.")
        return
    amount = float(input("Loan amount (R): "))
    rate = float(input("Interest rate (%): "))
    duration = int(input("Duration (months): "))
    loan_id = generate_id()
    append_csv(loans_file, {
        'loan_id': loan_id,
        'borrower_id': borrower_id,
        'amount': amount,
        'interest_rate': rate,
        'duration': duration,
        'status': 'open'
    })
    print(f"📌 Loan listed with ID: {loan_id}")

def view_loans():
    loans = [l for l in load_csv(loans_file) if l['status'] == 'open']
    if not loans:
        print("No open loans available.")
        return
    print("\n📊 Open Loans:")
    for loan in loans:
        print(f"ID: {loan['loan_id']}, Amount: R{loan['amount']}, Rate: {loan['interest_rate']}%, Duration: {loan['duration']} months")

def invest():
    investor_id = input("Enter your user ID: ")
    users = load_csv(users_file)
    if not any(u['user_id'] == investor_id and u['role'] == 'investor' for u in users):
        print("❌ Invalid investor ID.")
        return
    view_loans()
    loan_id = input("Enter Loan ID to invest in: ")
    loans = load_csv(loans_file)
    loan = next((l for l in loans if l['loan_id'] == loan_id and l['status'] == 'open'), None)
    if not loan:
        print("❌ Invalid loan ID.")
        return
    monthly_payment = round(float(loan['amount']) * (1 + float(loan['interest_rate']) / 100) / int(loan['duration']), 2)
    for i in range(int(loan['duration'])):
        due_date = (datetime.today() + timedelta(days=30 * (i + 1))).strftime('%Y-%m-%d')
        append_csv(repayments_file, {
            'loan_id': loan_id,
            'investor_id': investor_id,
            'monthly_payment': monthly_payment,
            'due_date': due_date,
            'paid': 'False'
        })
    # Mark loan as funded
    for l in loans:
        if l['loan_id'] == loan_id:
            l['status'] = 'funded'
    write_csv(loans_file, loans, loans[0].keys())
    print("💰 Investment successful! Repayments will be tracked monthly.")

def process_repayments():
    repayments = load_csv(repayments_file)
    today = datetime.today().strftime('%Y-%m-%d')
    updated = False
    for r in repayments:
        if r['due_date'] <= today and r['paid'] == 'False':
            r['paid'] = 'True'
            updated = True
            print(f"✅ Processed repayment of R{r['monthly_payment']} for Loan ID {r['loan_id']} to Investor {r['investor_id']}")
    if updated:
        write_csv(repayments_file, repayments, repayments[0].keys())
    else:
        print("No repayments due today.")

def investor_dashboard():
    investor_id = input("Enter your user ID: ")
    data = load_csv(repayments_file)
    total_expected = sum(float(r['monthly_payment']) for r in data if r['investor_id'] == investor_id)
    total_paid = sum(float(r['monthly_payment']) for r in data if r['investor_id'] == investor_id and r['paid'] == 'True')
    print(f"\n📈 Total Expected: R{total_expected:.2f}\n✅ Total Paid: R{total_paid:.2f}\n❌ Outstanding: R{total_expected - total_paid:.2f}")

# Main Menu

def menu():
    while True:
        print("\n🔁 P2P Lending Menu")
        print("1. Register User")
        print("2. List Loan (Borrower)")
        print("3. View Open Loans (Investor)")
        print("4. Invest in Loan")
        print("5. Process Monthly Repayments")
        print("6. Investor Dashboard")
        print("7. Exit")
        choice = input("Choose an option: ")
        if choice == '1':
            register_user()
        elif choice == '2':
            list_loan()
        elif choice == '3':
            view_loans()
        elif choice == '4':
            invest()
        elif choice == '5':
            process_repayments()
        elif choice == '6':
            investor_dashboard()
        elif choice == '7':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == '__main__':
    menu()

