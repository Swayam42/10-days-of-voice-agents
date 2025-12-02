import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict

class FraudDatabase:
    def __init__(self, db_path: str = "fraud_cases.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fraud_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                userName TEXT NOT NULL,
                securityIdentifier TEXT NOT NULL,
                cardEnding TEXT NOT NULL,
                status TEXT DEFAULT 'pending_review',
                transactionName TEXT NOT NULL,
                transactionAmount REAL NOT NULL,
                transactionTime TEXT NOT NULL,
                transactionCategory TEXT NOT NULL,
                transactionSource TEXT NOT NULL,
                transactionLocation TEXT NOT NULL,
                securityQuestion TEXT NOT NULL,
                securityAnswer TEXT NOT NULL,
                outcome_note TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_sample_data(self):
        """Add Indian sample fraud cases for testing"""
        sample_cases = [
            {
                "userName": "Rahul Sharma",
                "securityIdentifier": "MUM2024",
                "cardEnding": "7890",
                "transactionName": "International Gaming Store",
                "transactionAmount": 89999.00,
                "transactionTime": "26-11-2025 02:30 AM",
                "transactionCategory": "online-gaming",
                "transactionSource": "steamgames.com",
                "transactionLocation": "New Delhi, India",
                "securityQuestion": "What is your mother's maiden name?",
                "securityAnswer": "Verma"
            },
            {
                "userName": "Priya Patel",
                "securityIdentifier": "AHM2024",
                "cardEnding": "4567",
                "transactionName": "Luxury Fashion Boutique",
                "transactionAmount": 125000.00,
                "transactionTime": "25-11-2025 11:45 PM",
                "transactionCategory": "fashion",
                "transactionSource": "luxuryfashion.ae",
                "transactionLocation": "Dubai, UAE",
                "securityQuestion": "What city were you born in?",
                "securityAnswer": "Ahmedabad"
            },
            {
                "userName": "Arjun Kumar",
                "securityIdentifier": "DEL2024",
                "cardEnding": "3456",
                "transactionName": "Electronic Gadgets Mega Sale",
                "transactionAmount": 67500.00,
                "transactionTime": "26-11-2025 09:15 AM",
                "transactionCategory": "electronics",
                "transactionSource": "cheapelectronics.cn",
                "transactionLocation": "Shenzhen, China",
                "securityQuestion": "What was your first pet's name?",
                "securityAnswer": "Max"
            },
            {
                "userName": "Anjali Reddy",
                "securityIdentifier": "HYD2024",
                "cardEnding": "9012",
                "transactionName": "Crypto Investment Platform",
                "transactionAmount": 250000.00,
                "transactionTime": "24-11-2025 08:30 PM",
                "transactionCategory": "cryptocurrency",
                "transactionSource": "quickcrypto.xyz",
                "transactionLocation": "Hong Kong",
                "securityQuestion": "What is your favorite food?",
                "securityAnswer": "Biryani"
            },
            {
                "userName": "Vikram Singh",
                "securityIdentifier": "BLR2024",
                "cardEnding": "2345",
                "transactionName": "Software Subscription Service",
                "transactionAmount": 45000.00,
                "transactionTime": "25-11-2025 03:20 PM",
                "transactionCategory": "software",
                "transactionSource": "subscriptionservice.io",
                "transactionLocation": "Singapore",
                "securityQuestion": "What is your father's middle name?",
                "securityAnswer": "Pratap"
            }
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM fraud_cases")
        
        for case in sample_cases:
            cursor.execute("""
                INSERT INTO fraud_cases (
                    userName, securityIdentifier, cardEnding, transactionName,
                    transactionAmount, transactionTime, transactionCategory,
                    transactionSource, transactionLocation, securityQuestion, securityAnswer
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                case["userName"], case["securityIdentifier"], case["cardEnding"],
                case["transactionName"], case["transactionAmount"], case["transactionTime"],
                case["transactionCategory"], case["transactionSource"], case["transactionLocation"],
                case["securityQuestion"], case["securityAnswer"]
            ))
        
        conn.commit()
        conn.close()
        print(f"Added {len(sample_cases)} Indian fraud cases to the database")
    
    def get_fraud_case_by_username(self, username: str) -> Optional[Dict]:
        """Retrieve a fraud case by username (case-insensitive)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM fraud_cases 
            WHERE LOWER(userName) = LOWER(?) AND status = 'pending_review'
            ORDER BY created_at DESC
            LIMIT 1
        """, (username.strip(),))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return dict(row)
        return None
    
    def update_fraud_case_status(self, case_id: int, status: str, outcome_note: str):
        """Update the status of a fraud case"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First check if case exists
        cursor.execute("SELECT userName, status FROM fraud_cases WHERE id = ?", (case_id,))
        existing = cursor.fetchone()
        
        if not existing:
            print(f"⚠️  WARNING: Case {case_id} not found in database!")
            conn.close()
            return
        
        old_status = existing[1]
        
        cursor.execute("""
            UPDATE fraud_cases 
            SET status = ?, outcome_note = ?, updated_at = ?
            WHERE id = ?
        """, (status, outcome_note, datetime.now().isoformat(), case_id))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        if rows_affected > 0:
            print(f"✅ DATABASE UPDATED: Case {case_id} - {old_status} → {status}")
            print(f"   Note: {outcome_note}")
        else:
            print(f"⚠️  WARNING: Update failed for case {case_id}")
    
    def get_all_cases(self):
        """Get all fraud cases for debugging"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM fraud_cases ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def reset_all_cases(self):
        """Reset all cases back to pending_review for testing"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE fraud_cases 
            SET status = 'pending_review', outcome_note = NULL, updated_at = ?
        """, (datetime.now().isoformat(),))
        
        conn.commit()
        conn.close()
        print("Reset all fraud cases to pending_review")


# Initialize database and add sample data when this module is run
if __name__ == "__main__":
    import sys
    
    db = FraudDatabase()
    
    # Check if --reset flag is provided
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        print("\n🔄 Resetting database with fresh sample data...")
        db.add_sample_data()
        print("✅ Database reset complete!\n")
    
    # Display all cases with current status
    print("\n" + "="*70)
    print("🏦 BHARAT SECURE BANK - FRAUD CASES DATABASE")
    print("="*70)
    
    cases = db.get_all_cases()
    
    if not cases:
        print("\n⚠️  No cases found! Run with --reset to add sample data:")
        print("   python src/database.py --reset")
        sys.exit(0)
    
    # Group by status for summary
    status_count = {}
    for case in cases:
        status = case['status']
        status_count[status] = status_count.get(status, 0) + 1
    
    # Print summary
    print(f"\n📊 SUMMARY:")
    print(f"   Total Cases: {len(cases)}")
    for status, count in sorted(status_count.items()):
        emoji = {
            'pending_review': '⏳',
            'confirmed_safe': '✅',
            'confirmed_fraud': '❌',
            'verification_failed': '⛔',
            'call_incomplete': '⚠️'
        }.get(status, '📋')
        print(f"   {emoji} {status}: {count}")
    
    # Display detailed case information
    print(f"\n📋 DETAILED CASES:")
    print("-" * 70)
    
    for i, case in enumerate(cases, 1):
        # Status emoji
        status_emoji = {
            'pending_review': '⏳',
            'confirmed_safe': '✅',
            'confirmed_fraud': '❌',
            'verification_failed': '⛔',
            'call_incomplete': '⚠️'
        }.get(case['status'], '📋')
        
        print(f"\n{status_emoji} Case {case['id']}: {case['userName']}")
        print(f"   Card: ****{case['cardEnding']}")
        print(f"   Amount: ₹{case['transactionAmount']:,.2f}")
        print(f"   Merchant: {case['transactionName']}")
        print(f"   Location: {case['transactionLocation']}")
        print(f"   Time: {case['transactionTime']}")
        print(f"   Status: {case['status'].upper().replace('_', ' ')}")
        
        if case['outcome_note']:
            print(f"   📝 Outcome: {case['outcome_note']}")
        
        print(f"   🔐 Security Q: {case['securityQuestion']}")
        print(f"   ✓ Answer: {case['securityAnswer']}")
        
        if case['updated_at']:
            print(f"   🕒 Last Updated: {case['updated_at']}")
    
    print("\n" + "="*70)
    
    # Show pending cases that need testing
    pending = [c for c in cases if c['status'] == 'pending_review']
    if pending:
        print(f"\n⏳ {len(pending)} PENDING CASE(S) - Ready for testing:")
        for case in pending:
            print(f"   • Call and say: \"{case['userName']}\" → Answer: \"{case['securityAnswer']}\"")
    
    # Show completed cases
    completed = [c for c in cases if c['status'] in ['confirmed_safe', 'confirmed_fraud', 'verification_failed']]
    if completed:
        print(f"\n✅ {len(completed)} COMPLETED CASE(S)")
    
    print("\n💡 COMMANDS:")
    print("   python src/database.py          # View current status")
    print("   python src/database.py --reset  # Reset all cases to pending")
    print("   python check_database.py        # Detailed status view")
    
    print("\n" + "="*70 + "\n")