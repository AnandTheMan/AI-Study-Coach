"""
Database migration script to add document_name and paper_type columns
Run this script to update your existing database
"""
import sqlite3

def migrate_database():
    try:
        conn = sqlite3.connect('oxford_papers.db')
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(papers)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add document_name column if it doesn't exist
        if 'document_name' not in columns:
            cursor.execute("ALTER TABLE papers ADD COLUMN document_name TEXT")
            print("✓ Added document_name column")
        else:
            print("✓ document_name column already exists")
        
        # Add paper_type column if it doesn't exist
        if 'paper_type' not in columns:
            cursor.execute("ALTER TABLE papers ADD COLUMN paper_type TEXT DEFAULT 'curriculum'")
            print("✓ Added paper_type column")
        else:
            print("✓ paper_type column already exists")
        
        # Update existing records to have paper_type = 'curriculum'
        cursor.execute("UPDATE papers SET paper_type = 'curriculum' WHERE paper_type IS NULL")
        
        # Make grade, subject, chapter nullable (SQLite doesn't support modifying columns directly)
        # This is automatically handled by the new schema
        
        conn.commit()
        conn.close()
        
        print("\n✅ Database migration completed successfully!")
        print("You can now restart your server and use the document-based endpoints.")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    print("Starting database migration...\n")
    migrate_database()
