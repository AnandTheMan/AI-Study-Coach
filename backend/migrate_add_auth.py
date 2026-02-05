"""
Database migration to add users table and update papers/evaluations
"""
import sqlite3

def migrate_add_users():
    try:
        conn = sqlite3.connect('oxford_papers.db')
        cursor = conn.cursor()
        
        print("Starting migration to add authentication...")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✓ Created users table")
        
        # Create a default user for existing data
        cursor.execute("""
            INSERT OR IGNORE INTO users (id, email, username, hashed_password, full_name)
            VALUES (1, 'admin@oxford.com', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5/Jiz0KT3/9GC', 'Admin User')
        """)
        print("✓ Created default admin user (email: admin@oxford.com, password: admin123)")
        
        # Check if user_id column exists in papers table
        cursor.execute("PRAGMA table_info(papers)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in columns:
            # Get existing papers
            cursor.execute("SELECT * FROM papers")
            papers = cursor.fetchall()
            
            # Drop and recreate papers table
            cursor.execute("DROP TABLE papers")
            cursor.execute("""
                CREATE TABLE papers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    grade TEXT,
                    subject TEXT,
                    chapter TEXT,
                    topic TEXT,
                    document_name TEXT,
                    paper_type TEXT DEFAULT 'curriculum',
                    questions TEXT NOT NULL,
                    total_marks INTEGER NOT NULL,
                    created_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Restore papers with default user_id = 1
            for paper in papers:
                cursor.execute("""
                    INSERT INTO papers (id, user_id, grade, subject, chapter, topic, document_name, paper_type, questions, total_marks, created_at)
                    VALUES (?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (paper[0], paper[1], paper[2], paper[3], paper[4], paper[5], paper[6], paper[7], paper[8], paper[9]))
            
            print(f"✓ Updated papers table with user_id ({len(papers)} papers migrated)")
        
        # Check if user_id column exists in evaluations table
        cursor.execute("PRAGMA table_info(evaluations)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in columns:
            # Get existing evaluations
            cursor.execute("SELECT * FROM evaluations")
            evaluations = cursor.fetchall()
            
            # Drop and recreate evaluations table
            cursor.execute("DROP TABLE evaluations")
            cursor.execute("""
                CREATE TABLE evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    paper_id INTEGER NOT NULL,
                    student_answers TEXT NOT NULL,
                    score REAL NOT NULL,
                    total_marks INTEGER NOT NULL,
                    feedback TEXT NOT NULL,
                    evaluated_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (paper_id) REFERENCES papers(id)
                )
            """)
            
            # Restore evaluations with default user_id = 1
            for eval in evaluations:
                cursor.execute("""
                    INSERT INTO evaluations (id, user_id, paper_id, student_answers, score, total_marks, feedback, evaluated_at)
                    VALUES (?, 1, ?, ?, ?, ?, ?, ?)
                """, (eval[0], eval[1], eval[2], eval[3], eval[4], eval[5], eval[6]))
            
            print(f"✓ Updated evaluations table with user_id ({len(evaluations)} evaluations migrated)")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Migration completed successfully!")
        print("\nDefault admin account:")
        print("  Email: admin@oxford.com")
        print("  Password: admin123")
        print("\nRestart your server now.")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    migrate_add_users()
