import pytest
from flask import url_for

def test_url_params_display(client):
    test_params = {'param1': 'value1', 'param2': 'value2'}
    response = client.get('/request-info', query_string=test_params)
    assert response.status_code == 200
    for key, value in test_params.items():
        assert key.encode() in response.data
        assert value.encode() in response.data

def test_request_headers_display(client):
    test_headers = {'User-Agent': 'Test Browser', 'Accept-Language': 'ru-RU'}
    response = client.get('/request-info', headers=test_headers)
    assert response.status_code == 200
    for key, value in test_headers.items():
        assert key.encode() in response.data
        assert value.encode() in response.data

def test_cookie_set_and_delete(client):
    response = client.get('/cookies')
    assert response.status_code == 302  
    
    response = client.get('/cookies')
    assert response.status_code == 200
    response_as_text = response.get_data(as_text=True)
    assert 'Значение куки:' in response_as_text
    
    response = client.post('/delete_cookie')
    assert response.status_code == 302  
    
    response = client.get('/cookies')
    assert response.status_code == 302  

def test_form_data_display(client):
    test_data = {'name': 'Test User', 'email': 'test@example.com'}
    response = client.get('/request-info', query_string=test_data)
    assert response.status_code == 200
    response_as_text = response.get_data(as_text=True)
    for key, value in test_data.items():
        assert key in response_as_text
        assert value in response_as_text

def test_phone_validation_correct_format(client):
    test_numbers = [
        '8-999-123-45-67',      
        '89991234567',          
        '+7-999-123-45-67',     
        '+7(999)123-45-67',     
        '8(999)123-45-67'      
    ]
    
    for number in test_numbers:
        response = client.post('/phone', data={'phone': number})
        response_as_text = response.get_data(as_text=True)
        assert response.status_code == 200
        assert 'is-invalid' not in response_as_text
        assert 'Недопустимый ввод' not in response_as_text

def test_phone_validation_incorrect_format(client):
    test_numbers = [
        '12345',
        'abcdef',
        '8-999-123-45-6',
        '8-999-123-45-678',
        '8-999-123-45-6a'
    ]
    
    for number in test_numbers:
        response = client.post('/phone', data={'phone': number})
        response_as_text = response.get_data(as_text=True)
        assert response.status_code == 200
        assert 'is-invalid' in response_as_text
        assert 'Недопустимый ввод' in response_as_text

def test_phone_validation_empty_input(client):
    response = client.post('/phone', data={'phone': ''})
    response_as_text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'alert-danger' not in response_as_text

def test_phone_validation_special_characters(client):
    test_numbers = [
        '8(999)123-45-67',
        '8.999.123.45.67',
        '8 999 123 45 67',
        '8-999-123-45-67'
    ]
    
    for number in test_numbers:
        response = client.post('/phone', data={'phone': number})
        response_as_text = response.get_data(as_text=True)
        assert response.status_code == 200
        assert '8-999-123-45-67' in response_as_text
        assert 'alert-danger' not in response_as_text

def test_phone_validation_international_format(client):
    test_numbers = [
        '+7-999-123-45-67',
        '+7(999)123-45-67',
        '+7 999 123 45 67'
    ]
    
    for number in test_numbers:
        response = client.post('/phone', data={'phone': number})
        response_as_text = response.get_data(as_text=True)
        assert response.status_code == 200
        assert '8-999-123-45-67' in response_as_text
        assert 'alert-danger' not in response_as_text

def test_phone_validation_error_message_display(client):
    response = client.post('/phone', data={'phone': 'invalid'})
    assert response.status_code == 200
    response_as_text = response.get_data(as_text=True)
    assert 'is-invalid' in response_as_text
    assert 'Недопустимый ввод' in response_as_text

def test_phone_validation_success_message_display(client):
    response = client.post('/phone', data={'phone': '8-999-123-45-67'})
    assert response.status_code == 200
    assert b'alert-danger' not in response.data
    assert b'8-999-123-45-67' in response.data

def test_phone_validation_whitespace_handling(client):
    test_numbers = [
        ' 8-999-123-45-67 ',
        '8 - 999 - 123 - 45 - 67',
        '8  999  123  45  67'
    ]
    
    for number in test_numbers:
        response = client.post('/phone', data={'phone': number})
        assert response.status_code == 200
        response_as_text = response.get_data(as_text=True)
        assert '8-999-123-45-67' in response_as_text
        assert 'alert-danger' not in response_as_text

def test_phone_validation_mixed_format(client):
    test_numbers = [
        '8(999)-123-45-67',
        '8.999-123.45-67',
        '8 999-123 45-67'
    ]
    
    for number in test_numbers:
        response = client.post('/phone', data={'phone': number})
        response_as_text = response.get_data(as_text=True)
        assert response.status_code == 200
        assert '8-999-123-45-67' in response_as_text
        assert 'alert-danger' not in response_as_text

def test_phone_validation_edge_cases(client):
    test_numbers = [
        '8-999-123-45-67',  
        '8-999-123-45-67-89',  
        '8-999-123-45-6',  
        '8-999-123-45-6a'  
    ]
    
    for number in test_numbers:
        response = client.post('/phone', data={'phone': number})
        response_as_text = response.get_data(as_text=True)
        assert response.status_code == 200
        
        if number == '8-999-123-45-67': 
            assert 'alert-success' in response_as_text
            assert '8-999-123-45-67' in response_as_text
            assert 'is-invalid' not in response_as_text
        else:
            assert 'is-invalid' in response_as_text
            assert 'Недопустимый ввод' in response_as_text
            assert 'alert-success' not in response_as_text

def test_phone_validation_10_digit_numbers(client):
    test_numbers = [
        '1234567890',           
        '123-456-78-90',        
        '123.456.78.90',        
        '123 456 78 90',        
        '(123)456-78-90',       
        '+1234567890'           
    ]
    
    for number in test_numbers:
        response = client.post('/phone', data={'phone': number})
        response_as_text = response.get_data(as_text=True)
        assert response.status_code == 200
        
        assert '8-123-456-78-90' in response_as_text
        assert 'is-invalid' not in response_as_text
        assert 'alert-success' in response_as_text



