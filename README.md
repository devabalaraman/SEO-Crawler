# Django Crawler Project

A Django-based web crawler project that provides APIs to crawl websites and retrieve structured data. This README contains all necessary instructions for setup, running, and testing the project.

## Table of Contents

1. [Setup Instructions](#setup-instructions)  
2. [How to Run](#how-to-run)  
3. [Example curl Requests](#example-curl-requests)  
4. [Notes](#notes)  


## Setup Instructions

### 1. Clone the repository

git clone https://github.com/devabalaraman/SEO-Crawler.git
cd your-repo

### 2. Create a virtual environment

python -m venv env
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Configure the database (optional - for mysql/postgresql)
python manage.py migrate


### How to Run

### 1. Start the Django server
python manage.py runserver
 
### 2. Run the crawler command
python manage.py crawl


### Example curl Requests

### 1. Get all domains
curl -X GET http://127.0.0.1:8000/domains/

### 2.a. Get all pages of a domain
curl -X GET http://127.0.0.1:8000/domains/1/pages/

### 2.b. Get specific page from a domain with page limit 
curl -X GET http://127.0.0.1:8000/domains/2/pages/?page=10&page_size=15/

### 3. Get insights of a page
curl -X GET http://127.0.0.1:8000/pages/1/insights/
