import unittest
import requests
import json

def test_access_success():
    response = requests.get("http://super-phase2-api.appspot.com/")
    assert response.status_code == 200
    
def test_char_access():
    response = requests.get("http://super-phase2-api.appspot.com/characters")
    response_body = response.json()
    assert response_body["response"]=="Success"
    
def test_char_page():
    response = requests.get("http://super-phase2-api.appspot.com/characters")
    response_body = response.json()
    assert response_body['page_num']==1
    
def test_char_page_count():
    response = requests.get("http://super-phase2-api.appspot.com/characters")
    response_body = response.json()
    assert response_body['pages_total']==5
    
def test_char_detail():
    response = requests.get("http://super-phase2-api.appspot.com/characters")
    response_body = response.json()
    assert response_body['results'][1]['name'] == "Aquaman"
    
def test_char_page():
    response = requests.get("http://super-phase2-api.appspot.com/characters/3")
    response_body = response.json()
    assert response_body['page_num']==3
    
def test_char_byName():
    response = requests.get("http://super-phase2-api.appspot.com/character/Spider-Man")
    response_body = response.json()
    assert response_body['results']['real_name']=="Peter Benjamin Parker"
    
    
    
def main():
    test_access_success()
    test_char_access()
    test_char_page()
    test_char_page_count()
    test_char_detail()
    test_char_page()
    test_char_byName()
    print("pass!")
    
    
    
main()
