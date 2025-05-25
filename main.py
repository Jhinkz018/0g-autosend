#!/usr/bin/env python3
import sys
import os
import time
from web3 import Web3
from web3.exceptions import Web3RPCError

# -------------------------------
# Configuration and Chain Details
# -------------------------------
RPC_URL = "https://evmrpc-testnet.0g.ai/"
CHAIN_ID = 16600

# Define thresholds (in A0GI tokens)
MIN_BALANCE_THRESHOLD = 0.01  # Skip if wallet holds less than 0.01 A0GI
RESERVE_BALANCE = 0.005       # Reserve 0.001 A0GI for gas fees

# -------------------------------
# Helper Functions
# -------------------------------

def load_wallet_private_keys():
    """
    Loads private keys from a file located in the 'keys' folder.
    Each line in 'keys/private_keys.txt' should contain one private key.
    WARNING: Do not use real private keys in production.
    """
    keys_folder = "keys"
    keys_file = os.path.join(keys_folder, "private_keys.txt")
    try:
        with open(keys_file, "r") as f:
            keys = [line.strip() for line in f if line.strip()]
        if not keys:
            print(f"No keys found in {keys_file}.")
        return keys
    except Exception as e:
        print(f"Error loading private keys from {keys_file}: {e}")
        return []

def send_all_but_reserve(w3, private_key, target_address):
    """
    For a given wallet (identified by its private key), send the entire balance minus a reserved amount
    (0.001 A0GI) for gas fees to the target_address. If the wallet's balance is below 0.01 A0GI, it is skipped.
    Returns the transaction hash (hex string) if successful, otherwise None.
    """
    account = w3.eth.account.from_key(private_key)
    from_address = account.address

    # Get the wallet's balance (in wei)
    balance = w3.eth.get_balance(from_address)
    min_balance = w3.to_wei(MIN_BALANCE_THRESHOLD, 'ether')
    reserve_balance = w3.to_wei(RESERVE_BALANCE, 'ether')

    # Skip if balance is below threshold.
    if balance < min_balance:
        print(f"[{from_address}] Balance {w3.from_wei(balance, 'ether')} A0GI is below {MIN_BALANCE_THRESHOLD} A0GI. Skipping.")
        return None

    # Calculate the sendable amount.
    amount_to_send = balance - reserve_balance
    if amount_to_send <= 0:
        print(f"[{from_address}] Insufficient funds after reserving gas fee. Skipping.")
        return None

    # Get the current nonce (use 'pending' to account for unmined transactions).
    nonce = w3.eth.get_transaction_count(from_address, 'pending')

    # Build the transaction.
    tx = {
        'nonce': nonce,
        'to': target_address,
        'value': amount_to_send,
        'gas': 21000,
        'gasPrice': w3.eth.gas_price,
        'chainId': CHAIN_ID,
    }

    # Sign the transaction.
    signed_tx = w3.eth.account.sign_transaction(tx, private_key)

    # Attempt to send the transaction, retrying if "mempool is full" error occurs.
    retries = 3
    for attempt in range(retries):
        try:
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            return tx_hash.hex()
        except Web3RPCError as e:
            error_str = str(e)
            if "mempool is full" in error_str:
                print(f"[{from_address}] Mempool is full, waiting before retrying... (Attempt {attempt+1}/{retries})")
                time.sleep(5)
            else:
                print(f"[{from_address}] Transaction error: {error_str}")
                return None
    print(f"[{from_address}] Transaction failed due to mempool full after {retries} attempts.")
    return None

def check_wallet_balances(w3, wallet_keys):
    """
    Iterates through each wallet (by private key) and prints its A0GI balance.
    """
    for pk in wallet_keys:
        account = w3.eth.account.from_key(pk)
        balance = w3.eth.get_balance(account.address)
        print(f"Wallet {account.address} has {w3.from_wei(balance, 'ether')} A0GI tokens.")

def transfer_tokens(w3, wallet_keys):
    """
    Prompts the user for a target wallet address and then attempts to transfer tokens from all loaded wallets.
    """
    target_address = input("Enter the target wallet address: ").strip()
    if not target_address:
        print("Invalid target address. Operation cancelled.")
        return

    for pk in wallet_keys:
        tx_hash = send_all_but_reserve(w3, pk, target_address)
        if tx_hash:
            from_addr = w3.eth.account.from_key(pk).address
            print(f"Transaction sent from {from_addr}. Tx hash: {tx_hash}")
        # Short pause to avoid nonce conflicts.
        time.sleep(1)

def display_menu():
    """
    Displays the available choices to the user.
    """
    print("\nSelect an option:")
    print("1. Check Wallet Balances")
    print("2. Transfer Token")

def main():
    # Initialize Web3 connection.
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("ERROR: Unable to connect to the RPC endpoint.")
        sys.exit(1)
    print("Connected to 0g Newton Testnet.")

    # Load wallet private keys from external file.
    wallet_keys = load_wallet_private_keys()
    if not wallet_keys:
        sys.exit("No wallet keys loaded. Exiting.")

    # Main loop: allow multiple operations until the user opts out.
    while True:
        display_menu()
        choice = input("Enter your choice (1 or 2): ").strip()
        if choice == "1":
            print("\nChecking wallet balances...\n")
            check_wallet_balances(w3, wallet_keys)
        elif choice == "2":
            print("\nInitiating token transfer...\n")
            transfer_tokens(w3, wallet_keys)
        else:
            print("Invalid choice. Please select a valid option.")

        again = input("\nDo you want to perform another operation? (y/n): ").strip().lower()
        if again != "y":
            print("Exiting. Goodbye!")
            break

if __name__ == '__main__':
    main()