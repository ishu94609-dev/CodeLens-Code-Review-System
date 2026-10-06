from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    jsonify
)

from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

import sqlite3
import os
import ast
import json
import re
import shutil
import subprocess
import tempfile
import secrets
import smtplib
import os
import requests
from datetime import datetime
from flask import send_file
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from email.message import EmailMessage
from datetime import datetime, timedelta, timezone

# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# FLASK CONFIGURATION
# =========================================================

app = Flask(__name__)



app.secret_key = os.getenv(
    "SECRET_KEY",
    "codelens-secret-key-change-this"
)


# =========================================================
# DATABASE CONFIGURATION
# =========================================================

BASE_DIR = os.path.abspath(
    os.path.dirname(__file__)
)

INSTANCE_DIR = os.path.join(
    BASE_DIR,
    "instance"
)

DATABASE = os.path.join(
    INSTANCE_DIR,
    "codelens.db"
)


os.makedirs(
    INSTANCE_DIR,
    exist_ok=True
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db():

    connection = sqlite3.connect(
        DATABASE
    )

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# DATABASE INITIALIZATION + MIGRATION
# =========================================================

def init_db():

    connection = get_db()

    # -----------------------------------------------------
    # USERS TABLE
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)


    # -----------------------------------------------------
    # ANALYSES TABLE
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT,
            language TEXT,
            code TEXT NOT NULL,
            issues_count INTEGER DEFAULT 0,
            quality_score REAL DEFAULT 0,
            complexity TEXT,
            analysis_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)


    # -----------------------------------------------------
    # SAVED CODE TABLE
    # -----------------------------------------------------

    connection.execute("""
    CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        used INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
""")


    # -----------------------------------------------------
    # REFACTORED CODE TABLE
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS refactored_code (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            analysis_id INTEGER,
            filename TEXT,
            language TEXT,
            original_code TEXT,
            refactored_code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(analysis_id) REFERENCES analyses(id)
        )
    """)


    # -----------------------------------------------------
    # REPORTS TABLE
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            report_name TEXT NOT NULL,
            report_type TEXT,
            language TEXT,
            analysis_id INTEGER,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(analysis_id) REFERENCES analyses(id)
        )
    """)

        # -----------------------------------------------------
    # PASSWORD RESET TOKENS TABLE
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            used INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)


    # =====================================================
    # DATABASE MIGRATION
    #
    # This is important because the database may already
    # exist from the previous version of the project.
    #
    # CREATE TABLE IF NOT EXISTS does NOT add new columns
    # to an existing table.
    # =====================================================

    columns = connection.execute(
        "PRAGMA table_info(analyses)"
    ).fetchall()


    existing_columns = {
        column["name"]
        for column in columns
    }


    # -----------------------------------------------------
    # ADD analysis_result IF MISSING
    # -----------------------------------------------------

    if "analysis_result" not in existing_columns:

        connection.execute("""
            ALTER TABLE analyses
            ADD COLUMN analysis_result TEXT
        """)


    # -----------------------------------------------------
    # ADD issues_count IF MISSING
    # -----------------------------------------------------

    if "issues_count" not in existing_columns:

        connection.execute("""
            ALTER TABLE analyses
            ADD COLUMN issues_count INTEGER DEFAULT 0
        """)


    # -----------------------------------------------------
    # ADD quality_score IF MISSING
    # -----------------------------------------------------

    if "quality_score" not in existing_columns:

        connection.execute("""
            ALTER TABLE analyses
            ADD COLUMN quality_score REAL DEFAULT 0
        """)


    # -----------------------------------------------------
    # ADD complexity IF MISSING
    # -----------------------------------------------------

    if "complexity" not in existing_columns:

        connection.execute("""
            ALTER TABLE analyses
            ADD COLUMN complexity TEXT
        """)


    connection.commit()

    connection.close()


# =========================================================
# RUN DATABASE INITIALIZATION
# =========================================================

init_db()


# =========================================================
# GOOGLE OAUTH
# =========================================================

oauth = OAuth(app)


google = oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url=(
        "https://accounts.google.com/"
        ".well-known/openid-configuration"
    ),
    client_kwargs={
        "scope": "openid email profile"
    }
)


# =========================================================
# LOGIN REQUIRED DECORATOR
# =========================================================

from functools import wraps


def login_required(function):

    @wraps(function)
    def decorated_function(*args, **kwargs):

        if "user_id" not in session:

            return redirect(
                url_for("login")
            )

        return function(
            *args,
            **kwargs
        )

    return decorated_function


# =========================================================
# HELPER - CURRENT USER
# =========================================================

def get_current_user():

    if "user_id" not in session:
        return None

    connection = get_db()

    user = connection.execute(
        """
        SELECT
            id,
            full_name,
            email,
            username,
            created_at
        FROM users
        WHERE id = ?
        """,
        (
            session["user_id"],
        )
    ).fetchone()

    connection.close()

    return user


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    if "user_id" in session:

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "home.html"
    )


# =========================================================
# REGISTER
# =========================================================


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        if not full_name or not email or not username or not password:
            return render_template(
                "register.html",
                error="All fields are required."
            )

        if password != confirm_password:
            return render_template(
                "register.html",
                error="Passwords do not match."
            )

        if len(password) < 6:
            return render_template(
                "register.html",
                error="Password must contain at least 6 characters."
            )

        connection = get_db()

        try:

            existing = connection.execute(
                """
                SELECT id
                FROM users
                WHERE email = ? OR username = ?
                """,
                (email, username)
            ).fetchone()

            if existing:
                connection.close()

                return render_template(
                    "register.html",
                    error="Email or username already exists."
                )

            connection.execute(
                """
                INSERT INTO users
                (
                    full_name,
                    email,
                    username,
                    password
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    full_name,
                    email,
                    username,
                    password
                )
            )

            connection.commit()
            connection.close()

            print("REGISTER SUCCESS:", username)

            return redirect(url_for("login"))

        except Exception as error:

            print("REGISTER ERROR:", error)

            connection.rollback()
            connection.close()

            return render_template(
                "register.html",
                error="Registration failed: " + str(error)
            )

    return render_template("register.html")

# =========================================================
# LOGIN
# =========================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        username = (
            request.form.get(
                "username"
            )
            or ""
        ).strip()

        password = (
            request.form.get(
                "password"
            )
            or ""
        )


        connection = get_db()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE
                (
                    username = ?
                    OR email = ?
                )
                AND password = ?
            """,
            (
                username,
                username,
                password
            )
        ).fetchone()

        connection.close()


        if user is None:

            return render_template(
                "login.html",
                error="Invalid username/email or password."
            )


        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["full_name"] = user["full_name"]


        return redirect(
            url_for("dashboard")
        )


    return render_template(
        "login.html"
    )

# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route("/forgot-password", methods=["POST"])
def forgot_password():

    try:

        data = request.get_json(silent=True) or {}

        email = (data.get("email") or "").strip().lower()

        # =====================================================
        # VALIDATE EMAIL
        # =====================================================

        if not email:
            return jsonify({
                "success": False,
                "message": "Please enter your email address."
            }), 400


        # =====================================================
        # GET USER
        # =====================================================

        connection = get_db()

        user = connection.execute(
            """
            SELECT id, full_name, email
            FROM users
            WHERE LOWER(email) = ?
            """,
            (email,)
        ).fetchone()


        if user is None:

            connection.close()

            return jsonify({
                "success": False,
                "message": "No account found with this email address."
            }), 404


        # =====================================================
        # DELETE OLD RESET TOKENS
        # =====================================================

        connection.execute(
            """
            DELETE FROM password_reset_tokens
            WHERE user_id = ?
            """,
            (user["id"],)
        )


        # =====================================================
        # CREATE NEW TOKEN
        # =====================================================

        token = secrets.token_urlsafe(32)

        expires_at = (
            datetime.utcnow() + timedelta(minutes=30)
        ).strftime("%Y-%m-%d %H:%M:%S")


        connection.execute(
            """
            INSERT INTO password_reset_tokens
            (
                user_id,
                token,
                expires_at,
                used
            )
            VALUES (?, ?, ?, 0)
            """,
            (
                user["id"],
                token,
                expires_at
            )
        )


        connection.commit()
        connection.close()


        # =====================================================
        # CREATE RESET LINK
        # =====================================================

        reset_link = url_for(
            "reset_password",
            token=token,
            _external=True
        )


        # =====================================================
        # MAIL SETTINGS
        # =====================================================

        mail_username = os.getenv("MAIL_USERNAME")

        mail_password = os.getenv("MAIL_PASSWORD")

        mail_server = os.getenv(
            "MAIL_SERVER",
            "smtp.gmail.com"
        )

        # Gmail SSL port
        mail_port = 465


        print("====================================")
        print("PASSWORD RESET")
        print("MAIL USERNAME:", mail_username)
        print("MAIL SERVER:", mail_server)
        print("MAIL PORT:", mail_port)


        if not mail_username:

            print("ERROR: MAIL_USERNAME missing")

            return jsonify({
                "success": False,
                "message": "MAIL_USERNAME is missing in .env"
            }), 500


        if not mail_password:

            print("ERROR: MAIL_PASSWORD missing")

            return jsonify({
                "success": False,
                "message": "MAIL_PASSWORD is missing in .env"
            }), 500


        # =====================================================
        # CREATE EMAIL
        # =====================================================

        message = EmailMessage()

        message["Subject"] = "CodeLens - Password Reset"

        message["From"] = mail_username

        message["To"] = email


        message.set_content(
            f"""
Hello {user["full_name"]},

We received a request to reset your CodeLens password.

Click the link below to create a new password:

{reset_link}

This link will expire in 30 minutes.

If you did not request this password reset,
you can safely ignore this email.

Regards,
CodeLens
Code Review & Refactoring System
"""
        )


        # =====================================================
        # SEND EMAIL USING GMAIL SSL
        # =====================================================

        print("CONNECTING TO GMAIL SSL...")


        with smtplib.SMTP_SSL(
            mail_server,
            mail_port,
            timeout=30
        ) as smtp:

            print("CONNECTED TO GMAIL")

            print("LOGGING INTO GMAIL...")
            print("USERNAME:", repr(mail_username))
            print("PASSWORD LENGTH:", len(mail_password) if mail_password else 0)

            smtp.login(
                mail_username,
                mail_password
            )


            print("GMAIL LOGIN SUCCESS")


            smtp.send_message(message)


        print("EMAIL SENT SUCCESSFULLY")
        print("PASSWORD RESET EMAIL SENT TO:", email)
        print("====================================")


        return jsonify({
            "success": True,
            "message": "Password reset link has been sent to your email."
        })


    except Exception as error:

        print("====================================")
        print("PASSWORD RESET ERROR")
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR:", str(error))
        print("====================================")


        return jsonify({
            "success": False,
            "message": "Unable to send reset link."
        }), 500
    # =========================================================
# RESET PASSWORD PAGE
# =========================================================

@app.route(
    "/reset-password/<token>",
    methods=["GET", "POST"]
)
def reset_password(token):

    connection = get_db()


    # -----------------------------------------------------
    # FIND TOKEN
    # -----------------------------------------------------

    reset_data = connection.execute(
        """
        SELECT
            password_reset_tokens.id,
            password_reset_tokens.user_id,
            password_reset_tokens.expires_at,
            password_reset_tokens.used
        FROM password_reset_tokens
        WHERE password_reset_tokens.token = ?
        """,
        (token,)
    ).fetchone()


    if reset_data is None:

        connection.close()

        return render_template(
            "reset_password.html",
            error="Invalid password reset link."
        )


    # -----------------------------------------------------
    # CHECK USED
    # -----------------------------------------------------

    if reset_data["used"] == 1:

        connection.close()

        return render_template(
            "reset_password.html",
            error="This password reset link has already been used."
        )


    # -----------------------------------------------------
    # CHECK EXPIRY
    # -----------------------------------------------------

    try:

        expires_at = datetime.strptime(
            reset_data["expires_at"],
            "%Y-%m-%d %H:%M:%S"
        )

    except ValueError:

        connection.close()

        return render_template(
            "reset_password.html",
            error="Invalid reset link."
        )


    if datetime.utcnow() > expires_at:

        connection.close()

        return render_template(
            "reset_password.html",
            error="This password reset link has expired."
        )


    # -----------------------------------------------------
    # POST - UPDATE PASSWORD
    # -----------------------------------------------------

    if request.method == "POST":

        new_password = (
            request.form.get(
                "password"
            )
            or ""
        )

        confirm_password = (
            request.form.get(
                "confirm_password"
            )
            or ""
        )


        if not new_password:

            connection.close()

            return render_template(
                "reset_password.html",
                token=token,
                error="Please enter a new password."
            )


        if len(new_password) < 6:

            connection.close()

            return render_template(
                "reset_password.html",
                token=token,
                error="Password must contain at least 6 characters."
            )


        if new_password != confirm_password:

            connection.close()

            return render_template(
                "reset_password.html",
                token=token,
                error="Passwords do not match."
            )


        # -------------------------------------------------
        # UPDATE PASSWORD
        # -------------------------------------------------

        connection.execute(
            """
            UPDATE users
            SET password = ?
            WHERE id = ?
            """,
            (
                new_password,
                reset_data["user_id"]
            )
        )


        # -------------------------------------------------
        # MARK TOKEN AS USED
        # -------------------------------------------------

        connection.execute(
            """
            UPDATE password_reset_tokens
            SET used = 1
            WHERE id = ?
            """,
            (
                reset_data["id"],
            )
        )


        connection.commit()

        connection.close()


        return redirect(
            url_for(
                "login",
                reset="success"
            )
        )


    connection.close()


    return render_template(
        "reset_password.html",
        token=token
    )

# =========================================================
# GOOGLE LOGIN
# =========================================================

@app.route("/login/google")
def google_login():

    redirect_uri = url_for(
        "google_callback",
        _external=True
    )

    print("================================")
    print("GOOGLE REDIRECT URI:")
    print(redirect_uri)
    print("================================")

    return google.authorize_redirect(
        redirect_uri
    )


# =========================================================
# GOOGLE CALLBACK
# =========================================================

@app.route("/login/google/callback")
def google_callback():

    try:

        token = google.authorize_access_token()

        user_info = token.get(
            "userinfo"
        )


        if not user_info:

            user_info = google.userinfo()


        email = (
            user_info.get("email")
            or ""
        ).strip().lower()

        full_name = (
            user_info.get("name")
            or "CodeLens User"
        ).strip()


        if not email:

            return redirect(
                url_for("login")
            )


        # Create a username from email
        username_base = email.split("@")[0]

        username = re.sub(
            r"[^a-zA-Z0-9_]",
            "",
            username_base
        )


        if not username:

            username = "codelens_user"


        connection = get_db()


        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE email = ?
            """,
            (
                email,
            )
        ).fetchone()


        if user is None:

            final_username = username

            counter = 1

            while True:

                existing = connection.execute(
                    """
                    SELECT id
                    FROM users
                    WHERE username = ?
                    """,
                    (
                        final_username,
                    )
                ).fetchone()


                if existing is None:
                    break


                final_username = (
                    username
                    + str(counter)
                )

                counter += 1


            cursor = connection.execute(
                """
                INSERT INTO users
                (
                    full_name,
                    email,
                    username,
                    password
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    full_name,
                    email,
                    final_username,
                    None
                )
            )

            connection.commit()

            user_id = cursor.lastrowid

        else:

            user_id = user["id"]

            final_username = user["username"]


        connection.close()


        session["user_id"] = user_id
        session["username"] = final_username
        session["full_name"] = full_name


        return redirect(
            url_for("dashboard")
        )


    except Exception as error:

        print(
            "Google OAuth error:",
            error
        )

        return redirect(
            url_for("login")
        )


# =========================================================
# LOGOUT
# =========================================================

@app.route(
    "/logout",
    methods=["POST", "GET"]
)
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    user = get_current_user()

    connection = get_db()


    total_analyses = connection.execute(
        """
        SELECT COUNT(*)
        FROM analyses
        WHERE user_id = ?
        """,
        (
            session["user_id"],
        )
    ).fetchone()[0]


    files_analyzed = connection.execute(
        """
        SELECT COUNT(*)
        FROM analyses
        WHERE
            user_id = ?
            AND filename IS NOT NULL
            AND filename != ''
        """,
        (
            session["user_id"],
        )
    ).fetchone()[0]


    issues_found = connection.execute(
        """
        SELECT COALESCE(
            SUM(issues_count),
            0
        )
        FROM analyses
        WHERE user_id = ?
        """,
        (
            session["user_id"],
        )
    ).fetchone()[0]


    suggestions = connection.execute(
        """
        SELECT COUNT(*)
        FROM refactored_code
        WHERE user_id = ?
        """,
        (
            session["user_id"],
        )
    ).fetchone()[0]


    connection.close()


    first_letter = "U"


    if user:

        name = (
            user["full_name"]
            or user["username"]
            or "User"
        )

        first_letter = name[0].upper()


    return render_template(
        "dashboard.html",
        user=user,
        first_letter=first_letter,
        total_analyses=total_analyses,
        files_analyzed=files_analyzed,
        issues_found=issues_found,
        suggestions=suggestions
    )

@app.route("/api/dashboard-stats")
@login_required
def dashboard_stats():

    connection = get_db()

    user_id = session["user_id"]

    # =====================================================
    # TOTAL ANALYSES
    # =====================================================

    total_analyses_row = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM analyses
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    total_analyses = total_analyses_row["total"] or 0


    # =====================================================
    # TOTAL ISSUES
    # =====================================================

    total_issues_row = connection.execute(
        """
        SELECT COALESCE(SUM(issues_count), 0) AS total
        FROM analyses
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    total_issues = total_issues_row["total"] or 0


    # =====================================================
    # REPORTS
    # =====================================================

    reports_row = connection.execute(
        """
        SELECT COUNT(*) AS total
        FROM reports
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()

    reports = reports_row["total"] or 0


    # =====================================================
    # SAVED CODE
    # =====================================================

    saved_code = 0

    try:

        saved_row = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM saved_code
            WHERE user_id = ?
            """,
            (user_id,)
        ).fetchone()

        saved_code = saved_row["total"] or 0

    except Exception:

        saved_code = 0


    # =====================================================
    # RECENT ANALYSES
    # =====================================================

    recent_rows = connection.execute(
        """
        SELECT
            id,
            filename,
            language,
            issues_count,
            quality_score,
            created_at
        FROM analyses
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (user_id,)
    ).fetchall()


    recent_analyses = []

    for row in recent_rows:

        recent_analyses.append({
            "id": row["id"],
            "filename": row["filename"] or "Untitled",
            "language": row["language"] or "Unknown",
            "issues_count": row["issues_count"] or 0,
            "quality_score": row["quality_score"] or 0,
            "created_at": row["created_at"]
        })


    # =====================================================
    # CODE QUALITY
    # =====================================================

    quality_row = connection.execute(
        """
        SELECT
            AVG(quality_score) AS quality,
            AVG(quality_score) AS maintainability,
            AVG(quality_score) AS reliability,
            AVG(quality_score) AS security,
            AVG(quality_score) AS readability
        FROM analyses
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()


    quality_score = 0

    quality_breakdown = {
        "quality": 0,
        "maintainability": 0,
        "reliability": 0,
        "security": 0,
        "readability": 0
    }


    if quality_row:

        quality_score = round(
            float(quality_row["quality"] or 0)
        )

        quality_breakdown = {
            "quality": round(
                float(quality_row["quality"] or 0)
            ),
            "maintainability": round(
                float(quality_row["maintainability"] or 0)
            ),
            "reliability": round(
                float(quality_row["reliability"] or 0)
            ),
            "security": round(
                float(quality_row["security"] or 0)
            ),
            "readability": round(
                float(quality_row["readability"] or 0)
            )
        }


    connection.close()


    # =====================================================
    # RESPONSE
    # =====================================================

    return jsonify({

        "success": True,

        "total_analyses": total_analyses,

        "total_issues": total_issues,

        "reports": reports,

        "saved_code": saved_code,

        "recent_analyses": recent_analyses,

        "quality_score": quality_score,

        "quality_breakdown": quality_breakdown

    })
    # =========================================================
    # AVERAGE FUNCTION
    # =========================================================

    def average_score(scores):

        if not scores:

            return 0

        return round(
            sum(scores) / len(scores),
            1
        )


    # =========================================================
    # FINAL QUALITY BREAKDOWN
    # =========================================================

    maintainability_score = average_score(
        maintainability_scores
    )


    reliability_score = average_score(
        reliability_scores
    )


    security_score = average_score(
        security_scores
    )


    readability_score = average_score(
        readability_scores
    )


    quality_breakdown = {

        "code_quality": quality_score,

        "maintainability":
            maintainability_score,

        "reliability":
            reliability_score,

        "security":
            security_score,

        "readability":
            readability_score

    }


    # =========================================================
    # RECENT ANALYSES
    # =========================================================

    recent_rows = connection.execute(
        """
        SELECT
            id,
            filename,
            language,
            issues_count,
            quality_score,
            created_at
        FROM analyses
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 5
        """,
        (user_id,)
    ).fetchall()


    recent_analyses = []


    for row in recent_rows:

        recent_analyses.append({

            "id":
                row["id"],

            "filename":
                row["filename"]
                or "Untitled Code",

            "language":
                row["language"]
                or "Unknown",

            "issues":
                row["issues_count"]
                or 0,

            "quality_score":
                round(
                    float(
                        row["quality_score"]
                        or 0
                    ),
                    1
                ),

            "created_at":
                row["created_at"]

        })


    connection.close()


    # =========================================================
    # RESPONSE
    # =========================================================

    return jsonify({

        "success": True,

        "total_analyses":
            total_analyses,

        "total_issues":
            total_issues,

        "refactorings":
            refactorings,

        "reports":
            reports,

        "saved_code":
            saved_code,

        "quality_score":
            quality_score,

        "quality_breakdown":
            quality_breakdown,

        "recent_analyses":
            recent_analyses

    })
# =========================================================
# ANALYZE PAGE
# =========================================================

@app.route("/analyze")
@login_required
def analyze():

    user = get_current_user()

    first_letter = "U"


    if user:

        name = (
            user["full_name"]
            or user["username"]
            or "User"
        )

        first_letter = name[0].upper()


    return render_template(
        "analyze.html",
        user=user,
        first_letter=first_letter
    )


# =========================================================
# CODELENS - STATIC ANALYSIS ENGINE
# Python + Java + C++
# =========================================================

# This section intentionally contains only analysis helpers.
# Existing Flask routes below this section are preserved.

import ast
import builtins
import keyword
from collections import Counter
import re


def _python_builtin_names():
    return set(dir(builtins)) | set(keyword.kwlist)


def _issue(severity, issue, line, details, suggestion=""):
    return {
        "severity": severity,
        "issue": issue,
        "line": int(line or 1),
        "details": details,
        "suggestion": suggestion,
        "type": issue,
        "message": details
    }


def _dedupe_issues(issues):
    seen = set()
    result = []
    order = {"Error": 0, "Warning": 1, "Info": 2}
    for item in issues:
        key = (
            item.get("line", 0),
            item.get("severity", "Info"),
            item.get("issue", ""),
            item.get("details", "")
        )
        if key not in seen:
            seen.add(key)
            result.append(item)
    result.sort(key=lambda x: (
        x.get("line", 0),
        order.get(x.get("severity", "Info"), 9),
        x.get("issue", "")
    ))
    return result


def _make_analysis(issues, metrics, complexity=None):
    issues = _dedupe_issues(issues)
    score = 100
    for item in issues:
        if item.get("severity") == "Error":
            score -= 15
        elif item.get("severity") == "Warning":
            score -= 5
        else:
            score -= 1
    return {
        "issues": issues,
        "issues_count": len(issues),
        "quality_score": max(0, min(100, score)),
        "complexity": complexity or {"score": 0, "level": "Low"},
        "metrics": metrics
    }


def _generic_metrics(code, language=""):
    lines = code.splitlines()
    blank = sum(1 for x in lines if not x.strip())
    if language == "python":
        comments = sum(1 for x in lines if x.strip().startswith("#"))
    else:
        comments = sum(1 for x in lines if (
            x.strip().startswith("//") or
            x.strip().startswith("/*") or
            x.strip().startswith("*") or
            x.strip().startswith("#")
        ))
    return lines, {
        "total_lines": len(lines),
        "code_lines": max(0, len(lines) - blank - comments),
        "comment_lines": comments,
        "blank_lines": blank,
        "functions": 0,
        "classes": 0,
        "imports": 0,
        "global_variables": 0
    }


def _complexity_from_text(code):
    patterns = [
        r"\bif\b", r"\belif\b", r"\belse\s+if\b", r"\bfor\b",
        r"\bwhile\b", r"\bcase\b", r"\bcatch\b", r"\bexcept\b",
        r"\bswitch\b", r"&&", r"\|\|", r"\?[^:]+:"
    ]
    score = 1 + sum(len(__import__("re").findall(p, code)) for p in patterns)
    level = "Low" if score <= 5 else "Medium" if score <= 10 else "High" if score <= 20 else "Very High"
    return {"score": score, "level": level}


# =========================================================
# CODELENS - STATIC ANALYSIS ENGINE
# =========================================================


class _PyScope:
    def __init__(self, parent=None, kind="module"):
        self.parent = parent
        self.kind = kind
        self.defined = set()
        self.global_names = set()
        self.nonlocal_names = set()

    def root(self):
        scope = self
        while scope.parent is not None:
            scope = scope.parent
        return scope

    def contains(self, name):
        if name in self.defined:
            return True
        if name in self.global_names:
            return name in self.root().defined
        if name in self.nonlocal_names:
            scope = self.parent
            while scope is not None:
                if scope.kind == "function" and name in scope.defined:
                    return True
                scope = scope.parent
            return False
        return self.parent.contains(name) if self.parent else False


def _python_builtin_names():
    return set(dir(builtins)) | set(keyword.kwlist)


def _issue(severity, issue, line, details, suggestion=""):
    return {
        "severity": severity,
        "issue": issue,
        "line": int(line or 1),
        "details": details,
        "suggestion": suggestion,
        "type": issue,
        "message": details,
    }


def _dedupe_issues(issues):
    seen = set()
    result = []
    order = {"Error": 0, "Warning": 1, "Info": 2}
    for item in issues:
        key = (
            item.get("line", 0),
            item.get("severity", "Info"),
            item.get("issue", ""),
            item.get("details", ""),
        )
        if key not in seen:
            seen.add(key)
            result.append(item)
    result.sort(key=lambda x: (
        x.get("line", 0),
        order.get(x.get("severity", "Info"), 9),
        x.get("issue", ""),
    ))
    return result


def _make_analysis(issues, metrics, complexity=None):
    issues = _dedupe_issues(issues)
    score = 100
    for item in issues:
        if item.get("severity") == "Error":
            score -= 15
        elif item.get("severity") == "Warning":
            score -= 5
        else:
            score -= 1
    return {
        "issues": issues,
        "issues_count": len(issues),
        "quality_score": max(0, min(100, score)),
        "complexity": complexity or {"score": 0, "level": "Low"},
        "metrics": metrics,
    }


def _generic_metrics(code, language=""):
    lines = code.splitlines()
    blank = sum(1 for line in lines if not line.strip())
    if language == "python":
        comments = sum(1 for line in lines if line.strip().startswith("#"))
    else:
        comments = sum(
            1 for line in lines
            if line.strip().startswith(("//", "/*", "*"))
        )
    return lines, {
        "total_lines": len(lines),
        "code_lines": max(0, len(lines) - blank - comments),
        "comment_lines": comments,
        "blank_lines": blank,
        "functions": 0,
        "classes": 0,
        "imports": 0,
        "global_variables": 0,
    }


def _complexity_from_text(code):
    patterns = [
        r"\bif\b", r"\belif\b", r"\belse\s+if\b", r"\bfor\b",
        r"\bwhile\b", r"\bcase\b", r"\bcatch\b", r"\bexcept\b",
        r"\bswitch\b", r"&&", r"\|\|", r"\?[^:]+:",
    ]
    score = 1 + sum(len(re.findall(pattern, code)) for pattern in patterns)
    level = (
        "Low" if score <= 5 else
        "Medium" if score <= 10 else
        "High" if score <= 20 else
        "Very High"
    )
    return {"score": score, "level": level}


# =========================================================
# PYTHON ANALYSIS
# =========================================================


def _target_names(target):
    if isinstance(target, ast.Name):
        return {target.id}
    if isinstance(target, (ast.Tuple, ast.List)):
        result = set()
        for item in target.elts:
            result.update(_target_names(item))
        return result
    if isinstance(target, ast.Starred):
        return _target_names(target.value)
    return set()


def _function_args(node):
    args = node.args
    names = {x.arg for x in args.posonlyargs + args.args + args.kwonlyargs}
    if args.vararg:
        names.add(args.vararg.arg)
    if args.kwarg:
        names.add(args.kwarg.arg)
    return names


def _bind_from_statement(node, scope):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            scope.defined.update(_target_names(target))
    elif isinstance(node, ast.AnnAssign):
        scope.defined.update(_target_names(node.target))
    elif isinstance(node, ast.AugAssign):
        scope.defined.update(_target_names(node.target))
    elif isinstance(node, (ast.For, ast.AsyncFor)):
        scope.defined.update(_target_names(node.target))
    elif isinstance(node, (ast.With, ast.AsyncWith)):
        for item in node.items:
            if item.optional_vars:
                scope.defined.update(_target_names(item.optional_vars))
    elif isinstance(node, ast.ExceptHandler) and node.name:
        scope.defined.add(node.name)
    elif isinstance(node, (ast.Import, ast.ImportFrom)):
        for alias in node.names:
            if alias.name != "*":
                scope.defined.add(alias.asname or alias.name.split(".")[0])
    elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        scope.defined.add(node.name)


def _collect_scope_bindings(body, scope):
    for node in body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            scope.defined.add(node.name)
            continue
        if isinstance(node, ast.Global):
            scope.global_names.update(node.names)
            continue
        if isinstance(node, ast.Nonlocal):
            scope.nonlocal_names.update(node.names)
            continue
        _bind_from_statement(node, scope)
        if isinstance(node, (ast.Lambda,)):
            continue
        _collect_scope_bindings(list(ast.iter_child_nodes(node)), scope)


def _scan_scope_loads(node, scope, issues, builtins_set):

    # -----------------------------------------------------
    # CLASS DEFINITIONS
    # -----------------------------------------------------
    # Do not skip the class bases.
    # Example:
    # class Day(Enum):
    #
    # If Enum is not imported/defined, it must be reported.
    # -----------------------------------------------------

    if isinstance(node, ast.ClassDef):

        # Check base classes
        for base in node.bases:
            _scan_scope_loads(
                base,
                scope,
                issues,
                builtins_set
            )

        # Check decorators
        for decorator in node.decorator_list:
            _scan_scope_loads(
                decorator,
                scope,
                issues,
                builtins_set
            )

        # Check keyword arguments in class definition
        for keyword in node.keywords:
            _scan_scope_loads(
                keyword.value,
                scope,
                issues,
                builtins_set
            )

        return

    # -----------------------------------------------------
    # FUNCTION DEFINITIONS
    # -----------------------------------------------------

    if isinstance(
        node,
        (
            ast.FunctionDef,
            ast.AsyncFunctionDef,
            ast.Lambda
        )
    ):

        # Function decorators can contain names
        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef
            )
        ):

            for decorator in node.decorator_list:

                _scan_scope_loads(
                    decorator,
                    scope,
                    issues,
                    builtins_set
                )

            # Default arguments
            for default in node.args.defaults:

                _scan_scope_loads(
                    default,
                    scope,
                    issues,
                    builtins_set
                )

            for default in node.args.kw_defaults:

                if default is not None:

                    _scan_scope_loads(
                        default,
                        scope,
                        issues,
                        builtins_set
                    )

        return

    # -----------------------------------------------------
    # NAME USAGE
    # -----------------------------------------------------

    if isinstance(node, ast.Name) and isinstance(
        node.ctx,
        ast.Load
    ):

        if (
            node.id not in builtins_set
            and not scope.contains(node.id)
        ):

            issues.append(
                _issue(
                    "Error",
                    "Undefined Name",
                    node.lineno,
                    f"`{node.id}` is used but is not defined or imported in the reachable scope.",
                    f"Define or import `{node.id}` before using it."
                )
            )

        return

    # -----------------------------------------------------
    # CHECK CHILD NODES
    # -----------------------------------------------------

    for child in ast.iter_child_nodes(node):

        _scan_scope_loads(
            child,
            scope,
            issues,
            builtins_set
        )


def _python_undefined_names(tree):
    issues = []
    builtins_set = _python_builtin_names()
    module = _PyScope(None, "module")
    _collect_scope_bindings(tree.body, module)
    for node in tree.body:
        _scan_scope_loads(node, module, issues, builtins_set)

    def visit_function(node, parent):
        scope = _PyScope(parent, "function")
        scope.defined.update(_function_args(node))
        _collect_scope_bindings(node.body, scope)
        for statement in node.body:
            _scan_scope_loads(statement, scope, issues, builtins_set)
        for statement in node.body:
            for child in ast.walk(statement):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)) and child is not node:
                    visit_function(child, scope)
                elif isinstance(child, ast.ClassDef):
                    for method in child.body:
                        if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            visit_function(method, parent)

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            visit_function(node, module)
        elif isinstance(node, ast.ClassDef):
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    visit_function(child, module)
    return issues


def _python_duplicate_imports(tree):
    seen = {}
    issues = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                key = alias.name
                if key in seen:
                    issues.append(_issue(
                        "Warning", "Duplicate Import", node.lineno,
                        f"`{key}` is imported more than once.",
                        "Remove the duplicate import.",
                    ))
                seen[key] = node.lineno
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                key = f"{node.module or ''}.{alias.name}"
                if key in seen:
                    issues.append(_issue(
                        "Warning", "Duplicate Import", node.lineno,
                        f"`{key}` is imported more than once.",
                        "Remove the duplicate import.",
                    ))
                seen[key] = node.lineno
    return issues


def _python_unused_imports(tree):
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((alias.asname or alias.name.split(".")[0], node.lineno))
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name != "*":
                    imports.append((alias.asname or alias.name, node.lineno))
    used = {
        n.id for n in ast.walk(tree)
        if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)
    }
    return [
        _issue(
            "Warning", "Unused Import", line,
            f"Imported name `{name}` is never used.",
            "Remove the unused import.",
        )
        for name, line in imports if name not in used
    ]


def _python_unused_variables(tree):
    issues = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        args = _function_args(fn)
        assigned = {}
        used = set()
        for node in ast.walk(fn):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node is not fn:
                continue
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Store) and node.id not in args:
                    assigned.setdefault(node.id, node.lineno)
                elif isinstance(node.ctx, ast.Load):
                    used.add(node.id)
        for name, line in assigned.items():
            if name.startswith("_") or name in {"self", "cls"}:
                continue
            if name not in used:
                issues.append(_issue(
                    "Warning", "Unused Variable", line,
                    f"Variable `{name}` is assigned but never used.",
                    "Remove the assignment or use the variable.",
                ))
    return issues


def _python_quality_checks(tree, code):
    issues = []
    lines = code.splitlines()
    builtins_set = set(dir(builtins))

    # Built-in shadowing.
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node.name in builtins_set:
                issues.append(_issue(
                    "Warning", "Built-in Shadowing", node.lineno,
                    f"`{node.name}` shadows a Python built-in name.",
                    "Rename it to avoid hiding the built-in.",
                ))
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if node.id in builtins_set and node.id not in {"id"}:
                issues.append(_issue(
                    "Warning", "Built-in Shadowing", node.lineno,
                    f"`{node.id}` shadows a Python built-in name.",
                    "Rename the variable.",
                ))

    # Functions, defaults, globals and nesting.
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        length = getattr(node, "end_lineno", node.lineno) - node.lineno + 1
        if length > 50:
            issues.append(_issue(
                "Warning", "Long Function", node.lineno,
                f"Function `{node.name}` contains {length} lines.",
                "Split the function into smaller logical units.",
            ))
        count = len(_function_args(node))
        if count > 6:
            issues.append(_issue(
                "Warning", "Too Many Arguments", node.lineno,
                f"Function `{node.name}` has {count} parameters.",
                "Simplify the function interface or group related values.",
            ))
        defaults = list(node.args.defaults) + [x for x in node.args.kw_defaults if x is not None]
        for default in defaults:
            if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                issues.append(_issue(
                    "Warning", "Mutable Default Argument", default.lineno,
                    f"Function `{node.name}` uses a mutable default argument.",
                    "Use None and create the mutable object inside the function.",
                ))

    # None / identity comparison mistakes.
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(comparator, ast.Constant) and comparator.value is None:
                    if isinstance(op, (ast.Eq, ast.NotEq)):
                        issues.append(_issue(
                            "Warning", "None Comparison", node.lineno,
                            "Use `is None` / `is not None` for None checks.",
                            "Replace equality with identity comparison.",
                        ))
                if isinstance(op, (ast.Is, ast.IsNot)) and isinstance(comparator, ast.Constant):
                    if comparator.value not in (None, True, False, Ellipsis, NotImplemented):
                        issues.append(_issue(
                            "Warning", "Incorrect Identity Comparison", node.lineno,
                            "`is` compares object identity, not ordinary value equality.",
                            "Use `==` / `!=` for value comparison.",
                        ))

    # Exceptions.
    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                issues.append(_issue(
                    "Warning", "Bare Except", node.lineno,
                    "Bare `except:` catches every exception.",
                    "Catch the specific exception types that are expected.",
                ))
            if not node.body or all(isinstance(x, ast.Pass) for x in node.body):
                issues.append(_issue(
                    "Warning", "Exception Swallowed", node.lineno,
                    "The exception is silently ignored.",
                    "Handle, log, or deliberately re-raise the exception.",
                ))

    # Dangerous execution / process / deserialization.
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = ""
        if isinstance(node.func, ast.Name):
            name = node.func.id
        elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            name = f"{node.func.value.id}.{node.func.attr}"

        if name in {"eval", "exec", "compile", "__import__"}:
            issues.append(_issue(
                "Error", "Dangerous Dynamic Execution", node.lineno,
                f"`{name}()` can execute dynamically supplied code.",
                "Avoid dynamic execution or strictly validate trusted input.",
            ))
        elif name in {"os.system", "os.popen", "subprocess.call", "subprocess.run", "subprocess.Popen"}:
            shell_true = any(
                isinstance(keyword_arg, ast.keyword)
                and keyword_arg.arg == "shell"
                and isinstance(keyword_arg.value, ast.Constant)
                and keyword_arg.value.value is True
                for keyword_arg in node.keywords
            )
            severity = "Error" if shell_true else "Warning"
            issues.append(_issue(
                severity, "Process Execution", node.lineno,
                f"`{name}()` starts an operating-system process.",
                "Use argument lists and never pass untrusted text to a shell.",
            ))
        elif name in {"pickle.load", "pickle.loads"}:
            issues.append(_issue(
                "Error", "Unsafe Deserialization", node.lineno,
                "Untrusted pickle data can execute arbitrary code during deserialization.",
                "Use a safe serialization format for untrusted data.",
            ))

        if name == "open" and node.args:
            first = node.args[0]
            if isinstance(first, ast.Call) and isinstance(first.func, ast.Name) and first.func.id == "input":
                issues.append(_issue(
                    "Warning", "Unvalidated File Path", node.lineno,
                    "A user-supplied value is used directly as a file path.",
                    "Validate and constrain paths before opening files.",
                ))

    # SQL injection.
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr.lower() in {"execute", "executemany", "executescript"} and node.args:
                arg = node.args[0]
                if isinstance(arg, (ast.JoinedStr, ast.BinOp)):
                    issues.append(_issue(
                        "Error", "Possible SQL Injection", node.lineno,
                        "SQL execution receives dynamically constructed text.",
                        "Use parameterized queries instead of string interpolation.",
                    ))

    # Conditions / unreachable / recursion.
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and isinstance(node.test, ast.Constant) and isinstance(node.test.value, bool):
            issues.append(_issue(
                "Warning", "Constant Condition", node.lineno,
                f"The condition is always `{node.test.value}`.",
                "Remove the unreachable branch or use a runtime condition.",
            ))
        if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True:
            if not any(isinstance(x, ast.Break) for x in ast.walk(node)):
                issues.append(_issue(
                    "Warning", "Potential Infinite Loop", node.lineno,
                    "The loop condition is always True and no break was found.",
                    "Add a reachable termination condition.",
                ))

    def check_block(body):
        terminated = False
        for statement in body:
            if terminated:
                issues.append(_issue(
                    "Warning", "Unreachable Code", statement.lineno,
                    "This statement follows an unconditional return/raise/break/continue.",
                    "Remove the unreachable statement or restructure the control flow.",
                ))
            if isinstance(statement, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
                terminated = True
            if isinstance(statement, ast.If):
                check_block(statement.body)
                check_block(statement.orelse)
            elif isinstance(statement, (ast.For, ast.AsyncFor, ast.While, ast.With, ast.AsyncWith)):
                check_block(statement.body)
                check_block(getattr(statement, "orelse", []))
            elif isinstance(statement, ast.Try):
                check_block(statement.body)
                for handler in statement.handlers:
                    check_block(handler.body)
                check_block(statement.orelse)
                check_block(statement.finalbody)
    check_block(tree.body)

    # Duplicate if/elif conditions.
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            conditions = set()
            current = node
            while isinstance(current, ast.If):
                key = ast.dump(current.test, include_attributes=False)
                if key in conditions:
                    issues.append(_issue(
                        "Warning", "Duplicate Condition", current.lineno,
                        "The same condition appears more than once in this conditional chain.",
                        "Remove or correct the duplicate branch.",
                    ))
                conditions.add(key)
                current = current.orelse[0] if len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If) else None

    # Potential ID collision.
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            if isinstance(node.right, ast.Constant) and node.right.value == 1:
                left = node.left
                if (
                    isinstance(left, ast.Call)
                    and isinstance(left.func, ast.Name)
                    and left.func.id == "len"
                    and len(left.args) == 1
                    and isinstance(left.args[0], ast.Name)
                ):
                    name = left.args[0].id
                    issues.append(_issue(
                        "Warning", "Potential ID Collision", node.lineno,
                        f"`len({name}) + 1` can reuse an existing ID after an item is removed.",
                        "Use a persistent unique ID strategy.",
                    ))

    # Global mutable state and TODO/FIXME markers.
    for node in tree.body:
        if isinstance(node, ast.Global):
            issues.append(_issue(
                "Warning", "Global State", node.lineno,
                "Global state can make code harder to test and maintain.",
                "Prefer passing state explicitly or encapsulating it.",
            ))
        if isinstance(node, ast.Assign):
            if isinstance(node.value, (ast.List, ast.Dict, ast.Set)):
                issues.append(_issue(
                    "Warning", "Mutable Global State", node.lineno,
                    "A mutable collection is defined at module scope.",
                    "Encapsulate mutable state or initialize it inside a function.",
                ))

    for line_no, line in enumerate(lines, 1):
        if len(line) > 120:
            issues.append(_issue(
                "Warning", "Long Line", line_no,
                f"Line contains {len(line)} characters.",
                "Break the statement into smaller readable lines.",
            ))
        if re.search(r"\b(?:TODO|FIXME)\b", line, re.I):
            issues.append(_issue(
                "Warning", "Pending TODO/FIXME", line_no,
                "The code contains a TODO/FIXME marker.",
                "Resolve the pending task before submission.",
            ))

    # Return-path analysis: Python permits an implicit None return, so only
    # report a missing return when a function already returns a value on at
    # least one path and another reachable path can fall through to the end.
    def _stmt_can_fall_through(stmt):
        if isinstance(stmt, (ast.Return, ast.Raise, ast.Break, ast.Continue)):
            return False

        if isinstance(stmt, ast.If):
            body_fall = _block_can_fall_through(stmt.body)
            if not stmt.orelse:
                return True
            else_fall = _block_can_fall_through(stmt.orelse)
            return body_fall or else_fall

        if isinstance(stmt, (ast.For, ast.AsyncFor, ast.While)):
            # Loops may execute zero times, so conservatively treat them as
            # fall-through unless the loop is an obvious unconditional loop
            # with no reachable break.
            if isinstance(stmt, ast.While) and isinstance(stmt.test, ast.Constant) and stmt.test.value is True:
                loop_nodes = list(ast.walk(stmt))
                if not any(isinstance(n, ast.Break) for n in loop_nodes):
                    return False
            return True

        if isinstance(stmt, ast.Try):
            # Every normal path must terminate for a try statement to be
            # considered non-fall-through. Exception handlers/finally can
            # still provide a path out, so be conservative.
            if stmt.finalbody:
                return _block_can_fall_through(stmt.finalbody)
            body_fall = _block_can_fall_through(stmt.body)
            handler_fall = any(_block_can_fall_through(h.body) for h in stmt.handlers)
            else_fall = _block_can_fall_through(stmt.orelse) if stmt.orelse else body_fall
            return body_fall or handler_fall or else_fall

        if hasattr(ast, "Match") and isinstance(stmt, ast.Match):
            if not stmt.cases:
                return True
            return any(_block_can_fall_through(case.body) for case in stmt.cases)

        return True

    def _block_can_fall_through(statements):
        for statement in statements:
            if not _stmt_can_fall_through(statement):
                return False
        return True

    # Mixed return behavior, missing return paths, and recursion without an
    # obvious base branch.
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        returns = [node for node in ast.walk(fn) if isinstance(node, ast.Return)]
        has_value = any(node.value is not None for node in returns)
        has_empty = any(node.value is None for node in returns)
        if returns and has_value and has_empty:
            issues.append(_issue(
                "Warning", "Inconsistent Return", fn.lineno,
                f"Function `{fn.name}` mixes value-returning and empty returns.",
                "Return a consistent value or explicitly document the optional result.",
            ))

        if has_value and _block_can_fall_through(fn.body):
            issues.append(_issue(
                "Warning", "Missing Return Statement", fn.lineno,
                f"Function `{fn.name}` returns a value on some paths but can reach the end without returning a value.",
                "Add a return value to every reachable execution path, or make the function consistently return None.",
            ))

        recursive = any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == fn.name
            for node in ast.walk(fn)
        )
        if recursive:
            has_conditional = any(isinstance(node, (ast.If, ast.Match)) for node in ast.walk(fn)) if hasattr(ast, "Match") else any(isinstance(node, ast.If) for node in ast.walk(fn))
            if not has_conditional:
                issues.append(_issue(
                    "Warning", "Recursion Without Visible Base Case", fn.lineno,
                    f"Function `{fn.name}` calls itself without an obvious conditional base case.",
                    "Ensure recursion has a reachable terminating condition.",
                ))

    # Empty branches and excessive nesting.
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.While, ast.With, ast.Try)):
            body = getattr(node, "body", [])
            if body and all(isinstance(item, ast.Pass) for item in body):
                issues.append(_issue(
                    "Warning", "Empty Branch", node.lineno,
                    "A control-flow branch contains only `pass`.",
                    "Implement the branch or document why it is intentionally empty.",
                ))

    def nesting_depth(node, depth=0):
        max_depth = depth
        if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.With, ast.AsyncWith)):
            depth += 1
            max_depth = max(max_depth, depth)
        for child in ast.iter_child_nodes(node):
            max_depth = max(max_depth, nesting_depth(child, depth))
        return max_depth

    depth = nesting_depth(tree)
    if depth >= 5:
        issues.append(_issue(
            "Warning", "Deep Nesting", 1,
            f"Control-flow nesting reaches depth {depth}.",
            "Extract nested logic into smaller functions.",
        ))

    # Duplicate consecutive source lines: conservative, ignores comments/blank lines.
    cleaned = [re.sub(r"\s+", " ", line.strip()) for line in lines if line.strip() and not line.strip().startswith("#")]
    seen_windows = {}
    for i in range(len(cleaned) - 2):
        window = tuple(cleaned[i:i + 3])
        if all(window) and window in seen_windows:
            issues.append(_issue(
                "Warning", "Duplicate Code Block", 1,
                "A three-line code pattern is repeated in the source.",
                "Extract repeated logic into a reusable function.",
            ))
            break
        seen_windows[window] = i

    # Hard-coded secrets.
    secret_re = re.compile(
        r"\b(password|passwd|secret|api[_-]?key|access[_-]?token|auth[_-]?token|private[_-]?key)\b\s*=\s*['\"][^'\"]+['\"]",
        re.I,
    )
    for line_no, line in enumerate(lines, 1):
        if secret_re.search(line):
            issues.append(_issue(
                "Error", "Hardcoded Secret", line_no,
                "A password, secret, token, or key appears to be hard-coded.",
                "Move secrets to environment variables or a secure secret store.",
            ))

    return issues


def _python_complexity(tree):
    score = 1
    for node in ast.walk(tree):
        if isinstance(node, (ast.If, ast.For, ast.AsyncFor, ast.While, ast.Try, ast.ExceptHandler, ast.With, ast.AsyncWith, ast.IfExp)):
            score += 1
        elif isinstance(node, ast.BoolOp):
            score += max(0, len(node.values) - 1)
        elif isinstance(node, ast.comprehension):
            score += 1
        elif hasattr(ast, "Match") and isinstance(node, ast.Match):
            score += len(node.cases)
    level = "Low" if score <= 5 else "Medium" if score <= 10 else "High" if score <= 20 else "Very High"
    return {"score": score, "level": level}



def _advanced_python_review(code, tree):
    """Broad, conservative Python review layer. Keeps normal I/O valid and adds
    high-confidence syntax/quality/security/logic/performance checks."""
    issues = []
    lines = code.splitlines()
    builtin_names = set(dir(__builtins__)) if isinstance(__builtins__, dict) else set(dir(__builtins__))

    # Duplicate definitions / wildcard imports / shadowed builtins.
    seen_defs = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            key = (type(node).__name__, node.name)
            if key in seen_defs:
                issues.append(_issue("Warning", "Duplicate Definition", node.lineno,
                                     f"`{node.name}` is defined more than once in this module.",
                                     "Remove the duplicate definition or give it a distinct purpose/name."))
            else:
                seen_defs[key] = node.lineno

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and any(alias.name == "*" for alias in node.names):
            issues.append(_issue("Warning", "Wildcard Import", node.lineno,
                                 "Wildcard imports make dependencies and name resolution unclear.",
                                 "Import only the names that are actually used."))
        if isinstance(node, ast.Name) and node.id in builtin_names and isinstance(node.ctx, ast.Store):
            if node.id not in {"id", "input", "print"}:
                issues.append(_issue("Warning", "Shadowed Builtin", node.lineno,
                                     f"`{node.id}` shadows a Python built-in name.",
                                     "Rename the variable or function to avoid hiding the built-in."))

    # Common correctness/style traps.
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare):
            for op, comparator in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(comparator, ast.Constant) and comparator.value is None:
                    issues.append(_issue("Warning", "None Comparison", node.lineno,
                                         "None is compared with == or != instead of identity comparison.",
                                         "Use `is None` or `is not None`."))
                if isinstance(op, (ast.Is, ast.IsNot)) and isinstance(comparator, ast.Constant) and isinstance(comparator.value, (str, int, float, bool, bytes)):
                    issues.append(_issue("Warning", "Identity Comparison", node.lineno,
                                         "`is`/`is not` compares object identity, not value equality for ordinary literals.",
                                         "Use == or != for value comparison."))
        if isinstance(node, ast.ExceptHandler):
            if node.type is None:
                issues.append(_issue("Warning", "Bare Except", node.lineno,
                                     "A bare except catches every exception, including system-exiting exceptions.",
                                     "Catch the specific exception types you can handle."))
            elif isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"}:
                if node.body and all(isinstance(x, ast.Pass) for x in node.body):
                    issues.append(_issue("Warning", "Exception Swallowed", node.lineno,
                                         "The exception is caught and silently ignored.",
                                         "Handle, log, or deliberately re-raise the exception."))
                else:
                    issues.append(_issue("Info", "Broad Exception Handler", node.lineno,
                                         f"`except {node.type.id}` may hide unrelated failures.",
                                         "Catch a narrower exception where practical."))
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Div, ast.FloorDiv, ast.Mod)):
            if isinstance(node.right, ast.Constant) and isinstance(node.right.value, (int, float)) and node.right.value == 0:
                issues.append(_issue("Error", "Division By Zero", node.lineno,
                                     "The expression divides by a constant zero.",
                                     "Correct the denominator or validate it before division."))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
            if not any(isinstance(parent, ast.With) for parent in []):
                # Heuristic handled below from source lines; don't flag open used with context managers.
                pass

    # Suspicious assignment inside conditions (walrus is valid, so don't flag it).
    for no, line in enumerate(lines, 1):
        code_line = _mask_python_line(line)
        if re.search(r"\bif\s*\([^)]*\b\w+\s*=\s*[^=]", code_line) or re.search(r"\bwhile\s*\([^)]*\b\w+\s*=\s*[^=]", code_line):
            issues.append(_issue("Error", "Assignment In Condition", no,
                                 "An assignment appears where a comparison was likely intended.",
                                 "Use == for comparison or := explicitly when assignment expressions are intended."))
        if re.search(r"\b(?:random\.random|random\.randint|random\.choice)\s*\(", line) and re.search(r"(?:token|secret|password|otp|auth|key)", code, re.I):
            issues.append(_issue("Warning", "Weak Randomness", no,
                                 "The standard random module is not intended for security-sensitive values.",
                                 "Use the secrets module for tokens, passwords, OTPs, and security-sensitive randomness."))
        if re.search(r"\b(?:open|Path)\s*\([^\n]*(?:input\s*\(|request\.|args\b|query\b)", line, re.I):
            issues.append(_issue("Warning", "Unvalidated File Path", no,
                                 "External input appears to influence a filesystem path.",
                                 "Validate and constrain the path to an allowed directory."))
        if re.search(r"\b(?:os\.system|os\.popen)\s*\(", line) or re.search(r"\bsubprocess\.(?:run|call|Popen|check_output|check_call)\s*\(", line):
            if re.search(r"shell\s*=\s*True", line):
                issues.append(_issue("Error", "Shell Command Injection Risk", no,
                                     "A subprocess call enables shell interpretation.",
                                     "Use shell=False and pass a list of arguments."))
        if re.search(r"\b(?:requests|httpx|urllib)\b.*https?://", line, re.I) and "http://" in line.lower():
            issues.append(_issue("Warning", "Unencrypted HTTP", no,
                                 "An HTTP URL transmits data without TLS protection.",
                                 "Use HTTPS for sensitive or authenticated traffic."))
        if re.search(r"\b(?:open|io\.open)\s*\(", line) and "with " not in line and not re.search(r"\.close\s*\(", code):
            issues.append(_issue("Warning", "Possible Resource Leak", no,
                                 "A file is opened without an obvious context manager or close call.",
                                 "Prefer `with open(...) as f:` so the file is closed reliably."))
        if re.search(r"\b(?:raise\s+Exception|raise\s+RuntimeError)\s*\(", line):
            issues.append(_issue("Info", "Generic Exception", no,
                                 "A generic exception type reduces the precision of error handling.",
                                 "Raise a specific exception type that describes the failure."))
        if re.search(r"\b(?:time\.sleep|sleep)\s*\(", line):
            issues.append(_issue("Info", "Blocking Sleep", no,
                                 "A sleep call blocks the current execution flow.",
                                 "Use event-driven/asynchronous waiting when blocking is unnecessary."))
        if re.search(r"\b(?:TODO|FIXME|HACK)\b", line, re.I):
            issues.append(_issue("Info", "Pending Marker", no,
                                 "A pending development marker remains in the source.",
                                 "Resolve or document the pending work before release."))

    # Detect direct open() calls not wrapped in a with statement more reliably.
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
            parent_with = False
            # Find source context by line; a line beginning with `with` is safe.
            line = lines[node.lineno - 1] if 0 < node.lineno <= len(lines) else ""
            if re.match(r"\s*with\b", line):
                parent_with = True
            if not parent_with and not re.search(r"\.close\s*\(\s*\)", code):
                issues.append(_issue("Warning", "Possible Resource Leak", node.lineno,
                                     "open() is not visibly managed by a context manager or close().",
                                     "Prefer a with-statement for deterministic file cleanup."))

    return issues


def _mask_python_line(line):
    """Lightweight masking of quoted text for Python line-level heuristics."""
    try:
        return re.sub(r"(['\"]).*?\1", "\"\"", line)
    except re.error:
        return line


def _advanced_java_review(code):
    """Broad conservative Java review layer. Compiler diagnostics remain authoritative."""
    issues = []
    lines = code.splitlines()
    masked = _mask_c_like(code)

    # Imports: duplicate and unused are handled elsewhere; detect common missing imports.
    common_imports = {
        "Scanner": "java.util.Scanner", "ArrayList": "java.util.ArrayList", "LinkedList": "java.util.LinkedList",
        "HashMap": "java.util.HashMap", "HashSet": "java.util.HashSet", "TreeMap": "java.util.TreeMap",
        "List": "java.util.List", "Map": "java.util.Map", "Set": "java.util.Set", "Queue": "java.util.Queue",
        "Deque": "java.util.Deque", "Collections": "java.util.Collections", "Arrays": "java.util.Arrays",
        "BufferedReader": "java.io.BufferedReader", "InputStreamReader": "java.io.InputStreamReader",
        "FileReader": "java.io.FileReader", "FileWriter": "java.io.FileWriter", "BufferedWriter": "java.io.BufferedWriter",
        "FileInputStream": "java.io.FileInputStream", "FileOutputStream": "java.io.FileOutputStream",
        "Path": "java.nio.file.Path", "Paths": "java.nio.file.Paths", "Files": "java.nio.file.Files",
        "LocalDate": "java.time.LocalDate", "LocalDateTime": "java.time.LocalDateTime", "DateTimeFormatter": "java.time.format.DateTimeFormatter",
    }
    imported = set(re.findall(r"^\s*import\s+(?:static\s+)?([\w.]+);", code, re.M))
    imported_simple = {x.split('.')[-1] for x in imported}
    for name, fqcn in common_imports.items():
        if re.search(r"\b" + re.escape(name) + r"\b", masked) and name not in imported_simple:
            # java.lang types and declarations do not need imports.
            if name not in {"Path", "Paths", "Files"} or re.search(r"\b(?:Path|Paths|Files)\b", masked):
                # Don't flag a declaration of the same name as an imported type.
                if not re.search(r"\b(?:class|interface|enum)\s+" + re.escape(name) + r"\b", masked):
                    line_no = next((i for i,l in enumerate(lines,1) if re.search(r"\b"+re.escape(name)+r"\b", l)), 1)
                    issues.append(_issue("Error", "Missing Import", line_no,
                                         f"`{name}` is used but `{fqcn}` is not imported.",
                                         f"Add `import {fqcn};` or use the fully qualified type."))

    # Empty catch, broad catch, duplicate conditions, dangerous comparisons and logic.
    for no, line in enumerate(lines, 1):
        if re.search(r"\bcatch\s*\([^)]*\)\s*\{\s*\}", line):
            issues.append(_issue("Warning", "Empty Catch Block", no,
                                 "The catch block silently ignores an exception.",
                                 "Handle, log, or deliberately propagate the exception."))
        if re.search(r"\bcatch\s*\(\s*(?:Exception|Throwable)\s+\w+", line):
            issues.append(_issue("Info", "Broad Exception Handler", no,
                                 "A broad exception handler may hide unrelated programming errors.",
                                 "Catch the narrowest exception type that can be handled."))
        if re.search(r"\b(?:String|Integer|Long|Double|Float|Boolean|Character)\b[^;]*(?:==|!=)[^;]*", line) and not re.search(r"==\s*null|!=\s*null", line):
            if "String" in line:
                issues.append(_issue("Warning", "String Identity Comparison", no,
                                     "String values should normally be compared by content, not object identity.",
                                     "Use `.equals()` or `.equalsIgnoreCase()` for string content."))
        if re.search(r"\bdouble\s+\w+\s*=\s*\w+\s*/\s*\w+\s*;", line):
            issues.append(_issue("Warning", "Integer Division", no,
                                 "Both operands appear to be integer variables before assignment to double.",
                                 "Cast an operand to double when fractional division is intended."))
        if re.search(r"/\s*0(?:\.0+)?\s*;", line):
            issues.append(_issue("Error", "Division By Zero", no,
                                 "The expression divides by a constant zero.",
                                 "Correct the denominator before running the program."))
        if re.search(r"\bwhile\s*\(\s*true\s*\)", line, re.I) and not re.search(r"\bbreak\b", code):
            issues.append(_issue("Warning", "Potential Infinite Loop", no,
                                 "The loop condition is always true and no break is visible.",
                                 "Add a reachable termination condition."))
        if re.search(r"\b(?:new\s+)?Random\s*\(", line) and re.search(r"(?:token|password|secret|otp|auth|key)", code, re.I):
            issues.append(_issue("Warning", "Weak Randomness", no,
                                 "java.util.Random is predictable for security-sensitive values.",
                                 "Use SecureRandom for security-sensitive random values."))
        if re.search(r"\b(?:MessageDigest|getInstance)\s*\([^\n]*(?:MD5|SHA-1)", line, re.I):
            issues.append(_issue("Warning", "Weak Hash Algorithm", no,
                                 "MD5/SHA-1 is unsuitable for modern security-sensitive hashing.",
                                 "Use a modern algorithm such as SHA-256 where appropriate."))
        if re.search(r"\bSystem\.exit\s*\(", line):
            issues.append(_issue("Warning", "Abrupt Program Exit", no,
                                 "System.exit terminates the JVM immediately and can bypass normal cleanup.",
                                 "Prefer structured return/error handling in application code."))
        if re.search(r"\bThread\.sleep\s*\(", line):
            issues.append(_issue("Info", "Blocking Sleep", no,
                                 "Thread.sleep blocks the current thread.",
                                 "Use scheduled/asynchronous mechanisms when blocking is unnecessary."))
        if re.search(r"\b(?:ArrayList|HashMap|HashSet|LinkedList|List|Map|Set)\s+\w+\s*(?:=|;)", line) and not re.search(r"<[^>]+>", line):
            issues.append(_issue("Warning", "Raw Collection Type", no,
                                 "A collection is declared without generic type parameters.",
                                 "Use a parameterized collection type."))
        if re.search(r"\b(?:String|StringBuilder)\s+\w+\s*=", line) and "+" in line and "for" not in line:
            pass
        if re.search(r"\bfor\s*\([^)]*\)\s*\{", line) and re.search(r"\+\s*\w+", line):
            # Only flag concatenation inside the same loop line; multiline loops are left to the compiler/static rules.
            pass
        if re.search(r"\b(?:TODO|FIXME|HACK)\b", line, re.I):
            issues.append(_issue("Info", "Pending Marker", no,
                                 "A pending development marker remains in the source.",
                                 "Resolve or document it before submission."))
        if re.search(r"\b(?:password|passwd|secret|api[_-]?key|token|private[_-]?key)\b\s*=\s*[\"'][^\"']+[\"']", line, re.I):
            issues.append(_issue("Error", "Hardcoded Secret", no,
                                 "A credential-like value is embedded directly in source code.",
                                 "Move secrets to secure configuration or environment variables."))
        if re.search(r"\b(?:new\s+File|Paths\.get|FileInputStream|FileReader|FileWriter)\s*\([^)]*(?:request|input|args|param|user)\b", line, re.I):
            issues.append(_issue("Warning", "Potential Path Traversal", no,
                                 "External input appears to influence a filesystem path.",
                                 "Validate and constrain paths before accessing the filesystem."))
        if re.search(r"\b(?:Runtime\.getRuntime\(\)\.exec|new\s+ProcessBuilder)\s*\(", line):
            issues.append(_issue("Error", "Command Execution", no,
                                 "The program launches an operating-system process.",
                                 "Avoid untrusted command construction and validate all arguments."))
        if re.search(r"\b(?:SELECT|INSERT|UPDATE|DELETE)\b", line, re.I) and "+" in line:
            issues.append(_issue("Error", "SQL Injection Risk", no,
                                 "SQL text appears to be concatenated with another value.",
                                 "Use PreparedStatement parameters instead of string concatenation."))
        if re.search(r"\b(?:ObjectInputStream|readObject)\b", line):
            issues.append(_issue("Warning", "Unsafe Deserialization", no,
                                 "Java object deserialization can execute unsafe object behavior with untrusted data.",
                                 "Avoid deserializing untrusted ObjectInputStream data or enforce a strict allow-list."))

    # Obvious duplicate conditions in adjacent if/else-if chains.
    for m in re.finditer(r"\bif\s*\(([^\n]+)\)", masked):
        pass
    return issues


def _advanced_cpp_review(code):
    """Broad conservative C++ review layer; compiler diagnostics catch hard errors."""
    issues = []
    lines = code.splitlines()
    masked = _mask_c_like(code)

    # Missing/duplicate includes and common API requirements.
    includes = re.findall(r"^\s*#\s*include\s*[<\"]([^>\"]+)[>\"]", code, re.M)
    seen = set()
    for no, line in enumerate(lines, 1):
        m = re.match(r"\s*#\s*include\s*[<\"]([^>\"]+)[>\"]", line)
        if m:
            hdr = m.group(1)
            if hdr in seen:
                issues.append(_issue("Warning", "Duplicate Include", no,
                                     f"`{hdr}` is included more than once.",
                                     "Remove the duplicate include."))
            seen.add(hdr)

    # Common correctness/security/logic checks.
    for no, line in enumerate(lines, 1):
        if re.search(r"\bif\s*\([^\n]*\b\w+\s*=\s*[^=]", line):
            issues.append(_issue("Error", "Assignment In Condition", no,
                                 "An assignment appears inside an if condition.",
                                 "Use == for comparison or make the assignment explicit."))
        if re.search(r"\bwhile\s*\([^\n]*\b\w+\s*=\s*[^=]", line):
            issues.append(_issue("Error", "Assignment In Condition", no,
                                 "An assignment appears inside a while condition.",
                                 "Use == for comparison or make the assignment explicit."))
        if re.search(r"/\s*0(?:\.0+)?\b", line):
            issues.append(_issue("Error", "Division By Zero", no,
                                 "The expression divides by a constant zero.",
                                 "Correct the denominator or validate it before division."))
        if re.search(r"\b(?:gets|strcpy|strcat|sprintf|vsprintf)\s*\(", line):
            fn = re.search(r"\b(gets|strcpy|strcat|sprintf|vsprintf)\s*\(", line).group(1)
            issues.append(_issue("Error", "Unsafe C String API", no,
                                 f"`{fn}()` can cause buffer overflows when input is not strictly bounded.",
                                 "Use safer, size-aware C++ string/container APIs."))
        if re.search(r"\b(?:scanf|sscanf|fscanf)\s*\([^\n]*%s", line):
            issues.append(_issue("Warning", "Unbounded String Input", no,
                                 "A scanf-style string conversion has no visible field width.",
                                 "Use a bounded width or std::string/std::getline."))
        if re.search(r"\b(?:system|popen)\s*\(", line):
            issues.append(_issue("Error", "Command Execution", no,
                                 "The program executes an operating-system command.",
                                 "Avoid shell execution with untrusted input."))
        if re.search(r"\b(?:password|passwd|secret|api[_-]?key|token|private[_-]?key)\b\s*=\s*[\"'][^\"']+[\"']", line, re.I):
            issues.append(_issue("Error", "Hardcoded Secret", no,
                                 "A credential-like value is embedded directly in source code.",
                                 "Move secrets to secure configuration."))
        if re.search(r"\b(?:reinterpret_cast|const_cast)\s*<", line):
            issues.append(_issue("Warning", "Unsafe Cast", no,
                                 "A low-level cast can bypass normal C++ type-safety guarantees.",
                                 "Prefer safe casts or redesign the interface where possible."))
        if re.search(r"\bdelete\s*\[\]", line) and not re.search(r"\bnew\s+\w+\s*\[", code):
            pass
        if re.search(r"\bnew\s+[A-Za-z_:][\w:<>]*\s*\[", line):
            var = re.search(r"\b(\w+)\s*=\s*new\s+[A-Za-z_:][\w:<>]*\s*\[", line)
            if var and not re.search(r"\bdelete\s*\[\]\s*" + re.escape(var.group(1)) + r"\b", code):
                issues.append(_issue("Warning", "Possible Memory Leak", no,
                                     f"Array allocation `{var.group(1)}` has no visible matching delete[].",
                                     "Prefer std::vector or another RAII-managed container."))
        if re.search(r"\bnew\s+[A-Za-z_:][\w:<>]*\s*\(", line):
            var = re.search(r"\b(\w+)\s*=\s*new\s+[A-Za-z_:][\w:<>]*\s*\(", line)
            if var and not re.search(r"\bdelete\s+" + re.escape(var.group(1)) + r"\b", code) and not re.search(r"\bunique_ptr\b|\bshared_ptr\b", line):
                issues.append(_issue("Warning", "Possible Memory Leak", no,
                                     f"Raw allocation for `{var.group(1)}` has no visible matching delete.",
                                     "Prefer RAII smart pointers or standard containers."))
        if re.search(r"\b(?:TODO|FIXME|HACK)\b", line, re.I):
            issues.append(_issue("Info", "Pending Marker", no,
                                 "A pending development marker remains in the source.",
                                 "Resolve or document it before submission."))
        if re.search(r"\b(?:std::)?endl\b", line):
            # Existing rule also reports this; dedupe later.
            pass
        if re.search(r"\b(?:malloc|calloc|realloc)\s*\(", line):
            if not re.search(r"\bfree\s*\(", code):
                issues.append(_issue("Warning", "Possible Memory Leak", no,
                                     "C-style heap allocation has no visible matching free().",
                                     "Prefer RAII containers/smart pointers or pair the allocation with free()."))
        if re.search(r"\b(?:printf|fprintf|snprintf)\s*\([^\n]*%[ns]", line) and re.search(r"\b(?:input|user|request|buffer)\b", line, re.I):
            issues.append(_issue("Warning", "Format String Review", no,
                                 "A formatted C-style I/O call uses data that may be externally influenced.",
                                 "Keep format strings constant and pass data as arguments."))

    # Use-after-free / double-free patterns.
    freed = {}
    for no, line in enumerate(lines, 1):
        m = re.search(r"\bfree\s*\(\s*(\w+)\s*\)", line)
        if m:
            var = m.group(1)
            if var in freed:
                issues.append(_issue("Error", "Double Free", no,
                                     f"`{var}` is freed more than once on visible control flow.",
                                     "Free the allocation exactly once and set the pointer to nullptr after release."))
            freed[var] = no
        for var, free_line in list(freed.items()):
            if no > free_line and re.search(r"\b" + re.escape(var) + r"\b", line) and not re.search(r"\bfree\s*\(", line):
                if re.search(r"\*\s*" + re.escape(var) + r"\b|\b" + re.escape(var) + r"\s*->", line):
                    issues.append(_issue("Error", "Use After Free", no,
                                         f"`{var}` appears to be dereferenced after free().",
                                         "Do not use the pointer after release; set it to nullptr or redesign ownership."))

    return issues


def _python_missing_return_checks(tree):
    """Find Python functions that return a value on some paths but can fall through.

    Python legitimately allows functions with no explicit return (they return None),
    so this check only runs when the function already contains at least one
    value-returning statement. That keeps normal procedures from being falsely
    reported while catching a return that was accidentally removed from one path.
    """
    issues = []

    def stmt_always_returns(stmt):
        if isinstance(stmt, (ast.Return, ast.Raise)):
            return True

        if isinstance(stmt, ast.If):
            if not stmt.orelse:
                return False
            return block_always_returns(stmt.body) and block_always_returns(stmt.orelse)

        if isinstance(stmt, ast.Try):
            # A finally block that always exits dominates every path.
            if stmt.finalbody and block_always_returns(stmt.finalbody):
                return True
            # Be conservative with try/except: every handler and the body must
            # return, and an else block (when present) must also return.
            if not block_always_returns(stmt.body):
                return False
            if stmt.handlers and not all(block_always_returns(h.body) for h in stmt.handlers):
                return False
            if stmt.orelse and not block_always_returns(stmt.orelse):
                return False
            return bool(stmt.handlers or stmt.orelse)

        # A loop is not assumed to execute, so it cannot prove a function returns.
        return False

    def block_always_returns(statements):
        for stmt in statements:
            if stmt_always_returns(stmt):
                return True
        return False

    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue

        value_returns = [
            node for node in ast.walk(fn)
            if isinstance(node, ast.Return) and node.value is not None
        ]
        if not value_returns:
            # No evidence that this function is intended to return a value.
            continue

        if not block_always_returns(fn.body):
            issues.append(_issue(
                "Warning", "Missing Return Statement", fn.lineno,
                f"Function `{fn.name}` returns a value on some paths but can reach the end without returning a value.",
                "Add a return statement for every value-returning execution path, or return explicitly where None is intended.",
            ))

    return issues

def analyze_python_code(code):
    try:
        tree = ast.parse(code)
    except SyntaxError as error:
        lines, metrics = _generic_metrics(code, "python")
        return {
            "issues": [_issue(
                "Error", "Syntax Error", error.lineno or 1,
                error.msg or "Invalid Python syntax.",
                "Fix the syntax error before static analysis.",
            )],
            "issues_count": 1,
            "quality_score": 40,
            "complexity": {"score": 0, "level": "Unknown"},
            "metrics": metrics,
        }

    lines, metrics = _generic_metrics(code, "python")
    issues = []
    issues.extend(_python_undefined_names(tree))
    issues.extend(_python_duplicate_imports(tree))
    issues.extend(_python_unused_imports(tree))
    issues.extend(_python_unused_variables(tree))
    issues.extend(_python_missing_return_checks(tree))
    issues.extend(_python_quality_checks(tree, code))
    issues.extend(_enhanced_python_review(code, tree))
    issues.extend(_advanced_python_review(code, tree))
    metrics["functions"] = sum(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(tree))
    metrics["classes"] = sum(isinstance(n, ast.ClassDef) for n in ast.walk(tree))
    metrics["imports"] = sum(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(tree))
    metrics["global_variables"] = sum(isinstance(n, (ast.Assign, ast.AnnAssign)) for n in tree.body)
    return _make_analysis(issues, metrics, _python_complexity(tree))


# =========================================================
# JAVA / C++ HELPERS
# =========================================================


def _mask_c_like(code):
    """Mask comments and string/character contents while preserving line breaks."""
    result = list(code)
    i = 0
    state = "normal"
    quote = ""
    escape = False
    while i < len(code):
        ch = code[i]
        nxt = code[i + 1] if i + 1 < len(code) else ""
        if state == "line_comment":
            if ch == "\n":
                state = "normal"
            else:
                result[i] = " "
            i += 1
            continue
        if state == "block_comment":
            if ch == "*" and nxt == "/":
                result[i] = result[i + 1] = " "
                i += 2
                state = "normal"
            else:
                if ch != "\n":
                    result[i] = " "
                i += 1
            continue
        if state == "string":
            if ch != "\n":
                result[i] = " "
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == quote:
                state = "normal"
            i += 1
            continue
        if ch == "/" and nxt == "/":
            result[i] = result[i + 1] = " "
            state = "line_comment"
            i += 2
            continue
        if ch == "/" and nxt == "*":
            result[i] = result[i + 1] = " "
            state = "block_comment"
            i += 2
            continue
        if ch in ('"', "'"):
            quote = ch
            result[i] = " "
            state = "string"
            i += 1
            continue
        i += 1
    return "".join(result)


def _delimiter_issues(code, language):
    masked = _mask_c_like(code)
    issues = []
    stack = []
    pairs = {"}": "{", ")": "(", "]": "["}
    opens = set(pairs.values())
    lines = masked.splitlines()
    for no, line in enumerate(lines, 1):
        for ch in line:
            if ch in opens:
                stack.append((ch, no))
            elif ch in pairs:
                if not stack or stack[-1][0] != pairs[ch]:
                    issues.append(_issue(
                        "Error", "Unmatched Delimiter", no,
                        f"`{ch}` does not match the previous opening delimiter.",
                        "Check parentheses, brackets, and braces.",
                    ))
                else:
                    stack.pop()
    for opening, no in reversed(stack):
        closing = {"{": "}", "(": ")", "[": "]"}[opening]
        issues.append(_issue(
            "Error", "Unclosed Delimiter", no,
            f"Opening `{opening}` has no matching `{closing}`.",
            "Close the delimiter at the correct nesting level.",
        ))
    return issues


def _java_cpp_metrics(code, language):
    lines = code.splitlines()
    masked = _mask_c_like(code)
    if language == "java":
        function_pattern = r"\b(?:public|private|protected|static|final|synchronized|abstract|native)?\s*(?:[A-Za-z_][\w<>\[\], ?]*\s+)?(?!if\b|for\b|while\b|switch\b|catch\b|synchronized\b)\w+\s*\([^;{}]*\)\s*(?:throws\s+[^{]+)?\{"
        classes = len(re.findall(r"\b(?:class|interface|enum)\s+\w+", masked))
        imports = len(re.findall(r"^\s*import\s+[^;]+;", code, re.M))
    else:
        function_pattern = r"\b(?:static|inline|virtual|constexpr|const|unsigned|signed|long|short|void|int|float|double|char|bool|auto|[A-Za-z_]\w*(?:::\w+)*)\s+(?!if\b|for\b|while\b|switch\b|catch\b)\w+\s*\([^;{}]*\)\s*(?:const\s*)?\{"
        classes = len(re.findall(r"\b(?:class|struct|union|enum|namespace)\s+\w+", masked))
        imports = len(re.findall(r"^\s*#\s*include\s*[<\"][^>\"]+[>\"]", code, re.M))
    functions = len(re.findall(function_pattern, masked))
    blank_lines = sum(1 for line in lines if not line.strip())
    comment_lines = sum(1 for line in lines if line.strip().startswith(("//", "/*", "*", "#")))
    return {
        "total_lines": len(lines),
        "code_lines": max(0, len(lines) - comment_lines - blank_lines),
        "comment_lines": comment_lines,
        "blank_lines": blank_lines,
        "functions": functions,
        "classes": classes,
        "imports": imports,
        "global_variables": 0,
    }


def _find_unused_declarations(code, language):
    issues = []
    lines = code.splitlines()
    if language == "java":
        patterns = [
            r"\b(?:int|long|double|float|boolean|char|byte|short|String)\s+(\w+)\s*(?:=|;)",
            r"\b(?:Scanner|ArrayList|HashMap|HashSet|LinkedList|TreeMap|TreeSet|List|Map|Set|Queue|Deque)\s*(?:<[^>]+>)?\s+(\w+)\s*(?:=|;)",
        ]
    else:
        patterns = [
            r"\b(?:int|long|short|float|double|char|bool|size_t)\s+(\w+)\s*(?:=|;)",
            r"\b(?:std::string|string|vector|map|set|unordered_map|unordered_set)\s*(?:<[^;]+>)?\s+(\w+)\s*(?:=|;)",
        ]
    declarations = []
    masked = _mask_c_like(code)
    for line_no, line in enumerate(masked.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        for pattern in patterns:
            for match in re.finditer(pattern, stripped):
                name = match.group(1)
                if name in {"i", "j", "k", "x", "y", "z", "argc", "argv", "password", "passwd", "secret", "apiKey", "api_key", "token", "privateKey", "private_key"}:
                    continue
                declarations.append((name, line_no))
    code_without_comments = re.sub(r"//.*", "", code, flags=re.MULTILINE)
    code_without_comments = re.sub(r"/\*.*?\*/", "", code_without_comments, flags=re.DOTALL)
    for name, line_no in declarations:
        occurrences = len(re.findall(r"\b" + re.escape(name) + r"\b", code_without_comments))
        if occurrences <= 1 and not name.startswith("_"):
            issues.append(_issue(
                "Warning", "Unused Variable", line_no,
                f"Variable `{name}` is declared but never used.",
                "Remove it or use it where required.",
            ))
    return issues


def _java_specific(code):
    issues = []
    lines = code.splitlines()
    masked = _mask_c_like(code)

    imports = {}
    imported_simple = set()
    wildcard_packages = set()
    for no, line in enumerate(lines, 1):
        match = re.match(r"\s*import\s+(?:static\s+)?([^;]+);", line)
        if match:
            name = match.group(1).strip()
            simple = name.split(".")[-1]
            if name in imports:
                issues.append(_issue("Warning", "Duplicate Import", no, f"`{name}` is imported more than once.", "Remove the duplicate import."))
            imports[name] = no
            imported_simple.add(simple)
            if name.endswith(".*"):
                wildcard_packages.add(name[:-2])

        if len(line) > 120:
            issues.append(_issue("Warning", "Long Line", no, f"Line contains {len(line)} characters.", "Break the statement into smaller lines."))

        if re.search(r"Runtime\.getRuntime\(\)\.exec\s*\(|new\s+ProcessBuilder\s*\(", line):
            issues.append(_issue("Error", "Process Execution", no, "The code starts an operating-system process.", "Never construct commands from untrusted input."))

        if re.search(r"\b(?:SELECT|INSERT|UPDATE|DELETE)\b", line, re.I) and ("+" in line or re.search(r"\b(?:format|formatted)\s*\(", line, re.I)):
            issues.append(_issue("Error", "Possible SQL Injection", no, "SQL appears to be constructed dynamically.", "Use PreparedStatement parameters instead of concatenating input."))

        if re.search(r"\b(?:password|passwd|secret|api[_-]?key|token|private[_-]?key)\b\s*=\s*(?:[\"'][^\"']+[\"']|\d+)", line, re.I):
            issues.append(_issue("Error", "Hardcoded Secret", no, "A sensitive credential appears to be hard-coded.", "Move secrets to secure configuration or environment variables."))

        if re.search(r"ObjectInputStream|\.readObject\s*\(", line):
            issues.append(_issue("Warning", "Unsafe Deserialization", no, "Java object deserialization can be unsafe for untrusted data.", "Validate the source and prefer safer serialization formats."))

        if re.search(r"MessageDigest\.getInstance\s*\(\s*[\"'](?:MD5|SHA-1)[\"']", line, re.I):
            issues.append(_issue("Warning", "Weak Cryptography", no, "MD5/SHA-1 is unsuitable for modern security-sensitive hashing.", "Use a modern cryptographic algorithm appropriate to the use case."))

        if re.search(r"\bwhile\s*\(\s*(?:true|1)\s*\)", line, re.I):
            issues.append(_issue("Warning", "Potential Infinite Loop", no, "The loop condition is always true.", "Ensure a reachable break or termination condition exists."))

        if re.search(r"new\s+String\s*\(\s*[\"']", line):
            issues.append(_issue("Info", "Unnecessary String Construction", no, "A String object is explicitly constructed from a string literal.", "Use the string literal directly."))

        if re.search(r"\bstatic\s+(?:final\s+)?(?:List|Map|Set|Collection)<", line) and "new " in line:
            issues.append(_issue("Warning", "Mutable Static State", no, "A mutable collection is stored in static state.", "Review shared mutable state and synchronization requirements."))

        # Dangerous reflection / native execution patterns.
        if re.search(r"Runtime\.getRuntime\(\)\.load|System\.load(?:Library)?\s*\(", line):
            issues.append(_issue("Warning", "Native Library Loading", no, "Native library loading can introduce platform and security risks.", "Load trusted libraries only and validate configuration."))

        if re.search(r"MessageDigest\.getInstance\s*\(\s*[\"']DES|Cipher\.getInstance\s*\(\s*[\"']DES", line, re.I):
            issues.append(_issue("Warning", "Weak Cryptography", no, "DES is obsolete for security-sensitive encryption.", "Use a modern authenticated encryption scheme."))

    # Missing imports. Wildcard imports count as satisfying members of that package.
    required_imports = {
        "Scanner": ("java.util.Scanner", "java.util"),
        "ArrayList": ("java.util.ArrayList", "java.util"),
        "LinkedList": ("java.util.LinkedList", "java.util"),
        "HashMap": ("java.util.HashMap", "java.util"),
        "HashSet": ("java.util.HashSet", "java.util"),
        "TreeMap": ("java.util.TreeMap", "java.util"),
        "TreeSet": ("java.util.TreeSet", "java.util"),
        "LinkedHashMap": ("java.util.LinkedHashMap", "java.util"),
        "LinkedHashSet": ("java.util.LinkedHashSet", "java.util"),
        "List": ("java.util.List", "java.util"),
        "Map": ("java.util.Map", "java.util"),
        "Set": ("java.util.Set", "java.util"),
        "Queue": ("java.util.Queue", "java.util"),
        "Deque": ("java.util.Deque", "java.util"),
        "Collections": ("java.util.Collections", "java.util"),
        "Arrays": ("java.util.Arrays", "java.util"),
        "StringTokenizer": ("java.util.StringTokenizer", "java.util"),
        "File": ("java.io.File", "java.io"),
        "FileReader": ("java.io.FileReader", "java.io"),
        "FileWriter": ("java.io.FileWriter", "java.io"),
        "BufferedReader": ("java.io.BufferedReader", "java.io"),
        "InputStreamReader": ("java.io.InputStreamReader", "java.io"),
        "OutputStreamWriter": ("java.io.OutputStreamWriter", "java.io"),
        "BufferedWriter": ("java.io.BufferedWriter", "java.io"),
        "FileInputStream": ("java.io.FileInputStream", "java.io"),
        "FileOutputStream": ("java.io.FileOutputStream", "java.io"),
        "LocalDate": ("java.time.LocalDate", "java.time"),
        "LocalDateTime": ("java.time.LocalDateTime", "java.time"),
        "DateTimeFormatter": ("java.time.format.DateTimeFormatter", "java.time.format"),
    }
    code_without_imports = re.sub(r"^\s*import\s+[^;]+;\s*$", "", masked, flags=re.MULTILINE)
    for class_name, (path, package) in required_imports.items():
        if class_name in imported_simple or package in wildcard_packages:
            continue
        usage = re.search(r"(?<![.\w])" + re.escape(class_name) + r"\b", code_without_imports)
        if usage:
            line_no = code_without_imports[:usage.start()].count("\n") + 1
            issues.append(_issue("Error", "Missing Import", line_no, f"`{class_name}` is used but `{path}` is not imported.", f"Add `import {path};` or use the fully-qualified class name."))

    # Empty catches across multiple lines.
    for match in re.finditer(r"catch\s*\([^)]*\)\s*\{\s*\}", masked, re.S):
        line_no = masked[:match.start()].count("\n") + 1
        issues.append(_issue("Warning", "Empty Catch Block", line_no, "The exception is silently ignored.", "Handle, log, or deliberately rethrow the exception."))

    # Duplicate conditions.
    seen_conditions = {}
    for match in re.finditer(r"\b(if|while|for)\s*\(([^\n()]*)\)", masked, re.I):
        condition = re.sub(r"\s+", " ", match.group(2).strip())
        if not condition:
            continue
        line_no = masked[:match.start()].count("\n") + 1
        key = (match.group(1).lower(), condition)
        if key in seen_conditions:
            issues.append(_issue("Warning", "Duplicate Condition", line_no, f"The same `{match.group(1)}` condition is repeated.", "Remove the duplicate branch or combine the logic."))
        else:
            seen_conditions[key] = line_no

    # String == / !=.
    string_vars = set(re.findall(r"\bString\s+(\w+)\s*(?:=|;|,)", masked))
    for no, line in enumerate(masked.splitlines(), 1):
        for var in string_vars:
            if re.search(r"\b" + re.escape(var) + r"\s*(?:==|!=)|(?:==|!=)\s*" + re.escape(var) + r"\b", line):
                issues.append(_issue("Warning", "String Identity Comparison", no, "`==`/`!=` compares String references instead of text values.", "Use `.equals()` or `.equalsIgnoreCase()` for string content comparison."))
                break

    # Resource leak.
    # Do not flag normal console input streams such as Scanner(System.in) or
    # BufferedReader(InputStreamReader(System.in)). These are process-level
    # console resources. The declaration may span several lines, so inspect
    # the complete statement up to its semicolon instead of checking only one
    # physical source line.
    resource_patterns = [
        r"\b(?:FileInputStream|FileOutputStream|FileReader|FileWriter|BufferedWriter)\s+(\w+)\s*=\s*new\s+",
        r"\bBufferedReader\s+(\w+)\s*=\s*new\s+BufferedReader\s*\(",
    ]
    resource_vars = []
    for pattern in resource_patterns:
        for match in re.finditer(pattern, masked, re.I):
            var = match.group(1)
            start = match.start()
            statement_end = masked.find(";", match.end())
            if statement_end == -1:
                statement_end = min(len(masked), match.end() + 1000)
            statement = masked[start:statement_end + 1]

            # System.in is intentionally excluded from resource-leak warnings.
            # This also handles multiline forms such as:
            # new BufferedReader(
            #     new InputStreamReader(System.in));
            if re.search(r"\bSystem\s*\.\s*in\b", statement):
                continue

            line_no = masked[:start].count("\n") + 1
            resource_vars.append((var, line_no))

    # A variable can be matched by more than one broad pattern; deduplicate it.
    seen_resources = set()
    for var, no in resource_vars:
        key = (var, no)
        if key in seen_resources:
            continue
        seen_resources.add(key)
        if not re.search(r"\b" + re.escape(var) + r"\.close\s*\(\s*\)", code):
            issues.append(_issue("Warning", "Resource Leak", no, f"Resource `{var}` is created without a visible close().", "Use try-with-resources so the resource is closed reliably."))

    # Unreachable code after simple terminators.
    for no, line in enumerate(masked.splitlines(), 1):
        if re.search(r"\b(?:return|throw|break|continue)\b[^;]*;\s*\S+", line):
            issues.append(_issue("Warning", "Unreachable Code", no, "Code appears after an unconditional control-flow terminator on the same line.", "Remove the unreachable statement."))

    # Suspicious comparisons / constant conditions.
    for no, line in enumerate(masked.splitlines(), 1):
        if re.search(r"\bif\s*\(\s*(?:true|false)\s*\)", line, re.I):
            issues.append(_issue("Warning", "Constant Condition", no, "The if condition is always true or always false.", "Remove the dead branch or use a runtime condition."))
        if re.search(r"\bif\s*\(\s*(\w+)\s*==\s*\1\s*\)", line):
            issues.append(_issue("Warning", "Self Comparison", no, "A value appears to be compared with itself.", "Compare against the intended value."))

    # Obvious array-index and division-by-zero mistakes.
    for no, line in enumerate(masked.splitlines(), 1):
        if re.search(r"/\s*0(?:\D|$)|%\s*0(?:\D|$)", line):
            issues.append(_issue("Error", "Division By Zero", no, "An expression divides or takes a remainder by zero.", "Ensure the divisor cannot be zero."))

    # Null dereference patterns with an explicit null assignment.
    null_vars = set()
    for no, line in enumerate(masked.splitlines(), 1):
        m = re.search(r"\b(?:String|Object|[A-Z]\w*)\s+(\w+)\s*=\s*null\s*;", line)
        if m:
            null_vars.add(m.group(1))
        for var in list(null_vars):
            if re.search(r"\b" + re.escape(var) + r"\.(?:length|size|toString|charAt|get|add|remove|substring)\s*\(", line):
                issues.append(_issue("Warning", "Null Dereference Risk", no, f"`{var}` may be null before this method call.", "Check for null or initialize the reference before use."))

    # Catching Throwable/Exception broadly can hide programming errors.
    for no, line in enumerate(lines, 1):
        if re.search(r"\bcatch\s*\(\s*(?:Exception|Throwable)\s+\w+\s*\)", line):
            issues.append(_issue("Info", "Broad Exception Catch", no, "A broad exception type is being caught.", "Catch the most specific expected exception type."))

    # String concatenation inside loops can create avoidable allocations.
    in_loop = 0
    brace_depth = 0
    for no, line in enumerate(masked.splitlines(), 1):
        if re.search(r"\b(?:for|while)\s*\(", line):
            in_loop += 1
        if in_loop and re.search(r"\b(?:String|StringBuilder)\s+\w+.*\+", line):
            issues.append(_issue("Info", "String Concatenation in Loop", no, "String concatenation inside a loop may create repeated temporary objects.", "Consider StringBuilder for repeated concatenation."))
        brace_depth += line.count("{") - line.count("}")
        if in_loop and brace_depth <= 0:
            in_loop = 0

    # TODO/FIXME and magic-number hints. Keep magic-number detection conservative.
    for no, line in enumerate(lines, 1):
        if re.search(r"\b(?:TODO|FIXME)\b", line, re.I):
            issues.append(_issue("Warning", "Pending TODO/FIXME", no, "The code contains a TODO/FIXME marker.", "Resolve the pending task before submission."))
        if re.search(r"\b(?:if|while)\s*\([^)]*(?:==|!=|>|<|>=|<=)\s*\d{2,}\b", line):
            issues.append(_issue("Info", "Magic Number", no, "A non-trivial numeric constant is used directly in a condition.", "Use a named constant when the value has business meaning."))

    return issues


def _cpp_specific(code):
    issues = []
    lines = code.splitlines()
    masked = _mask_c_like(code)

    includes = {}
    include_set = set()
    for no, line in enumerate(lines, 1):
        match = re.match(r"\s*#\s*include\s*[<\"]([^>\"]+)[>\"]", line)
        if match:
            name = match.group(1)
            if name in includes:
                issues.append(_issue("Warning", "Duplicate Include", no, f"`{name}` is included more than once.", "Remove the duplicate include."))
            includes[name] = no
            include_set.add(name)
        if len(line) > 120:
            issues.append(_issue("Warning", "Long Line", no, f"Line contains {len(line)} characters.", "Break the statement into smaller lines."))

        if re.search(r"\b(?:system|popen)\s*\(", line):
            issues.append(_issue("Error", "Process Execution", no, "The code invokes an operating-system command.", "Avoid shell commands with untrusted input; use safer APIs."))
        if re.search(r"\bgets\s*\(", line):
            issues.append(_issue("Error", "Unsafe Input Function", no, "gets() can overflow the destination buffer and is unsafe.", "Use a bounded input API such as std::getline."))
        unsafe = re.search(r"\b(strcpy|strcat|sprintf|vsprintf|gets)\s*\(", line)
        if unsafe:
            issues.append(_issue("Warning", "Unsafe String Function", no, f"`{unsafe.group(1)}()` can overflow a buffer when inputs are not bounded.", "Use size-aware alternatives and validate destination capacity."))
        if re.search(r"\b(?:password|passwd|secret|api[_-]?key|token|private[_-]?key)\b\s*=\s*(?:[\"'][^\"']+[\"']|\d+)", line, re.I):
            issues.append(_issue("Error", "Hardcoded Secret", no, "A sensitive credential appears to be hard-coded.", "Move secrets to secure configuration."))
        if re.search(r"\b(?:SELECT|INSERT|UPDATE|DELETE)\b", line, re.I) and "+" in line:
            issues.append(_issue("Error", "Possible SQL Injection", no, "SQL appears to be constructed using string concatenation.", "Use parameterized database APIs."))
        if re.search(r"\bprintf\s*\(\s*[A-Za-z_]\w*\s*\)", line):
            issues.append(_issue("Warning", "Uncontrolled Format String", no, "A variable is used directly as a printf format string.", "Use a constant format string such as printf(\"%s\", value)."))
        if "reinterpret_cast" in line:
            issues.append(_issue("Warning", "Unsafe Cast", no, "reinterpret_cast can bypass type-safety assumptions.", "Prefer a safer conversion or redesign the interface."))
        if re.search(r"\bwhile\s*\(\s*(?:true|1)\s*\)", line, re.I):
            issues.append(_issue("Warning", "Potential Infinite Loop", no, "The loop condition is always true.", "Ensure a reachable termination condition exists."))

        # A stream insertion/extraction operator cannot start a statement by
        # itself. This catches common C++ mistakes such as a missing `cout`
        # before `<<` without flagging valid `cout << ...` / `cin >> ...`.
        stripped_stream = line.split("//", 1)[0].strip()
        if re.match(r"^(?:<<|>>)", stripped_stream):
            operator = re.match(r"^(<<|>>)", stripped_stream).group(1)
            direction = "insertion" if operator == "<<" else "extraction"
            issues.append(_issue(
                "Error", "Invalid Stream Expression", no,
                f"The C++ stream {direction} operator `{operator}` appears without a left-hand stream object.",
                "Use a valid stream expression such as `cout << value;` or `cin >> value;`."
            ))

        # Also catch an orphaned stream operator after a statement separator,
        # e.g. `; << value`, while avoiding normal chained stream expressions.
        if re.search(r";\s*(?:<<|>>)\s*", stripped_stream):
            match = re.search(r";\s*(<<|>>)\s*", stripped_stream)
            operator = match.group(1)
            direction = "insertion" if operator == "<<" else "extraction"
            issues.append(_issue(
                "Error", "Invalid Stream Expression", no,
                f"The C++ stream {direction} operator `{operator}` is used without a valid left-hand stream object.",
                "Attach the operator to `cout`, `cin`, or another valid stream object."
            ))

        # Normalize the code line before the stream-specific checks.
        clean_cpp = stripped_stream.strip()

        # Strong stream-statement semicolon check. A stream statement such as
        # `cout << "text"` or `cin >> value` is complete when the line does
        # not end in `;`. This is deliberately separate from the broader
        # heuristic below so a missing semicolon is not hidden by chained
        # stream syntax.
        if (re.search(r"\b(?:cout|cin|cerr|clog)\b", clean_cpp)
                and re.search(r"(?:<<|>>)\s*", clean_cpp)
                and not re.search(r"[;{}:]\s*(?://.*)?$", clean_cpp)
                and not re.search(r"(?:<<|>>|[+\-*/%=&|?,.]|\\)\s*(?://.*)?$", clean_cpp)):
            issues.append(_issue(
                "Error", "Missing Semicolon", no,
                "This C++ stream statement appears to be missing a semicolon.",
                "Add `;` at the end of the statement."
            ))

        # Missing semicolon detection for ordinary C++ statements.
        # Compiler diagnostics are useful when a C++ compiler is available,
        # but CodeLens must still report this basic syntax error when only
        # static/heuristic analysis is available. Keep the rule conservative
        # so control-flow headers and multiline expressions are not flagged.
        if clean_cpp and not clean_cpp.startswith(("#", "//", "/*", "*")):
            statement_like = bool(re.match(
                r"^(?:cout|cin|cerr|clog|return\b|throw\b|[A-Za-z_][\w:<>]*(?:\s*<[^;{}]*>)?\s+[A-Za-z_]\w*\s*(?:=|;)|[A-Za-z_]\w*(?:\s*\.[A-Za-z_]\w*)*\s*\()",
                clean_cpp
            ))
            control_header = bool(re.match(
                r"^(?:if|else\s+if|for|while|switch|catch|else|do|try|class|struct|namespace|enum)\b",
                clean_cpp
            ))
            # A line ending with an opening brace, colon, comma, or an
            # operator is normally a continuation/header, not a complete
            # statement.
            continuation = bool(re.search(r"(?:[+\-*/%=&|?:.]|<<|>>|,|\\)$", clean_cpp))
            if statement_like and not control_header and not continuation and not clean_cpp.endswith((";", "{", "}", ":")):
                issues.append(_issue(
                    "Error", "Missing Semicolon", no,
                    "This C++ statement appears to be missing a semicolon.",
                    "Add `;` at the end of the statement."
                ))

        # Null dereference pattern: direct dereference in the same expression as a known null assignment.
        if re.search(r"\b(?:int|char|float|double|void|long)\s*\*\s*(\w+)\s*=\s*(?:nullptr|NULL|0)\s*;", line):
            var = re.search(r"\*\s*(\w+)", line).group(1)
            issues.append(_issue("Warning", "Null Pointer Dereference Risk", no, f"Pointer `{var}` is initialized to null.", "Check the pointer before dereferencing it."))
        if re.search(r"\bfree\s*\(\s*(\w+)\s*\)\s*;", line):
            var = re.search(r"\bfree\s*\(\s*(\w+)\s*\)", line).group(1)
            if re.search(r"\bdelete\s+(?:\[\])?\s*" + re.escape(var) + r"\b", code):
                issues.append(_issue("Error", "Mismatched Deallocation", no, f"`{var}` appears to be released with both free() and delete.", "Use the matching allocation/deallocation pair."))

    # Missing common standard-library includes.
    include_requirements = {
        "vector": {"vector", "bits/stdc++.h"},
        "map": {"map", "bits/stdc++.h"},
        "unordered_map": {"unordered_map", "bits/stdc++.h"},
        "set": {"set", "bits/stdc++.h"},
        "unordered_set": {"unordered_set", "bits/stdc++.h"},
        "string": {"string", "bits/stdc++.h"},
        "cout": {"iostream", "bits/stdc++.h"},
        "cin": {"iostream", "bits/stdc++.h"},
        "endl": {"iostream", "bits/stdc++.h"},
        "printf": {"cstdio", "stdio.h", "bits/stdc++.h"},
        "scanf": {"cstdio", "stdio.h", "bits/stdc++.h"},
        "memcpy": {"cstring", "string.h", "bits/stdc++.h"},
        "strlen": {"cstring", "string.h", "bits/stdc++.h"},
        "sqrt": {"cmath", "math.h", "bits/stdc++.h"},
        "unique_ptr": {"memory", "bits/stdc++.h"},
        "shared_ptr": {"memory", "bits/stdc++.h"},
    }
    for symbol, allowed in include_requirements.items():
        if not re.search(r"\b" + re.escape(symbol) + r"\b", masked):
            continue
        if not any(name in include_set for name in allowed):
            first = re.search(r"\b" + re.escape(symbol) + r"\b", masked)
            line_no = masked[:first.start()].count("\n") + 1 if first else 1
            preferred = next(iter(allowed - {"bits/stdc++.h"}), symbol)
            issues.append(_issue("Error", "Missing Include", line_no, f"`{symbol}` is used but its standard header is not included.", f"Add `#include <{preferred}>`."))

    # Duplicate conditions.
    seen_conditions = {}
    for match in re.finditer(r"\b(if|while|for)\s*\(([^\n()]*)\)", masked, re.I):
        condition = re.sub(r"\s+", " ", match.group(2).strip())
        if not condition:
            continue
        line_no = masked[:match.start()].count("\n") + 1
        key = (match.group(1).lower(), condition)
        if key in seen_conditions:
            issues.append(_issue("Warning", "Duplicate Condition", line_no, f"The same `{match.group(1)}` condition is repeated.", "Remove the duplicate branch or combine the logic."))
        else:
            seen_conditions[key] = line_no

    # Heap allocation / ownership.
    allocations = {}
    for no, line in enumerate(lines, 1):
        array_match = re.search(r"\b(\w+)\s*=\s*new\s+[^;\[]+\[[^\]]*\]", line)
        if array_match:
            allocations[array_match.group(1)] = (no, True)
            continue
        single_match = re.search(r"\b(\w+)\s*=\s*new\s+[^;]+", line)
        if single_match:
            allocations[single_match.group(1)] = (no, False)
    for var, (alloc_line, array_alloc) in allocations.items():
        delete_pat = r"\bdelete\s*\[\]\s*" + re.escape(var) + r"\b" if array_alloc else r"\bdelete\s+" + re.escape(var) + r"\b"
        if not re.search(delete_pat, masked):
            issues.append(_issue("Warning", "Possible Memory Leak", alloc_line, f"Heap allocation assigned to `{var}` has no matching delete detected in this file.", "Prefer RAII/smart pointers or ensure the allocation is released exactly once."))

    deleted = {}
    for no, line in enumerate(lines, 1):
        matches = list(re.finditer(r"\bdelete(?:\s*\[\])?\s+(\w+)", line))
        for match in matches:
            var = match.group(1)
            if var in deleted:
                issues.append(_issue("Error", "Double Delete", no, f"`{var}` is deleted more than once.", "Ensure ownership is released exactly once."))
            deleted[var] = no
        if matches:
            continue
        for var, delete_line in list(deleted.items()):
            if no > delete_line and re.search(r"\b" + re.escape(var) + r"\b", line):
                issues.append(_issue("Warning", "Possible Use After Free", no, f"`{var}` is referenced after it was deleted.", "Do not use a pointer after releasing its object."))
                del deleted[var]

    # Uninitialized primitive variables.
    declared = {}
    for no, line in enumerate(masked.splitlines(), 1):
        match = re.search(r"\b(int|float|double|bool|char|long|short)\s+(\w+)\s*(?:;|$)", line.strip())
        if match:
            declared[match.group(2)] = no
    for var, decl_line in declared.items():
        for no in range(decl_line + 1, len(masked.splitlines()) + 1):
            text_line = masked.splitlines()[no - 1]
            if re.search(r"\b" + re.escape(var) + r"\s*=", text_line):
                break
            if re.search(r"\b" + re.escape(var) + r"\b", text_line):
                issues.append(_issue("Warning", "Possible Uninitialized Variable", no, f"`{var}` is used before a visible initialization.", "Initialize the variable before reading it."))
                break

    # Unreachable statement on same line.
    for no, line in enumerate(masked.splitlines(), 1):
        if re.search(r"\b(?:return|throw|break|continue)\b[^;]*;\s*\S+", line):
            issues.append(_issue("Warning", "Unreachable Code", no, "Code appears after an unconditional control-flow terminator.", "Remove the unreachable statement."))

    # Constant conditions and division by zero.
    for no, line in enumerate(masked.splitlines(), 1):
        if re.search(r"\bif\s*\(\s*(?:true|false|1|0)\s*\)", line, re.I):
            issues.append(_issue("Warning", "Constant Condition", no, "The condition is constant and one branch is unreachable.", "Remove the dead branch or use a runtime condition."))
        if re.search(r"/\s*0(?:\D|$)|%\s*0(?:\D|$)", line):
            issues.append(_issue("Error", "Division By Zero", no, "An expression divides or takes a remainder by zero.", "Ensure the divisor cannot be zero."))
        if re.search(r"\b(?:TODO|FIXME)\b", lines[no - 1], re.I):
            issues.append(_issue("Warning", "Pending TODO/FIXME", no, "The code contains a TODO/FIXME marker.", "Resolve the pending task before submission."))

    # Null / dangling pointer patterns.
    null_pointer_vars = set()
    for no, line in enumerate(lines, 1):
        m = re.search(r"\b(?:int|char|float|double|bool|long|short)\s*\*\s*(\w+)\s*=\s*(?:nullptr|NULL|0)\s*;", line)
        if m:
            null_pointer_vars.add(m.group(1))
        for var in list(null_pointer_vars):
            if re.search(r"\*\s*" + re.escape(var) + r"\b", line) and not re.search(r"\b" + re.escape(var) + r"\s*=", line):
                issues.append(_issue("Warning", "Null Pointer Dereference Risk", no, f"Pointer `{var}` may be null when dereferenced.", "Check the pointer before dereferencing it."))

    # C-style casts and raw array parameters are common review hotspots.
    for no, line in enumerate(lines, 1):
        if re.search(r"\([A-Za-z_][\w:<>]*\)\s*[A-Za-z_]\w*", line) and "static_cast" not in line and "reinterpret_cast" not in line and "const_cast" not in line and "dynamic_cast" not in line:
            issues.append(_issue("Info", "C-Style Cast", no, "A C-style cast can bypass type-safety checks.", "Prefer static_cast, dynamic_cast, const_cast, or a redesign as appropriate."))

    # Obvious uninitialized primitive locals.
    masked_lines = masked.splitlines()
    declared = {}
    for no, line in enumerate(masked_lines, 1):
        match = re.search(r"\b(int|float|double|bool|char|long|short)\s+(\w+)\s*(?:;|$)", line.strip())
        if match:
            declared[match.group(2)] = no
    for var, decl_line in declared.items():
        for no in range(decl_line + 1, len(masked_lines) + 1):
            text_line = masked_lines[no - 1]
            if re.search(r"\b" + re.escape(var) + r"\s*=", text_line):
                break
            if re.search(r"\b" + re.escape(var) + r"\b", text_line):
                issues.append(_issue("Warning", "Possible Uninitialized Variable", no, f"`{var}` is used before a visible initialization.", "Initialize the variable before reading it."))
                break

    # malloc/calloc/realloc ownership checks.
    malloc_vars = {}
    for no, line in enumerate(lines, 1):
        match = re.search(r"\b(\w+)\s*=\s*(?:std::)?(?:malloc|calloc|realloc)\s*\(", line)
        if match:
            malloc_vars[match.group(1)] = no
    for var, alloc_line in malloc_vars.items():
        if not re.search(r"\bfree\s*\(\s*" + re.escape(var) + r"\s*\)", code):
            issues.append(_issue("Warning", "Possible Memory Leak", alloc_line, f"Heap allocation for `{var}` has no matching free() detected.", "Release malloc/calloc/realloc memory with free() or use RAII."))

    # Raw owning pointers are a maintainability risk; only flag obvious owning allocations.
    for no, line in enumerate(lines, 1):
        if re.search(r"\b(?:int|char|float|double|bool|long|short)\s*\*\s*\w+\s*=\s*new\b", line):
            issues.append(_issue("Info", "Raw Pointer Ownership", no, "A raw owning pointer is allocated with new.", "Prefer std::unique_ptr or std::vector where appropriate."))

    return issues


def _compiler_diagnostics(code, language):
    """Optional syntax/semantic checks using compiler frontends; target code is never executed."""
    compiler = shutil.which("javac" if language == "java" else "g++")
    if not compiler:
        return []
    issues = []
    temp_dir = tempfile.mkdtemp(prefix="codelens_")
    try:
        if language == "java":
            match = re.search(r"\bpublic\s+class\s+(\w+)", code)
            class_name = match.group(1) if match else "CodeLensTemp"
            source_path = os.path.join(temp_dir, class_name + ".java")
            with open(source_path, "w", encoding="utf-8") as handle:
                handle.write(code)
            command = [compiler, "-proc:none", "-Xlint:all", "-d", temp_dir, source_path]
        else:
            source_path = os.path.join(temp_dir, "codelens.cpp")
            with open(source_path, "w", encoding="utf-8") as handle:
                handle.write(code)
            command = [compiler, "-std=c++17", "-fsyntax-only", "-Wall", "-Wextra", "-Wpedantic", source_path]
        process = subprocess.run(command, capture_output=True, text=True, timeout=5)
        output = (process.stdout or "") + "\n" + (process.stderr or "")
        if process.returncode == 0:
            return issues

        for raw in output.splitlines():
            line_match = re.search(r"(?::|\.java:|\.cpp:)(\d+)(?::\d+)?:\s*(error|warning):\s*(.+)$", raw, re.I)
            if not line_match:
                continue
            line_no = int(line_match.group(1))
            level = line_match.group(2).lower()
            message = line_match.group(3).strip()
            # External dependencies can be unavailable in a demo environment;
            # don't turn those into false "missing import" errors here.
            if language == "java" and "package " in message and " does not exist" in message:
                continue
            severity = "Error" if level == "error" else "Warning"
            issues.append(_issue(
                severity,
                "Compiler Diagnostic",
                line_no,
                message,
                "Fix the compiler diagnostic before submission.",
            ))
    except (OSError, subprocess.SubprocessError, UnicodeError):
        return []
    finally:
        import shutil as _shutil
        _shutil.rmtree(temp_dir, ignore_errors=True)
    return issues



def _enhanced_python_review(code, tree):
    """Additional high-confidence Python review checks; keeps existing analyzer rules intact."""
    issues = []
    lines = code.splitlines()

    for no, line in enumerate(lines, 1):
        # Security-sensitive TLS configuration.
        if re.search(r"\bverify\s*=\s*False\b", line, re.I):
            issues.append(_issue("Error", "TLS Verification Disabled", no,
                                 "TLS certificate verification is disabled.",
                                 "Keep certificate verification enabled for network requests."))
        # Unsafe YAML loading.
        if re.search(r"\byaml\.load\s*\(", line) and "SafeLoader" not in line and "safe_load" not in line:
            issues.append(_issue("Error", "Unsafe YAML Deserialization", no,
                                 "yaml.load() can construct unsafe Python objects when used with untrusted data.",
                                 "Use yaml.safe_load() for untrusted YAML."))
        # Temporary debugging left in production code.
        if re.search(r"\b(?:breakpoint|pdb\.set_trace)\s*\(", line):
            issues.append(_issue("Warning", "Debug Breakpoint", no,
                                 "A debugging breakpoint remains in the source.",
                                 "Remove debugger calls before submission."))
        # Weak hash APIs in security-sensitive-looking code.
        if re.search(r"\b(?:hashlib\.)?(?:md5|sha1)\s*\(", line, re.I):
            issues.append(_issue("Warning", "Weak Hash Algorithm", no,
                                 "MD5/SHA-1 is weak for security-sensitive hashing.",
                                 "Use a modern hash such as SHA-256 where appropriate."))
        # Dangerous deserialization APIs beyond pickle.
        if re.search(r"\b(?:marshal\.loads|shelve\.open)\s*\(", line):
            issues.append(_issue("Warning", "Unsafe Deserialization", no,
                                 "This API can be unsafe with untrusted input.",
                                 "Use a safe serialization format for untrusted data."))
        # Mutable global containers.
        if re.match(r"\s*(?:[A-Z_][A-Z0-9_]*|[a-zA-Z_]\w*)\s*=\s*(?:\[|\{|set\s*\()", line):
            # Avoid duplicate reporting for obvious constants and empty declarations.
            if not re.search(r"\b(?:None|True|False)\b", line) and not re.search(r"\b(?:__all__|__version__)\b", line):
                try:
                    node_line = tree.body[lines[:no-1].__len__()] if False else None
                except Exception:
                    node_line = None
        # Logging a secret/password literal.
        if re.search(r"\b(?:password|passwd|secret|api[_-]?key|token)\b", line, re.I) and re.search(r"['\"][^'\"]+['\"]", line):
            if not re.search(r"os\.getenv|environ\.get|settings|config", line, re.I):
                issues.append(_issue("Warning", "Possible Credential Literal", no,
                                     "A credential-like value appears directly in source code.",
                                     "Load credentials from secure configuration or environment variables."))

    # Deprecated/unsafe subprocess shell construction.
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                if node.func.attr in {"run", "call", "Popen", "check_call", "check_output"}:
                    if any(k.arg == "shell" and isinstance(k.value, ast.Constant) and k.value.value is True for k in node.keywords):
                        issues.append(_issue("Error", "Shell Command Injection Risk", node.lineno,
                                             "subprocess is configured with shell=True.",
                                             "Prefer shell=False with a list of arguments."))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "assert":
            pass

    # Assert used as runtime validation can disappear under python -O.
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            issues.append(_issue("Info", "Assert Used for Validation", node.lineno,
                                 "assert statements can be disabled with optimized Python execution.",
                                 "Use an explicit condition and raise an exception for required runtime validation."))

    return issues


def _enhanced_java_review(code):
    """Additional Java review rules layered on top of the existing analyzer."""
    issues = []
    lines = code.splitlines()
    masked = _mask_c_like(code)

    for no, line in enumerate(lines, 1):
        # Java console output must use the case-sensitive System.out API.
        # Catch malformed/lowercase variants without flagging valid System.in/out usage.
        if re.search(r"\bsystem\s*\.\s*out\s*\.", line):
            issues.append(_issue(
                "Error",
                "Invalid Java Reference",
                no,
                "`system.out` is not a valid Java console output reference. Java uses the case-sensitive `System.out` API.",
                "Use `System.out.println(...)`, `System.out.print(...)`, or another valid `System.out` method."
            ))

        # A method call cannot omit the method name after System.out.
        if re.search(r"\bSystem\s*\.\s*out\s*\.\s*\(", line):
            issues.append(_issue(
                "Error",
                "Invalid Method Call",
                no,
                "`System.out.` must be followed by a valid output method name.",
                "Use a method such as `System.out.println(...)` or `System.out.print(...)`."
            ))

        # Object identity comparisons for boxed values.
        if re.search(r"\b(?:Integer|Long|Double|Float|Boolean|Short|Byte|Character)\s+\w+", masked) and re.search(r"\b\w+\s*(?:==|!=)\s*\w+", masked):
            if not re.search(r"System\.out|if\s*\(\s*\w+\s*==\s*(?:null|true|false)\b", masked):
                pass
        # Thread/process APIs with known bad practices.
        if re.search(r"\bThread\.stop\s*\(", line):
            issues.append(_issue("Warning", "Unsafe Thread Stop", no,
                                 "Thread.stop() is unsafe and deprecated.",
                                 "Use cooperative cancellation such as interruption."))
        if re.search(r"\b(?:Object|System)\.finalize\s*\(", line) or re.search(r"\bfinalize\s*\(\s*\)", line):
            issues.append(_issue("Warning", "Deprecated Finalization", no,
                                 "Java finalization is deprecated and unreliable for resource management.",
                                 "Use try-with-resources or explicit lifecycle management."))
        if re.search(r"\bSystem\.gc\s*\(\s*\)", line):
            issues.append(_issue("Info", "Explicit Garbage Collection", no,
                                 "Explicit GC requests are usually unnecessary and may hurt performance.",
                                 "Let the JVM manage garbage collection unless there is a measured reason."))
        if re.search(r"\b(?:Thread|Object)\.sleep\s*\(", line) and re.search(r"catch\s*\(\s*InterruptedException", code):
            # Inform only when interruption is explicitly swallowed.
            pass
        if re.search(r"catch\s*\(\s*InterruptedException\s+\w+\s*\)\s*\{\s*\}", masked):
            issues.append(_issue("Warning", "InterruptedException Swallowed", no,
                                 "InterruptedException is silently ignored.",
                                 "Restore the interrupt status or handle interruption deliberately."))
        # Raw collections.
        if re.search(r"\b(?:List|Map|Set|ArrayList|HashMap|HashSet)\s+\w+\s*(?:=|;)", masked) and not re.search(r"<[^>]+>", line):
            issues.append(_issue("Warning", "Raw Collection Type", no,
                                 "A collection is used without generic type parameters.",
                                 "Use parameterized collections such as List<String>."))
        # File paths assembled directly from user input.
        if re.search(r"(?:new\s+File|Paths\.get|FileInputStream|FileReader|FileWriter)\s*\([^)]*\b(?:request|input|args|param|user)\b", masked, re.I):
            issues.append(_issue("Warning", "Potential Path Traversal", no,
                                 "A filesystem path appears to use externally supplied input directly.",
                                 "Validate and constrain paths before accessing the filesystem."))
        # Weak randomness for security-sensitive identifiers.
        if re.search(r"\bnew\s+Random\s*\(", line) and re.search(r"(?:token|password|secret|key|otp|auth)", code, re.I):
            issues.append(_issue("Warning", "Weak Randomness", no,
                                 "java.util.Random is not suitable for security-sensitive values.",
                                 "Use SecureRandom for tokens, keys, OTPs, or authentication values."))
        # Direct SQL concatenation with variables.
        if re.search(r"\b(?:SELECT|INSERT|UPDATE|DELETE)\b", line, re.I) and re.search(r"\+\s*\w+", line):
            issues.append(_issue("Error", "SQL Injection Risk", no,
                                 "SQL appears to concatenate a variable into the statement.",
                                 "Use PreparedStatement parameters."))
        # Deprecated dangerous runtime execution patterns.
        if re.search(r"\bRuntime\.getRuntime\(\)\.exec\s*\(", line):
            issues.append(_issue("Error", "Command Injection Risk", no,
                                 "Runtime.exec executes operating-system commands.",
                                 "Avoid command execution or strictly validate fixed arguments."))

    # Detect methods that return null in a branch and a non-null value elsewhere only as an informational review.
    if re.search(r"\bpublic\s+[^;{]+\s+\w+\s*\([^)]*\)\s*\{", masked):
        for no, line in enumerate(masked.splitlines(), 1):
            if re.search(r"\breturn\s+null\s*;", line):
                issues.append(_issue("Info", "Null Return", no,
                                     "A method explicitly returns null; callers must handle the possibility.",
                                     "Consider a documented contract or Optional where appropriate."))

    return issues


def _enhanced_cpp_review(code):
    """Additional C++ review rules layered on top of the existing analyzer."""
    issues = []
    lines = code.splitlines()
    masked = _mask_c_like(code)

    for no, line in enumerate(lines, 1):
        # scanf-style unbounded string input.
        if re.search(r"\b(?:scanf|sscanf|fscanf)\s*\([^\n]*%s", line):
            issues.append(_issue("Warning", "Unbounded String Input", no,
                                 "A scanf-style call reads a string without a visible width limit.",
                                 "Use a bounded width or std::string/std::getline."))
        # More unsafe C string APIs.
        unsafe = re.search(r"\b(strncpy|strncat|memcpy|memmove)\s*\(", line)
        if unsafe and re.search(r"\b(?:input|user|request|data|buffer)\b", line, re.I):
            issues.append(_issue("Warning", "Buffer Safety Review", no,
                                 f"`{unsafe.group(1)}()` requires careful size validation.",
                                 "Validate source and destination sizes before copying memory."))
        # sizeof pointer bug.
        if re.search(r"\bsizeof\s*\(\s*\*?\s*\w+\s*\)\b", line) and re.search(r"\b\w+\s*\*", line):
            pass
        # Prefer RAII for raw new allocations.
        if re.search(r"\b(?:int|char|float|double|bool|long|short|std::string)\s*\*\s*\w+\s*=\s*new\b", line):
            issues.append(_issue("Info", "Raw Owning Pointer", no,
                                 "A raw pointer owns dynamically allocated memory.",
                                 "Prefer std::unique_ptr, std::shared_ptr, or standard containers when appropriate."))
        # Dangerous C library/process calls.
        if re.search(r"\b(?:system|popen)\s*\(", line):
            issues.append(_issue("Error", "Command Execution", no,
                                 "An operating-system command is executed from the program.",
                                 "Avoid shell execution with untrusted input."))
        # Secret-like literals.
        if re.search(r"\b(?:password|passwd|secret|api[_-]?key|token|private[_-]?key)\b\s*=\s*(?:\"[^\"]+\"|'[^']+'|\d+)", line, re.I):
            issues.append(_issue("Error", "Hardcoded Secret", no,
                                 "A sensitive credential appears to be embedded in source code.",
                                 "Move secrets to secure configuration."))
        # Dangerous cast.
        if re.search(r"\bconst_cast\s*<", line):
            issues.append(_issue("Warning", "Const Cast", no,
                                 "const_cast can remove const-safety guarantees.",
                                 "Avoid casting away const unless the underlying object is genuinely mutable."))
        # Virtual destructor review for polymorphic base classes.
        if re.search(r"\b(?:class|struct)\s+\w+[^\n{]*\{", line) and "virtual" not in line:
            pass
        # Signed/unsigned comparison is a common warning pattern.
        if re.search(r"\b(?:int|long|short)\s+\w+", line) and re.search(r"\b(?:size_t|unsigned)\b", line) and re.search(r"(?:<|>|<=|>=)", line):
            issues.append(_issue("Warning", "Signed/Unsigned Comparison", no,
                                 "Signed and unsigned numeric values are compared on the same expression.",
                                 "Use compatible types to avoid surprising conversion behavior."))
        # std::endl flushes every time.
        if "std::endl" in line or re.search(r"\bendl\b", line):
            issues.append(_issue("Info", "Frequent Stream Flush", no,
                                 "std::endl flushes the stream in addition to writing a newline.",
                                 "Use '\\n' when flushing is not required for better performance."))

    # Duplicate include guard / pragma once review.
    if re.search(r"#\s*ifndef\s+\w+", masked) and re.search(r"#\s*define\s+\w+", masked):
        pass

    return issues

def _java_syntax_issues(code):
    """High-confidence Java lexical/syntax checks with cascade suppression."""
    issues = []
    lines = code.splitlines()
    stack = []
    pairs = {')': '(', ']': '[', '}': '{'}
    opens = set(pairs.values())
    in_block_comment = False
    unterminated_string_lines = set()
    unmatched_close_lines = set()

    for line_no, raw in enumerate(lines, 1):
        i = 0
        in_string = None
        escaped = False
        code_chars = []
        while i < len(raw):
            ch = raw[i]
            nxt = raw[i + 1] if i + 1 < len(raw) else ''
            if in_block_comment:
                if ch == '*' and nxt == '/':
                    in_block_comment = False
                    i += 2
                else:
                    i += 1
                continue
            if in_string:
                if escaped:
                    escaped = False
                elif ch == '\\':
                    escaped = True
                elif ch == in_string:
                    in_string = None
                i += 1
                continue
            if ch == '/' and nxt == '*':
                in_block_comment = True
                i += 2
                continue
            if ch == '/' and nxt == '/':
                break
            if ch in ('"', "'"):
                in_string = ch
                i += 1
                continue
            code_chars.append(ch)
            if ch in opens:
                stack.append((ch, line_no))
            elif ch in pairs:
                if not stack or stack[-1][0] != pairs[ch]:
                    unmatched_close_lines.add(line_no)
                else:
                    stack.pop()
            i += 1

        if in_string:
            unterminated_string_lines.add(line_no)
            issues.append(_issue(
                'Error', 'Unterminated String Literal', line_no,
                'A string or character literal is not closed on this line.',
                'Add the missing closing quote before the end of the statement.'
            ))

        clean = ''.join(code_chars).strip()
        if not clean or clean.startswith(('@', 'package ', 'import ', 'public class ', 'class ', 'interface ', 'enum ')):
            continue
        if re.search(r'[{}]\s*$', clean) or re.match(r'^(if|else|for|while|switch|try|catch|finally|do|synchronized)\b', clean):
            continue
        if re.match(r'^(public|private|protected|static|final|abstract|native|synchronized)\b', clean) and re.search(r'\)\s*$', clean):
            continue
        if (re.search(r'(?:\)|\]|\b(?:int|long|double|float|boolean|char|byte|short|String|var|return|throw|break|continue|new|this|super|[A-Za-z_]\w*))\s*$', clean)
            and not clean.endswith(';') and not clean.endswith(':')):
            if not re.search(r'\b(?:if|for|while|switch|catch)\s*\([^)]*\)\s*$', clean):
                issues.append(_issue(
                    'Error', 'Missing Semicolon', line_no,
                    'This Java statement appears to be missing a semicolon.',
                    'Add `;` at the end of the statement.'
                ))

    # Do not emit a second delimiter error for a line already broken by an
    # unterminated quote. This prevents quote errors from cascading into
    # misleading ')' / '}' diagnostics.
    for line_no in sorted(unmatched_close_lines):
        if line_no in unterminated_string_lines:
            continue
        # If an earlier unterminated string exists, a later closing delimiter
        # may be a cascade artifact rather than an independent root cause.
        if any(x < line_no for x in unterminated_string_lines):
            continue
        raw = lines[line_no - 1]
        # Find the first closing delimiter that is obviously unmatched.
        for ch in raw:
            if ch in pairs:
                issues.append(_issue(
                    'Error', 'Unmatched Delimiter', line_no,
                    f'`{ch}` does not match the previous opening delimiter.',
                    'Check parentheses, brackets, and braces.'
                ))
                break

    # Missing closing delimiters. If the source is only a fragment (no class,
    # interface, enum, or method declaration) and has stray closing braces,
    # avoid inventing a second structural error; the fragment itself is enough
    # to explain that it is not a complete Java compilation unit.
    has_top_level_structure = bool(re.search(
        r'\b(?:class|interface|enum)\s+[A-Za-z_]\w*|\bmain\s*\([^)]*\)', code
    ))
    for opening, line_no in reversed(stack):
        closing = {'{': '}', '(': ')', '[': ']'}[opening]
        # If this opening delimiter is on a line with an unterminated
        # string/character literal, its apparent imbalance is usually a
        # consequence of the quote error. Report only the root cause.
        if line_no in unterminated_string_lines:
            continue
        # A later unmatched delimiter can also be a cascade from an earlier
        # unterminated string. Avoid duplicate/noisy structural errors.
        if any(x < line_no for x in unterminated_string_lines):
            continue
        if opening == '{' and not has_top_level_structure:
            continue
        issues.append(_issue(
            'Error', 'Unclosed Delimiter', line_no,
            f'Opening `{opening}` has no matching `{closing}`.',
            'Close the delimiter at the correct nesting level.'
        ))
    return issues


def analyze_java_code(code):
    issues = []
    lines, metrics = _generic_metrics(code, 'java')

    # Keep the existing analyzer rules, but use the Java-specific syntax pass
    # so missing semicolons and unterminated strings are reported precisely.
    issues.extend(_java_syntax_issues(code))
    issues.extend(_java_specific(code))
    issues.extend(_enhanced_java_review(code))
    issues.extend(_advanced_java_review(code))
    issues.extend(_find_unused_declarations(code, 'java'))

    compiler_issues = _compiler_diagnostics(code, 'java')
    missing_import_lines = {
        item.get('line') for item in issues if item.get('issue') == 'Missing Import'
    }
    issues.extend(
        item for item in compiler_issues
        if not (
            item.get('issue') == 'Compiler Diagnostic'
            and item.get('line') in missing_import_lines
            and 'cannot find symbol' in item.get('details', '')
        )
    )

    return _make_analysis(
        issues,
        _java_cpp_metrics(code, 'java'),
        _complexity_from_text(code)
    )


def _cpp_structure_issues(code):
    """High-confidence C++ function/block structure checks."""
    issues = []
    lines = _mask_c_like(code).splitlines()

    for i, raw in enumerate(lines):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not re.search(r"\)\s*$", line):
            continue
        if not re.search(
            r"\b(?:[A-Za-z_]\w*(?:::\w+)*\s+)+[A-Za-z_]\w*\s*\([^;{}]*\)\s*$",
            line
        ):
            continue
        if "{" in line:
            continue

        j = i + 1
        while j < len(lines) and not lines[j].strip():
            j += 1
        if j < len(lines) and lines[j].strip().startswith("{"):
            continue

        match = re.search(r"\b([A-Za-z_]\w*)\s*\([^;{}]*\)\s*$", line)
        function_name = match.group(1) if match else "function"
        issues.append(_issue(
            "Error", "Missing Opening Brace", i + 1,
            f"Function `{function_name}` has no opening `{{` before its body.",
            f"Add `{{` after the `{function_name}()` function declaration."
        ))

    return issues


def analyze_c_family_code(code, language):
    if language.lower() == "c":
        _, metrics = _generic_metrics(code, "cpp")
        return _make_analysis([
            _issue("Error", "Unsupported Language", 1, "C is not enabled in CodeLens. Use C++ instead.", "Select C++ as the analysis language.")
        ], metrics, {"score": 0, "level": "Not analyzed"})
    issues = []
    issues.extend(_cpp_structure_issues(code))
    issues.extend(_delimiter_issues(code, "cpp"))
    issues.extend(_cpp_specific(code))
    issues.extend(_enhanced_cpp_review(code))
    issues.extend(_advanced_cpp_review(code))
    issues.extend(_find_unused_declarations(code, "cpp"))
    compiler_issues = _compiler_diagnostics(code, "cpp")
    static_error_lines = {
        item.get("line") for item in issues
        if item.get("severity") == "Error"
        and item.get("issue") in {
            "Invalid Stream Expression", "Assignment In Condition",
            "Division By Zero", "Unsafe C String API", "Unmatched Delimiter",
            "Unclosed Delimiter", "Invalid Syntax"
        }
    }
    issues.extend(
        item for item in compiler_issues
        if not (item.get("issue") == "Compiler Diagnostic" and item.get("line") in static_error_lines)
    )
    metrics = _java_cpp_metrics(code, "cpp")
    return _make_analysis(issues, metrics, _complexity_from_text(code))


@app.route("/api/analyze", methods=["POST"])
@login_required
def api_analyze():

    try:
        # =====================================================
        # GET REQUEST DATA
        # =====================================================

        data = request.get_json(silent=True) or {}

        code = (data.get("code") or "").strip()
        language = (data.get("language") or "python").strip().lower()
        filename = (data.get("filename") or "Untitled").strip()

        # =====================================================
        # VALIDATE CODE
        # =====================================================

        if not code:
            return jsonify({
                "success": False,
                "message": "No code provided."
            }), 400

        # =====================================================
        # NORMALIZE LANGUAGE
        # =====================================================

        if language == "c++":
            language = "cpp"

        # =====================================================
        # RUN STATIC ANALYSIS
        # =====================================================

        if language == "python":

            analysis = analyze_python_code(code)

        elif language == "java":

            analysis = analyze_java_code(code)

        elif language in ("c", "cpp"):

            analysis = analyze_c_family_code(
                code,
                language
            )

        else:

            lines, metrics = _generic_metrics(
                code,
                language
            )

            analysis = _make_analysis(
                [
                    {
                        "severity": "Info",
                        "issue": "Language Review Not Available",
                        "line": 1,
                        "details":
                            f"Static review for '{language}' "
                            "is not configured yet."
                    }
                ],
                metrics,
                "Not analyzed"
            )

        # =====================================================
        # SAFETY CHECK
        # =====================================================

        if not isinstance(analysis, dict):
            return jsonify({
                "success": False,
                "message": "Analyzer returned an invalid result."
            }), 500

        # =====================================================
        # CALCULATE RESULT SCORES
        # =====================================================

        scores = _calculate_scores(
            analysis,
            code
        )

        # =====================================================
        # ADD SCORES TO ANALYSIS
        # =====================================================

        analysis["scores"] = {
            "quality": scores.get("quality", 0),
            "maintainability": scores.get("maintainability", 0),
            "complexity": scores.get("complexity", 0),
            "readability": scores.get("readability", 0),
            "security": scores.get("security", 0)
        }

        analysis["quality_score"] = scores.get(
            "quality",
            analysis.get("quality_score", 0)
        )

        analysis["maintainability"] = scores.get(
            "maintainability",
            0
        )

        analysis["complexity_score"] = scores.get(
            "complexity",
            0
        )

        analysis["readability"] = scores.get(
            "readability",
            0
        )

        analysis["security"] = scores.get(
            "security",
            0
        )

        # =====================================================
        # MAKE SURE ISSUES COUNT EXISTS
        # =====================================================

        if "issues_count" not in analysis:

            analysis["issues_count"] = len(
                analysis.get("issues", [])
            )

        # =====================================================
        # SAVE TO DATABASE
        # =====================================================

        connection = get_db()

        try:

            cursor = connection.execute(
                """
                INSERT INTO analyses
                (
                    user_id,
                    filename,
                    language,
                    code,
                    issues_count,
                    quality_score,
                    complexity,
                    analysis_result
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session["user_id"],
                    filename,
                    language,
                    code,
                    analysis["issues_count"],
                    analysis["quality_score"],
                    json.dumps(analysis.get("complexity", "Low")),
                    json.dumps(analysis)
                )
            )

            connection.commit()

            analysis_id = cursor.lastrowid

        except Exception as db_error:

            connection.rollback()

            print(
                "DATABASE ERROR:",
                repr(db_error)
            )

            return jsonify({
                "success": False,
                "message": "Unable to save analysis.",
                "error": str(db_error)
            }), 500

        finally:

            connection.close()

        # =====================================================
        # SUCCESS RESPONSE
        # =====================================================

        return jsonify({

            "success": True,

            "message":
                "Code analyzed successfully.",

            "analysis_id":
                analysis_id,

            # Front-end navigation target.
            # The Analyze page can use this value after a successful POST
            # to move the user directly to the Results page.
            "redirect_url":
                f"/results?analysis_id={analysis_id}",

            "results_url":
                f"/results?analysis_id={analysis_id}",

            "issues_count":
                analysis.get("issues_count", 0),

            "quality_score":
                analysis.get("quality_score", 0),

            "complexity":
                analysis.get("complexity", "Low"),

            "scores": {

                "quality":
                    analysis["scores"]["quality"],

                "maintainability":
                    analysis["scores"]["maintainability"],

                "complexity":
                    analysis["scores"]["complexity"],

                "readability":
                    analysis["scores"]["readability"],

                "security":
                    analysis["scores"]["security"]
            }

        }), 200

    # =========================================================
    # CATCH ALL ANALYSIS ERRORS
    # =========================================================

    except Exception as error:

        print(
            "ANALYSIS API ERROR:",
            repr(error)
        )

        return jsonify({

            "success": False,

            "message":
                "Code analysis failed.",

            "error":
                str(error)

        }), 500

@app.route(
    "/api/analysis/<int:analysis_id>"
)
@login_required
def get_analysis(analysis_id):

    user_id = session["user_id"]

    connection = get_db()


    analysis = connection.execute(

        """
        SELECT
            id,
            filename,
            language,
            code,
            issues_count,
            quality_score,
            complexity,
            analysis_result,
            created_at
        FROM analyses
        WHERE
            id = ?
            AND user_id = ?
        """,

        (
            analysis_id,
            user_id
        )
    ).fetchone()


    connection.close()


    # =====================================================
    # NOT FOUND
    # =====================================================

    if analysis is None:

        return jsonify({

            "success": False,

            "message":
                "Analysis not found."

        }), 404


    # =====================================================
    # PARSE ANALYSIS RESULT
    # =====================================================

    result = {}


    try:

        if analysis["analysis_result"]:

            if isinstance(
                analysis["analysis_result"],
                str
            ):

                result = json.loads(
                    analysis["analysis_result"]
                )

            else:

                result = (
                    analysis["analysis_result"]
                    or {}
                )

    except Exception as error:

        print(
            "Analysis result parse error:",
            error
        )

        result = {}


    # =====================================================
    # GET SCORES
    # =====================================================

    scores = (
        result.get("scores")
        or {}
    )


    quality = scores.get(
        "quality",
        result.get(
            "quality_score",
            analysis["quality_score"] or 0
        )
    )


    maintainability = scores.get(
        "maintainability",
        result.get(
            "maintainability",
            0
        )
    )


    complexity_score = scores.get(
        "complexity",
        result.get(
            "complexity_score",
            0
        )
    )


    readability = scores.get(
        "readability",
        result.get(
            "readability",
            0
        )
    )


    security = scores.get(
        "security",
        result.get(
            "security",
            0
        )
    )


    # =====================================================
    # RETURN COMPLETE ANALYSIS
    # =====================================================

    return jsonify({

        "success": True,

        "analysis": {

            "id":
                analysis["id"],

            "filename":
                analysis["filename"],

            "language":
                analysis["language"],

            "code":
                analysis["code"],

            "issues_count":
                analysis["issues_count"],

            "quality_score":
                analysis["quality_score"],

            "complexity":
                analysis["complexity"],

            "analysis_result":
                analysis["analysis_result"],

            "created_at":
                analysis["created_at"],


            # =============================================
            # FIVE SCORES
            # =============================================

            "scores": {

                "quality":
                    quality,

                "maintainability":
                    maintainability,

                "complexity":
                    complexity_score,

                "readability":
                    readability,

                "security":
                    security

            },


            # =============================================
            # DIRECT VALUES TOO
            # =============================================

            "maintainability":
                maintainability,

            "complexity_score":
                complexity_score,

            "readability":
                readability,

            "security":
                security

        }

    })

# =========================================================
# ANALYSIS HISTORY API
# =========================================================

@app.route(
    "/api/analyses"
)
@login_required
def get_analyses():

    connection = get_db()


    rows = connection.execute(
        """
        SELECT
            id,
            filename,
            language,
            issues_count,
            quality_score,
            complexity,
            created_at
        FROM analyses
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (
            session["user_id"],
        )
    ).fetchall()


    connection.close()


    analyses = []


    for row in rows:

        analyses.append({

            "id":
                row["id"],

            "filename":
                row["filename"],

            "language":
                row["language"],

            "issues_count":
                row["issues_count"],

            "quality_score":
                row["quality_score"],

            "complexity":
                row["complexity"],

            "created_at":
                row["created_at"]
        })


    return jsonify({

        "success": True,

        "analyses":
            analyses
    })

# =========================================================
# CODELENS - SCORE CALCULATION
# =========================================================

def _calculate_scores(analysis, code):
    """
    Calculate the five Results page scores.

    Overall Quality   : 0 - 100
    Maintainability   : 0 - 100
    Complexity         : 0 - 50
    Readability        : 0 - 100
    Security           : 0 - 100
    """

    issues = analysis.get("issues", []) or []
    metrics = analysis.get("metrics", {}) or {}

    quality_score = int(
        analysis.get("quality_score", 0) or 0
    )

    # The analyzer stores complexity as a dictionary, while the database
    # stores it as JSON text. Normalize both forms before calculating the
    # Results-page complexity score.
    raw_complexity = analysis.get("complexity", "Low") or "Low"

    if isinstance(raw_complexity, dict):
        complexity_text = str(
            raw_complexity.get("level", "Low") or "Low"
        ).strip().lower()
    else:
        complexity_text = str(raw_complexity).strip().lower()

        # Handle JSON saved in the analyses table.
        if complexity_text.startswith("{"):
            try:
                parsed_complexity = json.loads(raw_complexity)
                if isinstance(parsed_complexity, dict):
                    complexity_text = str(
                        parsed_complexity.get("level", "Low") or "Low"
                    ).strip().lower()
            except (TypeError, ValueError, json.JSONDecodeError):
                pass


    # =====================================================
    # 1. OVERALL QUALITY
    # =====================================================

    overall_quality = max(
        0,
        min(
            100,
            quality_score
        )
    )


    # =====================================================
    # 2. MAINTAINABILITY
    # =====================================================

    maintainability = 100

    for issue in issues:

        severity = str(
            issue.get("severity", "Info")
        ).lower()

        issue_name = str(
            issue.get("issue", "")
        ).lower()

        if severity == "error":
            maintainability -= 12

        elif severity == "warning":
            maintainability -= 6

        else:
            maintainability -= 2

        # Additional maintainability penalties
        if "long function" in issue_name:
            maintainability -= 4

        if "too many arguments" in issue_name:
            maintainability -= 4

        if "duplicate" in issue_name:
            maintainability -= 3

        if "unused variable" in issue_name:
            maintainability -= 2

        if "unused import" in issue_name:
            maintainability -= 2


    maintainability = max(
        0,
        min(
            100,
            maintainability
        )
    )


    # =====================================================
    # 3. COMPLEXITY SCORE /50
    # =====================================================

    if complexity_text == "low":
        complexity_score = 50

    elif complexity_text == "medium":
        complexity_score = 40

    elif complexity_text == "high":
        complexity_score = 25

    elif complexity_text == "very high":
        complexity_score = 10

    else:
        complexity_score = 0


    # =====================================================
    # 4. READABILITY
    # =====================================================

    readability = 100

    total_lines = int(
        metrics.get("total_lines", 0) or 0
    )

    comment_lines = int(
        metrics.get("comment_lines", 0) or 0
    )

    # Issue-based readability reduction
    for issue in issues:

        issue_name = str(
            issue.get("issue", "")
        ).lower()

        severity = str(
            issue.get("severity", "Info")
        ).lower()

        if "line too long" in issue_name:

            readability -= 5

        elif "print statement" in issue_name:

            readability -= 2

        elif "console output" in issue_name:

            readability -= 2

        elif "long function" in issue_name:

            readability -= 5

        elif "too many arguments" in issue_name:

            readability -= 4

        elif severity == "error":

            readability -= 3


    # Comment ratio can slightly improve readability.
    if total_lines > 0:

        comment_ratio = (
            comment_lines / total_lines
        )

        if comment_ratio >= 0.10:
            readability += 3

        elif comment_ratio == 0:
            readability -= 3


    readability = max(
        0,
        min(
            100,
            readability
        )
    )


    # =====================================================
    # 5. SECURITY
    # =====================================================

    security = 100

    security_keywords = [
        "security",
        "vulnerability",
        "unsafe",
        "eval",
        "exec",
        "injection",
        "password",
        "secret",
        "api key",
        "apikey",
        "system()",
        "gets()",
        "process execution",
        "sensitive data"
    ]


    security_issue_count = 0


    for issue in issues:

        issue_text = (
            str(issue.get("issue", "")) +
            " " +
            str(issue.get("details", "")) +
            " " +
            str(issue.get("message", ""))
        ).lower()


        if any(
            keyword in issue_text
            for keyword in security_keywords
        ):

            security_issue_count += 1


            severity = str(
                issue.get("severity", "Info")
            ).lower()


            if severity == "error":
                security -= 25

            elif severity == "warning":
                security -= 15

            else:
                security -= 5


    security = max(
        0,
        min(
            100,
            security
        )
    )


    # =====================================================
    # FINAL SCORE OBJECT
    # =====================================================

    return {
        "quality": overall_quality,
        "overall_quality": overall_quality,

        "maintainability": maintainability,

        "complexity": complexity_score,

        "readability": readability,

        "security": security
    }
# =========================================================
# RESULTS PAGE
# =========================================================

@app.route("/results")
@login_required
def results():

    user = get_current_user()

    first_letter = "U"


    if user:

        name = (
            user["full_name"]
            or user["username"]
            or "User"
        )

        first_letter = name[0].upper()


    return render_template(
        "results.html",
        user=user,
        first_letter=first_letter
    )


# =========================================================
# SAVED CODE PAGE
# =========================================================

@app.route("/saved-code")
@login_required
def saved_code():

    user = get_current_user()

    first_letter = "U"


    if user:

        name = (
            user["full_name"]
            or user["username"]
            or "User"
        )

        first_letter = name[0].upper()


    return render_template(
        "save.html",
        user=user,
        first_letter=first_letter
    )


# =========================================================
# SAVE CODE API
# =========================================================

@app.route(
    "/api/saved-code",
    methods=["GET", "POST"]
)
@login_required
def saved_code_api():

    connection = get_db()


    # -----------------------------------------------------
    # GET SAVED CODE
    # -----------------------------------------------------

    if request.method == "GET":

        rows = connection.execute(
            """
            SELECT
                id,
                filename,
                language,
                code,
                created_at
            FROM saved_code
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (
                session["user_id"],
            )
        ).fetchall()


        connection.close()


        saved = []


        for row in rows:

            saved.append({

                "id":
                    row["id"],

                "filename":
                    row["filename"],

                "language":
                    row["language"],

                "code":
                    row["code"],

                "created_at":
                    row["created_at"]
            })


        return jsonify({

            "success": True,

            "saved_code":
                saved
        })


    # -----------------------------------------------------
    # POST / SAVE CODE
    # -----------------------------------------------------

    data = (
        request.get_json(
            silent=True
        )
        or {}
    )


    filename = (
        data.get("filename")
        or "Untitled"
    ).strip()


    language = (
        data.get("language")
        or "python"
    ).strip().lower()


    code = (
        data.get("code")
        or ""
    )


    if not code.strip():

        connection.close()

        return jsonify({
            "success": False,
            "message":
                "No code provided."
        }), 400


    cursor = connection.execute(
        """
        INSERT INTO saved_code
        (
            user_id,
            filename,
            language,
            code
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            session["user_id"],
            filename,
            language,
            code
        )
    )


    connection.commit()

    saved_id = cursor.lastrowid

    connection.close()


    return jsonify({

        "success": True,

        "message":
            "Code saved successfully.",

        "saved_id":
            saved_id
    })


# =========================================================
# DELETE SAVED CODE
# =========================================================

@app.route(
    "/api/saved-code/<int:saved_id>",
    methods=["DELETE"]
)
@login_required
def delete_saved_code(
    saved_id
):

    connection = get_db()


    cursor = connection.execute(
        """
        DELETE FROM saved_code
        WHERE
            id = ?
            AND user_id = ?
        """,
        (
            saved_id,
            session["user_id"]
        )
    )


    connection.commit()

    deleted = cursor.rowcount

    connection.close()


    if deleted == 0:

        return jsonify({
            "success": False,
            "message":
                "Saved code not found."
        }), 404


    return jsonify({

        "success": True,

        "message":
            "Saved code deleted."
    })








# =========================================================
# REPORTS PAGE
# =========================================================

@app.route("/reports")
@login_required
def reports():

    user = get_current_user()

    first_letter = "U"

    if user:
        name = (
            user["full_name"]
            or user["username"]
            or "User"
        )

        first_letter = name[0].upper()

    return render_template(
        "reports.html",
        user=user,
        first_letter=first_letter
    )


# =========================================================
# REPORTS API
# =========================================================

@app.route("/api/reports", methods=["GET", "POST"])
@login_required
def reports_api():

    connection = get_db()

    # =====================================================
    # GET GENERATED REPORTS
    # =====================================================

    if request.method == "GET":

        rows = connection.execute(
            """
            SELECT
                id,
                report_name,
                report_type,
                language,
                analysis_id,
                file_path,
                created_at
            FROM reports
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (session["user_id"],)
        ).fetchall()

        connection.close()

        reports_data = []

        for row in rows:
            reports_data.append({
                "id": row["id"],
                "report_name": row["report_name"],
                "report_type": row["report_type"],
                "language": row["language"],
                "analysis_id": row["analysis_id"],
                "file_path": row["file_path"],
                "created_at": row["created_at"]
            })

        return jsonify({
            "success": True,
            "reports": reports_data
        })

    # =====================================================
    # POST - GENERATE PDF REPORT
    # =====================================================

    data = request.get_json(silent=True) or {}

    report_type = (
        data.get("report_type")
        or "Full Code Review"
    ).strip()

    allowed_types = [
        "Full Code Review",
        "Analysis Report"
    ]

    if report_type not in allowed_types:
        connection.close()

        return jsonify({
            "success": False,
            "message": "Invalid report type."
        }), 400

    analysis_id = data.get("analysis_id")

    # =====================================================
    # GET ANALYSIS
    # =====================================================

    if analysis_id:

        analysis = connection.execute(
            """
            SELECT
                id,
                filename,
                language,
                code,
                issues_count,
                quality_score,
                complexity,
                analysis_result,
                created_at
            FROM analyses
            WHERE id = ?
            AND user_id = ?
            """,
            (
                analysis_id,
                session["user_id"]
            )
        ).fetchone()

    else:

        analysis = connection.execute(
            """
            SELECT
                id,
                filename,
                language,
                code,
                issues_count,
                quality_score,
                complexity,
                analysis_result,
                created_at
            FROM analyses
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (session["user_id"],)
        ).fetchone()

    if not analysis:

        connection.close()

        return jsonify({
            "success": False,
            "message": "Please analyze your code before generating a report."
        }), 400

    # =====================================================
    # ANALYSIS INFORMATION
    # =====================================================

    analysis_id = analysis["id"]

    filename = analysis["filename"] or "Untitled Code"

    language = analysis["language"] or "Unknown"

    issues_count = analysis["issues_count"] or 0

    quality_score = analysis["quality_score"] or 0

    complexity = analysis["complexity"] or "Not Available"

    analysis_result = analysis["analysis_result"] or "{}"

    # =====================================================
    # PARSE ANALYSIS RESULT
    # =====================================================

    try:
        result_data = json.loads(analysis_result)

        if not isinstance(result_data, dict):
            result_data = {}

    except Exception:
        result_data = {}

    issues = result_data.get("issues", [])

    if not isinstance(issues, list):
        issues = []

    # =====================================================
    # REPORT DIRECTORY
    # =====================================================

    report_directory = os.path.join(
        app.root_path,
        "static",
        "reports"
    )

    os.makedirs(
        report_directory,
        exist_ok=True
    )

    # =====================================================
    # SAFE FILE NAME
    # =====================================================

    safe_filename = os.path.splitext(
        os.path.basename(filename)
    )[0]

    safe_filename = "".join(
        character
        for character in safe_filename
        if character.isalnum()
        or character in (" ", "_", "-")
    ).strip()

    if not safe_filename:
        safe_filename = "Code"

    # =====================================================
    # TIMESTAMP
    # =====================================================

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    report_name = (
        report_type
        + " - "
        + safe_filename
    )

    pdf_filename = (
        "codelens_"
        + safe_filename.replace(" ", "_")
        + "_"
        + timestamp
        + ".pdf"
    )

    pdf_path = os.path.join(
        report_directory,
        pdf_filename
    )

    # =====================================================
    # PDF DOCUMENT
    # =====================================================

    document = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # -----------------------------------------------------
    # PDF FONT SETUP
    # Georgia is used for titles/headings/table headers.
    # Times New Roman is used for normal text and numbers.
    # Windows font paths are used when available; otherwise
    # ReportLab built-in fonts are used as a safe fallback.
    # -----------------------------------------------------
    georgia_font = "Times-Bold"
    georgia_regular_font = "Times-Roman"
    times_font = "Times-Roman"
    times_bold_font = "Times-Bold"

    windows_fonts = os.path.join(
        os.environ.get("WINDIR", r"C:\Windows"),
        "Fonts"
    )

    georgia_regular_path = os.path.join(windows_fonts, "georgia.ttf")
    georgia_bold_path = os.path.join(windows_fonts, "georgiab.ttf")
    times_regular_path = os.path.join(windows_fonts, "times.ttf")
    times_bold_path = os.path.join(windows_fonts, "timesbd.ttf")

    try:
        if os.path.exists(georgia_regular_path):
            pdfmetrics.registerFont(
                TTFont("CodeLensGeorgia", georgia_regular_path)
            )
            georgia_regular_font = "CodeLensGeorgia"

        if os.path.exists(georgia_bold_path):
            pdfmetrics.registerFont(
                TTFont("CodeLensGeorgiaBold", georgia_bold_path)
            )
            georgia_font = "CodeLensGeorgiaBold"

        if os.path.exists(times_regular_path):
            pdfmetrics.registerFont(
                TTFont("CodeLensTimes", times_regular_path)
            )
            times_font = "CodeLensTimes"

        if os.path.exists(times_bold_path):
            pdfmetrics.registerFont(
                TTFont("CodeLensTimesBold", times_bold_path)
            )
            times_bold_font = "CodeLensTimesBold"
    except Exception:
        # Keep ReportLab built-in fonts if Windows fonts cannot be loaded.
        pass

    title_style = ParagraphStyle(
        "CodeLensTitle",
        parent=styles["Normal"],
        fontName=georgia_font,
        fontSize=17,
        leading=20,
        alignment=TA_CENTER,
        spaceAfter=8
    )

    heading_style = ParagraphStyle(
        "CodeLensHeading",
        parent=styles["Normal"],
        fontName=georgia_font,
        fontSize=10.5,
        leading=13,
        spaceBefore=6,
        spaceAfter=5
    )

    normal_style = ParagraphStyle(
        "CodeLensNormal",
        parent=styles["Normal"],
        fontName=times_font,
        fontSize=11,
        leading=14
    )

    table_header_style = ParagraphStyle(
        "CodeLensTableHeader",
        parent=styles["Normal"],
        fontName=georgia_font,
        fontSize=8.5,
        leading=10
    )

    table_number_style = ParagraphStyle(
        "CodeLensTableNumber",
        parent=styles["Normal"],
        fontName=times_font,
        fontSize=10.5,
        leading=13
    )

    table_content_style = ParagraphStyle(
        "CodeLensTableContent",
        parent=styles["Normal"],
        fontName=times_font,
        fontSize=10.5,
        leading=13
    )

    story = []

    # =====================================================
    # PDF TITLE
    # =====================================================

    story.append(
        Paragraph(
            "CODELENS",
            title_style
        )
    )

    story.append(
        Paragraph(
            str(report_type).upper(),
            heading_style
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    basic_data = [
        ["FILE", filename],
        ["LANGUAGE", language.upper()],
        ["REPORT TYPE", str(report_type).upper()],
        [
            "GENERATED",
            datetime.now().strftime(
                "%d %b %Y, %I:%M %p"
            )
        ],
        ["ANALYSIS ID", str(analysis_id)]
    ]

    basic_table = Table(
        basic_data,
        colWidths=[130, 350]
    )

    basic_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),
            (
                "FONTNAME",
                (0, 0),
                (-1, -1),
                times_font
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                8
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                6
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                6
            )
        ])
    )

    story.append(basic_table)

    story.append(
        Spacer(1, 20)
    )

    # =====================================================
    # SUMMARY
    # =====================================================

    story.append(
        Paragraph(
            "ANALYSIS SUMMARY",
            heading_style
        )
    )

    story.append(
        Spacer(1, 8)
    )

    summary_data = [
        [
            Paragraph("METRIC", table_header_style),
            Paragraph("VALUE", table_header_style)
        ],
        [
            Paragraph("ISSUES FOUND", table_header_style),
            Paragraph(str(issues_count), table_number_style)
        ],
        [
            Paragraph("QUALITY SCORE", table_header_style),
            Paragraph(str(quality_score) + "%", table_number_style)
        ],
        [
            Paragraph("COMPLEXITY", table_header_style),
            Paragraph(str(complexity), table_number_style)
        ]
    ]

    summary_table = Table(
        summary_data,
        colWidths=[250, 230]
    )

    summary_table.setStyle(
        TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#87CEEB")
            ),
            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.black
            ),
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),
            (
                "ALIGN",
                (1, 1),
                (1, -1),
                "CENTER"
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                5
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                5
            )
        ])
    )

    story.append(summary_table)

    story.append(
        Spacer(1, 20)
    )

    # =====================================================
    # ISSUES
    # =====================================================

    story.append(
        Paragraph(
            "ISSUES FOUND",
            heading_style
        )
    )

    story.append(
        Spacer(1, 8)
    )

    if issues:

        issue_rows = [
            [
                Paragraph("LINE", table_header_style),
                Paragraph("SEVERITY", table_header_style),
                Paragraph("ISSUE", table_header_style),
                Paragraph("DETAILS", table_header_style)
            ]
        ]

        for issue in issues:

            if not isinstance(issue, dict):
                continue

            line = issue.get(
                "line",
                "-"
            )

            severity = issue.get(
                "severity",
                "Info"
            )

            issue_name = issue.get(
                "issue",
                "Issue"
            )

            details = issue.get(
                "details",
                ""
            )

            issue_rows.append([
                Paragraph(str(line), table_number_style),
                Paragraph(str(severity), table_content_style),
                Paragraph(
                    str(issue_name),
                    normal_style
                ),
                Paragraph(
                    str(details),
                    normal_style
                )
            ])

        if len(issue_rows) > 1:

            issue_table = Table(
                issue_rows,
                colWidths=[
                    45,
                    70,
                    150,
                    215
                ],
                repeatRows=1
            )

            issue_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#87CEEB")
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "TOP"
                    ),
                    (
                        "TOPPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    ),
                    (
                        "BOTTOMPADDING",
                        (0, 0),
                        (-1, -1),
                        6
                    )
                ])
            )

            story.append(issue_table)

        else:

            story.append(
                Paragraph(
                    "No issues were found during the analysis.",
                    normal_style
                )
            )

    else:

        story.append(
            Paragraph(
                "No issues were found during the analysis.",
                normal_style
            )
        )

    # =====================================================
    # FULL CODE REVIEW
    # =====================================================

    if report_type == "Full Code Review":

        story.append(
            Spacer(1, 20)
        )

        story.append(
            Paragraph(
                "CODE REVIEW",
                heading_style
            )
        )

        story.append(
            Spacer(1, 8)
        )

        code_text = analysis["code"] or ""

        if code_text:

            escaped_code = (
                code_text
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("\n", "<br/>")
            )

            story.append(
                Paragraph(
                    escaped_code,
                    normal_style
                )
            )

        else:

            story.append(
                Paragraph(
                    "No source code available.",
                    normal_style
                )
            )

    # =====================================================
    # BUILD PDF
    # =====================================================

    document.build(story)

    # =====================================================
    # DATABASE RECORD
    # =====================================================

    relative_file_path = (
        "reports/"
        + pdf_filename
    )

    cursor = connection.execute(
        """
        INSERT INTO reports
        (
            user_id,
            report_name,
            report_type,
            language,
            analysis_id,
            file_path
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            session["user_id"],
            report_name,
            report_type,
            language,
            analysis_id,
            relative_file_path
        )
    )

    connection.commit()

    report_id = cursor.lastrowid

    connection.close()

    # =====================================================
    # RESPONSE
    # =====================================================

    return jsonify({
        "success": True,
        "message": "Report generated successfully.",
        "report_id": report_id,
        "report_name": report_name,
        "report_type": report_type,
        "language": language,
        "analysis_id": analysis_id,
        "file_path": "/static/" + relative_file_path
    })
@app.route("/api/reports/<int:report_id>", methods=["DELETE"])
@login_required
def delete_report(report_id):

    connection = get_db()

    report = connection.execute(
        """
        SELECT file_path
        FROM reports
        WHERE id = ?
        AND user_id = ?
        """,
        (
            report_id,
            session["user_id"]
        )
    ).fetchone()

    if not report:
        connection.close()

        return jsonify({
            "success": False,
            "message": "Report not found."
        }), 404

    file_path = report["file_path"]

    connection.execute(
        """
        DELETE FROM reports
        WHERE id = ?
        AND user_id = ?
        """,
        (
            report_id,
            session["user_id"]
        )
    )

    connection.commit()
    connection.close()


    # Delete physical PDF file

    if file_path:

        full_path = os.path.join(
            app.root_path,
            "static",
            file_path
        )

        if os.path.exists(full_path):

            try:
                os.remove(full_path)

            except OSError as error:

                print(
                    "PDF delete error:",
                    error
                )


    return jsonify({
        "success": True,
        "message": "Report deleted successfully."
    })
# =========================================================
# PROFILE
# =========================================================

@app.route("/profile")
@login_required
def profile():

    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    name = (
        user["full_name"]
        or user["username"]
        or "User"
    )

    first_letter = name[0].upper()

    return render_template(
        "profile.html",
        user=user,
        first_letter=first_letter
    )


# =========================================================
# PROFILE UPDATE
# =========================================================

@app.route("/api/profile", methods=["POST"])
@login_required
def update_profile():

    data = request.get_json(silent=True) or {}

    full_name = (
        data.get("full_name") or ""
    ).strip()

    email = (
        data.get("email") or ""
    ).strip().lower()

    username = (
        data.get("username") or ""
    ).strip()


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not full_name:
        return jsonify({
            "success": False,
            "message": "Full name is required."
        }), 400


    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required."
        }), 400


    if not username:
        return jsonify({
            "success": False,
            "message": "Username is required."
        }), 400


    connection = get_db()


    try:

        # -------------------------------------------------
        # CHECK DUPLICATE EMAIL
        # -------------------------------------------------

        existing_email = connection.execute(
            """
            SELECT id
            FROM users
            WHERE email = ?
              AND id != ?
            """,
            (
                email,
                session["user_id"]
            )
        ).fetchone()


        if existing_email:

            connection.close()

            return jsonify({
                "success": False,
                "message": "Email already exists."
            }), 400


        # -------------------------------------------------
        # CHECK DUPLICATE USERNAME
        # -------------------------------------------------

        existing_username = connection.execute(
            """
            SELECT id
            FROM users
            WHERE username = ?
              AND id != ?
            """,
            (
                username,
                session["user_id"]
            )
        ).fetchone()


        if existing_username:

            connection.close()

            return jsonify({
                "success": False,
                "message": "Username already exists."
            }), 400


        # -------------------------------------------------
        # UPDATE USER
        # -------------------------------------------------

        connection.execute(
            """
            UPDATE users
            SET
                full_name = ?,
                email = ?,
                username = ?
            WHERE id = ?
            """,
            (
                full_name,
                email,
                username,
                session["user_id"]
            )
        )


        connection.commit()


        # -------------------------------------------------
        # UPDATE SESSION
        # -------------------------------------------------

        session["user_name"] = full_name
        session["user_email"] = email
        session["username"] = username


    except sqlite3.IntegrityError:

        connection.close()

        return jsonify({
            "success": False,
            "message": "Email or username already exists."
        }), 400


    except Exception as e:

        connection.close()

        print("PROFILE UPDATE ERROR:", e)

        return jsonify({
            "success": False,
            "message": "Unable to update profile."
        }), 500


    connection.close()


    return jsonify({
        "success": True,
        "message": "Profile updated successfully."
    })


# =========================================================
# CHANGE PASSWORD
# =========================================================

# =========================================================
# CHANGE PASSWORD
# =========================================================

@app.route("/api/profile/password", methods=["POST"])
@login_required
def change_password():

    data = request.get_json(silent=True) or {}

    current_password = (
        data.get("current_password") or ""
    )

    new_password = (
        data.get("new_password") or ""
    )

    confirm_password = (
        data.get("confirm_password") or ""
    )


    # -----------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------

    if not current_password:

        return jsonify({
            "success": False,
            "message": "Current password is required."
        }), 400


    if not new_password:

        return jsonify({
            "success": False,
            "message": "New password is required."
        }), 400


    if not confirm_password:

        return jsonify({
            "success": False,
            "message": "Confirm password is required."
        }), 400


    if new_password != confirm_password:

        return jsonify({
            "success": False,
            "message": "New password and confirm password do not match."
        }), 400


    if len(new_password) < 6:

        return jsonify({
            "success": False,
            "message": "Password must be at least 6 characters."
        }), 400


    if current_password == new_password:

        return jsonify({
            "success": False,
            "message": "New password must be different from current password."
        }), 400


    # -----------------------------------------------------
    # DATABASE
    # -----------------------------------------------------

    connection = get_db()

    try:

        user = connection.execute(
            """
            SELECT password
            FROM users
            WHERE id = ?
            """,
            (
                session["user_id"],
            )
        ).fetchone()


        if user is None:

            return jsonify({
                "success": False,
                "message": "User not found."
            }), 404


        stored_password = user["password"]


        # -------------------------------------------------
        # CHECK CURRENT PASSWORD
        #
        # Your registration currently stores passwords
        # as plain text, so compare directly.
        # -------------------------------------------------

        if stored_password != current_password:

            return jsonify({
                "success": False,
                "message": "Current password is incorrect."
            }), 400


        # -------------------------------------------------
        # SAVE NEW PASSWORD
        #
        # Keep it plain text for now so it matches your
        # existing login system.
        # -------------------------------------------------

        connection.execute(
            """
            UPDATE users
            SET password = ?
            WHERE id = ?
            """,
            (
                new_password,
                session["user_id"]
            )
        )


        connection.commit()


        return jsonify({
            "success": True,
            "message": "Password changed successfully."
        })


    except Exception as error:

        connection.rollback()

        print(
            "PASSWORD UPDATE ERROR:",
            error
        )

        return jsonify({
            "success": False,
            "message": "Unable to change password."
        }), 500


    finally:

        connection.close()

# =========================================================
# CLEAR USER HISTORY
# =========================================================

@app.route("/api/profile/clear-history", methods=["POST"])
@login_required
def clear_analysis_history():

    connection = get_db()

    try:

        user_id = session["user_id"]

        # -------------------------------------------------
        # DELETE USER'S SAVED CODE
        # -------------------------------------------------

        connection.execute(
            """
            DELETE FROM saved_code
            WHERE user_id = ?
            """,
            (user_id,)
        )

        # -------------------------------------------------
        # DELETE USER'S REPORTS
        # -------------------------------------------------

        connection.execute(
            """
            DELETE FROM reports
            WHERE user_id = ?
            """,
            (user_id,)
        )

        # -------------------------------------------------
        # DELETE USER'S ANALYSIS HISTORY
        # -------------------------------------------------

        connection.execute(
            """
            DELETE FROM analyses
            WHERE user_id = ?
            """,
            (user_id,)
        )

        connection.commit()

        return jsonify({
            "success": True,
            "message": "Analysis history, saved code and reports cleared successfully."
        })

    except Exception as error:

        connection.rollback()

        print("CLEAR HISTORY ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Unable to clear history."
        }), 500

    finally:

        connection.close()

@app.route("/api/profile/delete-account", methods=["POST"])
@login_required
def delete_account():
    connection = get_db()

    try:
        user_id = session["user_id"]

        # Delete user's saved code
        connection.execute(
            "DELETE FROM saved_code WHERE user_id = ?",
            (user_id,)
        )

        # Delete user's analyses
        connection.execute(
            "DELETE FROM analyses WHERE user_id = ?",
            (user_id,)
        )

        # Delete user's refactored code
        connection.execute(
            "DELETE FROM refactored_code WHERE user_id = ?",
            (user_id,)
        )

        # Delete user's reports
        connection.execute(
            "DELETE FROM reports WHERE user_id = ?",
            (user_id,)
        )

        # Finally delete the user account
        cursor = connection.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )

        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({
                "success": False,
                "message": "Account not found."
            }), 404

        connection.commit()

        # Clear login session
        session.clear()

        return jsonify({
            "success": True,
            "message": "Account deleted successfully."
        })

    except Exception as error:
        connection.rollback()

        print("DELETE ACCOUNT ERROR:", error)

        return jsonify({
            "success": False,
            "message": "Unable to delete account."
        }), 500

    finally:
        connection.close()




# =========================================================
# HELP & SUPPORT
# =========================================================


@app.route("/help-support")
def help_support():
    return render_template("help.html")



# =========================================================
# APPLICATION ERROR HANDLER
# =========================================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "home.html"
    ), 404


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )