import sqlite3

def check_db():
    conn = sqlite3.connect('values.db')
    c = conn.cursor()
    
    # 테이블 목록 확인
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = c.fetchall()
    print("Tables in database:", tables)
    
    # value_items 테이블의 내용 확인
    try:
        c.execute('SELECT * FROM value_items')
        rows = c.fetchall()
        print("\nContents of value_items table:")
        for row in rows:
            print(row)
    except sqlite3.OperationalError as e:
        print("Error reading table:", e)
    
    conn.close()

if __name__ == "__main__":
    check_db() 