# CodeLens – Code Review System

## Abstract

CodeLens – Code Review System is a web-based static code analysis and code review system designed to help developers identify and understand common issues in source code without executing the program.

The system supports multiple programming languages, including Python, Java, and C++. It analyzes submitted source code using predefined static analysis rules and provides information about detected issues such as syntax errors, unused variables and imports, code complexity, code quality violations, security-related concerns, duplicate code, readability issues, and maintainability problems.

CodeLens provides a centralized platform where users can register, log in, submit or upload source code, perform code analysis, view analysis results, save source code, generate PDF reports, manage their profile and settings, and access help and support.

## Project Overview

CodeLens is developed as a Flask-based web application that performs static source code analysis without executing the submitted code.

The system analyzes the selected source code and presents the detected issues with relevant information such as:

- Line Number
- Severity
- Issue Description
- Suggested Improvement
- Code Quality Information
- Complexity Information

The main objective of the system is to help developers understand potential problems in their source code and improve its quality, readability, maintainability, and security.

## Supported Programming Languages

- Python
- Java
- C++

## Features

### User Authentication

- User Registration
- User Login
- Logout
- Google Login
- Forgot Password
- Password Reset

### Code Review

- Source Code Submission
- Source Code Upload
- Programming Language Selection
- Static Code Analysis
- Syntax Checking
- Code Quality Analysis
- Complexity Analysis
- Security-related Analysis
- Duplicate Code Detection
- Readability and Maintainability Checks

### Analysis Results

- Issue Detection
- Line Number Display
- Severity Classification
- Issue Description
- Suggested Improvements
- Quality Score
- Complexity Information

### Other Features

- Dashboard
- Saved Code
- PDF Report Generation
- Profile Management
- Settings
- Help & Support

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- SQLite
- ReportLab
- Visual Studio Code

## System Architecture

```text
                 USER
                   |
                   v
          Web User Interface
                   |
                   v
          Flask Application
                   |
          +--------+--------+
          |                 |
          v                 v
 Static Analysis       Database
     Engine             SQLite
          |
          v
   Analysis Results
          |
     +----+----+
     |         |
     v         v
 Results     PDF Reports

 ## Live Demo

The CodeLens – Code Review System is deployed and available online.

**Live Website:**  
https://codelens-code-review-system.onrender.com/