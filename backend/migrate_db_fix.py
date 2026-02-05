"""
Database migration script to fix NOT NULL constraints
This will recreate the papers table with nullable columns
"""
import sqlite3
import json

def migrate_database():
    try:
        conn = sqlite3.connect('oxford_papers.db')
        cursor = conn.cursor()
        
        print("Starting migration to fix NOT NULL constraints...\n")
        
        # Get existing data
        cursor.execute("SELECT * FROM papers")
        existing_papers = cursor.fetchall()
        print(f"Found {len(existing_papers)} existing papers")
        
        # Get column names
        cursor.execute("PRAGMA table_info(papers)")
        old_columns = cursor.fetchall()
        print(f"Current columns: {[col[1] for col in old_columns]}")
        
        # Drop old table
        cursor.execute("DROP TABLE IF EXISTS papers")
        print("✓ Dropped old papers table")
        
        # Create new table with correct schema
        cursor.execute("""
            CREATE TABLE papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                grade TEXT,
                subject TEXT,
                chapter TEXT,
                topic TEXT,
                document_name TEXT,
                paper_type TEXT DEFAULT 'curriculum',
                questions TEXT NOT NULL,
                total_marks INTEGER NOT NULL,
                created_at TIMESTAMP
            )
        """)
        print("✓ Created new papers table with nullable columns")
        
        # Restore existing data
        for paper in existing_papers:
            # Map old data to new schema
            # paper structure: (id, grade, subject, chapter, topic, questions, total_marks, created_at, document_name, paper_type)
            paper_id = paper[0]
            grade = paper[1]
            subject = paper[2]
            chapter = paper[3]
            topic = paper[4]
            questions = paper[5]
            total_marks = paper[6] if paper[6] is not None else 100
            created_at = paper[7]
            document_name = paper[8] if len(paper) > 8 else None
            paper_type = paper[9] if len(paper) > 9 else 'curriculum'
            
            cursor.execute("""
                INSERT INTO papers (id, grade, subject, chapter, topic, document_name, paper_type, questions, total_marks, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (paper_id, grade, subject, chapter, topic, document_name, paper_type, questions, total_marks, created_at))
        
        print(f"✓ Restored {len(existing_papers)} papers")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Database migration completed successfully!")
        print("The papers table now allows NULL values for grade, subject, and chapter.")
        print("You can now restart your server and use document-based endpoints.")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    migrate_database()
