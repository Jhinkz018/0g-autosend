# 0g-autosend

**0g-autosend** is a simple Python bot that automates sending all token balances from a list of wallets to a single main wallet address on the 0G Testnet V3.

It reads private keys from `pk.txt`, prompts for your main wallet address, and sends any available balance to that address.

---

## 🔧 Features

- Automatically sends from multiple wallets
- Private keys loaded from `pk.txt`
- Prompts for your main wallet address at runtime
- Built for 0G-Galileo-Testnet

---

## ✅ Requirements

- Python 3.7 or higher

---

## 📦 Full Setup (Copy & Paste)

```bash
# Clone the repo
git clone https://github.com/Jhinkz018/0g-autosend.git
cd 0g-autosend

# Install dependencies
pip install -r requirements.txt

# Create private key file
touch pk.txt

# Add private keys (one per line) to pk.txt
# Example:
# 0xabc123...
# 0xdef456...


🚀 How to Use

```python main.py```

You will be prompted:

Enter the main wallet address to receive all funds:
> 0xYourMainWalletAddress

🛡️ Warnings
Only use testnet private keys — this is not secure for mainnet use.

Make sure your private keys have OG tokens on the 0G testnet.

Sending may fail if there’s no gas or balance.

📄 License
MIT License — free to use, modify, and distribute.
