import streamlit as st
import pandas as pd
import sqlite3
import asyncio
import json
import websockets
import threading
import time
from datetime import datetime
from web3 import Web3
from pyvis.network import Network
import streamlit.components.v1 as components

# ==========================================
# 1. SYSTEM CONFIGURATION
# ==========================================
# Use your specific Alchemy API Key and Sepolia Contract Address
API_KEY = "Rb_74qoAC6_-Vhx3bWJVe" 
WSS_URL = f"wss://eth-sepolia.g.alchemy.com/v2/{API_KEY}"
RPC_URL = f"https://eth-sepolia.g.alchemy.com/v2/{API_KEY}"
CONTRACT_ADDR = "0x656663635368d4f28cD04fB1928460B8525a591c"

ABI = [
    {"inputs":[],"stateMutability":"nonpayable","type":"constructor"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"account","type":"address"},{"indexed":False,"internalType":"uint8","name":"level","type":"uint8"}],"name":"RiskLevelUpdated","type":"event"},
    {"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"from","type":"address"},{"indexed":True,"internalType":"address","name":"to","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"TransactionVerified","type":"event"},
    {"stateMutability":"payable","type":"fallback"},
    {"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"riskLevel","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},
    {"inputs":[{"internalType":"address payable","name":"_to","type":"address"}],"name":"secureTransfer","outputs":[],"stateMutability":"payable","type":"function"},
    {"inputs":[{"internalType":"address","name":"_account","type":"address"},{"internalType":"uint8","name":"_level","type":"uint8"}],"name":"setRiskLevel","outputs":[],"stateMutability":"nonpayable","type":"function"},
    {"stateMutability":"payable","type":"receive"}
]

w3 = Web3(Web3.HTTPProvider(RPC_URL))
contract_check = w3.to_checksum_address(CONTRACT_ADDR)
contract = w3.eth.contract(address=contract_check, abi=ABI)

# ==========================================
# 2. AUTONOMOUS ENFORCEMENT ENGINE
# ==========================================
def automated_risk_audit(addr, val, admin_p_key=None):
    conn = sqlite3.connect("coinEth_v2.db")
    c = conn.cursor()
    
    # Heuristic 1: Structuring Detection (Same amount frequency)
    c.execute("SELECT COUNT(*) FROM transactions WHERE from_a = ? AND value = ?", (addr, val))
    val_freq = c.fetchone()[0]
    
    # Heuristic 2: Velocity Auditing (Total transactions)
    c.execute("SELECT COUNT(*) FROM transactions WHERE from_a = ?", (addr,))
    total_tx = c.fetchone()[0]
    conn.close()

    target_level = 0
    risk_label = "Safe"
    
    if total_tx >= 10:
        target_level = 2
        risk_label = "🚨 AUTO-BLOCK: Excessive Velocity"
    elif val_freq >= 5:
        target_level = 1
        risk_label = "⚠️ WARNING: Structuring Pattern"
        
    # Autonomous On-Chain Escalation
    if admin_p_key and target_level > 0:
        try:
            current_onchain = contract.functions.riskLevel(w3.to_checksum_address(addr)).call()
            if target_level > current_onchain:
                admin = w3.eth.account.from_key(admin_p_key)
                # FIX: Use 'pending' to prevent "replacement transaction underpriced" errors
                nonce = w3.eth.get_transaction_count(admin.address, 'pending')
                
                tx = contract.functions.setRiskLevel(w3.to_checksum_address(addr), target_level).build_transaction({
                    'from': admin.address, 
                    'gas': 120000, 
                    'gasPrice': int(w3.eth.gas_price * 1.25), # 25% bump for priority
                    'nonce': nonce, 
                    'chainId': 11155111
                })
                signed = w3.eth.account.sign_transaction(tx, admin_p_key)
                w3.eth.send_raw_transaction(signed.raw_transaction) # Web3 v6 snake_case fix
        except Exception as e:
            print(f"Autonomous Enforcement Failed: {e}")
            
    return risk_label

# ==========================================
# 3. BACKGROUND BLOCKCHAIN LISTENER
# ==========================================
async def monitor_blockchain():
    async with websockets.connect(WSS_URL) as ws:
        sub = {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["alchemy_pendingTransactions"]}
        await ws.send(json.dumps(sub))
        while True:
            try:
                msg = await ws.recv()
                tx_data = json.loads(msg)['params']['result']
                val = float(int(tx_data.get('value', '0x0'), 16)) / 1e18
                f_addr = tx_data['from']
                t_addr = tx_data.get('to', "0x0000000000000000000000000000000000000000")
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Run forensic audit
                risk_status = automated_risk_audit(f_addr, val)
                
                conn = sqlite3.connect("coinEth_v2.db")
                conn.execute("INSERT OR IGNORE INTO transactions VALUES (?,?,?,?,?,?)",
                             (tx_data['hash'], f_addr, t_addr, val, risk_status, ts))
                conn.commit()
                conn.close()
            except:
                continue

if 'init_sys' not in st.session_state:
    conn = sqlite3.connect("coinEth_v2.db")
    conn.execute("CREATE TABLE IF NOT EXISTS transactions (hash TEXT PRIMARY KEY, from_a TEXT, to_a TEXT, value REAL, risk TEXT, timestamp TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS my_wallets (label TEXT PRIMARY KEY, address TEXT, p_key TEXT)")
    conn.commit()
    conn.close()
    threading.Thread(target=lambda: asyncio.run(monitor_blockchain()), daemon=True).start()
    st.session_state.init_sys = True

# ==========================================
# 4. DASHBOARD INTERFACE
# ==========================================
st.set_page_config(layout="wide", page_title="coinEth | Phase 2 Forensic Lab")
st.title("🛡️ coinEth: Forensic Surveillance & Automated Path Mapping")

with st.sidebar:
    st.header("📡 Infrastructure")
    if st.button("🔄 Clear Cache & Sync"):
        st.cache_data.clear()
        st.rerun()
    if w3.is_connected(): st.success("Connected to Sepolia")
    else: st.error("Connection Failed")

tab1, tab2, tab3 = st.tabs(["👑 Admin & Registry", "💸 Transaction Portal", "🕵️ Forensic Lab"])

# --- TAB 1: REGISTRY ---
with tab1:
    st.header("Managed Asset Registry")
    with st.expander("➕ Register Account Instance", expanded=False):
        c1, c2, c3 = st.columns(3)
        l_in = c1.text_input("Account Label (e.g., Admin, Suspect)")
        a_in = c2.text_input("Public Address")
        k_in = c3.text_input("Private Key", type="password")
        if st.button("Save Wallet"):
            if w3.is_address(a_in):
                conn = sqlite3.connect("coinEth_v2.db")
                conn.execute("INSERT OR REPLACE INTO my_wallets VALUES (?,?,?)", (l_in, w3.to_checksum_address(a_in), k_in))
                conn.commit()
                conn.close()
                st.rerun()

    st.divider()
    conn = sqlite3.connect("coinEth_v2.db")
    df_w = pd.read_sql_query("SELECT label, address FROM my_wallets", conn)
    conn.close()

    status_map = {0: "🟢 Safe", 1: "🟡 Warning", 2: "🔴 Frozen"}

    if not df_w.empty:
        for i, row in df_w.iterrows():
            m1, m2, m3, m4 = st.columns([1, 2, 1, 1])
            try:
                lv = contract.functions.riskLevel(w3.to_checksum_address(row['address'])).call()
                bal = w3.from_wei(w3.eth.get_balance(row['address']), 'ether')
            except:
                lv, bal = 0, 0
            
            m1.write(f"**{row['label']}**")
            m2.code(row['address'], language="text")
            m3.write(f"{bal:.4f} ETH")
            m4.write(f"**{status_map.get(lv, 'N/A')}**")
            
        st.divider()
        st.subheader("Manual Governance Interdiction")
        ad1, ad2 = st.columns(2)
        with ad1:
            adm_k = st.text_input("Master Admin Key", type="password")
            target = st.text_input("Target Address")
        with ad2:
            lv_choice = st.selectbox("Set Risk Level", [0, 1, 2], format_func=lambda x: status_map[x])
            if st.button("Broadcast Level Update"):
                try:
                    admin = w3.eth.account.from_key(adm_k)
                    nonce = w3.eth.get_transaction_count(admin.address, 'pending')
                    tx = contract.functions.setRiskLevel(w3.to_checksum_address(target), lv_choice).build_transaction({
                        'from': admin.address, 'gas': 120000, 'gasPrice': int(w3.eth.gas_price * 1.2), 'nonce': nonce, 'chainId': 11155111
                    })
                    signed = w3.eth.account.sign_transaction(tx, adm_k)
                    h = w3.eth.send_raw_transaction(signed.raw_transaction)
                    w3.eth.wait_for_transaction_receipt(h)
                    st.success("Governance Update Mined.")
                    st.rerun()
                except Exception as e: st.error(f"Governance Error: {e}")

# --- TAB 2: PORTAL ---
with tab2:
    st.header("Secure Transfer Portal")
    conn = sqlite3.connect("coinEth_v2.db")
    reg = pd.read_sql_query("SELECT * FROM my_wallets", conn)
    conn.close()

    if not reg.empty:
        choice = st.selectbox("Active Identity Session:", reg['label'])
        u = reg[reg['label'] == choice].iloc[0]
        u_lv = contract.functions.riskLevel(w3.to_checksum_address(u['address'])).call()
        
        if u_lv == 2: st.error("🛑 ACCESS DENIED: This account is FROZEN by coinEth Forensics.")
        else:
            if u_lv == 1: st.warning("⚠️ ATTENTION: Account is currently flagged for Structuring.")
            else: st.success("Authorized Session Active")
            
            t_addr = st.text_input("Recipient Public Address")
            val = st.number_input("Amount to Transfer (ETH)", 0.0001, format="%.5f")
            
            if st.button("🚀 Sign secureTransfer"):
                try:
                    # Run auto-block audit before signing to check thresholds
                    admin_row = reg[reg['label']=='Admin']
                    admin_pk = admin_row.iloc[0]['p_key'] if not admin_row.empty else None
                    automated_risk_audit(u['address'], val, admin_pk)
                    
                    nonce = w3.eth.get_transaction_count(u['address'], 'pending')
                    tx = contract.functions.secureTransfer(w3.to_checksum_address(t_addr)).build_transaction({
                        'from': u['address'], 'value': w3.to_wei(val, 'ether'), 'gas': 150000, 'gasPrice': w3.eth.gas_price, 'nonce': nonce, 'chainId': 11155111
                    })
                    signed = w3.eth.account.sign_transaction(tx, u['p_key'])
                    h = w3.eth.send_raw_transaction(signed.raw_transaction)
                    w3.eth.wait_for_transaction_receipt(h)
                    st.success(f"Transaction Confirmed! Hash: {w3.to_hex(h)}")
                    st.rerun()
                except Exception as e: st.error(f"Blockchain Block Error: {e}")

# --- TAB 3: FORENSIC LAB (FIXED VISUALIZER) ---
with tab3:
    st.header("🕵️ Path Reconstruction Visualizer")
    search = st.text_input("Trace Address Chronology:", placeholder="Paste 0x address to map money flow...").strip().lower()
    
    if search:
        with st.status("Analyzing Local Forensic Logs...", expanded=False) as status:
            conn = sqlite3.connect("coinEth_v2.db")
            query = "SELECT * FROM transactions WHERE LOWER(from_a)=? OR LOWER(to_a)=? ORDER BY timestamp ASC"
            df_t = pd.read_sql_query(query, conn, params=(search, search))
            conn.close()
            status.update(label="Analysis Complete!", state="complete")

        if not df_t.empty:
            st.info(f"Reconstructed {len(df_t)} transaction nodes. Rendering graph...")
            
            net = Network(height="600px", width="100%", bgcolor="#0e1117", font_color="white", directed=True)
            net.force_atlas_2based()
            
            nodes = set()
            for i, r in df_t.iterrows():
                for addr in [r['from_a'], r['to_a']]:
                    if addr not in nodes:
                        try:
                            # Verify on-chain status for live color coding
                            on_chain_lv = contract.functions.riskLevel(w3.to_checksum_address(addr)).call()
                        except:
                            on_chain_lv = 0
                        
                        color = {0: "#2ECC71", 1: "#F1C40F", 2: "#E74C3C"}.get(on_chain_lv, "#95a5a6")
                        net.add_node(addr, label=f"({on_chain_lv}) {addr[:6]}", color=color, title=f"Risk Level: {on_chain_lv}\nAddr: {addr}")
                        nodes.add(addr)
                
                # The Edge representing the sequential path (T0 -> T1 -> T2...)
                net.add_edge(r['from_a'], r['to_a'], 
                             title=f"Value: {r['value']} ETH\nTime: {r['timestamp']}", 
                             label=f"Path Seq: T{i}", 
                             width=2)
            
            # Save to temporary file and render
            try:
                vis_file = "forensic_map.html"
                net.save_graph(vis_file)
                with open(vis_file, 'r', encoding='utf-8') as f:
                    components.html(f.read(), height=650)
            except Exception as e:
                st.error(f"Visualizer Rendering Error: {e}")
            
            st.subheader("Verified Transaction Ledger")
            st.dataframe(df_t, use_container_width=True)
        else:
            st.warning("No forensic data found for this address. Verify that the address has engaged in transactions while the coinEth listener was active.")