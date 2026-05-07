# ============================================
# ATM MANAGEMENT SYSTEM
# ============================================

import os
from datetime import datetime

# ==========================================
# GLOBAL VARIABLES
# ==========================================

accounts = []
transactions = []
ACCOUNTS_FILE = "accounts.txt"
TRANSACTIONS_FILE = "transactions.txt"
current_user = None

# Transaction limits
DEPOSIT_MIN = 100
DEPOSIT_MAX = 50000
WITHDRAW_MIN = 100
WITHDRAW_MAX = 20000
MIN_BALANCE = 500


# ==========================================
# FILE HANDLING FUNCTIONS
# ==========================================

def load_accounts():
    """Load all accounts from file"""
    global accounts
    try:
        if os.path.exists(ACCOUNTS_FILE):
            with open(ACCOUNTS_FILE, 'r') as file:
                accounts = []
                for line in file:
                    line = line.strip()
                    if line:
                        parts = line.split(',')
                        account = {
                            'account_no': parts[0],
                            'name': parts[1],
                            'pin': parts[2],
                            'balance': float(parts[3]),
                            'status': parts[4],
                            'failed_attempts': int(parts[5])
                        }
                        accounts.append(account)
            print(f"✅ {len(accounts)} accounts loaded.\n")
        else:
            print("📁 No existing accounts file. Starting fresh!\n")
    except Exception as e:
        print(f"❌ Error loading accounts: {e}\n")


def save_accounts():
    """Save all accounts to file"""
    try:
        with open(ACCOUNTS_FILE, 'w') as file:
            for acc in accounts:
                file.write(f"{acc['account_no']},{acc['name']},{acc['pin']},{acc['balance']},{acc['status']},{acc['failed_attempts']}\n")
    except Exception as e:
        print(f"❌ Error saving accounts: {e}\n")


def load_transactions():
    """Load all transactions from file"""
    global transactions
    try:
        if os.path.exists(TRANSACTIONS_FILE):
            with open(TRANSACTIONS_FILE, 'r') as file:
                transactions = []
                for line in file:
                    line = line.strip()
                    if line:
                        parts = line.split(',')
                        transaction = {
                            'trans_id': parts[0],
                            'account_no': parts[1],
                            'type': parts[2],
                            'amount': float(parts[3]),
                            'balance_after': float(parts[4]),
                            'datetime': parts[5]
                        }
                        transactions.append(transaction)
            print(f"✅ {len(transactions)} transactions loaded.\n")
        else:
            print("📁 No existing transactions file.\n")
    except Exception as e:
        print(f"❌ Error loading transactions: {e}\n")


def save_transaction(trans):
    """Save a single transaction"""
    try:
        with open(TRANSACTIONS_FILE, 'a') as file:
            file.write(f"{trans['trans_id']},{trans['account_no']},{trans['type']},{trans['amount']},{trans['balance_after']},{trans['datetime']}\n")
        transactions.append(trans)
    except Exception as e:
        print(f"❌ Error saving transaction: {e}\n")


# ==========================================
# ACCOUNT MANAGEMENT FUNCTIONS
# ==========================================

def generate_account_number():
    """Generate unique account number"""
    if not accounts:
        return "1001"
    else:
        last_acc_no = int(accounts[-1]['account_no'])
        return str(last_acc_no + 1)


def generate_transaction_id():
    """Generate unique transaction ID"""
    if not transactions:
        return "T0001"
    else:
        last_trans_id = transactions[-1]['trans_id']
        num = int(last_trans_id[1:]) + 1
        return f"T{num:04d}"


def create_account():
    """Create new account"""
    print("\n" + "="*50)
    print("🆕 CREATE NEW ACCOUNT")
    print("="*50)
    
    try:
        name = input("\nEnter your name: ").strip()
        if not name:
            print("❌ Name cannot be empty!\n")
            return
        
        # PIN input and validation
        pin = input("Enter 4-digit PIN: ").strip()
        if not validate_pin(pin):
            print("❌ PIN must be exactly 4 digits!\n")
            return
        
        confirm_pin = input("Confirm PIN: ").strip()
        if pin != confirm_pin:
            print("❌ PINs do not match!\n")
            return
        
        # Initial deposit
        initial_deposit = float(input(f"Enter initial deposit (minimum ₹{MIN_BALANCE}): "))
        if initial_deposit < MIN_BALANCE:
            print(f"❌ Minimum deposit is ₹{MIN_BALANCE}!\n")
            return
        
        # Generate account number
        acc_no = generate_account_number()
        
        # Create account dictionary
        account = {
            'account_no': acc_no,
            'name': name,
            'pin': pin,
            'balance': initial_deposit,
            'status': 'active',
            'failed_attempts': 0
        }
        
        accounts.append(account)
        save_accounts()
        
        # Record transaction
        trans = {
            'trans_id': generate_transaction_id(),
            'account_no': acc_no,
            'type': 'opening',
            'amount': initial_deposit,
            'balance_after': initial_deposit,
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_transaction(trans)
        
        print("\n" + "="*50)
        print("✅ ACCOUNT CREATED SUCCESSFULLY!")
        print("="*50)
        print(f"Account Number: {acc_no}")
        print(f"Name: {name}")
        print(f"Initial Balance: ₹{initial_deposit:.2f}")
        print("\n⚠️  Please remember your Account Number and PIN!")
        print("="*50 + "\n")
        
    except ValueError:
        print("❌ Invalid input! Please enter correct values.\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")


def login():
    """User login"""
    global current_user
    
    print("\n" + "="*50)
    print("🔐 LOGIN TO YOUR ACCOUNT")
    print("="*50)
    
    try:
        acc_no = input("\nEnter Account Number: ").strip()
        
        # Find account
        account = get_account_by_number(acc_no)
        if not account:
            print("❌ Account not found!\n")
            return False
        
        # Check if account is locked
        if account['status'] == 'locked':
            print("❌ Account is locked due to multiple failed login attempts!")
            print("   Please contact bank administrator.\n")
            return False
        
        # PIN verification (3 attempts)
        attempts = 3
        while attempts > 0:
            pin = input(f"Enter PIN ({attempts} attempt(s) remaining): ").strip()
            
            if pin == account['pin']:
                # Successful login
                account['failed_attempts'] = 0
                save_accounts()
                current_user = account
                
                print("\n✅ Login Successful!")
                print(f"Welcome, {account['name']}! 🎉\n")
                return True
            else:
                attempts -= 1
                account['failed_attempts'] += 1
                
                if attempts > 0:
                    print(f"❌ Incorrect PIN! {attempts} attempt(s) remaining.\n")
                else:
                    print("❌ Account locked due to 3 failed attempts!\n")
                    account['status'] = 'locked'
                
                save_accounts()
        
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}\n")
        return False


def logout():
    """Logout current user"""
    global current_user
    if current_user:
        print(f"\n👋 Goodbye, {current_user['name']}!")
        print("Thank you for using our ATM! 🏦\n")
        current_user = None


# ==========================================
# BANKING OPERATIONS
# ==========================================

def check_balance():
    """Display current balance"""
    if not current_user:
        return
    
    print("\n" + "="*50)
    print("💰 ACCOUNT BALANCE")
    print("="*50)
    print(f"Account Number: {current_user['account_no']}")
    print(f"Account Holder: {current_user['name']}")
    print(f"Current Balance: ₹{current_user['balance']:.2f}")
    print("="*50 + "\n")


def deposit_money():
    """Deposit money"""
    if not current_user:
        return
    
    print("\n" + "="*50)
    print("📥 DEPOSIT MONEY")
    print("="*50)
    
    try:
        amount = float(input(f"\nEnter amount to deposit (₹{DEPOSIT_MIN} - ₹{DEPOSIT_MAX}): "))
        
        # Validation
        if not validate_amount(amount, DEPOSIT_MIN, DEPOSIT_MAX):
            print(f"❌ Amount must be between ₹{DEPOSIT_MIN} and ₹{DEPOSIT_MAX}!\n")
            return
        
        # Update balance
        current_user['balance'] += amount
        save_accounts()
        
        # Record transaction
        trans = {
            'trans_id': generate_transaction_id(),
            'account_no': current_user['account_no'],
            'type': 'deposit',
            'amount': amount,
            'balance_after': current_user['balance'],
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_transaction(trans)
        
        print("\n✅ Deposit Successful!")
        print(f"Deposited: ₹{amount:.2f}")
        print(f"New Balance: ₹{current_user['balance']:.2f}\n")
        
    except ValueError:
        print("❌ Invalid amount!\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")


def withdraw_money():
    """Withdraw money"""
    if not current_user:
        return
    
    print("\n" + "="*50)
    print("📤 WITHDRAW MONEY")
    print("="*50)
    print(f"Available Balance: ₹{current_user['balance']:.2f}")
    
    try:
        amount = float(input(f"\nEnter amount to withdraw (₹{WITHDRAW_MIN} - ₹{WITHDRAW_MAX}): "))
        
        # Validation
        if not validate_amount(amount, WITHDRAW_MIN, WITHDRAW_MAX):
            print(f"❌ Amount must be between ₹{WITHDRAW_MIN} and ₹{WITHDRAW_MAX}!\n")
            return
        
        # Check sufficient balance
        if current_user['balance'] - amount < MIN_BALANCE:
            print(f"❌ Insufficient balance! Minimum balance of ₹{MIN_BALANCE} must be maintained.\n")
            return
        
        # Update balance
        current_user['balance'] -= amount
        save_accounts()
        
        # Record transaction
        trans = {
            'trans_id': generate_transaction_id(),
            'account_no': current_user['account_no'],
            'type': 'withdraw',
            'amount': amount,
            'balance_after': current_user['balance'],
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_transaction(trans)
        
        print("\n✅ Withdrawal Successful!")
        print(f"Withdrawn: ₹{amount:.2f}")
        print(f"Remaining Balance: ₹{current_user['balance']:.2f}\n")
        
    except ValueError:
        print("❌ Invalid amount!\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")


def transfer_money():
    """Transfer money to another account"""
    if not current_user:
        return
    
    print("\n" + "="*50)
    print("💸 TRANSFER MONEY")
    print("="*50)
    print(f"Available Balance: ₹{current_user['balance']:.2f}")
    
    try:
        recipient_acc_no = input("\nEnter recipient account number: ").strip()
        
        # Find recipient
        recipient = get_account_by_number(recipient_acc_no)
        if not recipient:
            print("❌ Recipient account not found!\n")
            return
        
        if recipient['account_no'] == current_user['account_no']:
            print("❌ Cannot transfer to your own account!\n")
            return
        
        if recipient['status'] == 'locked':
            print("❌ Recipient account is locked!\n")
            return
        
        print(f"Recipient: {recipient['name']}")
        
        amount = float(input(f"Enter amount to transfer (₹{WITHDRAW_MIN} - ₹{WITHDRAW_MAX}): "))
        
        # Validation
        if not validate_amount(amount, WITHDRAW_MIN, WITHDRAW_MAX):
            print(f"❌ Amount must be between ₹{WITHDRAW_MIN} and ₹{WITHDRAW_MAX}!\n")
            return
        
        # Check sufficient balance
        if current_user['balance'] - amount < MIN_BALANCE:
            print(f"❌ Insufficient balance! Minimum balance of ₹{MIN_BALANCE} must be maintained.\n")
            return
        
        # Confirm transfer
        confirm = input(f"\nTransfer ₹{amount:.2f} to {recipient['name']}? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Transfer cancelled!\n")
            return
        
        # Perform transfer
        current_user['balance'] -= amount
        recipient['balance'] += amount
        save_accounts()
        
        # Record transactions (sender)
        trans_out = {
            'trans_id': generate_transaction_id(),
            'account_no': current_user['account_no'],
            'type': 'transfer_out',
            'amount': amount,
            'balance_after': current_user['balance'],
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_transaction(trans_out)
        
        # Record transaction (receiver)
        trans_in = {
            'trans_id': generate_transaction_id(),
            'account_no': recipient['account_no'],
            'type': 'transfer_in',
            'amount': amount,
            'balance_after': recipient['balance'],
            'datetime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_transaction(trans_in)
        
        print("\n✅ Transfer Successful!")
        print(f"Transferred: ₹{amount:.2f}")
        print(f"To: {recipient['name']} ({recipient_acc_no})")
        print(f"Your Balance: ₹{current_user['balance']:.2f}\n")
        
    except ValueError:
        print("❌ Invalid amount!\n")
    except Exception as e:
        print(f"❌ Error: {e}\n")


def transaction_history():
    """Show last 10 transactions"""
    if not current_user:
        return
    
    print("\n" + "="*70)
    print("📜 TRANSACTION HISTORY (Last 10 Transactions)")
    print("="*70)
    
    # Filter transactions for current user
    user_transactions = [t for t in transactions if t['account_no'] == current_user['account_no']]
    
    if not user_transactions:
        print("No transactions found.\n")
        return
    
    # Show last 10
    recent_trans = user_transactions[-10:]
    
    print(f"{'ID':<8} {'Type':<15} {'Amount':<12} {'Balance':<12} {'Date/Time':<20}")
    print("-"*70)
    
    for trans in reversed(recent_trans):
        print(f"{trans['trans_id']:<8} {trans['type']:<15} ₹{trans['amount']:<11.2f} ₹{trans['balance_after']:<11.2f} {trans['datetime']:<20}")
    
    print("="*70 + "\n")


def mini_statement():
    """Show last 5 transactions"""
    if not current_user:
        return
    
    print("\n" + "="*70)
    print("📄 MINI STATEMENT (Last 5 Transactions)")
    print("="*70)
    
    # Filter transactions for current user
    user_transactions = [t for t in transactions if t['account_no'] == current_user['account_no']]
    
    if not user_transactions:
        print("No transactions found.\n")
        return
    
    # Show last 5
    recent_trans = user_transactions[-5:]
    
    print(f"{'Type':<15} {'Amount':<12} {'Balance':<12} {'Date/Time':<20}")
    print("-"*70)
    
    for trans in reversed(recent_trans):
        print(f"{trans['type']:<15} ₹{trans['amount']:<11.2f} ₹{trans['balance_after']:<11.2f} {trans['datetime']:<20}")
    
    print("-"*70)
    print(f"Current Balance: ₹{current_user['balance']:.2f}")
    print("="*70 + "\n")


def change_pin():
    """Change account PIN"""
    if not current_user:
        return
    
    print("\n" + "="*50)
    print("🔒 CHANGE PIN")
    print("="*50)
    
    try:
        old_pin = input("\nEnter current PIN: ").strip()
        
        if old_pin != current_user['pin']:
            print("❌ Incorrect current PIN!\n")
            return
        
        new_pin = input("Enter new 4-digit PIN: ").strip()
        if not validate_pin(new_pin):
            print("❌ PIN must be exactly 4 digits!\n")
            return
        
        if new_pin == old_pin:
            print("❌ New PIN cannot be same as old PIN!\n")
            return
        
        confirm_pin = input("Confirm new PIN: ").strip()
        if new_pin != confirm_pin:
            print("❌ PINs do not match!\n")
            return
        
        # Update PIN
        current_user['pin'] = new_pin
        save_accounts()
        
        print("\n✅ PIN changed successfully!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}\n")


# ==========================================
# UTILITY FUNCTIONS
# ==========================================

def validate_pin(pin):
    """Check if PIN is exactly 4 digits"""
    return len(pin) == 4 and pin.isdigit()


def validate_amount(amount, min_amt, max_amt):
    """Validate transaction amount"""
    return min_amt <= amount <= max_amt


def get_account_by_number(acc_no):
    """Find account by account number"""
    for account in accounts:
        if account['account_no'] == acc_no:
            return account
    return None


# ==========================================
# MENU FUNCTIONS
# ==========================================

def show_main_menu():
    """Show main menu (before login)"""
    print("\n" + "="*50)
    print("🏦 ATM MANAGEMENT SYSTEM 🏦")
    print("="*50)
    print("1. 🆕 Create New Account")
    print("2. 🔐 Login to Account")
    print("3. ℹ️  About System")
    print("4. 🚪 Exit")
    print("="*50)


def show_atm_menu():
    """Show ATM menu (after login)"""
    print("\n" + "="*50)
    print(f"Welcome, {current_user['name']}!")
    print(f"Account: {current_user['account_no']}")
    print("="*50)
    print("1. 💰 Check Balance")
    print("2. 📥 Deposit Money")
    print("3. 📤 Withdraw Money")
    print("4. 💸 Transfer Money")
    print("5. 📜 Transaction History")
    print("6. 📄 Mini Statement")
    print("7. 🔒 Change PIN")
    print("8. 🚪 Logout")
    print("="*50)


def show_about():
    """Show about information"""
    print("\n" + "="*50)
    print("ℹ️  ABOUT ATM SYSTEM")
    print("="*50)
    print("Version: 1.0")
    print("Developed by: [Your Name]")
    print("\nFeatures:")
    print("• Account creation and management")
    print("• Secure PIN-based login")
    print("• Deposit and withdrawal")
    print("• Money transfer between accounts")
    print("• Transaction history tracking")
    print("• Mini statement generation")
    print("• PIN change facility")
    print("• Account locking after failed attempts")
    print("="*50 + "\n")


# ==========================================
# MAIN PROGRAM
# ==========================================

def main():
    """Main program function"""
    print("\n" + "="*50)
    print("🏦 WELCOME TO ATM MANAGEMENT SYSTEM 🏦")
    print("="*50)
    
    # Load data
    load_accounts()
    load_transactions()
    
    while True:
        try:
            if not current_user:
                # Main menu (not logged in)
                show_main_menu()
                choice = input("\nEnter your choice (1-4): ").strip()
                
                if choice == '1':
                    create_account()
                elif choice == '2':
                    login()
                elif choice == '3':
                    show_about()
                elif choice == '4':
                    print("\n👋 Thank you for using ATM System!")
                    print("Goodbye! 🏦\n")
                    break
                else:
                    print("❌ Invalid choice! Please select 1-4.\n")
            
            else:
                # ATM menu (logged in)
                show_atm_menu()
                choice = input("\nEnter your choice (1-8): ").strip()
                
                if choice == '1':
                    check_balance()
                elif choice == '2':
                    deposit_money()
                elif choice == '3':
                    withdraw_money()
                elif choice == '4':
                    transfer_money()
                elif choice == '5':
                    transaction_history()
                elif choice == '6':
                    mini_statement()
                elif choice == '7':
                    change_pin()
                elif choice == '8':
                    logout()
                else:
                    print("❌ Invalid choice! Please select 1-8.\n")
        
        except KeyboardInterrupt:
            print("\n\n⚠️ Program interrupted by user!")
            if current_user:
                logout()
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}\n")


# ==========================================
# PROGRAM START
# ==========================================

if __name__ == "__main__":
    main()


