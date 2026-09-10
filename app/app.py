import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"]
    )


def initialize_database():
    """Create the employees table if it does not already exist."""

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,
                employee_id VARCHAR(50) UNIQUE NOT NULL,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(150) NOT NULL,
                department VARCHAR(100),
                designation VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.commit()

    except Exception as e:
        print(f"Database initialization failed: {e}")

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.route("/")
def home():
    search = request.args.get("search", "").strip()

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if search:
            cursor.execute("""
                SELECT
                    id,
                    employee_id,
                    name,
                    email,
                    department,
                    designation
                FROM employees
                WHERE
                    employee_id ILIKE %s
                    OR name ILIKE %s
                    OR email ILIKE %s
                    OR department ILIKE %s
                    OR designation ILIKE %s
                ORDER BY id DESC
            """, (
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
                f"%{search}%",
                f"%{search}%"
            ))
        else:
            cursor.execute("""
                SELECT
                    id,
                    employee_id,
                    name,
                    email,
                    department,
                    designation
                FROM employees
                ORDER BY id DESC
            """)

        employees = cursor.fetchall()

        return render_template(
            "index.html",
            employees=employees,
            search=search
        )

    except Exception as e:
        return render_template(
            "index.html",
            employees=[],
            search=search,
            error=f"Unable to load employees: {str(e)}"
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.route("/health")
def health():
    return {
        "application": "Employeehub",
        "status": "healthy"
    }


@app.route("/db-test")
def db_test():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT version();")
        result = cursor.fetchone()

        return {
            "database": "connected",
            "version": result[0]
        }

    except Exception as e:
        return {
            "database": "connection failed",
            "error": str(e)
        }, 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.route("/employees/add", methods=["POST"])
def add_employee():
    employee_id = request.form.get("employee_id", "").strip()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    department = request.form.get("department", "").strip()
    designation = request.form.get("designation", "").strip()

    if not employee_id or not name or not email:
        return redirect(
            url_for(
                "home",
                error="Required fields are missing"
            )
        )

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO employees
            (
                employee_id,
                name,
                email,
                department,
                designation
            )
            VALUES (%s, %s, %s, %s, %s)
        """, (
            employee_id,
            name,
            email,
            department,
            designation
        ))

        connection.commit()

        return redirect(url_for("home"))

    except psycopg2.errors.UniqueViolation:
        if connection:
            connection.rollback()

        return redirect(
            url_for(
                "home",
                error=f"Employee ID '{employee_id}' already exists"
            )
        )

    except Exception as e:
        if connection:
            connection.rollback()

        return redirect(
            url_for(
                "home",
                error=f"Unable to add employee: {str(e)}"
            )
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.route("/employees/edit/<int:employee_id>", methods=["GET", "POST"])
def edit_employee(employee_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        if request.method == "POST":

            employee_code = request.form.get(
                "employee_id",
                ""
            ).strip()

            name = request.form.get(
                "name",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip()

            department = request.form.get(
                "department",
                ""
            ).strip()

            designation = request.form.get(
                "designation",
                ""
            ).strip()

            if not employee_code or not name or not email:
                return redirect(
                    url_for(
                        "edit_employee",
                        employee_id=employee_id
                    )
                )

            cursor.execute("""
                UPDATE employees
                SET
                    employee_id = %s,
                    name = %s,
                    email = %s,
                    department = %s,
                    designation = %s
                WHERE id = %s
            """, (
                employee_code,
                name,
                email,
                department,
                designation,
                employee_id
            ))

            connection.commit()

            return redirect(url_for("home"))

        cursor.execute("""
            SELECT
                id,
                employee_id,
                name,
                email,
                department,
                designation
            FROM employees
            WHERE id = %s
        """, (employee_id,))

        employee = cursor.fetchone()

        if not employee:
            return "Employee not found", 404

        return render_template(
            "edit_employee.html",
            employee=employee
        )

    except Exception as e:
        if connection:
            connection.rollback()

        return f"Error: {str(e)}", 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


@app.route("/employees/delete/<int:employee_id>", methods=["POST"])
def delete_employee(employee_id):
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM employees
            WHERE id = %s
        """, (employee_id,))

        connection.commit()

        return redirect(url_for("home"))

    except Exception as e:
        if connection:
            connection.rollback()

        return f"Unable to delete employee: {str(e)}", 500

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


# Initialize database when application starts
initialize_database()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )