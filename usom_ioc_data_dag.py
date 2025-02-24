from airflow import DAG
from airflow.operators.python import PythonOperator  # type: ignore
from datetime import datetime, timedelta
import requests
import json
import os
import time
from requests.adapters import HTTPAdapter, Retry

# API URL
API_URL = "https://www.usom.gov.tr/api/address/index"

# Retry ile requests oturum oluşturma
session = requests.Session()
retries = Retry(
    total=5,  # Maksimum tekrar sayısı
    backoff_factor=1,  # Exponential backoff katsayısı
    status_forcelist=[429, 500, 502, 503, 504],  # Hangi durum kodlarında tekrar denenecek
)
session.mount("https://", HTTPAdapter(max_retries=retries))


# Tüm mevcut datayı çeken fonksiyon
def fetch_all_data(**kwargs):
    page = 1
    total_data = []
    retries = 5  # Maksimum API hata denemesi
    rate_limit_errors = 0  # Oran sınırlama hatalarının sayacı
    backoff_time = 10  # İlk bekleme süresi
    output_file_path = '/home/can/Desktop/output_ioc.json'

    while True:
        try:
            response = session.get(f"{API_URL}?page={page}", timeout=60)  # Zaman aşımı süresi artırıldı
            print(f"Sayfa {page} yanıtı alındı.")

            # API oran sınırlaması kontrolü
            if response.status_code == 429:
                print("API oran sınırlamasına takıldı, bekleniyor...")
                rate_limit_errors += 1

                if rate_limit_errors >= 2:  # Art arda 2 oran sınırlama hatası
                    print("API oran sınırlama hatası üst üste iki kez alındı, 1 saat bekleniyor...")
                    time.sleep(3600)  # 1 saat bekle
                    rate_limit_errors = 0  # Sayaç sıfırlanıyor
                else:
                    time.sleep(60)  # 60 saniye bekle ve devam et
                continue

            # Hata durumlarında yeniden deneme
            if response.status_code != 200:
                print(f"Error: API response {response.status_code}")
                retries -= 1
                if retries == 0:
                    raise Exception("API çağrıları başarısız oldu, işlem durduruluyor.")
                print(f"{backoff_time} saniye bekleniyor ve tekrar deneniyor...")
                time.sleep(backoff_time)
                backoff_time *= 2  # Bekleme süresini artır
                continue

            # Başarılı yanıt durumunda
            rate_limit_errors = 0
            backoff_time = 10  # Bekleme süresini sıfırla

            data = response.json()
            print(f"Sayfa {page} verisi çekildi: {len(data.get('models', []))} kayıt")

            # Daha fazla veri olmadığında döngüyü bitir
            if 'models' not in data or not data['models']:
                print("Tüm veriler alındı, döngü tamamlandı.")
                break

            total_data.extend(data['models'])

            # Son sayfaya ulaşıldığında döngüyü bitir
            if page >= data.get('pageCount', 0):
                print(f"Son sayfaya ulaşıldı: {page}")
                break

            page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error during API request: {e}")
            retries -= 1
            if retries == 0:
                raise Exception("Bağlantı hatası nedeniyle işlem durduruluyor.")
            print(f"{backoff_time} saniye bekleniyor ve tekrar deneniyor...")
            time.sleep(backoff_time)
            backoff_time *= 2

    # Verileri dosyaya kaydet
    try:
        with open(output_file_path, 'w') as f:
            json.dump(total_data, f)
            print(f"Veriler başarıyla {output_file_path} dosyasına yazdırıldı.")
    except IOError as e:
        raise Exception(f"Veri dosyasına yazılırken bir hata oluştu: {e}")

    # XCom ile dosya yolunu paylaş
    kwargs['ti'].xcom_push(key='output_file_path', value=output_file_path)


def fetch_data_after_date(target_date, **kwargs):
    # XCom'dan dosya yolunu al
    output_file_path = kwargs['ti'].xcom_pull(key='output_file_path', task_ids='fetch_all_data')
    if not output_file_path or not os.path.exists(output_file_path):
        print("Uyarı: Geçici dosya bulunamadı.")
        return []

    # Geçici dosyayı oku
    try:
        with open(output_file_path, 'r') as f:
            total_data = json.load(f)
    except IOError as e:
        raise Exception(f"Dosya okunurken bir hata oluştu: {e}")

    filtered_data = []
    for item in total_data:
        try:
            # Tarihi doğru formatta parse et
            item_date = datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S.%f')
            if item_date > target_date:
                filtered_data.append(item)
        except (KeyError, ValueError) as e:
            print(f"Error parsing date for item: {item} - {e}")

    print(f"Kullanıcının belirttiği tarihten sonraki {len(filtered_data)} kayıt bulundu.")

    # Filtrelenmiş verileri kaydet
    filtered_output_file_path = '/home/can/Desktop/filtered_output_ioc.json'
    try:
        with open(filtered_output_file_path, 'w') as f:
            json.dump(filtered_data, f)
            print(f"Filtrelenmiş veriler başarıyla {filtered_output_file_path} dosyasına yazdırıldı.")
    except IOError as e:
        raise Exception(f"Filtrelenmiş veri dosyasına yazılırken bir hata oluştu: {e}")

    return filtered_data


# Airflow DAG tanımlaması
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ioc_data_fetch_dag',
    default_args=default_args,
    description='USOM IoC verilerini çeken ve tarihe göre filtreleyen DAG',
    schedule=timedelta(days=1),
    catchup=False,
) as dag:

    task_fetch_all_data = PythonOperator(
        task_id='fetch_all_data',
        python_callable=fetch_all_data,
        provide_context=True
    )

    task_fetch_data_after_date = PythonOperator(
        task_id='fetch_data_after_date',
        python_callable=fetch_data_after_date,
        op_args=[datetime(2024, 10, 1)],
        provide_context=True
    )

   # task_fetch_all_data >> task_fetch_data_after_date
