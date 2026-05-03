import mysql.connector
import psycopg2


DB_CONFIG = {
    'mysql': {
        'host': 'localhost', 'port': 3306, 'database': 'education_db',
        'users': {
            'admin': {'user': 'admin_user', 'password': 'AdminPass123!'},
            'viewer': {'user': 'viewer_user', 'password': 'ViewPass123!'},
            'operator': {'user': 'operator_user', 'password': 'OperPass123!'}
        }
    },
    'postgres': {
        'host': 'localhost', 'port': 5432, 'database': 'education_db',
        'users': {
            'admin': {'user': 'admin_user', 'password': 'AdminPass123!'},
            'viewer': {'user': 'viewer_user', 'password': 'ViewPass123!'},
            'operator': {'user': 'operator_user', 'password': 'OperPass123!'}
        }
    }
}

def run_test(cursor, query, params=None, description="", expected_success=True, db_type="mysql"):
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        
        if query.strip().upper().startswith("SELECT"):
            cursor.fetchall()

        if expected_success:
            print(f"   {description}: УСПЕШНО")
        else:
            print(f"   {description}: ОЖИДАЛАСЬ ОШИБКА, но выполнилось!")
        return True
    except Exception as e:
        
        if db_type == 'postgres':
            cursor.connection.rollback()
            
        if not expected_success:
            print(f"{description}: ДОСТУП ЗАПРЕЩЁН (как и ожидалось)")
        else:
            print(f"{description}: НЕОЖИДАННАЯ ОШИБКА -> {type(e).__name__}")
        return False

def test_dbms(db_type, config):
    print(f"{'='*55}")
    print(f"ТЕСТИРОВАНИЕ: {db_type.upper()}")
    

    for role, creds in config['users'].items():
        print(f"\n Группа: {role.upper()}")
        conn = None
        try:
         
            if db_type == 'mysql':
                conn = mysql.connector.connect(host=config['host'], port=config['port'],
                                               database=config['database'], **creds, buffered=True)
            else:
                conn = psycopg2.connect(host=config['host'], port=config['port'],
                                        dbname=config['database'], **creds)
            conn.autocommit = True  
            cursor = conn.cursor()

            
            run_test(cursor, "SELECT * FROM vw_student_grades LIMIT 1",
                     description="SELECT vw_student_grades", expected_success=True, db_type=db_type)

            
            run_test(cursor, "SELECT * FROM students LIMIT 1",
                     description="SELECT students", expected_success=(role == 'admin'), db_type=db_type)

           
            insert_q = "INSERT INTO grades (student_id, subject_id, grade_value, grade_date) VALUES (%s, %s, %s, %s)"
            run_test(cursor, insert_q, params=(1, 1, '5', '2024-11-01'),
                     description="INSERT INTO grades", expected_success=(role in ['admin', 'operator']), db_type=db_type)

           
            update_q = ("UPDATE students SET full_name = CONCAT(full_name, ' ') WHERE student_id = 1" 
                        if db_type == 'mysql' else 
                        "UPDATE students SET full_name = full_name || ' ' WHERE student_id = 1")
            run_test(cursor, update_q,
                     description="UPDATE students", expected_success=(role == 'admin'), db_type=db_type)

            cursor.close()

        except Exception as e:
            print(f"   Критическая ошибка: {e}")
        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    test_dbms('mysql', DB_CONFIG['mysql'])
    test_dbms('postgres', DB_CONFIG['postgres'])
    print("\n Тестирование завершено.")