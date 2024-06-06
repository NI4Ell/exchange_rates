import requests
from django.http import JsonResponse, HttpResponse
from django.views import View
from datetime import datetime, timedelta
import zlib
import logging

logger = logging.getLogger(__name__)

def calculate_crc32(data):
    return zlib.crc32(data.encode())

class CurrencyRatesView(View):
    def get(self, request, date):
        url = f'https://www.nbrb.by/api/exrates/rates?ondate={date}&periodicity=0'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            response_data = {
                'status': 'success',
                'data': data
            }
            response_json = JsonResponse(response_data)
            response_json['CRC32'] = calculate_crc32(response_json.content.decode())
            logger.info(f'Request: {request.path}, Response: {response_data}')
            return response_json
        except requests.RequestException as e:
            error_data = {'status': 'error', 'message': str(e)}
            logger.error(f'Request: {request.path}, Error: {error_data}')
            return JsonResponse(error_data, status=500)

class CurrencyRateByCodeView(View):
    def get(self, request, date, code):
        url = f'https://www.nbrb.by/api/exrates/rates?ondate={date}&periodicity=0'
        try:
            response = requests.get(url)
            response.raise_for_status()
            rates = response.json()
            rate = next((item for item in rates if item['Cur_Abbreviation'] == code), None)
            
            if not rate:
                return JsonResponse({'status': 'error', 'message': 'Currency code not found'}, status=404)
            
            # Fetch previous working day's rate for comparison
            prev_date = (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
            prev_url = f'https://www.nbrb.by/api/exrates/rates?ondate={prev_date}&periodicity=0'
            prev_response = requests.get(prev_url)
            prev_response.raise_for_status()
            prev_rates = prev_response.json()
            prev_rate = next((item for item in prev_rates if item['Cur_Abbreviation'] == code), None)
            
            change_info = 'No previous data'
            if prev_rate:
                if rate['Cur_OfficialRate'] > prev_rate['Cur_OfficialRate']:
                    change_info = 'Increased'
                elif rate['Cur_OfficialRate'] < prev_rate['Cur_OfficialRate']:
                    change_info = 'Decreased'
                else:
                    change_info = 'No change'
            
            response_data = {
                'status': 'success',
                'data': rate,
                'change': change_info
            }
            response_json = JsonResponse(response_data)
            response_json['CRC32'] = calculate_crc32(response_json.content.decode())
            logger.info(f'Request: {request.path}, Response: {response_data}')
            return response_json
        except requests.RequestException as e:
            error_data = {'status': 'error', 'message': str(e)}
            logger.error(f'Request: {request.path}, Error: {error_data}')
            return JsonResponse(error_data, status=500)
