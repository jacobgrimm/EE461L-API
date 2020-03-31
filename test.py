import unittest
import requests
import json

def test_access_success():
    response = requests.get("http://super-phase2-api.appspot.com/")
    assert response.status_code == 200
    
#test Characters
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
    
    
#test issues    
def test_issue_access():
    response = requests.get("http://super-phase2-api.appspot.com/issues")
    response_body = response.json()
    assert response_body["response"]=="Success"
    
def test_issue_page():
    response = requests.get("http://super-phase2-api.appspot.com/issues")
    response_body = response.json()
    assert response_body['page_num']==1
    
def test_issue_page_count():
    response = requests.get("http://super-phase2-api.appspot.com/issues")
    response_body = response.json()
    assert response_body['pages_total']==5
    
def test_issue_detail():
    response = requests.get("http://super-phase2-api.appspot.com/issues")
    response_body = response.json()
    assert response_body['results'][0]['cover_date'] == "1991-10-01"
    
def test_issue_page():
    response = requests.get("http://super-phase2-api.appspot.com/issues/2")
    response_body = response.json()
    assert response_body['page_num']==2
    
def test_issue_page_content():
    response = requests.get("http://super-phase2-api.appspot.com/issues/2")
    response_body = response.json()
    assert response_body['results'][0]['name']=="Introducing the Sensational Black Panther"
    
def test_issue_byName():
    response = requests.get("http://super-phase2-api.appspot.com/issue/Made In China Part One")
    response_body = response.json()
    assert response_body['results']['series']=="New Super-Man"
    
#test authors
def test_author_access():
    response = requests.get("http://super-phase2-api.appspot.com/authors")
    response_body = response.json()
    assert response_body["response"]=="Success"
    
def test_author_page():
    response = requests.get("http://super-phase2-api.appspot.com/authors")
    response_body = response.json()
    assert response_body['page_num']==1
    
def test_author_page_count():
    response = requests.get("http://super-phase2-api.appspot.com/authors")
    response_body = response.json()
    assert response_body['pages_total']==7
    
def test_author_detail():
    response = requests.get("http://super-phase2-api.appspot.com/authors")
    response_body = response.json()
    assert response_body['results'][3]['name'] == "Billy Tan"
    
def test_author_page():
    response = requests.get("http://super-phase2-api.appspot.com/authors/3")
    response_body = response.json()
    assert response_body['page_num']==3
    
def test_author_content():
    response = requests.get("http://super-phase2-api.appspot.com/authors/2")
    response_body = response.json()
    assert response_body['results'][0]['name']=="Introducing the Sensational Black Panther"
    
def test_author_byName():
    response = requests.get("http://super-phase2-api.appspot.com/author/Stan Lee")
    response_body = response.json()
    assert response_body['results']['hometown']=="New York City"

def test_all_characters():
    response = requests.get('http://super-phase2-api.appspot.com/listChars')
    response = response.json()
    for i in response['Result']:
        resp2 = requests.get('http://super-phase2-api.appspot.com/character/' + i)
        resp2 = resp2.json()
        assert resp2['response'] == 'Success'
    
    
def test_all_issues():
    response = requests.get('http://super-phase2-api.appspot.com/listIssues')
    response = response.json()
    for i in response['Result']:
        resp2 = requests.get('http://super-phase2-api.appspot.com/issue/' + i)
        resp2 = resp2.json()
        assert resp2['response'] == 'Success'

def test_all_authors():
    response = requests.get('http://super-phase2-api.appspot.com/listAuthors')
    response = response.json()
    for i in response['Result']:
        resp2 = requests.get('http://super-phase2-api.appspot.com/author/' + i)
        resp2 = resp2.json()
        assert resp2['response'] == 'Success'


def main():
    test_all_characters()
    test_all_authors()
    test_all_issues()

    test_access_success()
    
    test_char_access()
    test_char_page()
    test_char_page_count()
    test_char_detail()
    test_char_page()
    test_char_byName()
    
    test_issue_access()
    test_issue_page()
    test_issue_page_count()
    test_issue_detail()
    test_issue_page()
    test_issue_page_content()
    test_issue_byName()
    
    test_author_access()
    test_author_page()
    test_author_page_count()
    test_author_detail()
    test_author_page()
    test_author_byName()
    
    print("pass all!")
    
    
    
main()
