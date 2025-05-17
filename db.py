users = {}
wallets = {}
referrals = {}
bonuses = {}
withdraw_requests = []

def add_user(user_id, ref_id=None):
    if user_id not in users:
        users[user_id] = {"balance": 0}
        if ref_id and ref_id != user_id and ref_id in users:
            users[ref_id]["balance"] += 25
            referrals.setdefault(ref_id, []).append(user_id)
            bonuses[user_id] = 25

def get_balance(user_id):
    return users.get(user_id, {}).get("balance", 0)

def get_referrals(user_id):
    return referrals.get(user_id, [])

def get_bonus(user_id):
    return bonuses.get(user_id, 0)

def request_withdraw(user_id):
    if get_balance(user_id) >= 500:
        withdraw_requests.append(user_id)
        return True
    return False

def set_wallet(user_id, address):
    wallets[user_id] = address

def get_wallet(user_id):
    return wallets.get(user_id)
